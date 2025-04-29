import requests

class FiveSimAPI:
    """
    A class to interact with the 5sim.net API.
    """
    def __init__(self, token: str, country: str, operator: str, product: str = "facebook"):
        self.token = token
        self.country = country
        self.operator = operator
        self.product = product  # Default value is "facebook"
        self.base_url = "https://5sim.net/v1/user"
        self.headers = {
            'Authorization': f'Bearer {self.token}',
            'Accept': 'application/json',
        }


    def get_available_number(self):
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
        url = f"https://5sim.net/v1/user/buy/activation/{self.country}/{self.operator}/{self.product}"
        headers = {
            'Authorization': f'Bearer {self.token}',
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
    

    def get_sms(self,activation_id):
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
            'Authorization': f'Bearer {self.token}',
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

    def get_latest_sms_code(self,activation_id):
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
            'Authorization': f'Bearer {self.token}',
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

    def cancel_activation(self,activation_id):
        headers = {
            'Authorization': 'Bearer ' + self.token,
            'Accept': 'application/json',
        }

        response = requests.get(f'https://5sim.net/v1/user/cancel/{activation_id}', headers=headers)
        if response.status_code == 200:
            print('Activation cancelled')

    def ban_number(self,activation_id):
        headers = {
            'Authorization': 'Bearer ' + self.token,
            'Accept': 'application/json',
        }

        response = requests.get(f'https://5sim.net/v1/user/bn/{activation_id}', headers=headers)
        if response.status_code == 200:
            print('Activation Banned')
            
    def finish_number(self,activation_id):
        headers = {
            'Authorization': 'Bearer ' + self.token,
            'Accept': 'application/json',
        }

        response = requests.get(f'https://5sim.net/v1/user/finish/{activation_id}', headers=headers)
        if response.status_code == 200:
            print('Number Completed')


    def get_balance(self):
        """
        Fetches the current balance from the 5sim.net account.

        Returns:
            float: The current balance if successful, else None.
        """
        headers = {
            'Authorization': 'Bearer ' + self.token,
            'Accept': 'application/json',
        }

        response = requests.get('https://5sim.net/v1/user/profile', headers=headers)
        
        #get balance from the json response
        if response.status_code == 200:
            data = response.json()
            balance = data.get("balance")
            if balance is not None:
                print(f"Current Balance: {balance}")
                return balance
            else:
                print("Error: Balance not found in the response.")
                return None
        else:
            print(f"Error: {response.status_code}, {response.text}")
            return None



# # get_balance()


# # activation_id, five_sim_number = get_available_number()
# # print(activation_id,five_sim_number)

# # cancel_activation("754867428")

# # activation_id = 754879629
# api = FiveSimAPI(token="eyJhbGciOiJSUzUxMiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3NzUzMDgxMjgsImlhdCI6MTc0Mzc3MjEyOCwicmF5IjoiN2YyMTMyMjNmNTcxMjIwMTUzMjM2NDhhM2JiYjM1ZjciLCJzdWIiOjMxMzM0ODR9.aHYVLcrpXSBva917hFbtXAqMgppHuJ5c1yYRzqwEl7QAg8dgehZR7DaWqbbnGhRUThUZqpv6P6NwEDfNa9v2vxFJelwM-XMANchSqOd8vrSht-n1Z_6aLEWefwCYvRHbjT4z3lTB4kJ7X4hkVELiy03PjYvuhCdUGQeV_L0L53LRgrJ2aLi71mv6TZ7MKy7BfYzXmFMaiZ0azH5qbb6jaQR_REPR_1AD0gf4E5-Ue9DP66FunR1UIxtVImZV7Htd0YswQYoJe8-cOrbTlWRMbEoiGfsLjFm17TMj6Ol_tYsdl4d_L6NFWG2mrdd58xGMAM1nnwldzOalkYn1CRRPOg", country="mongolia", operator="virtual21")
# result = api.get_latest_sms_code(770141971)
# print(result)

# # print(get_available_number())