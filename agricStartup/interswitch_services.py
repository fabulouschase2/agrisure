import os
import requests
from requests.auth import HTTPBasicAuth

INTERSWITCH_BASE = os.environ.get('INTERSWITCH_BASE_URL')
CLIENT_ID = os.environ.get('INTERSWITCH_CLIENT_ID')
CLIENT_SECRET = os.environ.get('INTERSWITCH_CLIENT_SECRET')

def get_access_token():
    """Obtain OAuth token from Interswitch."""
    url = f"{INTERSWITCH_BASE}/passport/oauth/token"
    auth = HTTPBasicAuth(CLIENT_ID, CLIENT_SECRET)
    data = {'grant_type': 'client_credentials', 'scope': 'profile'}
    resp = requests.post(url, auth=auth, data=data)
    resp.raise_for_status()
    return resp.json()['access_token']

def _call_interswitch_api(method, endpoint, payload=None, params=None):
    token = get_access_token()
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    url = f"{INTERSWITCH_BASE}{endpoint}"
    if method == 'GET':
        resp = requests.get(url, headers=headers, params=params)
    elif method == 'POST':
        resp = requests.post(url, headers=headers, json=payload)
    else:
        raise ValueError("Unsupported method")
    resp.raise_for_status()
    return resp.json()

# ---------- Data Services ----------
def get_customer_demographics(identification_type, identification_number):
    endpoint = "/api/v1/request/customer-insights/kyc-attributes"
    payload = {
        "identificationType": identification_type,
        "identificationNumber": identification_number
    }
    return _call_interswitch_api('POST', endpoint, payload=payload)

def get_financial_history(identification_number, start_year_month, end_year_month):
    endpoint = "/api/v1/request/customer-insights/financial-attributes"
    payload = {
        "identificationNumber": identification_number,
        "startYearMonth": start_year_month,
        "endYearMonth": end_year_month
    }
    return _call_interswitch_api('POST', endpoint, payload=payload)

def get_financial_habits(identification_number, year_month):
    endpoint = "/api/v1/request/customer-insights/derived-attributes"
    payload = {
        "identificationNumber": identification_number,
        "yearMonth": year_month
    }
    return _call_interswitch_api('POST', endpoint, payload=payload)

def get_credit_score(msisdn):
    endpoint = f"/v1/credit-score?msisdn={msisdn}"
    return _call_interswitch_api('GET', endpoint)

# ---------- Nano Loans ----------
def get_loan_offers(customer_id):
    endpoint = "/lending-service/api/v1/offers"
    payload = {"customerId": customer_id}
    return _call_interswitch_api('POST', endpoint, payload=payload)

def accept_loan_offer(customer_id, offer_id, destination_account_number,
                      destination_bank_code, loan_reference_id):
    endpoint = f"/lending-service/api/v1/offers/{offer_id}/accept"
    payload = {
        "customerId": customer_id,
        "offerId": offer_id,
        "destinationAccountNumber": destination_account_number,
        "destinationBankCode": destination_bank_code,
        "loanReferenceId": loan_reference_id
    }
    return _call_interswitch_api('POST', endpoint, payload=payload)

def verify_bank_account(bank_code, account_number):
    endpoint = f"/api/v1/inquiry/bank-code/{bank_code}/account/{account_number}"
    return _call_interswitch_api('GET', endpoint)

def update_loan_status(loan_id, status):
    endpoint = f"/lending-service/api/v1/loans/{loan_id}/update"
    payload = {"status": status}
    return _call_interswitch_api('PUT', endpoint, payload=payload)