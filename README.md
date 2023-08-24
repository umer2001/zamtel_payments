## Zamtel Payments

A frappe app that provides a way to pay through zamtel

## Installation

install the app by following 2 step process

### Add app to bench

```bash
  bench get-app zamtel_payments https://github.com/[username]/zamtel_payments.git
```

### Install app on the site

```bash
  bench --site [site-name] install-app zamtel_payments
```

### Setup guide

After installing the app, open **Desk**, search for **Zamtel Settings List**:

1. Click **Add Zamtel Settings**
2. Add API **username**
3. Add API **password**
4. Add API **requestingAccount**
5. Click on **save**

#### License

MIT
