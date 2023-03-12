from flask import Flask, render_template, request, session, redirect, url_for
from flask_socketio import join_room, leave_room, send, SocketIO, emit
import random
from string import ascii_uppercase

app = Flask(__name__)
app.config['SECRET_KEY'] = "helllo"
socketio = SocketIO(app)

rooms = {}

def generate_unique_code(length):
    while True:
        code = ""
        for _ in range(length):
            code += random.choice(ascii_uppercase)
        if code  not in rooms:
            break
    return code


@app.route("/", methods = ['GET','POST'])
def home(): 
    session.clear()
    if request.method == 'POST':
        name = request.form.get("name")
        code = request.form.get("code")
        join = request.form.get("join", False)
        create = request.form.get("create", False)

        if not name:
            return render_template("home.html", error="Please enter a name.", name=name, code = code)
        if join != False and not code:
            return render_template("home.html", error="Please enter a room code.", name=name, code=code)

        room = code
        if create != False:
            room = generate_unique_code(4)
            rooms[room] = {"members":0, "messages":[]}
        elif code not in rooms:
            return render_template("home.html", error="Rooms does not exist.", name= name, code = code)
        

        session["room"] = room
        session["name"] = name
        return redirect(url_for('room'))
    
    return render_template("home.html")

@app.route('/room')
def room():
    if room is None or session.get("name") == None or session.get('room') == None:
        return render_template(url_for('home'))
    
    return render_template('room.html', room = session.get('room'))

@socketio.on('connect')
def connect():
    room = session.get('room')
    name = session.get('name')
    if name is None and room is None:
        return 
    if room not in rooms:
        leave_room(room) #when they want to connect to room and if they not in room that is not already created then leave from that room
        return
    
    join_room(room)
    emit("messages", {"message": name + " has entered the room "}, room=room)

@socketio.on('disconnect')
def disconnect():
    room = session.get('room')
    name = session.get('name')
    leave_room(room)
    emit("messages", {"message": name + " has left the room "}, room = room)

@socketio.on('addmessage')
def add_message(data):
    room = session.get('room')
    name = session.get('name')
    print(data)
    emit("messages", {"message": data['message']}, room = room)

if __name__ == "__main__":
    socketio.run(app, debug = True)
    