import random
import secrets
import string
import names

email_domains = [
{
    "main_email": "gold168@zohomail.com",
    "pass_mail": "9FxNJG2TLLWW"
},
{
    "main_email": "usdt168@zohomail.com",
    "pass_mail": "jWuNc5bWvF45"
},
{
    "main_email": "neo168@zohomail.com",
    "pass_mail": "mr5YSG5zkaTP"
},
{
    "main_email": "cake168@zohomail.com",
    "pass_mail": "41GZzK37J6t9"
},
{
    "main_email": "chilliz168@zohomail.com",
    "pass_mail": "wHFgS7xUCNRe"
},
{
    "main_email": "spx168@zohomail.com",
    "pass_mail": "NEg6Wev9XfgX"
},
{
    "main_email": "pax168@zohomail.com",
    "pass_mail": "1uQCU4K7Jnhr"
},
{
    "main_email": "stacks168@zohomail.com",
    "pass_mail": "jY7tismh7Zv3"
},
{
    "main_email": "bonk168@zohomail.com",
    "pass_mail": "tSkZmMU57EEU"
},
{
    "main_email": "floki168@zohomail.com",
    "pass_mail": "FyFiyiQ11PCp"
},
{
    "main_email": "nexo168@zohomail.com",
    "pass_mail": "jLykfQnRRRpi"
},
{
    "main_email": "iota168@zohomail.com",
    "pass_mail": "eMvmXg94VLJ2"
},
{
    "main_email": "eos168@zohomail.com",
    "pass_mail": "GE4pNSDeXmWv"
},
{
    "main_email": "mantle168@zohomail.com",
    "pass_mail": "qEyYJy9Zjh52"
},
{
    "main_email": "lido168@zohomail.com",
    "pass_mail": "snT1rgHyiceq"
},
{
    "main_email": "cosmo168@zohomail.com",
    "pass_mail": "GmYe1VTxDEfY"
},
{
    "main_email": "binance168@zohomail.com",
    "pass_mail": "vW06XcjGxG5Z"
},
{
    "main_email": "sui168@zohomail.com",
    "pass_mail": "ws7zvFWycdTN"
},
{
    "main_email": "dai168@zohomail.com",
    "pass_mail": "hi0u4syjtWu7"
},
{
    "main_email": "apt168@zohomail.com",
    "pass_mail": "29Fb2vhKy111"
},
{
    "main_email": "okb168@zohomail.com",
    "pass_mail": "C5PQLdwnqWsD"
},
{
    "main_email": "kaspa168@zohomail.com",
    "pass_mail": "UN7yZqQrvcAZ"
},
{
    "main_email": "ondo168@zohomail.com",
    "pass_mail": "sAuRKJHj0wfL"
},
{
    "main_email": "raven168@zohomail.com",
    "pass_mail": "euKrw2MiHdz3"
},
{
    "main_email": "dxy168@zohomail.com",
    "pass_mail": "wAqrYCcLuwh2"
},
{
    "main_email": "alt168@zohomail.com",
    "pass_mail": "ewz7smb469AM"
},
{
    "main_email": "aii168@zohomail.com",
    "pass_mail": "gfvcX8EyHDWn"
},
{
    "main_email": "avax168@zohomail.com",
    "pass_mail": "ydaUqLHEgsvE"
},
{
    "main_email": "storm168@zohomail.com",
    "pass_mail": "WgbBmSrm7aWP"
},
{
    "main_email": "luna168@zohomail.com",
    "pass_mail": "C3DyTL2gNsJ5"
},
{
    "main_email": "ftx168@zohomail.com",
    "pass_mail": "U6LrUKaLvgW8"
},
{
    "main_email": "bybit168@zohomail.com",
    "pass_mail": "x2xZykcZd9fk"
},
{
    "main_email": "one168@zohomail.com",
    "pass_mail": "FYEt1C72VBSD"
},
{
    "main_email": "matic168@zohomail.com",
    "pass_mail": "r7qHKNpsYSQG"
},
{
    "main_email": "beta168@zohomail.com",
    "pass_mail": "gq6xY5MJq5gf"
},
{
    "main_email": "gmt168@zohomail.com",
    "pass_mail": "HhFbgHrSGSw3"
},
{
    "main_email": "atom168@zohomail.com",
    "pass_mail": "R5pdf3Schu94"
},
{
    "main_email": "btc168@zohomail.com",
    "pass_mail": "DY2FszYFnU2P"
},
{
    "main_email": "dot168@zohomail.com",
    "pass_mail": "4iJnsDB8EBXa"
},
{
    "main_email": "axs168@zohomail.com",
    "pass_mail": "Cx0L0Rbnighq"
},
{
    "main_email": "etc168@zohomail.com",
    "pass_mail": "jgYd4yRs1c78"
},
{
    "main_email": "ape168@zohomail.com",
    "pass_mail": "uVXq7GGUzsvg"
},
{
    "main_email": "bat168@zohomail.com",
    "pass_mail": "TiaynCzTDTfg"
},
{
    "main_email": "trx168@zohomail.com",
    "pass_mail": "JbDRPq0XtwLC"
},
{
    "main_email": "gala168@zohomail.com",
    "pass_mail": "GtLUBxNGF5CW"
},
{
    "main_email": "sand168@zohomail.com",
    "pass_mail": "KLnP1S1i8yCX"
},
{
    "main_email": "mana666@zohomail.com",
    "pass_mail": "bpE6GqMf1BNG"
},
{
    "main_email": "ada168@zohomail.com",
    "pass_mail": "Aucu32i92DTm"
},
{
    "main_email": "near168@zohomail.com",
    "pass_mail": "DURbciQNj5wr"
},
{
    "main_email": "bnb168@zohomail.com",
    "pass_mail": "ThCQMwH903Pf"
},
{
    "main_email": "trump168@zohomail.com",
    "pass_mail": "e2vjYvZEzvUv"
},
{
    "main_email": "ftm168@zohomail.com",
    "pass_mail": "s4tBXH6N7qLm"
},
{
    "main_email": "xrp168@zohomail.com",
    "pass_mail": "UKth3J6unMky"
},
{
    "main_email": "sol168@zohomail.com",
    "pass_mail": "aqD7fXNAxvKd"
},
{
    "main_email": "polkadot168@zohomail.com",
    "pass_mail": "YyEy5Nh6eia6"
},
{
    "main_email": "eth_creator@zohomail.com",
    "pass_mail": "wSTrFKtzj1vr"
},
{
    "main_email": "eth168@zohomail.com",
    "pass_mail": "SeJrd7FY5d2s"
},
{
    "main_email": "labubu168@zohomail.com",
    "pass_mail": "4Sz1R8MXGuAX"
}
]

