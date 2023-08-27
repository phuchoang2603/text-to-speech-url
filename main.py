from flask import Flask, request, jsonify
import requests
import json
from configparser import ConfigParser
import os

def upload_audio_file(object_location, oauth2_token, object_content_type, bucket_name, object_name):
    url = f"https://storage.googleapis.com/upload/storage/v1/b/{bucket_name}/o?uploadType=media&name={object_name}"
    headers = {
        "Authorization": f"Bearer {oauth2_token}",
        "Content-Type": object_content_type
    }
    with open(object_location, "rb") as file:
        response = requests.post(url, data=file, headers=headers)
    if response.status_code == 200:
        print("Audio file uploaded successfully.")
    else:
        print("Error uploading audio file.")

# Function that generates the audio file for a given text
def generate_audio(text, viettel_api_key):
    payload = {
        "text": text,
        "voice": "hn-thaochi",
        "speed": 1,
        "tts_return_option": 3,
        "token": viettel_api_key,
        "without_filter": False
    }

    headers = {'accept': '*/*','Content-Type': 'application/json'}

    response = requests.post('https://viettelgroup.ai/voice/api/tts/v1/rest/syn', data=json.dumps(payload), headers=headers)

    # save the audio file
    with open('file.mp3', 'wb') as f:
        f.write(response.content)

app = Flask(__name__)

@app.route('/', methods=['POST'])
def main():
    # Set up API key information
    config = ConfigParser()
    config.read('config.ini')
    bucket_name = config.get('google-cloud-storage', 'bucket_name')
    viettel_api_key = config.get('viettel-ai', 'api_key')
    oauth2_token = config.get('google-cloud-storage', 'oauth2_token')

    # Get the text from the request
    text = request.form['text']

    # Generate the audio file from vietel.ai
    generate_audio(text, viettel_api_key)

    # Upload the audio file to Google Cloud Storage
    object_location = "file.mp3"
    object_content_type = "audio/mpeg"
    bucket_name = bucket_name
    # generate random name for audio file uploaded to GCS
    object_name = os.urandom(16).hex() + ".mp3"

    upload_audio_file(object_location, oauth2_token, object_content_type, bucket_name, object_name)

    # Return the URL of the audio file
    return jsonify({"url": f"https://storage.googleapis.com/{bucket_name}/{object_name}"})

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
