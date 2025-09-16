from flask import Flask, request, jsonify, render_template
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime

# Initialize Flask
app = Flask(__name__)

# Firebase setup
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

# Home route
@app.route('/')
def home():
    return render_template('index.html')

# Get all messages
@app.route('/messages', methods=['GET'])
def get_messages():
    messages_ref = db.collection('messages').order_by('timestamp')
    docs = messages_ref.stream()
    messages = []
    for doc in docs:
        msg = doc.to_dict()
        msg['timestamp'] = msg.get('timestamp') if msg.get('timestamp') else ''
        messages.append(msg)
    return jsonify(messages)

# Send a new message
@app.route('/messages', methods=['POST'])
def send_message():
    data = request.get_json()
    text = data.get('text')
    user = data.get('user')

    if not text or not user:
        return jsonify({"error": "Missing data"}), 400

    # Timestamp in HH:MM format
    timestamp = datetime.utcnow().strftime('%H:%M')

    # Add message to Firestore
    db.collection('messages').add({
        'text': text,
        'user': user,
        'timestamp': timestamp
    })

    return jsonify({"success": True}), 200

# Run the app
if __name__ == '__main__':
    app.run(debug=True)
