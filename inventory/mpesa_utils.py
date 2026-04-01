import requests
import base64
from datetime import datetime
from django.conf import settings
from requests.auth import HTTPBasicAuth

def get_access_token():
    """Generates the temporary token needed to call M-Pesa APIs"""
    api_url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
    consumer_key = settings.MPESA_CONSUMER_KEY
    consumer_secret = settings.MPESA_CONSUMER_SECRET
    
    try:
        res = requests.get(api_url, auth=HTTPBasicAuth(consumer_key, consumer_secret))
        res.raise_for_status() # Check if request was successful
        return res.json()['access_token']
    except Exception as e:
        print(f"Error getting access token: {e}")
        return None

def generate_mpesa_password():
    """Generates the password required for STK Push"""
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    shortcode = settings.MPESA_SHORTCODE
    passkey = settings.MPESA_PASSKEY
    
    data_to_encode = shortcode + passkey + timestamp
    online_password = base64.b64encode(data_to_encode.encode()).decode('utf-8')
    
    return online_password, timestamp