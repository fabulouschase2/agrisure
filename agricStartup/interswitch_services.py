import requests
import os

INTERSWITCH_BASE = os.environ.get('INTERSWITCH_BASE_URL')
AUTH_HEADER = os.environ.get('INTERSWITCH_AUTHORIZATION')

def get_customer_demographics(identification_type, identification_number):
    url = f"{INTERSWITCH_BASE}/api/v1/request/customer-insights/kyc-attributes"
    headers = {
        'Authorization': AUTH_HEADER,
        'Content-Type': 'application/json'
    }
    
    payload = {
        'identificationType': identification_type,
        'identificationNumber': identification_number
    }
    response = requests.post(url, json=payload, headers=headers)
    return response.json()

def get_credit_score(msisdn):
    url = f"{INTERSWITCH_BASE}/v1/credit-score?msisdn={msisdn}"
    headers = {'Authorization': AUTH_HEADER}
    response = requests.get(url, headers=headers)
    return response.json()