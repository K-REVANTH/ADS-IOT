from flask import (
    Flask,
    request,
    render_template,
    redirect,
    make_response,
)
import sqlite3
import hashlib
import jwt
from datetime import datetime, timedelta
from functools import wraps
from flask_socketio import SocketIO
from flask_cors import CORS

app = Flask(__name__)
app.secret_key = "107 1S 7H3 k3y 70 s3cur17y"
socketio = SocketIO(app, cors_allowed_origins=["http://192.168.159.17" , "http://127.0.0.1"])
CORS(app)

@socketio.on('connect')
def handle_connect():
    print(f'Client connected: {request.sid}')

@socketio.on('disconnect')
def handle_disconnect():
    print(f'Client disconnected: {request.sid}')

@socketio.on('notify')
def handle_notify(message):
    print(f'Received notification: {message}')
    socketio.emit('notification', message)

@app.route("/your_endpoint", methods=["GET", "POST"])
def receive_data():
    data = request.form.get("message_sent", "No data received")
    motion = data.split(",")[0]
    device_mac = data.split(",")[1]
    bluetooth_devices = data.split(",")[2:]
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    if motion == "No Motion":
        print("No Motion detected")
        cursor.execute("UPDATE users SET status = 'Not Available' WHERE device = ?", (device_mac,))
    else:
        if device_mac in bluetooth_devices:
            print("device in ble devices")
            cursor.execute("UPDATE users SET status = 'Available' WHERE device = ?", (device_mac,))
        else:
            print("device not in ble devices")
            cursor.execute("UPDATE users SET status = 'Not Available' WHERE device = ?", (device_mac,))
            # handle_notify(f"{device_mac} is not in range")
    conn.commit()
    conn.close()
    print(f"Received data: {data}")
    return "Data Received"

@app.route("/status", methods=["GET", "POST"])
def status():
    if request.method == "POST":
        status = request.form.get("status")
        token = request.cookies.get("token")
        data = jwt.decode(token, app.secret_key, algorithms=["HS256"])
        email = data["email"]
        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET status = ? WHERE email = ?", (status, email))
        conn.commit()
        conn.close()
        return "Status Updated"
    
@app.route("/timings", methods=["GET", "POST"])
def timings():
    if request.method == "POST":
        timings = request.form.get("timings")
        token = request.cookies.get("token")
        data = jwt.decode(token, app.secret_key, algorithms=["HS256"])
        email = data["email"]
        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET timings = ? WHERE email = ?", (timings, email))
        conn.commit()
        conn.close()
        return "Timings Updated"

@app.route("/", methods=["POST", "GET"])
def index():
    return render_template("index.html")

@app.route("/search", methods=["POST", "GET"])
def search():
    # handle_notify("Welcome to A.D.S")
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    if request.method == "POST":
        search_word = request.form["query"]
        print(search_word)
        if search_word == "":
            query = "SELECT username, email, phone, cabin, status, timings from users ORDER BY username ASC"
            cursor.execute(query)
            faculty = cursor.fetchall()
        else:
            cursor.execute(
                "SELECT username, email, phone, cabin, status, timings FROM users WHERE username LIKE ? COLLATE NOCASE",
                ("%" + search_word + "%",),
            )
            faculty = cursor.fetchall()
            print(faculty)
    conn.close()
    return render_template("response.html", faculty=faculty)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()
        cursor.execute("SELECT password FROM users WHERE email = ?", (email,))
        result = cursor.fetchone()
        if result:
            hashed_password = hashlib.sha256(password.encode()).hexdigest()
            if result[0] == hashed_password:
                token = jwt.encode(
                    {"email": email, "exp": datetime.utcnow() + timedelta(minutes=600)},
                    app.secret_key,
                    algorithm="HS256"
                )
                response = make_response(redirect("/dashboard"))
                response.set_cookie("token", token)
                return response
            else:
                return """
                <script>
                    alert("Incorrect Password.");
                    window.location.href = '/login';
                </script>"""
        else:
            return """
                <script>
                    alert("Incorrect Email Id");
                    window.location.href = '/login';
                </script>"""
        conn.close()
    return render_template("login.html")

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.cookies.get("token")
        # return 401 if token is not passed
        if not token:
            return """
                <script>
                    alert("Please Login to view dashboard.");
                    window.location.href = '/login';
                </script>""", 401
        try:
            # decoding the payload to fetch the stored details
            data = jwt.decode(token, app.secret_key, algorithms=["HS256"])
            conn = sqlite3.connect("users.db")
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM users WHERE email = ?", (data["email"],)
            )
            current_user = cursor.fetchone()
            conn.close()
        except:
            return """
                <script>
                    alert("Invalid auth.");
                    window.location.href = '/login';
                </script>""", 401
        # returns the current logged in users context to the routes
        return f(current_user, *args, **kwargs)
    return decorated

@app.route("/dashboard", methods=["GET", "POST"])
@token_required
def dashboard(current_user):
    print(current_user)
    return render_template("dashboard.html", username=current_user[1], status=current_user[6], availability_msg=current_user[7])

@app.route("/logout", methods=["GET", "POST"])
def logout():
    response = make_response(redirect("/"))
    response.delete_cookie("token")
    return response

if __name__ == "__main__":
    # app.run(host="0.0.0.0", port=80, ssl_context=("E:\BTech\IOT\ssl_cert\server.crt","E:\BTech\IOT\ssl_cert\server.key"))
    socketio.run(app, host="0.0.0.0", port=80)