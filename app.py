from flask import Flask, render_template, request, redirect, url_for, session
import subprocess

app = Flask(__name__)
app.secret_key = 'vpn123'

LOGIN = 'lemonroot'
PASSWORD = 'lemonroot'

@app.route("/")
def index():
    if not session.get("logged_in"):
        return redirect(url_for("login"))
    vpn_status = "Подключено: SOCKS5"
    current_ip = subprocess.getoutput("curl -s https://api.ipify.org")
    logs = get_logs()
    return render_template("index.html", vpn_status=vpn_status, current_ip=current_ip, logs=logs)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if request.form["username"] == LOGIN and request.form["password"] == PASSWORD:
            session["logged_in"] = True
            return redirect(url_for("index"))
    return render_template("login.html")

@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/section/PPTP", methods=["GET", "POST"])
def pptp():
    if not session.get("logged_in"):
        return redirect(url_for("login"))
    status = subprocess.getoutput("nmcli con show --active | grep pptp") or "Не подключено"
    ip = ""
    user = ""
    password = ""
    log = ""
    if request.method == "POST":
        ip = request.form["pptp_ip"]
        user = request.form["pptp_user"]
        password = request.form["pptp_pass"]
        if request.form["action"] == "connect":
            cmd = f"nmcli con add type vpn con-name pptp-vpn ifname -- vpn-type pptp " \
                  f"&& nmcli con modify pptp-vpn vpn.data 'gateway={ip},user={user}' " \
                  f"&& nmcli con modify pptp-vpn vpn.secrets 'password={password}' " \
                  f"&& nmcli con up pptp-vpn"
            log = subprocess.getoutput(cmd)
        elif request.form["action"] == "disconnect":
            log = subprocess.getoutput("nmcli con down pptp-vpn")
    return render_template("section.html", section='PPTP', ip=ip, user=user, password=password, status=status, log=log)

@app.route("/section/<name>")
def section(name):
    if not session.get("logged_in"):
        return redirect(url_for("login"))
    return render_template("section.html", section=name)

def get_logs():
    try:
        with open("log.txt", "r") as f:
            return f.read().splitlines()[-15:]
    except:
        return []

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
