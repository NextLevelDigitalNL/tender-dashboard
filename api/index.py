import os
import urllib.request
import urllib.error
import json
from flask import Flask, request, send_from_directory, jsonify

WEBHOOK_TOKEN   = os.getenv("APP_PASSWORD", "Iu8pe15v_YRl")
WEBHOOK_TENDERS = os.getenv("WEBHOOK_TENDERS", "https://partou.app.n8n.cloud/webhook/03a8a398-4616-4dad-9e1d-e94c9303d529")
WEBHOOK_OVERIG  = os.getenv("WEBHOOK_OVERIG",  "https://partou.app.n8n.cloud/webhook/13d888d9-ee00-484a-9ee9-ebb6d5402291")

BASE_DIR   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PUBLIC_DIR = os.path.join(BASE_DIR, "public")

app = Flask(__name__)


def fetch_webhook(url):
    req = urllib.request.Request(url, headers={"Authorization": WEBHOOK_TOKEN})
    with urllib.request.urlopen(req, timeout=15) as resp:
        data = json.loads(resp.read().decode())
    if isinstance(data, dict):
        if "items" in data and isinstance(data["items"], list):
            data = data["items"]
        else:
            data = [data]
    return data


def serve_html(filename):
    filepath = os.path.join(PUBLIC_DIR, filename)
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        return content, 200, {"Content-Type": "text/html; charset=utf-8"}
    except Exception as e:
        debug_info = (
            f"FOUT: {e}\n"
            f"__file__: {__file__}\n"
            f"BASE_DIR: {BASE_DIR}\n"
            f"PUBLIC_DIR: {PUBLIC_DIR}\n"
            f"CWD: {os.getcwd()}\n"
        )
        try:
            debug_info += f"Inhoud BASE_DIR: {os.listdir(BASE_DIR)}\n"
        except Exception as e2:
            debug_info += f"Kan BASE_DIR niet lezen: {e2}\n"
        return debug_info, 500, {"Content-Type": "text/plain"}


@app.route("/")
@app.route("/dashboard")
@app.route("/tenders")
def tenders():
    return serve_html("dashboard.html")


@app.route("/overige-opdrachten")
def overige_opdrachten():
    return serve_html("overige-opdrachten.html")


@app.route("/api/opdrachten")
def api_opdrachten():
    try:
        return jsonify(fetch_webhook(WEBHOOK_TENDERS))
    except urllib.error.HTTPError as e:
        return jsonify({"error": f"Webhook fout: {e.code}"}), 502
    except Exception as e:
        return jsonify({"error": str(e)}), 502


@app.route("/api/overige-opdrachten")
def api_overige_opdrachten():
    try:
        return jsonify(fetch_webhook(WEBHOOK_OVERIG))
    except urllib.error.HTTPError as e:
        return jsonify({"error": f"Webhook fout: {e.code}"}), 502
    except Exception as e:
        return jsonify({"error": str(e)}), 502
