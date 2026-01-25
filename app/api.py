import os
from contextlib import contextmanager
from typing import Callable, Optional

from flask import Flask, jsonify, request

from src.account import PersonalAccount
from src.registry import AccountRegistry, DuplicatePeselError
from src.repositories.mongo_repository import MongoAccountsRepository

app = Flask(__name__)
registry = AccountRegistry()


ALLOWED_PERSISTENCE_OVERRIDE_KEYS = {
    "connection_string",
    "database_name",
    "collection_name",
}


def _close_repository(repo: MongoAccountsRepository) -> None:
    """Dispose of the repository client if it exposes a close method."""
    close_fn = getattr(repo, "close", None)
    if callable(close_fn):
        close_fn()


def _build_persistence_config(overrides: Optional[dict] = None) -> dict:
    """Build persistence configuration merging environment, app config, and explicit overrides."""
    base_config = {
        "connection_string": os.getenv("MONGO_URI", "mongodb://localhost:27017/"),
        "database_name": os.getenv("MONGO_DB_NAME", "bank_app"),
        "collection_name": os.getenv("MONGO_COLLECTION_NAME", "accounts"),
    }

    flask_config_overrides: dict[str, str] = {}
    config_key_map = {
        "connection_string": "MONGO_URI",
        "database_name": "MONGO_DB_NAME",
        "collection_name": "MONGO_COLLECTION_NAME",
    }
    for config_key, flask_key in config_key_map.items():
        value = app.config.get(flask_key)
        if value:
            flask_config_overrides[config_key] = value

    persistence_config = app.config.get("PERSISTENCE_CONFIG")
    if isinstance(persistence_config, dict):
        for key in ALLOWED_PERSISTENCE_OVERRIDE_KEYS:
            if key in persistence_config:
                flask_config_overrides[key] = persistence_config[key]

    base_config.update(flask_config_overrides)

    if overrides:
        base_config.update(
            {
                key: overrides[key]
                for key in ALLOWED_PERSISTENCE_OVERRIDE_KEYS
                if key in overrides
            }
        )
    return base_config


@contextmanager
def persistence_repository(
    overrides: Optional[dict] = None,
    factory: Optional[Callable[..., MongoAccountsRepository]] = None,
):
    """Context manager that yields a Mongo-backed repository, allows custom factories, and handles optional cleanup."""
    config = _build_persistence_config(overrides)
    repo_factory = factory or MongoAccountsRepository
    repo = repo_factory(
        connection_string=config["connection_string"],
        database_name=config["database_name"],
        collection_name=config["collection_name"],
    )
    should_auto_close = factory is None
    try:
        yield repo
    finally:
        if should_auto_close:
            _close_repository(repo)


def _extract_persistence_overrides(payload: Optional[dict]) -> dict:
    """Extract allowed config overrides from request payload."""
    if not isinstance(payload, dict):
        return {}
    raw_overrides = payload.get("config", payload)
    if not isinstance(raw_overrides, dict):
        return {}
    return {
        key: raw_overrides[key]
        for key in ALLOWED_PERSISTENCE_OVERRIDE_KEYS
        if key in raw_overrides
    }


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


@app.route("/api/accounts/save", methods=["POST"])
def save_accounts_to_persistence():
    print("Save accounts to persistence request received")
    payload = request.get_json(silent=True)
    overrides = _extract_persistence_overrides(payload)
    try:
        with persistence_repository(
            overrides,
            factory=app.config.get("ACCOUNTS_REPOSITORY_FACTORY"),
        ) as repo:
            saved = registry.save_accounts_to_repository(repo)
        return jsonify({"message": "Accounts saved to MongoDB", "count": saved}), 200
    except Exception as exc:
        return jsonify({"error": f"Failed to save accounts: {exc}"}), 500


@app.route("/api/accounts/load", methods=["POST"])
def load_accounts_from_persistence():
    print("Load accounts from persistence request received")
    payload = request.get_json(silent=True)
    overrides = _extract_persistence_overrides(payload)
    try:
        with persistence_repository(
            overrides,
            factory=app.config.get("ACCOUNTS_REPOSITORY_FACTORY"),
        ) as repo:
            loaded = registry.load_accounts_from_repository(repo)
        return jsonify(
            {"message": "Accounts loaded from MongoDB", "count": loaded}
        ), 200
    except Exception as exc:
        return jsonify({"error": f"Failed to load accounts: {exc}"}), 500
