import imaplib
import email
import re
from email.header import decode_header

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
    for eid in reversed(email_ids[-20:]):
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

# # Example usage:
# gmail_address = "jennahrubin69@gmail.com"
# app_password = "vdme mtmz alnw rxuq"
# alias = "johnburrussnpe5f6yj@rlfarm666.com"

# code = get_domain_confirm_code(gmail_address, app_password, alias)
# print("Code:", code)
