import os
import google.generativeai as genai
from flask import Flask, request
from twilio.twiml.voice_response import VoiceResponse
 
app = Flask(__name__)
 
# Gemini API Configuration
genai.configure(api_key=os.environ["GEMINI_API_KEY"])
 
# Model setup (Gemini 1.5 Flash - fast and cost-effective)
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    system_instruction="నువ్వు ఒక సహాయకారిగా ఉండే బాట్ వి. యూజర్ అడిగే ప్రశ్నలకు ఎల్లప్పుడూ క్లుప్తంగా, మర్యాదగా తెలుగులోనే సమాధానం ఇవ్వు."
)
 
@app.route("/voice", methods=['POST'])
def voice():
    """కాల్ రాగానే ప్లే అయ్యే ఫస్ట్ మెసేజ్"""
    response = VoiceResponse()
    response.say("హలో! నమస్కారం. నేను మీకు ఎలా సహాయపడగలను?", voice='alice', language='te-IN')
    
    # యూజర్ నుండి స్పీచ్ తీసుకోవడానికి gather
    response.gather(input='speech', action='/handle-transcription', timeout=3, speech_timeout='auto')
    return str(response)
 
@app.route("/handle-transcription", methods=['POST'])
def handle_transcription():
    """యూజర్ మాటలను ప్రాసెస్ చేసి ఆన్సర్ ఇచ్చే ఫంక్షన్"""
    user_text = request.values.get('SpeechResult', '') # Twilio నుండి వచ్చే యూజర్ టెక్స్ట్
 
    if not user_text:
        # యూజర్ ఏమీ మాట్లాడకపోతే
        response = VoiceResponse()
        response.say("క్షమించండి, నాకు వినిపించలేదు. ఇంకేమైనా అడగాలనుకుంటున్నారా?", voice='alice', language='te-IN')
        response.gather(input='speech', action='/handle-transcription', timeout=3, speech_timeout='auto', language='te-IN')
        return str(response)
 
    # Gemini నుండి రెస్పాన్స్ పొందడం
    try:
        gemini_response = model.generate_content(user_text)
        bot_answer = gemini_response.text
    except Exception as e:
        bot_answer = "క్షమించండి, సాంకేతిక కారణాల వల్ల నేను సమాధానం ఇవ్వలేకపోతున్నాను."
 
    # Twilio రెస్పాన్స్
    response = VoiceResponse()
    response.say(bot_answer, voice='alice', language='te-IN')
    
    # మళ్ళీ యూజర్ ని అడగడానికి gather
    response.gather(input='speech', action='/handle-transcription', timeout=3, speech_timeout='auto', language='te-IN')
    
    return str(response)
 
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
