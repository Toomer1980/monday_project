from flask import Flask
from flask_socketio import SocketIO

app = Flask(__name__)
# The library automatically detects eventlet if installed
socketio = SocketIO(app, async_mode='eventlet', cors_allowed_origins="*")

@socketio.on('telemetry')
def handle_telemetry(data):
    print(f"HUD Telemetry Received: {data['status_report']}")
    # Optional: Relay status to other components

if __name__ == '__main__':
    # Simply run the socketio instance without the extra 'server' argument
    socketio.run(app, host='0.0.0.0', port=5001)