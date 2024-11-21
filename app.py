from flask import Flask, render_template_string, request, redirect, url_for
import os

app = Flask(__name__)

# Path for static folder to store uploaded images
UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Initializing global variables
conversations = []

# Default animated images (used if no custom images are uploaded)
DEFAULT_IMAGE1 = os.path.join(UPLOAD_FOLDER, "download.jpg")
DEFAULT_IMAGE2 = os.path.join(UPLOAD_FOLDER, "download (1).jpg")

# Upload default images to the static folder (if they don't exist)
if not os.path.exists(DEFAULT_IMAGE1):
    with open(DEFAULT_IMAGE1, "wb") as f:
        f.write(open("D:\\download.jpg", "rb").read())

if not os.path.exists(DEFAULT_IMAGE2):
    with open(DEFAULT_IMAGE2, "wb") as f:
        f.write(open("D:\\download (1).jpg", "rb").read())

# HTML Templates
index_html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Alliance Conversations</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #f4f4f9;
            margin: 0;
            padding: 0;
        }
        header {
            background-color: #0056b3;
            color: #fff;
            padding: 1rem;
            text-align: center;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        .container {
            padding: 2rem;
            max-width: 900px;
            margin: 2rem auto;
            background: #ffffff;
            border-radius: 10px;
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
        }
        .conversation-card {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 1rem;
            margin-bottom: 1rem;
            border: 1px solid #ddd;
            border-radius: 10px;
            transition: transform 0.3s, box-shadow 0.3s;
        }
        .conversation-card:hover {
            transform: scale(1.02);
            box-shadow: 0 6px 15px rgba(0, 0, 0, 0.2);
        }
        .conversation-card img {
            width: 60px;
            height: 60px;
            border-radius: 50%;
        }
        .conversation-card h3 {
            flex: 1;
            margin: 0 1rem;
            font-size: 1.2rem;
            color: #333;
        }
        .new-conversation-btn {
            display: block;
            width: 100%;
            text-align: center;
            padding: 1rem;
            background: #0056b3;
            color: white;
            text-decoration: none;
            font-weight: bold;
            border-radius: 8px;
            margin-bottom: 2rem;
        }
        .new-conversation-btn:hover {
            background: #003f7f;
        }
    </style>
</head>
<body>
<header>
    <h1>Alliance Conversations</h1>
</header>
<div class="container">
    <a href="{{ url_for('new_conversation') }}" class="new-conversation-btn">Start a New Conversation</a>
    <h2>Available Conversations</h2>
    {% if conversations %}
        {% for convo in conversations %}
        <div class="conversation-card">
            <img src="{{ url_for('static', filename=convo.image1) }}" alt="{{ convo.person1 }}">
            <h3><a href="{{ url_for('conversation', conversation_id=loop.index0) }}">{{ convo.person1 }} & {{ convo.person2 }}</a></h3>
            <img src="{{ url_for('static', filename=convo.image2) }}" alt="{{ convo.person2 }}">
        </div>
        {% endfor %}
    {% else %}
        <p>No conversations available. Click "Start a New Conversation" to begin.</p>
    {% endif %}
</div>
</body>
</html>
"""

new_html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>New Conversation</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #f9f9f9;
            margin: 0;
            padding: 0;
        }
        header {
            background-color: #0056b3;
            color: #fff;
            padding: 1rem;
            text-align: center;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        .container {
            max-width: 600px;
            margin: 2rem auto;
            padding: 1rem;
            background: #fff;
            border-radius: 8px;
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
        }
        form {
            display: flex;
            flex-direction: column;
        }
        label {
            margin-bottom: 0.5rem;
        }
        input, button {
            margin-bottom: 1rem;
            padding: 0.5rem;
            font-size: 1rem;
        }
        button {
            background: #0056b3;
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
        }
        button:hover {
            background: #003f7f;
        }
    </style>
</head>
<body>
<header>
    <h1>Start a New Conversation</h1>
</header>
<div class="container">
    <form method="POST">
        <label for="person1">Person 1 Name:</label>
        <input type="text" name="person1" id="person1" required>
        <label for="person2">Person 2 Name:</label>
        <input type="text" name="person2" id="person2" required>
        <button type="submit">Create Conversation</button>
    </form>
</div>
</body>
</html>
"""

conversation_html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Conversation</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #f4f4f9;
            margin: 0;
            padding: 0;
        }
        header {
            background-color: #0056b3;
            color: #fff;
            padding: 1rem;
            text-align: center;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        .container {
            padding: 2rem;
            max-width: 800px;
            margin: 2rem auto;
            background: #ffffff;
            border-radius: 10px;
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
        }
        .message {
            margin: 1rem 0;
            padding: 0.8rem;
            border-radius: 10px;
        }
        .person1 {
            background: #cce5ff;
            text-align: left;
        }
        .person2 {
            background: #d4edda;
            text-align: right;
        }
        form {
            margin-top: 2rem;
        }
        input, button {
            width: 100%;
            margin-bottom: 1rem;
            padding: 0.8rem;
            font-size: 1rem;
        }
        button {
            background: #0056b3;
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
        }
        button:hover {
            background: #003f7f;
        }
    </style>
</head>
<body>
<header>
    <h1>Conversation Between {{ convo.person1 }} and {{ convo.person2 }}</h1>
</header>
<div class="container">
    <h2>Messages</h2>
    {% if convo.conversation %}
        {% for msg in convo.conversation %}
        <div class="message {{ loop.index0 % 2 == 0 and 'person1' or 'person2' }}">
            {{ msg }}
        </div>
        {% endfor %}
    {% else %}
        <p>No messages yet. Start the conversation below!</p>
    {% endif %}
    <form method="POST">
        <input type="text" name="message" placeholder="Type your message..." required>
        <button type="submit" name="continue" value="yes">Send Message</button>
        <button type="submit" name="continue" value="no">End Conversation</button>
    </form>
</div>
</body>
</html>
"""

# Routes
@app.route('/')
def index():
    return render_template_string(index_html, conversations=conversations)

@app.route('/new', methods=['GET', 'POST'])
def new_conversation():
    if request.method == 'POST':
        person1 = request.form['person1']
        person2 = request.form['person2']
        conversations.append({
            "person1": person1,
            "person2": person2,
            "conversation": [],
            "image1": "uploads/download.jpg",
            "image2": "uploads/download (1).jpg",
        })
        return redirect(url_for('index'))
    return render_template_string(new_html)

@app.route('/conversation/<int:conversation_id>', methods=['GET', 'POST'])
def conversation(conversation_id):
    if conversation_id >= len(conversations):
        return "Conversation not found", 404
    convo = conversations[conversation_id]
    
    if request.method == 'POST':
        message = request.form.get('message')
        continue_chat = request.form.get('continue')
        
        if message:
            convo['conversation'].append(message)
        
        if continue_chat == 'no':
            return redirect(url_for('index'))
        elif continue_chat == 'yes':
            return redirect(url_for('conversation', conversation_id=conversation_id))
    
    return render_template_string(conversation_html, convo=convo)


if __name__ == '__main__':
    app.run(debug=True)
