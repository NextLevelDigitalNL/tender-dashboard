import os
import urllib.request
import urllib.error
import json
from flask import Flask, request, redirect, url_for, session, send_from_directory, jsonify

# Load credentials from .env (never exposed to browser)
from dotenv import load_dotenv
load_dotenv()

WEBHOOK_TOKEN   = os.getenv("APP_PASSWORD")
WEBHOOK_TENDERS = os.getenv("WEBHOOK_TENDERS", "https://partou.app.n8n.cloud/webhook/03a8a398-4616-4dad-9e1d-e94c9303d529")
WEBHOOK_OVERIG  = os.getenv("WEBHOOK_OVERIG",  "https://partou.app.n8n.cloud/webhook/13d888d9-ee00-484a-9ee9-ebb6d5402291")

app = Flask(__name__, static_folder="public")
app.secret_key = os.getenv("SESSION_SECRET", "change_this_secret")

# Load users from config/users.json (server-side only, never exposed to browser)
USERS_FILE = os.path.join(os.path.dirname(__file__), "config", "users.json")
with open(USERS_FILE, "r") as f:
    USERS = {u["username"]: u["password"] for u in json.load(f)}


def logged_in():
    return session.get("authenticated") is True


def fetch_webhook(url):
    """Fetch data from a webhook URL and normalize to a list."""
    req = urllib.request.Request(url, headers={"Authorization": WEBHOOK_TOKEN})
    with urllib.request.urlopen(req, timeout=15) as resp:
        data = json.loads(resp.read().decode())
    if isinstance(data, dict):
        if "items" in data and isinstance(data["items"], list):
            data = data["items"]
        else:
            data = [data]
    return data


@app.route("/")
def index():
    if logged_in():
        return redirect(url_for("tenders"))
    return redirect(url_for("login_page"))


@app.route("/login")
def login_page():
    if logged_in():
        return redirect(url_for("tenders"))
    return send_from_directory("public", "login.html")


@app.route("/login", methods=["POST"])
def login():
    username = request.form.get("username", "").strip()
    password = request.form.get("password", "")
    if username in USERS and USERS[username] == password:
        session["authenticated"] = True
        session["user"] = username
        return redirect(url_for("tenders"))
    return redirect(url_for("login_page") + "?error=1")


@app.route("/dashboard")
@app.route("/tenders")
def tenders():
    if not logged_in():
        return redirect(url_for("login_page"))
    return send_from_directory("public", "dashboard.html")


@app.route("/overige-opdrachten")
def overige_opdrachten():
    if not logged_in():
        return redirect(url_for("login_page"))
    return send_from_directory("public", "overige-opdrachten.html")


@app.route("/api/opdrachten")
def api_opdrachten():
    if not logged_in():
        return jsonify({"error": "Unauthorized"}), 401
    try:
        return jsonify(fetch_webhook(WEBHOOK_TENDERS))
    except urllib.error.HTTPError as e:
        return jsonify({"error": f"Webhook fout: {e.code}"}), 502
    except Exception as e:
        return jsonify({"error": str(e)}), 502


@app.route("/api/overige-opdrachten")
def api_overige_opdrachten():
    if not logged_in():
        return jsonify({"error": "Unauthorized"}), 401
    try:
        return jsonify(fetch_webhook(WEBHOOK_OVERIG))
    except urllib.error.HTTPError as e:
        return jsonify({"error": f"Webhook fout: {e.code}"}), 502
    except Exception as e:
        return jsonify({"error": str(e)}), 502


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login_page"))


@app.route("/public/<path:filename>")
def static_files(filename):
    return send_from_directory("public", filename)


if __name__ == "__main__":
    port = int(os.getenv("PORT", 3000))
    app.run(debug=False, port=port)
