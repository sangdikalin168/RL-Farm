import requests

token = 'eyJhbGciOiJSUzUxMiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3NzUzMDgxMjgsImlhdCI6MTc0Mzc3MjEyOCwicmF5IjoiN2YyMTMyMjNmNTcxMjIwMTUzMjM2NDhhM2JiYjM1ZjciLCJzdWIiOjMxMzM0ODR9.aHYVLcrpXSBva917hFbtXAqMgppHuJ5c1yYRzqwEl7QAg8dgehZR7DaWqbbnGhRUThUZqpv6P6NwEDfNa9v2vxFJelwM-XMANchSqOd8vrSht-n1Z_6aLEWefwCYvRHbjT4z3lTB4kJ7X4hkVELiy03PjYvuhCdUGQeV_L0L53LRgrJ2aLi71mv6TZ7MKy7BfYzXmFMaiZ0azH5qbb6jaQR_REPR_1AD0gf4E5-Ue9DP66FunR1UIxtVImZV7Htd0YswQYoJe8-cOrbTlWRMbEoiGfsLjFm17TMj6Ol_tYsdl4d_L6NFWG2mrdd58xGMAM1nnwldzOalkYn1CRRPOg'
country = 'england'
operator = 'virtual52'
product = 'facebook'

headers = {
    'Authorization': 'Bearer ' + token,
    'Accept': 'application/json',
}

response = requests.get('https://5sim.net/v1/user/buy/activation/' + country + '/' + operator + '/' + product, headers=headers)

print(response.status_code)
print(response.text)