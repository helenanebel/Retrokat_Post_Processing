import json


def get_credentials():
    with open("k10plus_credentials.json", "r") as credential_file:
        credential_dict = json.load(credential_file)
        username = credential_dict["username"]
        password = credential_dict["password"]
    return username, password
