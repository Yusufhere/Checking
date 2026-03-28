from flask import Flask, request, jsonify, render_template_string
import time, uuid

app = Flask(__name__)

licenses = {}

HTML = """
<h2>🔥 License Panel</h2>

<h3>Create License</h3>
<form method='post' action='/create'>
Days: <input name='days' value='365'>
<input type='submit'>
</form>

<h3>All Licenses</h3>
<table border=1>
<tr><th>Key</th><th>Expiry</th><th>Device</th><th>Action</th></tr>
{% for k,v in licenses.items() %}
<tr>
<td>{{k}}</td>
<td>{{v['expiry']}}</td>
<td>{{v['device']}}</td>
<td><a href='/delete/{{k}}'>Delete</a></td>
</tr>
{% endfor %}
</table>
"""

@app.route("/")
def panel():
    return render_template_string(HTML, licenses=licenses)

@app.route("/create", methods=["POST"])
def create():
    days = int(request.form.get("days", 365))
    key = "KEY-" + str(uuid.uuid4())[:8]

    licenses[key] = {
        "expiry": time.time() + days*86400,
        "device": ""
    }

    return f"Created: {key}<br><a href='/'>Back</a>"

@app.route("/delete/<key>")
def delete(key):
    if key in licenses:
        del licenses[key]
    return "Deleted <br><a href='/'>Back</a>"

@app.route("/verify", methods=["POST"])
def verify():
    data = request.json
    key = data.get("key")
    device = data.get("device_id")

    if key not in licenses:
        return jsonify({"status": "invalid"})

    lic = licenses[key]

    if time.time() > lic["expiry"]:
        return jsonify({"status": "expired"})

    if lic["device"] == "":
        lic["device"] = device
    elif lic["device"] != device:
        return jsonify({"status": "unauthorized_device"})

    return jsonify({"status": "valid"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
