import os
import re
import sqlite3
from contextlib import closing
from pathlib import Path

from flask import Flask, jsonify, redirect, render_template, request, url_for


BASE_DIR = Path(__file__).resolve().parent
DEFAULT_DATABASE = BASE_DIR / "database" / "app.db"
EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def create_app(test_config=None):
    app = Flask(__name__)
    app.config.from_mapping(
        SECRET_KEY=os.environ.get("SECRET_KEY", "dev"),
        DATABASE=os.environ.get("DATABASE_URL", str(DEFAULT_DATABASE)),
    )

    if test_config:
        app.config.update(test_config)

    init_db(app.config["DATABASE"])

    @app.route("/")
    def index():
        return render_template("index.html")

    @app.route("/register", methods=["POST"])
    def register():
        data = request.get_json(silent=True) if request.is_json else request.form
        payload = {
            "name": (data.get("name") or "").strip(),
            "email": (data.get("email") or "").strip().lower(),
            "event": (data.get("event") or "").strip(),
        }

        errors = validate_registration(payload)
        if errors:
            if request.is_json:
                return jsonify({"errors": errors}), 400
            return render_template("index.html", errors=errors, form=payload), 400

        try:
            user_id = save_registration(app.config["DATABASE"], payload)
        except sqlite3.IntegrityError:
            message = "This email is already registered."
            if request.is_json:
                return jsonify({"errors": [message]}), 409
            return render_template("index.html", errors=[message], form=payload), 409

        if request.is_json:
            return jsonify({"id": user_id, "message": "Registration successful"}), 201
        return redirect(url_for("success", user_id=user_id))

    @app.route("/success")
    def success():
        user_id = request.args.get("user_id", type=int)
        registration = get_registration(app.config["DATABASE"], user_id) if user_id else None
        return render_template("success.html", registration=registration)

    @app.route("/users")
    def users():
        registrations = list_registrations(app.config["DATABASE"])
        return render_template("users.html", registrations=registrations)

    @app.route("/api/users")
    def api_users():
        registrations = [dict(row) for row in list_registrations(app.config["DATABASE"])]
        return jsonify(registrations)

    @app.route("/health")
    def health():
        return jsonify({"status": "ok"})

    return app


def get_connection(database_path):
    connection = sqlite3.connect(database_path)
    connection.row_factory = sqlite3.Row
    return connection


def init_db(database_path):
    Path(database_path).parent.mkdir(parents=True, exist_ok=True)
    with closing(get_connection(database_path)) as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS registrations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                event TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        connection.commit()


def validate_registration(data):
    errors = []
    if not data["name"]:
        errors.append("Name is required.")
    if not data["email"]:
        errors.append("Email is required.")
    elif not EMAIL_PATTERN.match(data["email"]):
        errors.append("Enter a valid email address.")
    if not data["event"]:
        errors.append("Event name is required.")
    return errors


def save_registration(database_path, data):
    with closing(get_connection(database_path)) as connection:
        cursor = connection.execute(
            "INSERT INTO registrations (name, email, event) VALUES (?, ?, ?)",
            (data["name"], data["email"], data["event"]),
        )
        connection.commit()
        return cursor.lastrowid


def get_registration(database_path, user_id):
    with closing(get_connection(database_path)) as connection:
        return connection.execute(
            "SELECT id, name, email, event, created_at FROM registrations WHERE id = ?",
            (user_id,),
        ).fetchone()


def list_registrations(database_path):
    with closing(get_connection(database_path)) as connection:
        return connection.execute(
            """
            SELECT id, name, email, event, created_at
            FROM registrations
            ORDER BY created_at DESC, id DESC
            """
        ).fetchall()


app = create_app()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
