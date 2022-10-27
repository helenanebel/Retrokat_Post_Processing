import json


def get_name():
    with open("name.json", "r") as name_file:
        name_dict = json.load(name_file)
        BENU_username = name_dict["name"]
    return BENU_username
