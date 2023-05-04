from flask import Flask, render_template, request
from apscheduler.schedulers.background import BackgroundScheduler
from flask_socketio import SocketIO

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

@app.route('/')
def home():
    return render_template('home.html')


# example of scheduler:
def update_status():
    print("update status")
    pass

def update_status2():
    print("update status 2")
    pass

scheduler = BackgroundScheduler()
#scheduler.add_job(func=update_status, trigger='interval', seconds=0.5)
#scheduler.add_job(func=update_status2, trigger='interval', seconds=1)
scheduler.start()
scheduler.shutdown()


# sockeets

@socketio.on('connect')
def test_connect():
    print('Client connected')

@socketio.on('disconnect')
def test_disconnect():
    print('Client disconnected')

@socketio.on('message')
def handle_message(message):
    print('received message: ' + message)
    socketio.send('echo: ' + message)

if __name__ == '__main__':
    socketio.run(app)
