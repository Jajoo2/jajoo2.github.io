from flask import Flask, render_template, request
from flask_socketio import SocketIO, send
import time

app = Flask(__name__)
app.config["SECRET_KEY"] = "secret!"  # just for sessions
socketio = SocketIO(app)
users = {}

# store timestamps for each user by sid
last_name_change = {}
NAME_CHANGE_COOLDOWN = 10  # seconds

def unique_name(desired, users):
    original = desired
    count = 1
    while desired in users.values():
        desired = f"{original}({count})"
        count += 1
    return desired


@socketio.on("connect")
def handle_connect():
    print("someone connected")
    # get ip thru cf tunnel
    # ip = request.headers.get('CF-Connecting-IP', request.remote_addr)
    

@socketio.on("disconnect")
def handle_disconnect():
    print(f"[{request.sid}]  | ",users[request.sid]+" left the chat!")
    send(users[request.sid]+" left the chat!", broadcast=True)
    users[request.sid] = ""


@socketio.on("message")
def handle_message(msg):
    print("Received message:", msg)
    if msg.startswith("-NAME-= "):
        now = time.time()
        last_change = last_name_change.get(request.sid, 0)

        if now - last_change < NAME_CHANGE_COOLDOWN:
            send("<#AAAAAA>[SYSTEM] You must wait before changing your name again.</>", to=request.sid)
            return  
        
        name = msg.split("-NAME-= ")[1]
        if name in users.values():
            name = unique_name(name, users)
        users[request.sid] = name
        last_name_change[request.sid] = now
        send(name+" joined the chat!", broadcast=True)
        print(f"[{request.sid}]  | ",name+" joined the chat!")
    else:
        if request.sid in users:
            send(users[request.sid] + ": " + msg, broadcast=True)


@app.route("/")
def index():
    return render_template("index.html")


if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000)
