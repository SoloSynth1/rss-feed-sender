import base64

import google.auth
from googleapiclient.discovery import build
from flask import Flask, request, json


PORT = 8080
HOST = "0.0.0.0"
SCOPES = ['https://www.googleapis.com/auth/chat.bot']

credentials, project_id = google.auth.default()
credentials = credentials.with_scopes(scopes=SCOPES)
chat = build('chat', 'v1', credentials=credentials)

app = Flask(__name__)


@ app.route('/', methods=['POST'])
def home_post():

    envelope = request.get_json()
    if not envelope:
        msg = 'no Pub/Sub message received'
        print(f'error: {msg}')
        return f'Bad Request: {msg}', 400

    if not isinstance(envelope, dict) or 'message' not in envelope:
        msg = 'invalid Pub/Sub message format'
        print(f'error: {msg}')
        return f'Bad Request: {msg}', 400

    pubsub_message = envelope['message']

    if isinstance(pubsub_message, dict) and 'data' in pubsub_message:


        json_str = base64.b64decode(pubsub_message['data']).decode('utf-8').strip()
        message_json = json.loads(json_str)
        push_message(message_json)

        return json.jsonify({}), 204
    else:
        msg = 'error when processing request'
        return f'Bad Request: {msg}', 500


def push_message(message_json):
    feed_name = message_json['name']
    title = message_json['title']
    link = message_json['link']
    room = message_json['space']

    message = {'text':  f"[{feed_name}] {title}\n{link}"}
    chat.spaces().messages().create(parent=room, body=message).execute()


if __name__ == '__main__':
    app.run(host=HOST, port=PORT, debug=True)
