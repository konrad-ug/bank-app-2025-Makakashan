from flask import Flask, jsonify, request

from src.account import PersonalAccount
from src.registry import AccountRegistry, DuplicatePeselError

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
    try:
        registry.add_account(account)
        return jsonify({"message": "Account created"}), 201
    except DuplicatePeselError:
        return jsonify(
            {"error": f"Account with PESEL {data['pesel']} already exists"}
        ), 409


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


@app.route("/api/accounts/<pesel>/transfer", methods=["POST"])
def transfer(pesel):
    print(f"Transfer request for PESEL: {pesel}")

    # Find account
    account = registry.find_account_by_pesel(pesel)
    if account is None:
        return jsonify({"error": "Account not found"}), 404

    # Get request data
    data = request.get_json()

    # Validate required fields
    if not data or "amount" not in data or "type" not in data:
        return jsonify({"error": "Missing required fields: amount and type"}), 400

    amount = data["amount"]
    transfer_type = data["type"]

    # Validate amount
    if not isinstance(amount, (int, float)) or amount <= 0:
        return jsonify({"error": "Amount must be a positive number"}), 400

    # Validate transfer type
    valid_types = ["incoming", "outgoing", "express"]
    if transfer_type not in valid_types:
        return jsonify(
            {
                "error": f"Invalid transfer type. Must be one of: {', '.join(valid_types)}"
            }
        ), 400

    # Execute transfer based on type
    try:
        if transfer_type == "incoming":
            account.incoming_transfer(amount)
            return jsonify({"message": "Zlecenie przyjęto do realizacji"}), 200

        elif transfer_type == "outgoing":
            initial_balance = account.balance
            account.outgoing_transfer(amount)

            # Check if transfer was successful (balance changed)
            if account.balance == initial_balance:
                return jsonify({"error": "Insufficient funds"}), 422

            return jsonify({"message": "Zlecenie przyjęto do realizacji"}), 200

        elif transfer_type == "express":
            initial_balance = account.balance
            account.express_transfer(amount)

            # Check if transfer was successful (balance changed)
            if account.balance == initial_balance:
                return jsonify({"error": "Insufficient funds"}), 422

            return jsonify({"message": "Zlecenie przyjęto do realizacji"}), 200

    except Exception as e:
        return jsonify({"error": f"Transfer failed: {str(e)}"}), 500
