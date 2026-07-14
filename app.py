import os
import httpx # Idi import cheyyandi
import requests
from flask import Flask, request
from twilio.twiml.voice_response import VoiceResponse
from twilio.rest import Client
from openai import OpenAI
from dotenv import load_dotenv
 
# .env file load cheyyandi
load_dotenv()
 
app = Flask(__name__)
 
# Credentials
account_sid = 'ACfecde84f2d1572166557fa133164f1b0'
auth_token = '4202027e0c6ac83a9dff3220fa17b355'
client = Client(account_sid, auth_token)
 
# OpenAI Client (SSL bypass tho)
http_client = httpx.Client(verify=False)
openai_client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    http_client=http_client
)
 
@app.route("/voice", methods=['POST'])
def voice():
    response = VoiceResponse()
    response.say("Namaskaram. Sarathi AI ki swagatham. Dayachesi mee sandesham cheppandi.")
    # Call cut ayyaka '/handle-transcription' ki pampistundi
    response.record(max_length=30, transcribe=False, recording_status_callback='/handle-transcription')
    return str(response)
 
@app.route("/handle-transcription", methods=['POST'])
def handle_transcription():
    recording_url = request.form.get('RecordingUrl')
    
    # 1. Audio file download
    audio_file_path = "recording.wav"
    auth = (account_sid, auth_token)
    response = requests.get(recording_url, auth=auth)
    with open(audio_file_path, "wb") as f:
        f.write(response.content)
 
    # 2. Whisper API dwara transcription
    audio_file = open(audio_file_path, "rb")
    transcript = openai_client.audio.transcriptions.create(
        model="whisper-1",
        file=audio_file,
        language="te"
    )
    transcription_text = transcript.text
    
    # 3. WhatsApp ki pampadam
    print(f"Telugu Text: {transcription_text}")
    client.messages.create(
        body=f"New Voice Message: {transcription_text}",
        from_='whatsapp:+14155238886',
        to='whatsapp:+919493918625'
    )
    return "OK", 200
 
if __name__ == '__main__':
    app.run(port=5000)