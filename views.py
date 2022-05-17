from flask import request, jsonify
from werkzeug.utils import redirect
# from services import Telegram
from updater import app
from handler import *
from config import Utils

CONFIG = Utils.load_env()


@app.route('/createusers/', methods=['POST'])
def create_users_to_1C():
    if not check_permission(request.json):
        return app.make_response(f"Error: Access denied")
    result = get_valid_user_from_db()
    if not result:
        return app.make_response(f"Error: incoming data is incorrect")
    data_to_sent = user_data_processing(result)
    entity = CONFIG["ONE_C_USERS_API_CREATE"]
    response = get_response_1C(entity, data_to_sent, method="POST")
    return app.make_response(f"Process complete")


@app.route('/users/', methods=['POST'])
def get_all_telegram_users_from_1c():
    if not check_permission(request.json):
        return app.make_response(f"Error: Access denied")
    entity = CONFIG["ONE_C_USERS_API_LIST"]
    data = {
        "token": CONFIG["ONE_C_TOKEN"]
    }
    response = get_response_1C(entity, data, method="POST")
    json_r = response.json()
    if json_r.get("error") == 1 or json_r.get("error") is None:
        return app.make_response(f"Error: {json_r.get('description')}")
    else:
        for user_data in json_r.get("data"):
            update_user_data_to_db(user_data.get("id"))
    return app.make_response(f"Process complete")


@app.route('/bonuses/', methods=['POST'])
def get_bonuses_for_all_users():
    if not check_permission(request.json):
        return app.make_response(f"Error: Access denied")
    entity = CONFIG["ONE_C_BONUSES_API_LIST"]
    data = {
        "token": CONFIG["ONE_C_TOKEN"]
    }
    response = get_response_1C(entity, data, method="POST")
    json_r = response.json()
    if json_r.get("error") == 1 or json_r.get("error") is None:
        return app.make_response(f"Error: {json_r.get('description')}")
    else:
        data = json_r.get("data")
        for bonus_data in data:
            update_bonuses_to_db(bonus_data)
    return app.make_response(f"Process complete")


@app.route('/promotions/', methods=['POST'])
def get_all_promotions():
    if not check_permission(request.json):
        return app.make_response(f"Error: Access denied")
    entity = CONFIG["ONE_C_PROMOTIONS_API_LIST"]
    data = {
        "token": CONFIG["ONE_C_TOKEN"]
    }
    response = get_response_1C(entity, data, method="POST")
    json_r = response.json()
    if json_r.get("error") == 1 or json_r.get("error") is None:
        return app.make_response(f"Error: {json_r.get('description')}")
    else:
        data = json_r.get("data")
        for user_data in data:
            create_promotion_to_db(user_data)
    return app.make_response(f"Process complete")
