import requests

country = 'mongolia'
operator = 'virtual21'


product = 'facebook'
token = 'eyJhbGciOiJSUzUxMiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3NzI0NjEwNTMsImlhdCI6MTc0MDkyNTA1MywicmF5IjoiNjFhZTM4NTQ3NmY3OGM0MzlkODk1ZGY2YTkyMTg4NDEiLCJzdWIiOjIwNTQ3OTF9.hBcz9PwIMtnn60JM_dQ5p-glZ_lFb8j3XH0oq8Hkp4QcSo8oT9ezngA-KgwIFn_c-rRoKM81MQOvdIuN7-cdPhUQhsCi3GgiXS2fF1i03GU8qCR61E2rTkDFKNy-Da0g0-T5fPE_bGIqltce_3a-uLXKx5HHiLN1oUgHdX3v0In2ghIsBKIILJDYGwGVppjly3eaitzwpDfBRrkOJoPeEoce22V9FhgFXrn7JXeTugb_G7FLgS7PFecFwt45Cy2Q408PBD81GknqdlcfTNES2K9D6dMoSFykvqC65WEF6Exp3NFM1PBe9N1n0ezoSYzYCGYM_GBk2Uwpvxr2GajJCA'


def get_available_number():
    """
    Fetches an available phone number for the specified country, operator, and product.

    Args:
        token (str): API token from 5sim.net.
        country (str): Country code (e.g., "usa", "england").
        operator (str): Mobile operator or "any" for random.
        product (str): Service for which the number is needed (e.g., "facebook", "whatsapp").

    Returns:
        tuple: (id, phone) if successful, else None.
    """
    url = f"https://5sim.net/v1/user/buy/activation/{country}/{operator}/{product}"
    headers = {
        'Authorization': f'Bearer {token}',
        'Accept': 'application/json',
    }

    try:
        response = requests.get(url, headers=headers)

        # Check if response body is empty
        if response.status_code == 200 and response.text.strip():
            try:
                data = response.json()
                activation_id = data.get("id")
                phone_number = data.get("phone")

                if activation_id and phone_number:
                    return activation_id, phone_number
                else:
                    print("Error: `id` or `phone` not found in the response.")
                    return None
            except requests.exceptions.JSONDecodeError:
                # print("Error: Response is not valid JSON")
                return None
        else:
            print(f"Error {response.status_code}: Empty or Invalid Response")
            return None

    except requests.exceptions.RequestException as e:
        print(f"Network Request Failed: {e}")
        return None
    
def get_sms(activation_id):
    """
    Fetches the received SMS verification code for a given activation ID.
    
    Args:
        token (str): API token from 5sim.net.
        activation_id (int): The ID of the purchased number.
    
    Returns:
        str: The extracted verification code if available, else None.
    """
    url = f"https://5sim.net/v1/user/check/{activation_id}"
    headers = {
        'Authorization': f'Bearer {token}',
        'Accept': 'application/json',
    }

    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        if data.get("sms") and len(data["sms"]) > 0:
            print(data)
            return data["sms"][0]["code"]  # Extracts the verification code
        else:
            print("No SMS received yet.")
            return None
    else:
        print(f"Error: {response.status_code}, {response.text}")
        return None 

def get_latest_sms_code(activation_id):
    """
    Fetches the latest received SMS verification code for a given activation ID.

    Args:
        token (str): API token from 5sim.net.
        activation_id (int): The ID of the purchased number.

    Returns:
        str: The latest verification code if available, else None.
    """
    url = f"https://5sim.net/v1/user/check/{activation_id}"
    headers = {
        'Authorization': f'Bearer {token}',
        'Accept': 'application/json',
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        
        # Check if SMS data exists
        if data.get("sms") and len(data["sms"]) > 0:
            latest_sms = data["sms"][-1]  # Get the most recent SMS
            return latest_sms["code"]  # Extract verification code
        
        print("No SMS received yet.")
        return None
    else:
        print(f"Error: {response.status_code}, {response.text}")
        return None

def cancel_activation(id):
    headers = {
        'Authorization': 'Bearer ' + token,
        'Accept': 'application/json',
    }

    response = requests.get(f'https://5sim.net/v1/user/cancel/{id}', headers=headers)
    if response.status_code == 200:
        print('Activation cancelled')

def ban_number(id):
    headers = {
        'Authorization': 'Bearer ' + token,
        'Accept': 'application/json',
    }

    response = requests.get(f'https://5sim.net/v1/user/bn/{id}', headers=headers)
    if response.status_code == 200:
        print('Activation Banned')
        
def finish_number(id):
    headers = {
        'Authorization': 'Bearer ' + token,
        'Accept': 'application/json',
    }

    response = requests.get(f'https://5sim.net/v1/user/finish/{id}', headers=headers)
    if response.status_code == 200:
        print('Number Completed')

# activation_id, five_sim_number = get_available_number()
# print(activation_id,five_sim_number)

# cancel_activation("754867428")

# activation_id = 754879629
# result = get_latest_sms_code(763229731)
# print(result)

# print(get_available_number())