def generate_secure_password(length=12):
    # Define the character set to include only uppercase letters and digits
    characters = string.ascii_uppercase + string.digits
    # Generate a secure random password
    password = ''.join(secrets.choice(characters) for _ in range(length))
    return password

def generate_info():
    """
    Generate a random first name, last name, US phone number, password, and Fastmail alias email address.
    The alias email will follow the format: <prefix><random_suffix>@fastmail.com
    """
    # Generate a random male first name and a random last name
    while True:
        first_name = names.get_first_name(gender='male')
        last_name = names.get_last_name()
        # Ensure the generated names are alphabetic and resemble human names
        if first_name.isalpha() and last_name.isalpha():
            break

    # Common New York area codes
    ny_area_codes = [212, 718, 917, 646, 332, 347]
    area_code = random.choice(ny_area_codes)  # Select a random New York area code

    # Fix the second digit to '6', so the exchange code is always '6XX'
    exchange_code_first_digit = 6
    exchange_code_remaining_digits = random.randint(0, 9) * 10 + random.randint(0, 9)  # Remaining two digits
    exchange_code = exchange_code_first_digit * 100 + exchange_code_remaining_digits

    # Subscriber numbers range from 1000 to 9999
    subscriber_number = random.randint(1000, 9999)

    # Format the phone number as +1<area_code><exchange_code><subscriber_number>
    phone_number = f"+1{area_code}{exchange_code}{subscriber_number}"

    # Fixed password
    password = "Reelfb@#1992"

    # Generate a Fastmail alias email address
 
    # Select a random email domain from the list
    chosen_email = random.choice(email_domains)
    main_email = chosen_email["main_email"]
    pass_mail = chosen_email["pass_mail"]


    # Generate alias email using only a random alphanumeric suffix
    random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
    alias_email = f"{main_email.split('@')[0]}+{random_suffix}@{main_email.split('@')[1]}"

    # Return generated information
    return {
        "first_name": first_name,
        "last_name": last_name,
        "phone_number": phone_number,
        "password": password,
        "alias_email": alias_email,
        "main_email": main_email,
        "pass_mail": pass_mail
    }


# # Example usage

# if __name__ == "__main__":
#     info = generate_info()

#     # Unpacking dictionary keys into variables
#     first_name, last_name, phone_number, password, alias_email, main_email, pass_mail = info.values()

#     print(first_name) 
#     print(alias_email) 