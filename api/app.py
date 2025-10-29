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
import sqlite3
import threading # I know a certain someone who LOVES this word. <3
from PIL import Image
from difflib import SequenceMatcher

def similarity(a, b):
    return SequenceMatcher(None, a, b).ratio()

# connect once at startup
conn = sqlite3.connect("chat.db", check_same_thread=False)
c = conn.cursor()
c.execute("""
CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    text TEXT,
    time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")
conn.commit()


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

def check_banned():
    with open('banlist.json','r') as f:
        ip = request.headers.get('CF-Connecting-IP', request.remote_addr)
        bans = json.load(f)
        for key, value in bans.items():
            if ip == key:
                return jsonify({'status': 'failure', 'reason': f'Banned. Reason: {value}'}), 403


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

def get_audio_duration(filename):
    import subprocess
    result = subprocess.run(
        [
            "ffprobe",
            "-v", "error",
            "-show_entries", "format=duration",
            "-of", "csv=p=0",
            filename
        ],
        stdout=subprocess.PIPE,
        text=True
    )
    return float(result.stdout.strip())

lock = threading.Lock()

@app.route('/api/place/update', methods=['POST'])
def update_pixels():
    data = request.get_json()
    pixels = data.get("pixels", [])

    with lock:
        img = Image.open("canvas.png")
        px = img.load()
        for p in pixels:
            x, y = p["x"], p["y"]
            r, g, b = p["color"]
            px[x, y] = (r, g, b)
        img.save("canvas.png")

    return jsonify({'status': 'success'}), 200

@app.route('/api/place/getcanvas')
def get_canvas():
    return send_file('canvas.png', mimetype='image/png')


@app.route('/api/files',methods=['GET'])
def filespage():
    files = os.listdir("uploads/")
    filelist = ""
    for i in files:
        filelist += f'<li><a href="uploads/{i}">{i}/</a></li>'
    style="""                        body
            {
                background-color: #2f2f2f;
                color: #CCC;
                font-family: monospace;
            }

            li
            {
                color: #FFFFFF75;
            }

            .folder a {
                color: #4caf50; /* green for folders */
            }

            .file a {
                color: #2196f3; /* blue for files */
            }

            a
            {
                color: #FFF;
                text-decoration: none;
            }

            a:hover
            {
                font-weight: bold;
                text-decoration: underline;
            }

            .filelist
            {
                font-size: 15px;
                width:fit-content;
                padding-right: 30px;
                background-color: #00000075;
                border: solid;
                border-radius: 10px;
                border-width: 1.5px;
            }"""
    return f"""<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd">
            <html><head>
            <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
            <title>Directory listing for uploads/</title>
            <style>
            {style}
            </style>
            </head>
            <body>
            <h1>Directory listing for uploads/</h1>
            <hr>
            <ul>
            {filelist}
            </ul>
            <hr>
            </body></html>"""

@app.route('/api/video',methods=['GET'])
def videolink():
    import subprocess
    text = request.args.get("text","Arguments are bgcol, text, fgcol")
    bgcol = request.args.get("bgcol","black")
    fgcol = request.args.get("fgcol","white")
    tts = request.args.get("tts","false")
    
        
    text = text.replace("'","").replace('"',"").replace(";","\\;").replace(':','\\:')
    video_width = 1280//2
    base_fontsize = 50
    # rough approximation: assume each char ~ base_fontsize/2 pixels wide
    char_width_factor = 0.6  # average char is ~60% of fontsize wide
    estimated_text_width = len(text) * base_fontsize * char_width_factor
    fontsize = min(base_fontsize, int(video_width / estimated_text_width * base_fontsize))
    outpath = f"videos/{text}-{bgcol}-{fgcol}-{tts}.mp4"
    dur = 0.1
    if os.path.exists(outpath):
        return send_file(outpath, mimetype="video/mp4")
    
    if tts=="true":
        #subprocess.run(["espeak", text, "-w", "speech.wav"])
        #dur = get_audio_duration('speech.wav')
        return 501

    merge_cmd = [
        "ffmpeg",
        "-i", outpath,
        "-i", "speech.wav",
        "-c:v", "copy",
        "-c:a", "aac",
        "-shortest",
        "-y", "videos/tmp.mp4",
    ]
    
    
    cmd = [
        "ffmpeg",
        "-nostdin",
        "-f", "lavfi",
        "-i", f"color=c={bgcol}:s=1280x720:d={dur}",
        "-vf", f"drawtext=fontfile=font.ttf:text='{text}':fontsize={fontsize}:fontcolor={fgcol}:x=(w-text_w)/2:y=(h-text_h)/2",
        "-c:v", "libopenh264",
        "-pix_fmt", "yuv420p",
        "-g","1",
        "-y",
        outpath,
        
    ]  # USE libopenh264 ON SERVER
    
    subprocess.run(cmd)
    if tts=="true":
        subprocess.run(merge_cmd)
        os.remove(outpath)
        os.rename("videos/tmp.mp4", outpath)
    
    return send_file(outpath, mimetype="video/mp4")

import requests
@app.route("/api/scratch/projects/<int:project_id>")
def get_scratch_project(project_id):
    r = requests.get(f"https://api.scratch.mit.edu/projects/{project_id}")
    data = r.json()
    response = jsonify(data)
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response

@app.route("/api/scratch/comments/<string:user_name>/<int:project_id>")
def get_scratch_comments(user_name,project_id):
    r = requests.get(f"https://api.scratch.mit.edu/users/{user_name}/projects/{project_id}/comments/")
    data = r.json()
    response = jsonify(data)
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response


@app.route('/api/msgboard', methods=['POST', 'GET'])
def msgb():
    if request.method == 'GET':
        with open('messageboard.json','r') as f:
            return json.load(f)
    elif request.method == 'POST':
        banned = check_banned()
        if banned:
            return banned  
        data = request.get_json()
        message = data.get('message', 'help im trapped in a default message')
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
    with open('server.log','a') as f:
        ip = request.headers.get('CF-Connecting-IP', request.remote_addr)
        f.write(f"{ip} said \"{message}\" on messageboard\n")
    return jsonify({'status': 'success'}), 201

# upload endpoint
@app.route("/api/uploadfile", methods=["POST"])
def upload_file():
    banned = check_banned()
    if banned:
        return banned
    file = request.files.get("file")
    if not file or file.filename == "":
        return jsonify({"error": "no file provided"}), 400
    
    filename = secure_filename(file.filename)
    file.save(os.path.join(UPLOAD_FOLDER, filename))
    with open('server.log','a') as f:
        ip = request.headers.get('CF-Connecting-IP', request.remote_addr)
        f.write(f"{ip} uploaded {filename}\n")
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
    arg = request.args.get("author")
    if arg:
        with open('../userprojects.json', 'r') as f:
            projects = json.load(f)
        
        filtered = {k: v for k, v in projects.items() if v.get("author") == arg}
        return filtered
    else:
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
    banned = check_banned()
    if banned:
        return banned
    try:
        with open("../userprojects.json", "r") as f:
            data = json.load(f)

        project_id = request.json.get('id')
        name = request.json.get('name', 'John Untitled')
        text = request.json.get('text')
        if len(text) > 1000:
            return jsonify({'status': 'failure', 'reason': 'comment is more than 1k chars'}), 400
        
        
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
        with open('server.log','a') as f:
            ip = request.headers.get('CF-Connecting-IP', request.remote_addr)
            f.write(f"{ip} made a comment on {project_id}: {name}: {text}\n")
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

def project_similarity(p1, p2):
    score = 0
    fields = ["title", "description", "summary","author"]
    for f in fields:
        score += SequenceMatcher(None, p1.get(f,""), p2.get(f,"")).ratio()
    score /= len(fields)
    return score  # 0..1

@app.route('/api/upload', methods=['POST'])
def upload_proj():
    banned = check_banned()
    if banned:
        return banned  
    with open('../userprojects.json', 'r') as f:
        projects = json.load(f)
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

    new_project = {
        'title': title,
        'description': description,
        'summary': summary,
        'videoId': videoId,
        'thumbnail': thumbnail,
        'images': images,
        'author': username
    }

    for existing_id, existing_project in projects.items():
        sim = project_similarity(new_project, existing_project)
        if sim > 0.8 and existing_id != projid:  # threshold for "very similar"
            #return jsonify({'status': 'error', 'message': 'Project is eerily similar to another project'}), 409
                print(f"New project is eerily similar to another project ({existing_id})!!! Flagging")
                description += f"<br><span style=\"font-size: x-small; color: #cccccc75\">Possible clone of project {existing_id}."
                title += f"<span title=\"May be a clone of {existing_id}\" style=\"font-size: x-large; color: #fff\">⚠️"
                with open('server.log','a') as f:
                    ip = request.headers.get('CF-Connecting-IP', request.remote_addr)
                    f.write(f"{ip} made {projid}, a likely clone of {existing_id} \n")
    
    try:
        
        if not projid:
            return jsonify({'status': 'error', 'message': 'Dumbass forgot the project id????'}), 422
        if not password:
            return jsonify({'status': 'error', 'message': 'Password missing????'}), 422

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
    
    with open('server.log','a') as f:
        ip = request.headers.get('CF-Connecting-IP', request.remote_addr)
        f.write(f"{ip} made a project with id {projid}\n")
    return jsonify({'status': 'success'}), 201

@app.route('/api/user', methods=['POST'])
def create_user():
    banned = check_banned()
    if banned:
        return banned  
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
gamers = []
boxes = {} # "id" : [ [ (10,10) , (50,50) ] ]




# store timestamps for each user by sid
last_name_change = {}
NAME_CHANGE_COOLDOWN = 2  # seconds

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
    with open('server.log','a') as f:
        f.write(f"{ip} joined chat\n")
    ips[request.sid] = ip
    print(request.sid,"|",ip)
    c.execute("SELECT username, text FROM messages ORDER BY id DESC LIMIT 100")
    for name, text in reversed(c.fetchall()):
        send(f"<#7F7F7F>{name}: {text}</>", to=request.sid)
    return
    

@socketio.on("disconnect")
def handle_disconnect():
    print(f"[{request.sid}]  |  disconnected")
    if request.sid in gamers:
        gamers.remove(request.sid)
        return
    send(users[request.sid]+" left the chat!", broadcast=True)
    del users[request.sid]
    


@socketio.on("message")
def handle_message(msg):
    #print("Received message:", msg)
    with open('banlist.json','r') as f:
        ip = request.headers.get('CF-Connecting-IP', request.remote_addr)
        bans = json.load(f)
        for key, value in bans.items():
            if ip == key:
                send(f"<#ff5252>You're banned. Reason: {value}</>", to=request.sid)
                return
    if msg == "-GAME-=.join" and request.sid not in gamers:
        gamers.append(request.sid)
        return
    
    
    # Gaming area
    
    
    if request.sid in gamers:
        data = msg
        data["id"] = request.sid
        send(data, broadcast=True)
    
        return 
    
    if isinstance(msg, dict):
        return
   
    if ";users;" in msg:
        send("<span style=\"color: #7f7f7f\">Userlist:\n"+("\n".join(f"{v.replace('<','')}</span>" for k, v in users.items())), to=request.sid)
        return  
    
    if msg.startswith("-NAME-= "):
        now = time.time()
        last_change = last_name_change.get(request.sid, 0)

        if now - last_change < NAME_CHANGE_COOLDOWN:
            send(f"<#AAAAAA>[SYSTEM] You must wait {str(NAME_CHANGE_COOLDOWN - (now - last_name_change))} seconds before changing your name again.</>", to=request.sid)
            return  
        
        name = msg.split("-NAME-= ")[1]
        if name in users.values():
            name = unique_name(name, users)
        users[request.sid] = name
        last_name_change[request.sid] = now
        send(name+" joined the chat!", broadcast=True)
        with open('server.log','a') as f:
            f.write(f"{ip} changed their name to {name}\n")
        print(f"[{request.sid}]  | ",name+" joined the chat!")
    else:
        if request.sid in users:
            send(users[request.sid] + ": " + msg, broadcast=True)
            c.execute("INSERT INTO messages (username, text) VALUES (?, ?)",
                    (users[request.sid], msg))
            conn.commit()

    
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
print("Yes, I'm running!")
socketio.run(app, debug=DBUG,host="0.0.0.0",port=8001)
