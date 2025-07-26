import requests
import time

# Polling settings
MAX_RETRIES = 15
POLL_INTERVAL = 5


def rent_gmail():
    """
    Rent a temporary Gmail address for receiving OTP.
    Returns rented email or None.
    """

    print("Renting temporary Gmail...")
    try:
        response = requests.get("https://api.sptmail.com/api/otp-services/mail-otp-rental?apiKey=IC3H70T796NFAU1N&otpServiceCode=facebook",timeout=10)
    except requests.RequestException as e:
        print(f"⚠️ Network error during rental: {e}")
        return None

    if response.status_code == 200:
        try:
            data = response.json()
            print("Rent Response:", data)

            if data.get("success") and "gmail" in data:
                rented_email = data["gmail"]
                print(f"Rented Email: {rented_email}")
                return rented_email
            else:
                print("❌ Failed to get rented email.")
                print("Raw response:", data)
        except ValueError:
            print("⚠️ Failed to parse JSON:", response.text)
    else:
        print(f"❌ Error {response.status_code}: {response.text}")
        return "No rented email"

    return None


def get_otp_stp(rented_email):
    """
    Fetch OTP from the rented email.
    Returns OTP string or None.
    """

    print(f"🔍 Waiting for OTP at {rented_email}...")

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = requests.get(f'https://api.sptmail.com/api/otp-services/mail-otp-lookup?apiKey=IC3H70T796NFAU1N&otpServiceCode=facebook&gmail={rented_email}',timeout=10)
        except requests.RequestException as e:
            print(f"⚠️ Network error: {e}")
            continue

        if response.status_code == 200:
            try:
                data = response.json()
                print("📥 OTP Lookup Response:", data)

                if data.get("success") and "otp" in data:
                    otp = data["otp"]
                    print(f"✅ OTP Received: {otp}")
                    return otp
                else:
                    print(f"🔑 No OTP yet ({attempt}/{MAX_RETRIES})")
            except ValueError:
                print("⚠️ Failed to parse JSON:", response.text)
        else:
            print(f"❌ Error {response.status_code}: {response.text}")
            break

        time.sleep(POLL_INTERVAL)

    print("⏰ Timed out waiting for OTP.")
    return None


# if __name__ == "__main__":
#     # Step 1: Rent an email
#     rented_email = rent_gmail()
#     print("📧 Rented Email:", rented_email)
    
#     # otp = get_otp_stp("zacukmaria@gmail.com")
    
#     # print("📧 OTP:", otp)
