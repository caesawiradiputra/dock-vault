import json
import traceback

from configs.logging import logger
from flask import Blueprint, jsonify, render_template, request, session, url_for

from app.auth import (
    initialize_master_key,
    is_master_key_initialized,
    login_required,
    verify_master_key,
)
from app.models import CredentialManager

bp = Blueprint("main", __name__)


@bp.route("/")
def index():
    # Check if master key is initialized
    if not is_master_key_initialized():
        return render_template("init.html")  # Show initialization page

    # Check if user is logged in
    if "master_key" not in session:
        return render_template("login.html")  # Show login page

    # Show main application
    return render_template("index.html")


@bp.route("/api/init", methods=["POST"])
def init_app():
    try:
        data = request.get_json()
        master_key = data.get("master_key")

        if not master_key or len(master_key) < 8:
            return jsonify({"error": "Master key must be at least 8 characters"}), 400

        initialize_master_key(master_key)
        session["master_key"] = master_key  # Auto-login after initialization
        return jsonify({"status": "success", "redirect": url_for("main.index")})

    except Exception as e:
        logger.error(traceback.format_exc())
        logger.error(f"Init error: {str(e)}")
        return jsonify({"error": str(e)}), 400


@bp.route("/api/login", methods=["POST"])
def login():
    try:
        data = request.get_json()
        master_key = data.get("master_key")

        if verify_master_key(master_key):
            session["master_key"] = master_key
            return jsonify({"status": "success", "redirect": url_for("main.index")})

        return jsonify({"error": "Invalid master key"}), 401

    except Exception as e:
        logger.error(traceback.format_exc())
        logger.error(f"Login error: {str(e)}")
        return jsonify({"error": "Login failed"}), 500


@bp.route("/api/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"status": "success", "redirect": url_for("main.index")})


@bp.route("/api/check-auth")
def check_auth():
    return jsonify(
        {
            "initialized": is_master_key_initialized(),
            "authenticated": "master_key" in session,
        }
    )


@bp.route("/api/credentials", methods=["GET"])
@login_required
def get_credentials():
    try:
        manager = CredentialManager(session["master_key"])
        return jsonify(manager.get_all_credentials())

    except Exception as e:
        logger.error(traceback.format_exc())
        logger.error(f"Get credentials error: {str(e)}")
        return jsonify({"error": str(e)}), 500


@bp.route("/api/credential/<cred_id>", methods=["GET"])
@login_required
def get_credential(cred_id):
    try:
        manager = CredentialManager(session["master_key"])
        return jsonify(manager.get_credential(cred_id=cred_id))

    except Exception as e:
        logger.error(traceback.format_exc())
        logger.error(f"Get credentials error: {str(e)}")
        return jsonify({"error": str(e)}), 500


@bp.route("/api/credentials", methods=["POST"])
@login_required
def add_credential():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400

        # Validate required fields
        required_fields = ["name", "type", "username", "secret"]
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({"error": f"Missing required field: {field}"}), 400

        manager = CredentialManager(session["master_key"])
        manager.add_credential(
            name=data["name"],
            cred_type=data["type"],
            env=data.get("env", "dev"),  # Default to dev if not specified
            username=data["username"],
            secret=data["secret"],
            details=data.get("details", {}),  # Ensure details is always a dict
            ssh_passphrase=(
                data.get("ssh_passphrase") if data["type"] == "ssh" else None
            ),
        )

        return jsonify({"status": "success"})

    except Exception as e:
        logger.error(traceback.format_exc())
        logger.error(f"Add credential error: {str(e)}")
        return jsonify({"error": str(e)}), 400


@bp.route("/api/credentials/<cred_id>", methods=["PUT"])
@login_required
def update_credential(cred_id):
    try:
        # Ensure request contains JSON
        if not request.is_json:
            return jsonify({"error": "Missing JSON in request"}), 400

        data = request.get_json()

        manager = CredentialManager(session["master_key"])
        cred = manager.get_credential(cred_id)

        if not cred:
            return jsonify({"error": "Credential not found"}), 404

        # Validate and prepare update data
        update_data = {}
        if "name" in data:
            update_data["name"] = data["name"]
        if "type" in data:
            update_data["type"] = data["type"]
        if "env" in data:
            update_data["env"] = data["env"]
        if "username" in data:
            update_data["username"] = data["username"]
        if "secret" in data:
            update_data["secret"] = data["secret"]
        if "details" in data:
            try:
                update_data["details"] = (
                    data["details"] if isinstance(data["details"], dict) else {}
                )
            except ValueError:
                return jsonify({"error": "Invalid details format"}), 400

        if manager.update_credential(cred_id, **update_data):
            return jsonify({"status": "success"})

        return jsonify({"error": "Update failed"}), 500

    except Exception as e:
        logger.error(f"Update error: {str(e)}")
        return jsonify({"error": str(e)}), 400


@bp.route("/api/credentials/<cred_id>", methods=["DELETE"])
@login_required
def delete_credential(cred_id):
    try:
        manager = CredentialManager(session["master_key"])
        manager.delete_credential(cred_id)
        return jsonify({"status": "success"})

    except Exception as e:
        logger.error(traceback.format_exc())
        logger.error(f"Delete credential error: {str(e)}")
        return jsonify({"error": str(e)}), 400


@bp.route("/api/export", methods=["POST"])
@login_required
def export_data():
    try:
        data = request.get_json()
        if not data or "passphrase" not in data:
            return jsonify({"error": "Passphrase required"}), 400

        manager = CredentialManager(session["master_key"])
        encrypted_data = manager.export_encrypted_data(data["passphrase"])

        return jsonify({"status": "success", "data": encrypted_data})

    except Exception as e:
        logger.error(f"Export error: {str(e)}")
        return jsonify({"error": str(e)}), 500


@bp.route("/api/import", methods=["POST"])
@login_required
def import_data():
    try:
        data = request.get_json()
        if not data or "data" not in data or "passphrase" not in data:
            return jsonify({"error": "Data and passphrase required"}), 400

        manager = CredentialManager(session["master_key"])
        try:
            manager.import_encrypted_data(data["data"], data["passphrase"])
            return jsonify({"status": "success"})
        except ValueError as e:
            return jsonify({"error": str(e)}), 401  # 401 for unauthorized

    except Exception as e:
        logger.error(f"Import error: {str(e)}")
        return jsonify({"error": str(e)}), 500
