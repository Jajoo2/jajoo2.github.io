from flask import Flask, request, jsonify, send_file, abort, render_template, send_from_directory
import json
import os
from flask_cors import CORS
import random
import re
import sys
import bcrypt
from werkzeug.utils import secure_filename
import os
from datetime import datetime, timezone
from flask_socketio import SocketIO, send, emit
import time


# To hash a plaintext password before storing
def hash_password(plain_text_password):
    # bcrypt requires bytes, so encode the string first
    salt = bcrypt.gensalt()  # automatically generates a strong salt
    hashed = bcrypt.hashpw(plain_text_password.encode('utf-8'), salt)
    return hashed.decode('utf-8')  # store as string in your JSON/db

# To check password on login or edit
def check_password(plain_text_password, hashed_password):
    # hashed_password must be bytes, so encode it again
    return bcrypt.checkpw(plain_text_password.encode('utf-8'), hashed_password.encode('utf-8'))


MAX_SIZE = 5 * 1024 * 1024  # 5 MB in bytes

def exceeds_5mb(value):
    if value is None:
        return False
    if isinstance(value, list):
        return sys.getsizeof(str(value).encode('utf-8')) > MAX_SIZE
    return sys.getsizeof(value.encode('utf-8')) > MAX_SIZE



app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@app.route('/api/msgboard', methods=['POST', 'GET'])
def msgb():
    if request.method == 'GET':
        with open('messageboard.json','r') as f:
            return json.load(f)
    elif request.method == 'POST':
        data = request.get_json()
        message = data.get('message', 'I was here!')
        x = data.get('x')
        y = data.get('y')
        color = data.get('color')
        
        with open('messageboard.json', 'r') as f:
            messageboardjson = json.load(f)
        
        try:

            if (message != "") and (x != "" and (y != "")):
                now = datetime.now(timezone.utc)
                timestamp = now.isoformat()
                
                messageboardjson["messages"].insert(0, {"message": message, "x": x, "y": y, "color": color, "timestamp": timestamp})
            else:
                return jsonify({'status': 'failure', 'reason': 'no message or position'}), 400
                
            with open('messageboard.json', 'w') as f:
                json.dump(messageboardjson, f, indent=4)
        except Exception as ex:
            print(ex)
            return jsonify({'status': 'failure', 'reason': f'500 internal server error?! exception: {ex}'}), 500
        
    return jsonify({'status': 'success'}), 201

# upload endpoint
@app.route("/api/uploadfile", methods=["POST"])
def upload_file():
    file = request.files.get("file")
    if not file or file.filename == "":
        return jsonify({"error": "no file provided"}), 400
    
    filename = secure_filename(file.filename)
    file.save(os.path.join(UPLOAD_FOLDER, filename))
    
    return jsonify({
        "message": "file uploaded",
        "url": f"https://api.meisite.xyz/api/files/{filename}"
    })

# download endpoint
@app.route("/api/files/<path:filename>", methods=["GET"])
def serve_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)


@app.route('/api/motd', methods=['GET'])
def get_motd():
    f = open("motd.txt","r")
    return jsonify(f.read().replace("\n",""))

@app.route('/api/embed', methods=['GET'])
def get_embed():
    return f"""<!DOCTYPE html>
<html>

<head>
	<title>Example</title>
    <meta name="description" content="This is an example page with proper Open Graph meta tags for Discord embeds.">

    <!-- Open Graph (used by Discord, Facebook, etc.) -->
    <meta property="og:title" content="Example Site Title">
    <meta property="og:description" content="A brief description that shows in the embed.">
    <meta property="og:type" content="website">
    <meta property="og:url" content="https://example.com/page">
    <meta property="og:site_name" content="ExampleSite">
    <meta property="og:image" content="https://i.imgur.com/AfFp7pu.png">
    <meta property="og:image:alt" content="Illustrative example image">
    <meta property="og:image:width" content="800">
    <meta property="og:image:height" content="450">
</head>

<body>
    <h1>why</h1>
</body>

</html>"""



@app.route('/api/uploads', methods=['GET'])
def get_projects():
    with open('../userprojects.json', 'r') as f:
        return json.load(f)

@app.route('/api/posts', methods=['GET'])
def get_posts():
    with open('posts.json', 'r') as f:
        return json.load(f)

@app.route('/api/commentblog', methods=['POST'])
def post_comment_blog():
    try:
        with open("posts.json", "r") as f:
            data = json.load(f)

        project_id = request.json.get('id')
        name = request.json.get('name', 'John Untitled')
        text = request.json.get('text')
        
        
        if not text:
            return jsonify({'status': 'failure', 'reason': 'no text in comment'}), 400

        if project_id not in data:
            return jsonify({'status': 'failure', 'reason': 'project not found'}), 404

        new_comment = {"user": name, "text": text}

        data[project_id]["comments"].insert(0, new_comment)

        with open("posts.json", "w") as f:
            json.dump(data, f, indent=4)
            
    except Exception as ex:
        print("ERROR!!  |  ", ex)
        return jsonify({'status': 'failure', 'reason': f'backend error, oh no!: {ex}'}), 500
    return jsonify({'status': 'success'}), 201

