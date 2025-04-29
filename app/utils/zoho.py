import imaplib
import email
import re

def get_confirmation_code(provider, primary_email, alias_email, password):
    imap_servers = {
        'zoho': 'imap.zoho.com',
        'yandex': 'imap.yandex.com',
    }

    provider = provider.lower()
    imap_host = imap_servers.get(provider)
    if not imap_host:
        print(f"❌ Unsupported provider: {provider}")
        return None

    try:
        # Connect and login
        mail = imaplib.IMAP4_SSL(imap_host)
        mail.login(primary_email, password)
        mail.select('INBOX')

        # Search all emails
        status, data = mail.search(None, 'ALL')
        if status != 'OK':
            print("❌ Failed to search mailbox.")
            return None

        # Get latest email IDs (limit to last 50)
        email_ids = data[0].split()[-50:]

        for eid in reversed(email_ids):
            status, msg_data = mail.fetch(eid, '(RFC822)')
            if status != 'OK':
                continue

            msg = email.message_from_bytes(msg_data[0][1])

            # Delivered-To check
            delivered_to = msg.get("Delivered-To", "")
            to_header = msg.get("To", "")

            if alias_email.lower() not in to_header.lower() and alias_email.lower() not in delivered_to.lower():
                continue

            print(f"✅ Found email to alias: {alias_email}")

            subject = msg.get("Subject", "")
            body = ""

            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_content_type() == "text/plain":
                        charset = part.get_content_charset() or 'utf-8'
                        body = part.get_payload(decode=True).decode(charset, errors="ignore")
                        break
            else:
                charset = msg.get_content_charset() or 'utf-8'
                body = msg.get_payload(decode=True).decode(charset, errors="ignore")

            # Search for code in subject
            match = re.search(r"\b\d{5,8}\b", subject)
            if match:
                return match.group(0)

            # Search in body if not found in subject
            match = re.search(r"\b\d{5,8}\b", body)
            if match:
                return match.group(0)

        print(f"⚠️ No confirmation code found. {alias_email}")
        return None

    except Exception as e:
        print(f"❌ Error: {e}")
        return None


# # Usage Example
# code = get_confirmation_code(provider="zoho",primary_email="eth168@zohomail.com", alias_email="eth168+jeffreymerritt8uc2@zohomail.com", password="SeJrd7FY5d2s")
# if code:
#     print(f"Your Facebook confirmation code is: {code}")
# else:
#     print("No security code found.")