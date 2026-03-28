# License Control Panel

from flask import Flask, request, jsonify, redirect
import time
import os
import json

app = Flask(__name__)

DB_FILE = "licenses.json"

# ===== LOAD DB =====
def load_db():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f:
            return json.load(f)
    return {}

# ===== SAVE DB =====
def save_db(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f)

licenses = load_db()

# ===== REGISTER =====
@app.route("/register", methods=["POST"])
def register():
    data = request.json
    device = data.get("device_id")
    expiry = data.get("expiry")

    licenses[device] = {
        "expiry": expiry,
        "blocked": False,
        "created": int(time.time())
    }

    save_db(licenses)

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
        save_db(licenses)
    return redirect("/")

# ===== UNBLOCK =====
@app.route("/unblock/<device>")
def unblock(device):
    if device in licenses:
        licenses[device]["blocked"] = False
        save_db(licenses)
    return redirect("/")

# ===== DELETE =====
@app.route("/delete/<device>")
def delete(device):
    if device in licenses:
        del licenses[device]
        save_db(licenses)
    return redirect("/")

# ===== PANEL =====
@app.route("/")
def panel():
    html = """
    <html>
    <head>
    <title>🔥 License Control Panel</title>
    <style>
        body {
            background:#0f172a;
            color:#e2e8f0;
            font-family:Arial;
            text-align:center;
        }
        h1 {
            color:#22c55e;
            margin-top:20px;
        }
        table {
            margin:auto;
            width:90%;
            background:#1e293b;
            border-collapse:collapse;
            box-shadow:0 0 20px rgba(0,0,0,0.6);
        }
        th,td {
            padding:12px;
            border-bottom:1px solid #334155;
        }
        th {
            background:#020617;
            color:#22c55e;
        }
        tr:hover {
            background:#334155;
        }
        .btn {
            padding:6px 12px;
            border:none;
            border-radius:6px;
            cursor:pointer;
            font-weight:bold;
        }
        .block {background:#ef4444;color:white;}
        .unblock {background:#22c55e;color:black;}
        .delete {background:#facc15;color:black;}
        .status-active {color:#22c55e;font-weight:bold;}
        .status-blocked {color:#ef4444;font-weight:bold;}
    </style>
    </head>
    <body>

    <h1>🔥 License Control Panel</h1>

    <table>
    <tr>
        <th>Device ID</th>
        <th>Expiry</th>
        <th>Status</th>
        <th>Action</th>
    </tr>
    """

    for d, v in licenses.items():
        status = "Blocked" if v["blocked"] else "Active"
        status_class = "status-blocked" if v["blocked"] else "status-active"

        # Buttons
        if v["blocked"]:
            btn = f"<a href='/unblock/{d}'><button class='btn unblock'>Unblock</button></a>"
        else:
            btn = f"<a href='/block/{d}'><button class='btn block'>Block</button></a>"

        btn += f" <a href='/delete/{d}'><button class='btn delete'>Delete</button></a>"

        html += f"""
        <tr>
            <td>{d}</td>
            <td>{v['expiry']}</td>
            <td class="{status_class}">{status}</td>
            <td>{btn}</td>
        </tr>
        """

    html += """
    </table>
    </body>
    </html>
    """

    return html

# ===== RUN =====
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)
