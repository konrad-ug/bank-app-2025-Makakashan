from flask import Flask, jsonify, request

from src.account import PersonalAccount
from src.registry import AccountRegistry

app = Flask(__name__)
registry = AccountRegistry()


@app.route("/")
def home():
    return "Welcome to the Bank Account API"


@app.route("/api/accounts", methods=["POST"])
def create_account():
    data = request.get_json()
    print(f"Create account request: {data}")
    account = PersonalAccount(
        first_name=data["name"],
        last_name=data["surname"],
        balance=0.0,
        pesel=data["pesel"],
    )
    registry.add_account(account)
    return jsonify({"message": "Account created"}), 201


@app.route("/api/accounts", methods=["GET"])
def get_all_accounts():
    print("Get all accounts request received")
    accounts = registry.get_all_accounts()
    accounts_data = [
        {
            "name": acc.first_name,
            "surname": acc.last_name,
            "pesel": acc.pesel,
            "balance": acc.balance,
        }
        for acc in accounts
    ]
    return jsonify(accounts_data), 200


@app.route("/api/accounts/count", methods=["GET"])
def get_account_count():
    print("Get account count request received")
    count = registry.get_account_count()
    return jsonify({"count": count}), 200


@app.route("/api/accounts/<pesel>", methods=["GET"])
def get_account_by_pesel(pesel):
    print(f"Get account by PESEL request: {pesel}")
    account = registry.find_account_by_pesel(pesel)

    if account is None:
        return jsonify({"error": "Account not found"}), 404

    return jsonify(
        {
            "name": account.first_name,
            "surname": account.last_name,
            "pesel": account.pesel,
            "balance": account.balance,
        }
    ), 200


@app.route("/api/accounts/<pesel>", methods=["PUT"])
def update_account(pesel):
    print(f"Update account by PESEL request: {pesel}")
    data = request.get_json()

    account = registry.update_account(
        pesel=pesel, first_name=data.get("name"), last_name=data.get("surname")
    )

    if account is None:
        return jsonify({"error": "Account not found"}), 404

    return jsonify(
        {
            "name": account.first_name,
            "surname": account.last_name,
            "pesel": account.pesel,
            "balance": account.balance,
        }
    ), 200


@app.route("/api/accounts/<pesel>", methods=["DELETE"])
def delete_account(pesel):
    print(f"Delete account by PESEL request: {pesel}")

    success = registry.delete_account(pesel)

    if not success:
        return jsonify({"error": "Account not found"}), 404

    return jsonify({"message": "Account deleted"}), 200
