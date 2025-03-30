import time
import requests
import re
import json

# Set your credentials and tokens
client_id = "1000.O1TR2DS6JX62BQYDKJOP9QWPZQ9OXB"
client_secret = "fe3032d5aa3dfd9828300a683ab85b1a260ca44798"
refresh_token = "1000.4f354fe82a32a0fd4f1291f812e54a2b.a29a495ae82a2e1a23e736e311c5b24d"  # Replace with your actual refresh token
access_token = None  # Initially None
access_token_expiry = 0  # Timestamp when the access token expires
# Use your existing access token and account ID
folderId = "2067301000000008014"
accountId = "2067301000000008002"

# Function to revoke the refresh token
def revoke_refresh_token(token):
    revoke_url = f"https://accounts.zoho.com/oauth/v2/token/revoke?token={token}"
    response = requests.post(revoke_url)

    if response.status_code == 200:
        print("Refresh token revoked successfully.")
    else:
        print("Failed to revoke refresh token:", response.json())

# Function to get a new access token using the refresh token
def refresh_access_token():
    global access_token, access_token_expiry, refresh_token
    token_url = "https://accounts.zoho.com/oauth/v2/token"
    data = {
        "client_id": client_id,
        "client_secret": client_secret,
        "refresh_token": refresh_token,
        "grant_type": "refresh_token"
    }

    response = requests.post(token_url, data=data)
    token_data = response.json()


    if response.status_code == 200:
        access_token = token_data.get("access_token")
        new_refresh_token = token_data.get("refresh_token")
        expires_in = token_data.get("expires_in")

        if expires_in is not None:
            access_token_expiry = expires_in + time.time()
        else:
            print("Error: 'expires_in' not found in token data.")

        if new_refresh_token:
            with open('refresh_token.json', 'w') as f:
                json.dump({"refresh_token": new_refresh_token}, f)

        print(f"New Access Token: {access_token}")
    else:
        if "invalid" in token_data.get("error", "").lower():
            print("Refresh token is invalid. Revoking it...")
            revoke_refresh_token(refresh_token)
            refresh_token = None
        print("Failed to refresh access token:", token_data)

# Function to check if the access token is expired
def is_access_token_expired():
    return access_token is None or time.time() >= access_token_expiry

# Function to delete a message by its ID
def delete_message(accountId, folderId, messageId):
    api_url = f"https://mail.zoho.com/api/accounts/{accountId}/folders/{folderId}/messages/{messageId}"
    headers = {
        "Authorization": f"Zoho-oauthtoken {access_token}"
    }
    
    response = requests.delete(url=api_url, headers=headers)
    
    if response.status_code == 204:
        print(f"Message with ID {messageId} deleted successfully.")
    else:
        print(f"Failed to delete message. Status code: {response.status_code}, Response: {response.text}")

def zoho_api_get_security_code(recipient_email):
    global access_token
    if is_access_token_expired():
        refresh_access_token()

    headers = {
        "Accept": "application/json",
        "Authorization": f"Zoho-oauthtoken {access_token}"
    }
    
    response = requests.get(url=f"https://mail.zoho.com/api/accounts/{accountId}/messages/view?folderId={folderId}", headers=headers)

    if response.status_code == 200:
        data = response.json().get('data', [])
        
        recipient_email = recipient_email.lower()
        print(f"Looking for security codes sent to: {recipient_email}")
        
        # Filter emails that match the recipient email in the "toAddress" field
        matched_emails = [
            email for email in data 
            if recipient_email in email.get('toAddress', '').lower()
        ]

        print(f"Found {len(matched_emails)} email(s) matching the recipient email.")
        
        for email in matched_emails:
            print(email['subject'])
            subject = email.get('subject', '')
            subject_match = re.search(r'(\d{5,8}) is your security code', subject, re.IGNORECASE)
            if subject_match:
                code = subject_match.group(1)
                print(f"Confirmation code found in subject: {code}")

                # Attempt to delete the message
                try:
                    message_id = email['messageId']
                    delete_message(accountId, folderId, message_id)
                    print(f"Message {message_id} deleted successfully.")
                except Exception as e:
                    print(f"Failed to delete message {message_id}: {e}")
                
                return code

    else:
        print(f"Failed to retrieve data. Status code: {response.status_code}")
        return None
    
def extract_confirmation_code(email_data, recipient_email):

    # Ensure recipient_email is lowercase for comparison
    recipient_email = recipient_email.lower()
    print(f"Looking for confirmation codes sent to: {recipient_email}")

    # Filter emails that match the recipient email in the "toAddress" field
    matched_emails = [
        email for email in email_data 
        if recipient_email in email.get('toAddress', '').lower()
    ]

    print(f"Found {len(matched_emails)} email(s) matching the recipient email.")

    
    for email in matched_emails:
        
        # Try extracting the confirmation code from the subject
        subject = email.get('subject', '')
        # print(email)
        subject_match = re.search(r'(\d{6}) is your code to confirm this email', subject, re.IGNORECASE)
        if subject_match:
            code = subject_match.group(1)
            print(f"Confirmation code found in subject: {code}")

            # Attempt to delete the message
            try:
                message_id = email['messageId']
                delete_message(accountId, folderId, message_id)
                print(f"Message {message_id} deleted successfully.")
            except Exception as e:
                print(f"Failed to delete message {message_id}: {e}")
            
            return code

        # Fallback to extracting from the summary
        summary = email.get('summary', '')
        summary_match = re.search(r"confirmation code:\s*(\d{5})", summary, re.IGNORECASE)
        if summary_match:
            code = summary_match.group(1)
            print(f"Confirmation code found in summary: {code}")

            # Attempt to delete the message
            try:
                message_id = email['messageId']
                delete_message(accountId, folderId, message_id)
                print(f"Message {message_id} deleted successfully.")
            except Exception as e:
                print(f"Failed to delete message {message_id}: {e}")
            
            return code

    print("No confirmation code found.")
    return None  # Return None if no matching email is found

def zoho_api_get_confirmation_code(recipient_email):
    global access_token
    if is_access_token_expired():
        refresh_access_token()

    headers = {
        "Accept": "application/json",
        "Authorization": f"Zoho-oauthtoken {access_token}"
    }

    # Fetch emails from the API
    response = requests.get(url=f"https://mail.zoho.com/api/accounts/{accountId}/messages/view?folderId={folderId}", headers=headers)
    if response.status_code == 200:
        data = response.json().get('data', [])
        return extract_confirmation_code(data, recipient_email)
    else:
        print(f"Failed to retrieve emails. Status code: {response.status_code}, Response: {response.text}")
        return None


# print(zoho_api_get_confirmation_code("eth168+v2fqehww@zohomail.com"))