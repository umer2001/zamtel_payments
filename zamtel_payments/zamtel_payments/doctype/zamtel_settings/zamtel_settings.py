# Copyright (c) 2023, DNDEV Agency and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import call_hook_method
from zamtel_payments.zamtel_payments.doctype.zamtel_settings.zamtel_connector import ZamtelConnector
from zamtel_payments.zamtel_payments.doctype.zamtel_settings.zamtel_custom_fields import (
    create_custom_pos_fields,
)
from erpnext.erpnext_integrations.utils import create_mode_of_payment
from erpnext.utilities import payment_app_import_guard


class ZamtelSettings(Document):
    supported_currencies = ["ZMW"]

    def validate_transaction_currency(self, currency):
        """Validate if the currency is supported by Zamtel."""
        if currency not in self.supported_currencies:
            frappe.throw(
                _(
                    "Please select another payment method. Zamtel does not support transactions in currency '{0}'"
                ).format(currency)
            )

    def on_update(self):
        with payment_app_import_guard():
            from payments.utils import create_payment_gateway

        create_custom_pos_fields()
        create_payment_gateway(
            "Zamtel-" + self.username,
            settings="Zamtel Settings",
            controller=self.username,
        )
        call_hook_method(
            "payment_gateway_enabled", gateway="Zamtel-" + self.username, payment_channel="Phone"
        )

        # required to fetch the bank account details from the payment gateway account
        frappe.db.commit()
        create_mode_of_payment("Zamtel-" + self.username, payment_type="Phone")

    def request_for_payment(self, **kwargs):
        args = frappe._dict(kwargs)
        request_amounts = [args.request_amount]

        for i, amount in enumerate(request_amounts):
            args.request_amount = amount
            response = frappe._dict(generate_zamtel_push(**args))

            verify_transaction(result=response, **args)


def generate_zamtel_push(**kwargs):
    """Generate zamtel push by making a API call to the zamtel push API."""
    args = frappe._dict(kwargs)
    print("args=>", args)
    try:
        zamtel_settings = frappe.get_doc(
            "Zamtel Settings", args.payment_gateway[7:])

        connector = ZamtelConnector(
            username=zamtel_settings.username,
            password=zamtel_settings.get_password("password"),
        )

        mobile_number = sanitize_mobile_number(args.sender)

        response = connector.zamtel_push(
            amount=args.request_amount,
            phone_number=mobile_number,
            requesting_account=zamtel_settings.requesting_account,
        )

        print("response =>", response)
        return response

    except Exception:
        frappe.log_error("Zamtel Express Transaction Error")
        frappe.throw(
            _("Issue detected with Zamtel configuration, check the error logs for more details"),
            title=_("Zamtel Express Error"),
        )


def sanitize_mobile_number(number):
    """Add country code and strip leading zeroes from the phone number."""
    return str(number).lstrip("+")


@frappe.whitelist(allow_guest=True)
def verify_transaction(result, **kwargs):
    """Verify the transaction result received via callback from stk."""
    args = frappe._dict(kwargs)
    total_paid = 0  # for multiple integration request made against a pos invoice
    success = False  # for reporting successfull callback to point of sale ui

    if args.reference_doctype and args.reference_docname:
        try:
            zamtel_receipt = args.payment_reference
            pr = frappe.get_doc(
                args.reference_doctype, args.reference_docname
            )

            total_paid = args.request_amount
            zamtel_receipts = ", ".join([zamtel_receipt])

            if total_paid >= pr.grand_total:
                pr.run_method("on_payment_authorized", "Completed")
                success = True

            frappe.db.set_value("POS Invoice", pr.reference_name,
                                "zamtel_receipt_number", zamtel_receipts)
        except Exception:
            frappe.log_error("Zamtel: Failed to verify transaction")

    else:
        frappe.log_error("Zamtel: Failed to verify transaction")

    frappe.publish_realtime(
        event="process_phone_payment",
        doctype="POS Invoice",
        docname=args.payment_reference,
        user=frappe.session.user,
        message={
            "amount": total_paid,
            "success": success,
            "failure_message": result.get("code"),
        },
    )
