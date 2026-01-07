from flask import Flask, jsonify, abort, request, send_file
from flask_cors import CORS
import json
import random
import hashlib
import secrets
from pathlib import Path
from datetime import datetime, timezone
import uuid


def hash_password(password):
    salt = secrets.token_hex(16)
    h = hashlib.sha256((salt + password).encode()).hexdigest()
    return salt, h


def verify(password, salt, stored_hash):
    h = hashlib.sha256((salt + password).encode()).hexdigest()
    return h == stored_hash


app = Flask(__name__)
CORS(app)
BANNED_IPS = []
with open("bans.txt",'r') as f:
    for i in f.readlines():
        BANNED_IPS.append(i.strip())

@app.before_request
def block_banned_ips():
    global BANNED_IPS
    with open("bans.txt",'r') as f:
        for i in f.readlines():
            BANNED_IPS = []
            BANNED_IPS.append(i.strip())
    real_ip = request.headers.get("X-Forwarded-For", request.remote_addr).split(",")[0].strip()
    ip_ip = request.remote_addr
    if real_ip in BANNED_IPS or ip_ip in BANNED_IPS:
        return jsonify({"message": "Get banned dumbass"}), 403

@app.route("/")
def home():
    return "<!DOCTYPE html> <html lang=\"en\"> <body> <h1>Not Found</h1> <p>The requested URL was not found on the server. If you entered the URL manually please check your spelling and try again. Fuck you.</p>"


@app.route("/ping")
def ping():
    return jsonify({"message": f"api online! heres a random 4 digit number. {random.randint(1000,9999)}"}), 200
    


@app.route("/projectupload", methods=["POST"])
def projectupload():
    data = request.json
    user = data.get("user")
    thumb = data.get("thumb")
    images = data.get("images")
    description = data.get("description")
    title = data.get("title")


@app.route("/signup", methods=["POST"])
def signup():
    data = request.json
    user = data.get("user")
    password = data.get("password")
    pfp = data.get("pfp", "/img/mei.png")

    if user is None or password is None:
        return jsonify({"status": "failure", "reason": "Missing user or password"}), 400
    with open("users.json") as f:
        db = json.load(f)
    if user not in db["users"]:
        salt, h = hash_password(password)
        db["users"][user] = {
            "salt": salt,
            "hash": h,
            "bio": "You have chosen, or been chosen, to relocate to one of our finest remaining urban centers.",
            "pfp": pfp,
            "files": [],
            "showfiles": False,
            "admin": False,
            "posts": []
        }
        with open("users.json", "w") as f:
            json.dump(db, f, indent=2)
        return jsonify({"status": "success"}), 201
    else:
        return jsonify({"status": "failure", "reason": "Name taken"}), 401


@app.route("/login", methods=["POST"])
def login():
    data = request.json
    user = data.get("user")
    password = data.get("password")

    if user is None or password is None:
        return jsonify({"status": "failure", "reason": "Missing user or password"}), 400
    with open("users.json") as f:
        db = json.load(f)
    if user not in db["users"]:
        return jsonify({"status": "failure", "reason": "no user with this name"}), 404
    salt = db["users"][user]["salt"]
    password_hash = db["users"][user]["hash"]
    ver = verify(password, salt, password_hash)
    if ver:
        return jsonify(salt, password_hash)
    else:
        return jsonify({"status": "failure", "reason": "incorrect login details?"}), 401


@app.route("/userinfo", methods=["GET"])
def userinfo():
    user = request.args.get("user")
    with open("users.json") as f:
        db = json.load(f)
    if user not in db["users"]:
        return jsonify({"status": "failure", "reason": "no user with this name"}), 404
    filess = ["files/hidden.html"]
    if db["users"][user]["showfiles"] == True:
        filess = db["users"][user]["files"]
    posts = db["users"][user]["posts"]
    return jsonify(
        {"user": user, "pfp": db["users"][user]["pfp"], "admin": db["users"][user]["admin"], "bio": db["users"][user]["bio"], "files": filess, "posts": posts}
    )


@app.route("/users", methods=["GET"])
def users():
    with open("users.json") as f:
        db = json.load(f)
    users_info = {user: db["users"][user]["pfp"] for user in db["users"]}
    return jsonify(users_info)


