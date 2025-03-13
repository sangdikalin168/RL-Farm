
import requests

country = 'england'
operator = 'virtual51'
product = 'facebook'
token = 'eyJhbGciOiJSUzUxMiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3NzI0NjEwNTMsImlhdCI6MTc0MDkyNTA1MywicmF5IjoiNjFhZTM4NTQ3NmY3OGM0MzlkODk1ZGY2YTkyMTg4NDEiLCJzdWIiOjIwNTQ3OTF9.hBcz9PwIMtnn60JM_dQ5p-glZ_lFb8j3XH0oq8Hkp4QcSo8oT9ezngA-KgwIFn_c-rRoKM81MQOvdIuN7-cdPhUQhsCi3GgiXS2fF1i03GU8qCR61E2rTkDFKNy-Da0g0-T5fPE_bGIqltce_3a-uLXKx5HHiLN1oUgHdX3v0In2ghIsBKIILJDYGwGVppjly3eaitzwpDfBRrkOJoPeEoce22V9FhgFXrn7JXeTugb_G7FLgS7PFecFwt45Cy2Q408PBD81GknqdlcfTNES2K9D6dMoSFykvqC65WEF6Exp3NFM1PBe9N1n0ezoSYzYCGYM_GBk2Uwpvxr2GajJCA'


    
def get_sms(id):
    """
    Fetches the SMS code for the specified activation ID.
    
    Args:
        token (str): API token from 5sim.net.
        id (str): Activation ID for which to fetch the SMS code.
    
    Returns:
        str: The SMS code if successful, else None.
    """
    url = f"https://5sim.net/v1/user/check/{id}"
    headers = {
        'Authorization': f'Bearer {token}',
        'Accept': 'application/json',
    }

    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        print(f"Error: {response.status_code}, {response.text}")
        return None  # Return None in case    
 

result = get_sms(744585497)
if result:
    print("FB Code:", result)
else:
    print("No Code available.")    


# id = "744571002"

# headers = {
#     'Authorization': 'Bearer ' + token,
#     'Accept': 'application/json',
# }

# response = requests.get('https://5sim.net/v1/user/finish/' + id, headers=headers)
