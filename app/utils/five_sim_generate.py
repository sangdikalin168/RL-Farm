import random
import string

import names

def five_sim_generate_info(main_email):
    """Generate a random first name, last name, and US phone number."""
    # Generate a random male first name and a random last name
    while True:
        first_name = names.get_first_name(gender='male')
        last_name = names.get_last_name()
        # Ensure the generated names are alphabetic and resemble human names
        if first_name.isalpha() and last_name.isalpha():
            break

    
    password = "RLFARM!#666#"
    random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=4))  # Random 4-character suffix

    email = f"{main_email.split('@')[0]}+{first_name.lower()}{last_name.lower()}{random_suffix}@{main_email.split('@')[1]}"

    return first_name, last_name, password, email


if __name__ == "__main__":
    info = five_sim_generate_info("eth168@zohomail.com")
    print(info[3])
