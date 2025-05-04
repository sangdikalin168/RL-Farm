import random
import secrets
import string

import names
# Sample first and last names


def generate_secure_password(length=12):
    # Define the character set to include only uppercase letters and digits
    characters = string.ascii_uppercase + string.digits
    # Generate a secure random password
    password = ''.join(secrets.choice(characters) for _ in range(length))
    return password

def generate_zoho_info():
    """Generate a random first name, last name, and US phone number."""
    # Generate a random male first name and a random last name
    while True:
        first_name = names.get_first_name(gender='male')
        last_name = names.get_last_name()
        # Ensure the generated names are alphabetic and resemble human names
        if first_name.isalpha() and last_name.isalpha():
            break

    """
    Generate a US phone number with a fixed second digit '6' after the New York area code.
    """
    ny_area_codes = [212, 718, 917, 646, 332, 347]  # Common New York area codes
    area_code = random.choice(ny_area_codes)  # Select a random New York area code
    
    # Fix the second digit to '6', so exchange code is always '6XX' 
    exchange_code_first_digit = 6
    exchange_code_remaining_digits = random.randint(0, 9) * 10 + random.randint(0, 9)  # Remaining two digits
    
    exchange_code = exchange_code_first_digit * 100 + exchange_code_remaining_digits
    subscriber_number = random.randint(1000, 9999)  # Subscriber numbers range from 1000 to 9999
    
    phone_number = f"+1{area_code}{exchange_code}{subscriber_number}"
    
    password = "Reelfb@#2016"
    random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))  # Random 4-character suffix
    email = f"eth168+{random_suffix}@zohomail.com"
    
    return first_name, last_name, phone_number, password, email
