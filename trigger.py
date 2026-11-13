import socketio

# Initialize the client
sio = socketio.SimpleClient()

# Connect to your laptop's server
sio.connect('http://10.181.2.99:5001')

# Send the event
sio.emit('status', {'event': 'BROADSIDE'})

# Close the connection
sio.disconnect()
print("Broadside signal sent.")