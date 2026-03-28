# License Management System

from flask import Flask, request, jsonify, redirect
import time
import os

app = Flask(__name__)

licenses = {}

# ===== REGISTER =====
@app.route("/register", methods=["POST"])
def register():
    data = request.json
    device = data.get("device_id")
    expiry = data.get("expiry")

    if device not in licenses:
        licenses[device] = {
            "expiry": expiry,
            "blocked": False,
            "created": int(time.time())
        }

    return jsonify({"status": "registered"})


# ===== VERIFY =====
@app.route("/verify", methods=["POST"])
def verify():
    data = request.json
    device = data.get("device_id")

    if device not in licenses:
        return jsonify({"status": "invalid"})

    lic = licenses[device]

    if lic["blocked"]:
        return jsonify({"status": "blocked"})

    if time.time() > lic["expiry"]:
        return jsonify({"status": "expired"})

    return jsonify({"status": "valid"})


# ===== BLOCK =====
@app.route("/block/<device>")
def block(device):
    if device in licenses:
        licenses[device]["blocked"] = True
    return redirect("/")


# ===== UNBLOCK =====
@app.route("/unblock/<device>")
def unblock(device):
    if device in licenses:
        licenses[device]["blocked"] = False
    return redirect("/")


# ===== PANEL =====
@app.route("/")
def panel():
    html = """
    <html>
    <head>
    <title>🔥 License Control Panel</title>
    <style>
        body {background:#0f172a;color:#e2e8f0;font-family:Arial;text-align:center;}
        h1 {color:#22c55e;}
        table {margin:auto;width:90%;background:#1e293b;border-collapse:collapse;}
        th,td {padding:10px;border-bottom:1px solid #334155;}
        th {background:#020617;color:#22c55e;}
        tr:hover {background:#334155;}
        .block{background:red;color:white;padding:5px;}
        .unblock{background:green;color:black;padding:5px;}
    </style>
    </head>
    <body>
    <h1>🔥 License Control Panel</h1>
    <table>
    <tr><th>Device</th><th>Expiry</th><th>Status</th><th>Action</th></tr>
    """

    for d, v in licenses.items():
        status = "Blocked" if v["blocked"] else "Active"

        btn = f"<a href='/unblock/{d}'><button class='unblock'>Unblock</button></a>" \
            if v["blocked"] else \
            f"<a href='/block/{d}'><button class='block'>Block</button></a>"

        html += f"<tr><td>{d}</td><td>{v['expiry']}</td><td>{status}</td><td>{btn}</td></tr>"

    html += "</table></body></html>"
    return html


# ===== RUN =====
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)
