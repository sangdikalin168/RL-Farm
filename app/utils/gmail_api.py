import requests

def get_order():
    url = "https://api.otp.cheap/stubs/action/neworder?api_key=MaFItTqlxEyT63S4JLth&service_id=facebook&multicode=true&priority=vip"

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        if data.get("success") and "quid" in data:
            print(f"Order successful! Quid: {data['quid']}")
            return data["quid"]
        else:
            print("Order failed or 'quid' missing in response.")
            return None
    except Exception as e:
        print(f"Error in get_order: {e}")
        return None


def get_otp(quid):
    url = f"https://api.otp.cheap/stubs/action/getorder?api_key=MaFItTqlxEyT63S4JLth&quid={quid}"

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        email = data.get("email")
        codes = data.get("all_codes", [])
        latest_code = codes[-1] if codes else None
        
        return email, latest_code

    except Exception as e:
        print(f"Error in get_otp: {e}")
        return None, None



# # # Run it directly
# if __name__ == "__main__":
# #     # get_order()
# #     # quid = get_order()
    
# #     # print(f"Quid: {quid}")
    
#     email, latest_code = get_otp(11961502)
#     print(f"Email: {email}, Latest Code: {latest_code}")
