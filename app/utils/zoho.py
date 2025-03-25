# import re
# import sys
# from imap_tools import MailBox
# # Ensure correct UTF-8 encoding for output
# sys.stdout.reconfigure(encoding='utf-8')

# def get_confirmation_code(primary_email, alias_email, password):
#     IMAP_SERVER = "imap.zoho.com"

#     try:
#         with MailBox(IMAP_SERVER).login(primary_email, password, initial_folder="INBOX") as mailbox:
#             emails = mailbox.fetch(limit=35, reverse=True) # Fetch the latest 30 emails

#             for msg in emails:
#                 email_to = list(msg.to)  # Convert tuple to list
#                 delivered_to = msg.headers.get("Delivered-To", "Not Found")  # Check Delivered-To header

#                 # print("\n📧 Email Details:")
#                 # print(f"🔹 From: {msg.from_}")
#                 # print(f"🔹 To: {email_to}")
#                 # print(f"🔹 Delivered-To: {delivered_to}")
#                 # print(f"🔹 Subject: {msg.subject}")

#                 # **Manually filter by alias email**
#                 if alias_email.lower() not in [t.lower() for t in email_to] and alias_email.lower() not in delivered_to.lower():
#                     # print(f"🚨 Skipping: Not sent to alias {alias_email}")
#                     continue

#                 print(f"✅ Processing email sent to alias: {alias_email}")

#                 # **Extract confirmation code from subject**
#                 subject_match = re.search(r"\b\d{5,8}\b", msg.subject)
#                 if subject_match:
#                     confirmation_code = subject_match.group(0)
#                     print(f"✅ Facebook Confirmation Code (from subject): {confirmation_code}")
#                     return confirmation_code

#                 # **Extract from email body if not found in subject**
#                 body_match = re.search(r"\b\d{5,8}\b", msg.text)
#                 if body_match:
#                     confirmation_code = body_match.group(0)
#                     print(f"✅ Facebook Confirmation Code (from body): {confirmation_code}")
#                     return confirmation_code

#         print("⚠️ No confirmation code found in emails sent to alias.")
#         return None

#     except Exception as e:
#         print(f"❌ Error retrieving confirmation code: {e}")
#         return None

# def get_security_code(primary_email, alias_email, password):
    
#     IMAP_SERVER = "imap.zoho.com"
#     """
#     Fetch the latest security code from emails sent to the alias.
#     - Searches only in `INBOX`
#     - Extracts code from `SUBJECT` first (fastest)
#     - If not found in subject, extracts from `BODY`
#     """
#     try:
#         with MailBox(IMAP_SERVER).login(primary_email, password, initial_folder="INBOX") as mailbox:
#             # **IMAP search: Only fetch emails TO the alias**
#             emails = mailbox.fetch(limit=50, reverse=True) # Fetch the latest 200 emails

#             print(f"\n📩 Checking up to 100 emails sent to {alias_email}.")

#             for msg in emails:
#                 email_to = list(msg.to)  # Convert tuple to list
#                 delivered_to = msg.headers.get("Delivered-To", "Not Found")  # Check Delivered-To header
#                 # print("\n📧 Email Details:")
#                 # print(f"🔹 From: {msg.from_}")
#                 # print(f"🔹 To: {msg.to}")
#                 # print(f"🔹 Subject: {msg.subject}")
                
#                 # **Manually filter by alias email**
#                 if alias_email.lower() not in [t.lower() for t in email_to] and alias_email.lower() not in delivered_to.lower():
#                     # print(f"🚨 Skipping: Not sent to alias {alias_email}")
#                     continue

#                 # **Extract security code from subject**
#                 subject_match = re.search(r"\b\d{8}\b", msg.subject)
#                 if subject_match:
#                     security_code = subject_match.group(0)
#                     print(f"✅ Security Code (from subject): {security_code}")
#                     return security_code

#                 # **Extract from email body if not found in subject**
#                 body_match = re.search(r"\b\d{8}\b", msg.text)
#                 if body_match:
#                     security_code = body_match.group(0)
#                     print(f"✅ Security Code (from body): {security_code}")
#                     return security_code

#         print("⚠️ No security code found in emails sent to alias.")
#         return None

#     except Exception as e:
#         print(f"❌ Error retrieving security code: {e}")
#         return None
    
# # # Usage Example
# # code = get_security_code(primary_email="labubu168@zohomail.com", alias_email="labubu168+7876mecz@zohomail.com", password="4Sz1R8MXGuAX")
# # if code:
# #     print(f"🎉 Your Facebook confirmation code is: {code}")
# # else:
# #     print("⚠️ No security code found.")


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


# # # Usage Example
# code = get_confirmation_code(provider="yandex",primary_email="sangdikalin@yandex.com", alias_email="sangdikalin+nswrkw@yandex.com", password="jemkbsquucsaljjf")
# if code:
#     print(f"🎉 Your Facebook confirmation code is: {code}")
# else:
#     print("⚠️ No security code found.")