import requests
import humanize
from threading import Lock
from datetime import datetime, timedelta
from flask import Flask, render_template, session
from flask_socketio import SocketIO, emit

async_mode = None

app = Flask(__name__)
socketio = SocketIO(app, async_mode=async_mode)
thread = None
thread_lock = Lock()


connected_clients = 0

#Event Handling Connect and Disconnects
@socketio.event
def connect():
    global thread, connected_clients
    session['connected_since'] = datetime.now()
    connected_clients +=1
    with thread_lock:
        if thread is None:
            thread = socketio.start_background_task(background_thread)
    emit('my_response', {'data': 'Establishing Connection ..', 'count': 0})


@socketio.event
def disconnect():
    connected_clients -=1


#Continous background broadcasts
def background_thread():
    """Example of how to send server generated events to clients."""
    count = 0
    while True:
        socketio.sleep(60)
        socketio.emit('my_response', {'data': 'Connected', 'count':0})

def get_server_timestamp():
	return str(datetime.now())

def get_connected_since():
	delta =  datetime.now() - session.get('connected_since')
	return humanize.naturaltime(delta)




@socketio.on('stime')
def handle_message(data):
    print('received message: ' + str(data))
    emit('stime_response', {'data': f'Server Timestamp: {get_server_timestamp()}'})
@socketio.event
def my_event(message):
    emit('my_response',
         {'data': message['data'], 'count': 0})


@socketio.on('ctime')
def handle_message(data):
    print('received message: ' + str(data))
    emit('ctime_response', {'data': f'Session active since: {get_connected_since()}'})
@socketio.event
def my_event(message):
    emit('my_response',
         {'data': message['data'], 'count': 0})


@socketio.on('clients')
def handle_message(data):
    print('received message: ' + str(data))
    emit('clients_response', {'data': f'Connected Clients: {connected_clients}'})
@socketio.event
def my_event(message):
    emit('my_response',
         {'data': message['data'], 'count': 0})



@app.route('/')
def index():
    return render_template('index.html', async_mode=socketio.async_mode)



if __name__ == '__main__':
    socketio.run(app)
