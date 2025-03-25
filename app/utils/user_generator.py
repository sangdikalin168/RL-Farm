import random
import secrets
import string
import names

zoho_domains  = [
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

yandex_domains = [
    {"main_email": "sangdikalin@yandex.com", "pass_mail": "tmrabikharckqjmt"},
] 

custom_domain = [
    {"main_email": "jennahrubin69@gmail.com", "pass_mail": "vdme mtmz alnw rxuq", "domain_name": "rlfarm666.com"},
]

def generate_secure_password(length=12):
    # Define the character set to include only uppercase letters and digits
    characters = string.ascii_uppercase + string.digits
    # Generate a secure random password
    password = ''.join(secrets.choice(characters) for _ in range(length))
    return password

def generate_info(provider="zoho"):
    """
    Generate a random user profile and email alias using the specified provider: "zoho" or "yandex".
    """

    # Random name
    while True:
        first_name = names.get_first_name(gender='male')
        last_name = names.get_last_name()
        if first_name.isalpha() and last_name.isalpha():
            break

    # Select domain list by provider
    if provider == "zoho":
        domain_list = zoho_domains
    elif provider == "yandex":
        domain_list = yandex_domains
    elif provider == "custom":
        domain_list = custom_domain
    else:
        raise ValueError("Unsupported provider. Choose 'zoho' or 'yandex'.")

    # Select a random email account
    chosen_email = random.choice(domain_list)
    main_email = chosen_email["main_email"]
    pass_mail = chosen_email["pass_mail"]

    # Generate alias
    random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
    
    if provider == "custom":
        alias_email = f"{first_name.lower()}{last_name.lower()}{random_suffix}@{chosen_email["domain_name"]}"
    else:
        alias_email = f"{main_email.split('@')[0]}+{random_suffix}@{main_email.split('@')[1]}"



    # US phone number
    ny_area_codes = [212, 718, 917, 646, 332, 347]
    area_code = random.choice(ny_area_codes)
    exchange_code = 600 + random.randint(0, 99)
    subscriber_number = random.randint(1000, 9999)
    phone_number = f"+1{area_code}{exchange_code}{subscriber_number}"

    # Password (can replace with generate_secure_password())
    password = "Reelfb@#1992"

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
#     info = generate_info("custom")

#     # Unpacking dictionary keys into variables
#     first_name, last_name, phone_number, password, alias_email, main_email, pass_mail = info.values()

#     print(first_name) 
#     print(alias_email) 