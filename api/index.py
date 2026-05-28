import os
import urllib.request
import urllib.error
import json
from flask import Flask, jsonify

WEBHOOK_TOKEN   = os.getenv("APP_PASSWORD", "Iu8pe15v_YRl")
WEBHOOK_TENDERS = os.getenv("WEBHOOK_TENDERS", "https://partou.app.n8n.cloud/webhook/03a8a398-4616-4dad-9e1d-e94c9303d529")
WEBHOOK_OVERIG  = os.getenv("WEBHOOK_OVERIG",  "https://partou.app.n8n.cloud/webhook/13d888d9-ee00-484a-9ee9-ebb6d5402291")

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