@app.route('/api/uploadpost', methods=['POST'])
def upload_post():
    data = request.get_json()
    title = data.get('title', 'Untitled')
    content = data.get('content','No content')
    summary = data.get('summary','')
    postid = data.get('id')
    username = data.get('username') 
    date = data.get('date') 
    password = data.get('password') 
    
    if any([
        exceeds_5mb(title),
        exceeds_5mb(content),
        exceeds_5mb(postid),
        exceeds_5mb(summary),
        exceeds_5mb(username),
        exceeds_5mb(password), 
    ]):
        return jsonify({'status': 'error', 'message': 'One or more fields exceed 5MB limit. I\'m watching you...'}), 413

    
    try:
        with open('posts.json', 'r') as f:
            posts = json.load(f)
        if not postid:
            return jsonify({'status': 'error', 'message': 'Dumbass forgot the post id????'}), 400
        if not password:
            return jsonify({'status': 'error', 'message': 'Password missing????'}), 400

        if postid in posts:
            stored_hash = posts[postid].get("passhash")
            if not check_password(password, stored_hash):
                return jsonify({'status': 'error', 'message': 'Incorrect password for existing post'}), 401
            if title == "":
                del posts[postid]

        if title != "":
            posts[postid] = {
                "title": title,
                "content": content,
                "summary": summary,
                "author": username,
                "passhash": hash_password(password),
                "date": date,
                "comments": []
            }
        with open('posts.json', 'w') as f:
            json.dump(posts, f, indent=4)
    except Exception as ex:
        print(ex)
        return jsonify({'status': 'failure', 'reason': f'server error?! exception: {ex}'}), 500
    
    
    return jsonify({'status': 'success'}), 201

@app.route('/api/post', methods=['GET']) 
def get_post():
    key = request.args.get('id')  # gets ?id=value from URL teehee
    if not key:
        return jsonify({"error": "No ID provided"}), 400

    with open('posts.json', 'r') as f:
        data = json.load(f)
        
    if key in data:
        return jsonify(data[key])
    else:
        return jsonify({"error": "Post not found   :("}), 404

@app.route('/api/up', methods=['GET'])
def pingme():
    return jsonify(True)

@app.route('/api/project', methods=['GET']) 
def get_project():
    key = request.args.get('id')  # gets ?id=value from URL teehee
    if not key:
        return jsonify({"error": "No ID provided"}), 400

    with open('../userprojects.json', 'r') as f:
        data = json.load(f)
        
    if key in data:
        return jsonify(data[key])
    else:
        return jsonify({"error": "Project not found   :("}), 404
    
@app.route('/api/comment', methods=['POST'])
def post_comment():
    try:
        with open("../userprojects.json", "r") as f:
            data = json.load(f)

        project_id = request.json.get('id')
        name = request.json.get('name', 'John Untitled')
        text = request.json.get('text')
        
        
        if not text:
            return jsonify({'status': 'failure', 'reason': 'no text in comment'}), 400

        if project_id not in data:
            return jsonify({'status': 'failure', 'reason': 'project not found'}), 404

        new_comment = {"user": name, "text": text}

        data[project_id]["comments"].insert(0, new_comment)

        with open("../userprojects.json", "w") as f:
            json.dump(data, f, indent=4)
            
    except Exception as ex:
        print("ERROR!!  |  ", ex)
        return jsonify({'status': 'failure', 'reason': f'backend error, oh no!: {ex}'}), 500
    return jsonify({'status': 'success'}), 201

    
@app.route('/api/notif', methods=['POST'])
def post_notif():
    try:
        text = request.json.get('text')
        os.system(f"notify-send -u low -a api 'API message:' '{text}'")
            
    except Exception as ex:
        print("ERROR!!  |  ", ex)
        return jsonify({'status': 'failure', 'reason': f'backend error, oh no!: {ex}'}), 500
    return jsonify({'status': 'success'}), 201

@app.route('/api/upload', methods=['POST'])
def upload_proj():
    data = request.get_json()
    title = data.get('title', 'Untitled')
    description = data.get('description','No description')
    summary = data.get('summary','')
    videoId = data.get('videoId')
    thumbnail = data.get('thumbnail')
    images = data.get('images')
    projid = data.get('id')
    username = data.get('username') 
    password = data.get('password') 
    
    if any([
        exceeds_5mb(title),
        exceeds_5mb(description),
        exceeds_5mb(thumbnail),
        exceeds_5mb(projid),
        exceeds_5mb(summary),
        exceeds_5mb(videoId),
        exceeds_5mb(username),
        exceeds_5mb(password), 
    ]):
        return jsonify({'status': 'error', 'message': 'One or more fields exceed 5MB limit. I\'m watching you...'}), 413

    
    try:
        with open('../userprojects.json', 'r') as f:
            projects = json.load(f)
        if not projid:
            return jsonify({'status': 'error', 'message': 'Dumbass forgot the project id????'}), 400
        if not password:
            return jsonify({'status': 'error', 'message': 'Password missing????'}), 400

        if projid in projects:
            stored_hash = projects[projid].get("passhash")
            if not check_password(password, stored_hash):
                return jsonify({'status': 'error', 'message': 'Incorrect password for existing project'}), 401
            if title == "":
                del projects[projid]

        if title != "":
            projects[projid] = {
                "title": title,
                "description": description,
                "summary": summary,
                "videoId": videoId,
                "thumbnail": thumbnail,
                "images": images,
                "author": username,
                "passhash": hash_password(password),
                "comments": []
            }
        # DEELETION NOT GUARANTEED TO WORK IM AT 5%, GOOD LUCK !!! HOPE YOU DON'T SCRAP THIS IM REALLY LIKING IT ACTUALLY THIS WAS KINDA FUN
        # it worked
        with open('../userprojects.json', 'w') as f:
            json.dump(projects, f, indent=4)
    except Exception as ex:
        print(ex)
        return jsonify({'status': 'failure', 'reason': f'server error?! exception: {ex}'}), 500
    
    
    return jsonify({'status': 'success'}), 201

