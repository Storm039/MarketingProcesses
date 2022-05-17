import requests
from requests.auth import HTTPBasicAuth
from config import Utils
from datetime import datetime, date
import re

CONFIG = Utils.load_env()


def check_permission(json):
    return json.get("token") == CONFIG["PERMISSION_TOKEN"]


def get_response_1C(entity, data, method="GET"):
    if method == "GET":
        return requests.get(CONFIG["1C_SERVER"] + entity,
                            auth=HTTPBasicAuth(CONFIG["ONE_C_USER"], CONFIG["ONE_C_PASSWORD"]))
    elif method == "POST":
        return requests.post(CONFIG["1C_SERVER"] + entity,
                             auth=HTTPBasicAuth(CONFIG["ONE_C_USER"], CONFIG["ONE_C_PASSWORD"]),
                             json=data)
    elif method == "PUT":
        return requests.put(CONFIG["1C_SERVER"] + entity,
                            auth=HTTPBasicAuth(CONFIG["ONE_C_USER"], CONFIG["ONE_C_PASSWORD"]),
                            json=data)
    elif method == "PATCH":
        return requests.patch(CONFIG["1C_SERVER"] + entity,
                              auth=HTTPBasicAuth(CONFIG["ONE_C_USER"], CONFIG["ONE_C_PASSWORD"]),
                              json=data)
    else:
        return None


def get_response_DB(entity, data, method="GET"):
    if method == "GET":
        return requests.get(CONFIG["DB_SERVER"] + entity,
                            auth=HTTPBasicAuth(CONFIG["DB_USER"], CONFIG["DB_PASSWORD"]))
    elif method == "POST":
        return requests.post(CONFIG["DB_SERVER"] + entity,
                             auth=HTTPBasicAuth(CONFIG["DB_USER"], CONFIG["DB_PASSWORD"]),
                             json=data)
    elif method == "PUT":
        return requests.put(CONFIG["DB_SERVER"] + entity,
                            auth=HTTPBasicAuth(CONFIG["DB_USER"], CONFIG["DB_PASSWORD"]),
                            json=data)
    elif method == "PATCH":
        return requests.patch(CONFIG["DB_SERVER"] + entity,
                              auth=HTTPBasicAuth(CONFIG["DB_USER"], CONFIG["DB_PASSWORD"]),
                              json=data)
    else:
        return None


def update_user_data_to_db(user_id):
    method = "PATCH"
    entity = CONFIG["DB_USERS_API_UPDATE"] + str(user_id) + "/"
    data = {
        "create_1c": True
    }
    response_db = get_response_DB(entity, data=data, method=method)
    # В response_db могут возникать ошибки, например ответ 404 - когда БД не может найти
    # пользователя по идентификатору. Пока не обрабатываем такие моменты.


def create_promotion_to_db(data: dict):
    method = "POST"
    entity = CONFIG["DB_PROMOTIONS_API_UPDATE"]

    text, url = parsing_text_description(data["description"])
    data_start, data_end = parsing_date(data["date_start"], data["date_end"])
    data_for_update = {
        "date_start": data_start,
        "date_end": data_end,
        "description": text,
        "activity": True,
        "image_url": url,
        # "data_sync": datetime.now().isoformat(),
        "company": CONFIG["COMPANY_ID"],
        "guid_one_c": data["guid_one_c"]
    }
    response_db = get_response_DB(entity, data=data_for_update, method=method)


def update_bonuses_to_db(incoming_data: dict):
    method = "PUT"
    entity = CONFIG["DB_BONUSES_API_UPDATE"]

    data_for_update = {
        "quantity": incoming_data["balance"],
        "user": incoming_data["id"]
    }
    response_db = get_response_DB(entity, data=data_for_update, method=method)
    f = 0



def get_valid_user_from_db():
    method = "POST"
    entity = CONFIG["DB_VALID_USER_API"]
    data = {
        "id_company": CONFIG["COMPANY_ID"]
    }
    response_db = get_response_DB(entity, data=data, method=method)
    return response_db.json().get("result")


def user_data_processing(incoming_data: dict):
    data_to_sent = {
        "token": CONFIG["ONE_C_TOKEN"],
        "result": []
    }
    for user_info in incoming_data:
        data_to_sent["result"].append(
            {
                "pk": user_info.get("id"),
                "phone": validate_number_of_phone(user_info.get("phone")),
                "full_name": user_info.get("full_name")
            }
        )
    return data_to_sent


def parsing_text_description(text: str):
    utl_list = re.findall(r'\bhttp\S+', text)
    if len(utl_list) > 0:
        url = utl_list[0]
        for i in utl_list:
            text = text.replace(i, "")
    else:
        url = ""
    text = "".join(re.findall(r'\S+\s{0,2}', text))
    return text, url


def parsing_date(data_start: str, data_end: str):
    if datetime.fromisoformat(data_start) < datetime.now():
        data_start = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    else:
        data_start = datetime.strftime(datetime.fromisoformat(data_start), "%Y-%m-%d %H:%M:%S")
    if datetime.fromisoformat(data_end) < datetime(2022, 1, 1):
        data_end = datetime(2035, 1, 1).strftime("%Y-%m-%d %H:%M:%S")
    else:
        data_start = datetime.strftime(datetime.fromisoformat(data_end), "%Y-%m-%d %H:%M:%S")
    return data_start, data_end


def validate_number_of_phone(number: str):
    return re.findall(r"\d{10}\b", "".join(re.findall(r"\d", number)))[0]