@app.route("/changebio", methods=["POST"])
def changebio():
    data = request.json
    user = data.get("user")
    password = data.get("password")
    bio = data.get("bio")
    if user is None or password is None or bio is None:
        return jsonify({"status": "failure", "reason": "Missing user, password or bio"}), 400
    with open("users.json") as f:
        db = json.load(f)
    if user not in db["users"]:
        return jsonify({"status": "failure", "reason": "no user with this name"}), 404
    salt = db["users"][user]["salt"]
    password_hash = db["users"][user]["hash"]
    ver = verify(password, salt, password_hash)
    if ver:
        db["users"][user]["bio"] = bio
        with open("users.json", "w") as f:
            json.dump(db, f, indent=2)
        return jsonify({"status": "success"}), 201
    else:
        return jsonify({"status": "failure", "reason": "incorrect login details?"}), 401

@app.route("/changepfp", methods=["POST"])
def changepfp():
    data = request.json
    user = data.get("user")
    password = data.get("password")
    pfp = data.get("pfp")
    if user is None or password is None or pfp is None:
        return jsonify({"status": "failure", "reason": "Missing user, password or pfp"}), 400
    with open("users.json") as f:
        db = json.load(f)
    if user not in db["users"]:
        return jsonify({"status": "failure", "reason": "no user with this name"}), 404
    salt = db["users"][user]["salt"]
    password_hash = db["users"][user]["hash"]
    ver = verify(password, salt, password_hash)
    if ver:
        db["users"][user]["bio"] = bio
        with open("users.json", "w") as f:
            json.dump(db, f, indent=2)
        return jsonify({"status": "success"}), 201
    else:
        return jsonify({"status": "failure", "reason": "incorrect login details?"}), 401
    
@app.route("/showfiles", methods=["POST"])
def showfiles():
    data = request.json
    user = data.get("user")
    password = data.get("password")
    showfiles = data.get("showfiles")
    if user is None or password is None or showfiles is None:
        return jsonify({"status": "failure", "reason": "Missing user, password or the thing"}), 400
    with open("users.json") as f:
        db = json.load(f)
    if user not in db["users"]:
        return jsonify({"status": "failure", "reason": "no user with this name"}), 404
    salt = db["users"][user]["salt"]
    password_hash = db["users"][user]["hash"]
    ver = verify(password, salt, password_hash)
    if ver and type(showfiles) == bool:
        db["users"][user]["showfiles"] = showfiles
        with open("users.json", "w") as f:
            json.dump(db, f, indent=2)
        return jsonify({"status": "success"}), 201
    else:
        return jsonify({"status": "failure", "reason": "incorrect login details OR showfiles isn't boolean"}), 401


@app.route("/deleteprofile", methods=["POST"])
def deleteprofile():
    data = request.json
    user = data.get("user")
    password = data.get("password")
    if not user or not password:
        return jsonify({"status": "failure", "reason": "Missing user or password"}), 400

    with open("users.json") as f:
        db = json.load(f)
    if user not in db["users"]:
        return jsonify({"status": "failure", "reason": "no user with this name"}), 404
    salt = db["users"][user]["salt"]
    password_hash = db["users"][user]["hash"]
    ver = verify(password, salt, password_hash)
    if ver:
        del db["users"][user] # GOD i fucking hate del
        with open("users.json", "w") as f:
            json.dump(db, f, indent=2)
        return jsonify({"status": "success"}), 201
    else:
        return jsonify({"status": "failure", "reason": "incorrect login details?"}), 401
    
    
from werkzeug.utils import secure_filename
from flask import send_from_directory

@app.get("/files/<filename>")
def serve_file(filename):
    if filename == "undefined":
        return send_from_directory("files", "undefined.html")
    return send_from_directory("files", secure_filename(filename))


