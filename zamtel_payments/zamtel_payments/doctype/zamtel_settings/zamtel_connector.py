import requests


class ZamtelConnector:
    def __init__(
            self,
            username=None,
            password=None,
            live_url="http://172.233.201.113:7001",
    ):
        """Setup configuration for Zamtel connector and generate new access token."""
        self.username = username
        self.password = password
        self.base_url = live_url
        self.authenticate()

    def authenticate(self):
        """
        This method is used to fetch the access token required by Zamtel.

        Returns:
                access_token (str): This token is to be used with the Bearer header for further API calls to Zamtel.
        """
        authenticate_uri = "/login"
        authenticate_url = "{0}{1}".format(self.base_url, authenticate_uri)
        r = requests.post(authenticate_url, json={
                          "username": self.username, "password": self.password})
        self.authentication_token = r.json()["Authorization"]
        return r.json()["Authorization"]

    def zamtel_push(
            self,
            amount=None,
            phone=None,
            requesting_account=None,
    ):
        """
        This method uses Zamtel's Express API to initiate online payment on behalf of a customer.

        Args:
                amount (int): The amount being transacted
                phone(int): The Mobile Number to receive the STK Pin Prompt.
                requesting_account(int): The Till Number to receive the funds being transacted.	

        Success Response:
                CustomerMessage(str): Messages that customers can understand.
                CheckoutRequestID(str): This is a global unique identifier of the processed checkout transaction request.
                ResponseDescription(str): Describes Success or failure
                MerchantRequestID(str): This is a global unique Identifier for any submitted payment request.
                ResponseCode(int): 0 means success all others are error codes. e.g.404.001.03

        Error Reponse:
                requestId(str): This is a unique requestID for the payment request
                errorCode(str): This is a predefined code that indicates the reason for request failure.
                errorMessage(str): This is a predefined code that indicates the reason for request failure.
        """

        payload = {
            "amount": amount,
            "phone": phone,
            "requestingAccount": requesting_account,
        }
        headers = {
            "Authorization": self.authentication_token,
            "Content-Type": "application/json",
        }

        print("payload=>", payload)

        # saf_url = "{0}{1}".format("https://webhook.site", "/c04dce8d-3432-43a6-9ca7-e0c51a4aac0d")
        saf_url = "{0}{1}".format(self.base_url, "/api/zamtelPushService")
        r = requests.post(saf_url, headers=headers, json=payload)
        return r.json()
