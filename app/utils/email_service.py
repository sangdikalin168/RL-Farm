import imaplib
import email
import re
from email.header import decode_header

import sys
# sys.stdout.reconfigure(encoding='utf-8')


def get_email_body(msg):
    """
    Extracts and returns the plain text body of an email message.
    If the email is multipart, it looks for the text/plain part.
    """
    body = ""
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            content_disposition = str(part.get("Content-Disposition"))
            if content_type == "text/plain" and "attachment" not in content_disposition:
                charset = part.get_content_charset() or "utf-8"
                body = part.get_payload(decode=True).decode(charset, errors="replace")
                break
    else:
        charset = msg.get_content_charset() or "utf-8"
        body = msg.get_payload(decode=True).decode(charset, errors="replace")
    return body

def get_domain_confirm_code(primary_email, password, alias_email):
    # Connect to Gmail
    mail = imaplib.IMAP4_SSL("imap.gmail.com")
    mail.login(primary_email, password)
    mail.select("inbox")

    # Search all emails (you can modify the search query as needed)
    status, messages = mail.search(None, 'ALL')
    if status != "OK" or not messages[0]:
        print("📭 No emails found.")
        return None

    email_ids = messages[0].split()

    # Combined regex: try to match either digits then a phrase OR a phrase then digits.
    combined_pattern = re.compile(
        r"(?i)(?:(\d{5,6}).{0,20}(?:confirmation code|verification code|code))|(?:(?:confirmation code|verification code|code)[^\d]{0,10}(\d{5,6}))"
    )

    # Loop through recent messages (e.g., last 20)
    for eid in reversed(email_ids[-10:]):
        status, data = mail.fetch(eid, "(RFC822)")
        if status != "OK":
            continue
        raw_email = data[0][1]
        
        msg = email.message_from_bytes(raw_email)

        # Check if the email was sent to your alias (using "To" and "Delivered-To" headers)
        to_email = msg.get("To", "")
        delivered_to = msg.get("Delivered-To", "")
        if alias_email not in to_email and alias_email not in delivered_to:
            continue  # Skip if this email is not for your alias

        
        # Decode the Subject header
        subject = msg.get("Subject", "")
        decoded_fragments = decode_header(subject)
        decoded_subject = ""
        for fragment, encoding in decoded_fragments:
            if isinstance(fragment, bytes):
                try:
                    decoded_subject += fragment.decode(encoding if encoding else "utf-8", errors="replace")
                except Exception:
                    decoded_subject += fragment.decode("utf-8", errors="replace")
            else:
                decoded_subject += fragment

        # Show the email body as well
        email_body = get_email_body(msg)
        print("Email Subject:", decoded_subject)
        print("Email Body:")
        print(email_body)
        print("-" * 50)

        # Apply the combined regex pattern to the subject
        match = combined_pattern.search(decoded_subject)
        if match:
            # Either group 1 or group 2 will contain the code
            code = match.group(1) if match.group(1) is not None else match.group(2)
            print(f"✅ Code for {alias_email} found in subject: {code}")
            return code
        else:
            # Fallback: search for any 5 or 6-digit number in the subject
            fallback_match = re.search(r"\b\d{5,6}\b", decoded_subject)
            if fallback_match:
                code = fallback_match.group(0)
                print(f"⚠️ Fallback code for {alias_email} found in subject: {code}")
                return code
            else:
                print(f"⚠️ Email to {alias_email} found but no code matched in subject.")

    print(f"❌ No Facebook code found for {alias_email} in subjects.")
    return None


def get_domain_confirm_email(primary_email, password, alias_email):
    """
    Connects to Gmail, searches the inbox for emails sent to the specified alias,
    and prints the subject and body of the matched emails.
    
    Parameters:
        primary_email (str): Your Gmail address.
        password (str): Your Gmail password or app password.
        alias_email (str): The email alias to filter by.
    """
    try:
        # Connect to Gmail
        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        mail.login(primary_email, password)
        mail.select("inbox")
    except Exception as e:
        print("Error connecting to Gmail:", e)
        return

    result, data = mail.search(None, f'(TO "{alias_email}" SUBJECT "Confirm email")')
    if result != "OK" or not data[0]:
        print("No emails matched the search criteria.")
        return
    
    email_ids = data[0].split()

    # Process each matching email (you can change the order or limit if needed)
    for eid in reversed(email_ids):
        status, msg_data = mail.fetch(eid, "(RFC822)")
        if status != "OK":
            print(f"Failed to fetch email with ID {eid.decode() if isinstance(eid, bytes) else eid}")
            continue

        # Parse the email message from the raw bytes
        msg = email.message_from_bytes(msg_data[0][1])

        # Decode and display the subject
        subject = msg.get("Subject", "No Subject")
        decoded_fragments = decode_header(subject)
        decoded_subject = ""
        for fragment, encoding in decoded_fragments:
            if isinstance(fragment, bytes):
                try:
                    decoded_subject += fragment.decode(encoding if encoding else "utf-8", errors="replace")
                except Exception:
                    decoded_subject += fragment.decode("utf-8", errors="replace")
            else:
                decoded_subject += fragment

        # Extract the email body
        body = get_email_body(msg)

        # Print the subject and body
        print("Matched Email Subject:", decoded_subject)
        print("Email Body:")
        print(body)
        print("=" * 50)
        # This regex matches a sequence of 5 or 6 digits with word boundaries
        match = re.search(r'\b\d{5,6}\b', body)
        if match:
            code = match.group(0)
            print("Extracted code:", code)
            return code
        else:
            print("No code found.")

# # # Example usage:
# gmail_address = "jennahrubin69@gmail.com"
# app_password = "vdme mtmz alnw rxuq"
# alias = "eth1688lzt390f@rlfarm666.com"

# code = get_domain_confirm_code(gmail_address, app_password, alias)
# print("Code:", code)