@app.route("/uploadfile", methods=["POST"])
def uploadfile():
    user = request.form.get("user")
    password = request.form.get("password")
    file = request.files.get("file")
    print("form:", request.form)
    print("files:", request.files)
    # Source - https://stackoverflow.com/a/23601025
    # Posted by Steely Wing, modified by community. See post 'Timeline' for change history
    # Retrieved 2025-12-08, License - CC BY-SA 4.0
    # |
    # V
    file_length = file.seek(0, 2)
    file.seek(0, 0)
    print(file_length)
    if(file_length > 250000000):
        return jsonify({"status": "failure", "reason": "File size > 250 MB and I hate you."}), 403
    

    if user is None or password is None or file is None:
        return jsonify({"status": "failure", "reason": "Missing user, password, or file"}), 400

    with open("users.json") as f:
        db = json.load(f)
    if user not in db["users"]:
        return jsonify({"status": "failure", "reason": "no user with this name"}), 404
    salt = db["users"][user]["salt"]
    password_hash = db["users"][user]["hash"]
    ver = verify(password, salt, password_hash)
    if ver:
        file = request.files["file"]

        h = hashlib.sha256()

        for chunk in file.stream:
            h.update(chunk)

        digest = h.hexdigest()
        filename = digest+Path(file.filename).suffix
        file.stream.seek(0) # groan
        file.save("files/"+filename)
        if "/" in filename or "\\" in filename or ";" in filename:
            return jsonify({"status": "failure", "reason": "Bad boy. No paths"}), 403
        if "files/"+filename not in db["users"][user]["files"]:
            db["users"][user]["files"].append("files/"+filename)
        with open("users.json", "w") as f:
            json.dump(db, f, indent=2)
        return jsonify({"status": "success", "filename": filename}), 201
    else:
        return jsonify({"status": "failure", "reason": "incorrect login details?"}), 401

def auth(request):
    data = request.json
    user = data.get("user")
    password = data.get("password")

    if user is None or password is None:
        return jsonify({"status": "failure", "reason": "Missing user or password"}), 400
    with open("users.json") as f:
        db = json.load(f)
    if user not in db["users"]:
        return jsonify({"status": "failure", "reason": "no user with this name"}), 404
    salt = db["users"][user]["salt"]
    password_hash = db["users"][user]["hash"]
    ver = verify(password, salt, password_hash)
    return ver

def get_timestamp():
    now = datetime.now(timezone.utc)
    iso_z = now.replace(microsecond=0).isoformat().replace("+00:00", "Z")
    return iso_z  # "2025-12-27T16:45:12Z"


# Insert thingyard stuff here.

# thingyard json layout:
# Incremental ID!
# "1" {
#    "title": "joes joeinator",
#    "author": "joe",
#    "summary": "testtingigtn",
#    "body": "really long body that i like haha legs",
#    "image": "URL",
#    "comments": [
#        "1" (incremental) {
#            "name": "marisas",
#            "body": "Haha wow. Incredible!",
#            "timestamp": some ISO 8601 timestamp (YYYY-MM-DD T HH:MM:SS Z) (e.g. 2025-03-18T14:32:09Z)
#        }
#    ],
#    thats it? TODO: maybe add more to this if needed
# } to get timestamp use get_timestamp(), uuids are uuid.uuid4()

@app.route("/thingyard/upload", methods=["POST"])
def uploadthing():
    data = request.json
    title = data.get("title")
    body = data.get("body")
    summary = data.get("summary")
    image = data.get("image")
    authorized = auth(request)
    
    if authorized:
        if len(title)+len(body)+len(summary)+len(image) > 10000:
            return jsonify({"status": "failure", "reason": "over 10mb, CALM DOWN!"}), 413
        with open("thingyard.json") as f:
            db = json.load(f)
            proj = {
                "title": title,
                "author": data.get("user"),
                "summary": summary,
                "body": body,
                "image": image,
                "comments": [],
                "timestamp": str(get_timestamp())
            }
            db[str(len(db.keys()))] = proj
        with open("thingyard.json","w") as f:
            json.dump(db,f,indent=2)
        return jsonify({"status": "success"}), 200
    else:
        return jsonify({"status": "failure", "reason": "incorrect login details?"}), 401

@app.route("/thingyard", methods=["GET"])
def things():
    return send_file("thingyard.json")

@app.route("/thingyard/<thingid>", methods=["GET"])
def thing(thingid):
    with open("thingyard.json") as f:
        db = json.load(f)
    if thingid in db.keys():
        return db[thingid]
    else:
        return jsonify({"status": "failure", "reason": "No such thing"}), 404
    

@app.route("/thingyard/comment", methods=["POST"])
def comment():
    data = request.json
    body = data.get("body")
    id = data.get("id")
    authorized = auth(request)
    
    if authorized:
        if len(body) > 10000:
            return jsonify({"status": "failure", "reason": "over 10mb, CALM DOWN!"}), 413
        with open("thingyard.json") as f:
            db = json.load(f)
        db[id][comments].append(body)
        with open("thingyard.json","w") as f:
            json.dump(db,f,indent=2)
        return jsonify({"status": "success"}), 200
    else:
        return jsonify({"status": "failure", "reason": "incorrect login details?"}), 401
    

app.run(host="0.0.0.0", port=27935)