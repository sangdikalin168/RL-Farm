from time import sleep
import requests
from typing import Optional, Dict, Any


class GmailAPI:
    """
    Gmail API service for creating email orders and retrieving OTPs
    """
    
    def __init__(self, api_key: str = "smfHyExkaKDKyDgJWW04yLycW5vbcwGn"):
        """
        Initialize the Gmail API service
        
        Args:
            api_key (str): API key for the service
        """
        self.api_key = api_key
        self.base_url = "https://yshshopmails.shop/v1/api"
    
    def create_order(self, service: str = "facebook") -> Optional[Dict[str, str]]:
        url = f"{self.base_url}/create-order.php?key={self.api_key}&service={service}"

        # time_out_second = 2000
        # total_time = 1
        
        # while total_time < time_out_second:
        #     try:
        #         response = requests.post(
        #             f"https://yshshopmails.shop/v1/api/create-order.php?key={self.api_key}&service={service}",
        #             timeout=10
        #         )
        #         response.raise_for_status()

        #         data = response.json()
        #         return data.get("mail"), data.get("order_id")

        #     except requests.HTTPError as e:
        #         status_code = e.response.status_code
        #         if status_code == 502:
        #             raise Exception("Invalid API key.") from e
        #         if 500 <= status_code <= 550:
        #             try:
        #                 data = e.response.json()
        #                 msg = data.get("error", e.response.text)
        #                 print(f"API error {status_code}: {msg}")
        #             except ValueError:
        #                 print(f"API error {status_code}: {e.response.text}")
        #         else:
        #             print(f"Unexpected status code: {status_code}")
        #         sleep(1)

        #     except requests.RequestException as e:
        #         print(f"Request error: {e}")
        #         sleep(1)

        #     total_time += 1

        # return None, None
        
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            
            print(data)
            
            # response from api
            # {
            #     "mail": "example@gmail.com",
            #     "order_id": "abc123xyz"
            # }
            
            email = data.get("mail")
            order_id = data.get("order_id")
            
            if email and order_id:
                result = {
                    "email": email,
                    "order_id": order_id
                }
                print(f"Email: {email}, Order ID: {order_id}")
                return result
            else:
                print("Invalid response: missing email or order_id")
                return None

        except requests.RequestException as e:
            print(f"Request error in create_order: {e}")
            return None
        except Exception as e:
            print(f"Error in create_order: {e}")
            return None

    def get_otp(self, order_id: str) -> Optional[str]:
        """
        Get OTP for a specific order
        
        Args:
            order_id (str): Order ID to check for OTP
            
        Returns:
            OTP string if available, None if failed or not ready
        """
        url = f"{self.base_url}/check-otp.php?key={self.api_key}&id={order_id}"

        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            
            # Response (JSON):
            # {
            #     "otp": "123456",
            #     "amount": "0.042",
            #     "time": "2025-07-12 08:00:00"
            # }
            
            otp = data.get("otp")
            return otp

        except requests.RequestException as e:
            print(f"Request error in get_otp: {e}")
            return None
        except Exception as e:
            print(f"Error in get_otp: {e}")
            return None

    def get_full_otp_details(self, order_id: str) -> Optional[Dict[str, Any]]:
        """
        Get full OTP details including amount and time
        
        Args:
            order_id (str): Order ID to check for OTP
            
        Returns:
            Dict containing otp, amount, and time, or None if failed
        """
        url = f"{self.base_url}/check-otp.php?key={self.api_key}&id={order_id}"

        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            
            otp = data.get("otp")
            amount = data.get("amount")
            time = data.get("time")
            
            if otp:
                return {
                    "otp": otp,
                    "amount": amount,
                    "time": time
                }
            return None

        except requests.RequestException as e:
            print(f"Request error in get_full_otp_details: {e}")
            return None
        except Exception as e:
            print(f"Error in get_full_otp_details: {e}")
            return None


# Run it directly
if __name__ == "__main__":
    # Initialize the Gmail API service
    gmail_service = GmailAPI()
    
    # Example usage
    # Create order
    order_data = gmail_service.create_order()
    if order_data:
        print(f"Created order - Email: {order_data['email']}, Order ID: {order_data['order_id']}")
        
        # Get OTP for the order
        otp = gmail_service.get_otp(order_data['order_id'])
        if otp:
            print(f"OTP: {otp}")
        else:
            print("OTP not ready yet")
    
    # Test with existing order ID
    # order_id = "pyAwDH7TPmzZfgeg"
    # otp = gmail_service.get_otp(order_id)
    # if otp:
    #     print(f"OTP for order {order_id}: {otp}")
    # else:
    #     print("Failed to retrieve OTP.")