@app.route('/api/user', methods=['POST'])
def create_user():
    data = request.get_json()
    username = data.get('username', 'Untitled')
    password = data.get('password')
    
    with open('users.json', 'r') as f:
        users = json.load(f)

    if username not in users:
        users[username] = {'username': username, 'password': password}
    else:
        return jsonify({'status': 'failure', 'reason': 'User already exists'}), 422
    
    with open('users.json', 'w') as f:
        json.dump(users, f, indent=2)

    return jsonify({'status': 'success'}), 201
    
@app.route('/api/checkpassword', methods=['POST'])
def check_pass():
    data = request.get_json()
    code = data.get('password')
    requsername = data.get('username')
    
    with open('users.json', 'r') as f:
        users = json.load(f)
    
    if requsername not in users:
        return jsonify({'status': 'failure', 'reason': 'User not found'}), 404
    
    user = users[requsername]
    print(requsername, code, " | ", user['username'], user['password'])
    if code == user['password']:
        return jsonify(True)
    else:
        return jsonify(False)
    
app.config["SECRET_KEY"] = "secret!"  # just for sessions
socketio = SocketIO(app, cors_allowed_origins="*")  # allow all origins

users = {}
ips = {}


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
    ip = request.headers.get('CF-Connecting-IP', request.remote_addr)
    ips[request.sid] = ip
    print(request.sid,"|",ip)
    

@socketio.on("disconnect")
def handle_disconnect():
    print(f"[{request.sid}]  | ",users[request.sid]+" left the chat!")
    send(users[request.sid]+" left the chat!", broadcast=True)
    users[request.sid] = ""


@socketio.on("message")
def handle_message(msg):
    print("Received message:", msg)
    if ";users;" in msg:
        send("Userlist:\n"+("\n".join(f"{k}: {v}" for k, v in users.items())), to=request.sid)
        return  
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

    
DBUG = "-D" in sys.argv[1:]

import sqlite3

# --- Database Setup ---
def init_db():
    conn = sqlite3.connect('extensions.db')
    cursor = conn.cursor()
    # Create table if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS extensions (
            id TEXT PRIMARY KEY,
            content TEXT
        )
    ''')
    conn.commit()
    conn.close()

# Initialize the database when the app starts
init_db()

# --- API Endpoints for Extensions ---
@app.route('/api/extensions', methods=['GET', 'POST'])
def handle_extensions():
    conn = sqlite3.connect('extensions.db')
    conn.row_factory = sqlite3.Row # Makes rows behave like dicts
    cursor = conn.cursor()

    if request.method == 'GET':
        cursor.execute('SELECT id, content FROM extensions')
        rows = cursor.fetchall()
        extensions = {row['id']: row['content'] for row in rows}
        conn.close()
        return jsonify(extensions)

    if request.method == 'POST':
        data = request.get_json()
        ext_id = data.get('id')
        content = data.get('content')

        if not ext_id or not content:
            conn.close()
            return jsonify({'status': 'error', 'message': 'Missing id or content'}), 400

        # INSERT OR REPLACE is atomic: it updates if the id exists, or inserts if it's new.
        cursor.execute('INSERT OR REPLACE INTO extensions (id, content) VALUES (?, ?)', (ext_id, content))
        conn.commit()
        conn.close()

        # Broadcast the update to all connected clients
        socketio.emit('extension_updated', {'id': ext_id, 'content': content})
        return jsonify({'status': 'success', 'message': f'Extension {ext_id} saved.'}), 201

@app.route('/api/extensions/<string:ext_id>', methods=['DELETE'])
def delete_extension(ext_id):
    conn = sqlite3.connect('extensions.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM extensions WHERE id = ?', (ext_id,))
    conn.commit()
    conn.close()
    
    # Broadcast the removal to all connected clients
    socketio.emit('extension_removed', {'id': ext_id})
    return jsonify({'status': 'success', 'message': f'Extension {ext_id} deleted.'}), 200

# --- Socket.IO Relay for Extensions ---
@socketio.on("extension_message")
def handle_extension_message(data):
    emit('extension_broadcast', data, broadcast=True)

socketio.run(app, debug=DBUG,host="0.0.0.0",port=8001)
