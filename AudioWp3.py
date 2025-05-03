#  Whatsapp Audio chatbot created using twilio
# run this .py the port number passed in cmd using- ngrok http 5008
# the link generated is passed to sandbox setting and then whatsapp msg to twilio nmber sent for chatting

# A Flask-based WhatsApp voice chatbot that:
# 1. Receives voice notes (OGG/Opus) via Twilio
# 2. Downloads the audio (authenticated)
# 3. Converts to WAV via ffmpeg (no pydub used)
# 4. Transcribes with OpenAI Whisper API
# 5. Generates a response via LangChain ChatOpenAI
# 6. Replies back on WhatsApp with text

# Install dependencies:
# pip install flask twilio requests openai python-dotenv langchain_openai langchain_core


from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client
import os
import requests
import subprocess 
# ffmpeg converts ogg to wav, but subprocess.run-allows you to
# run that ffmpeg command from Python without using pydub for conversion
from dotenv import load_dotenv
from openai import OpenAI
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

# Load environment variables from .env
load_dotenv()

# Twilio client setup
ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
AUTH_TOKEN  = os.getenv("TWILIO_AUTH_TOKEN")
twilio_client = Client(ACCOUNT_SID, AUTH_TOKEN)

# OpenAI clients
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
# Whisper client (for audio transcription)
whisper_client = OpenAI(api_key=OPENAI_API_KEY)
# ChatGPT client via LangChain
llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.4,
    api_key=OPENAI_API_KEY
)

# Flask app initialization
# app = Flask(__name__)
app = Flask(__name__, static_url_path='/static', static_folder='static')


# -- Utility Functions --

def download_audio(url: str, filename: str = "user_audio.ogg") -> str:
    """
    Download the media from Twilio into a local OGG file using HTTP Basic Auth.
    """
    response = requests.get(url, auth=(ACCOUNT_SID, AUTH_TOKEN))
    response.raise_for_status()
    with open(filename, "wb") as f:
        f.write(response.content)
    return filename


def convert_ogg_to_wav(source: str = "user_audio.ogg", target: str = "user_audio.wav") -> str:
    """
    Use ffmpeg CLI to convert Opus-in-OGG to a mono, 16kHz WAV file.
    """
    subprocess.run([
        "ffmpeg", "-y",
        "-i", source,
        "-ar", "16000",  # resample to 16 kHz
        "-ac", "1",      # mono channel
        target
    ], check=True)
    return target


def transcribe_audio(audio_path: str) -> str:
    """
    Send the WAV file to OpenAI Whisper for transcription.
    """
    with open(audio_path, "rb") as f:
        resp = whisper_client.audio.transcriptions.create(
            model="whisper-1",
            file=f
        )
    return resp.text


def get_chat_response(user_input: str) -> str:
    """
    Generate a chat response using LangChain ChatOpenAI.
    """
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a concise and helpful chatbot assistant that gives all the updates."),
        ("human", "{input}")
    ])
    messages = prompt.format_messages(input=user_input)
    reply = llm.predict_messages(messages)
    return reply.content

#convert reply to audio
from gtts import gTTS
import os

def speak_text(text, filename="llm_response.mp3"):
    """
    Convert text to speech using gTTS and save in ./static for serving.
    """
    filepath = os.path.join("static", filename)
    tts = gTTS(text=text, lang="en")
    tts.save(filepath)
    print("🔊 LLM response converted to speech.")
    return filepath  # returns "static/llm_response.mp3"




# -- Flask Webhook --

@app.route("/whatsapp", methods=["POST"])
def whatsapp_webhook():
    media_url  = request.values.get("MediaUrl0")
    media_type = request.values.get("MediaContentType0", "")
    resp = MessagingResponse()

    if media_url and media_type.startswith("audio"):
        try:
            # 1) Download the voice note (with auth)
            ogg_file = download_audio(media_url)
            # 2) Convert to WAV
            wav_file = convert_ogg_to_wav(ogg_file)
            # 3) Transcribe with Whisper
            transcription = transcribe_audio(wav_file)

            # 4) Generate chat response
            reply_text = get_chat_response(transcription)

            # convert text to audio
            audio_reply=speak_text(reply_text)

            # Extract just the filename from the full file path
            filename = os.path.basename(audio_reply)
            
            # Construct the public URL for the audio file
            public_url = request.host_url.replace("http://", "https://")  # Ensure HTTPS
            audio_url = public_url + "static/" + filename  # Correct URL path

            # Send the audio URL as a media message
            msg = resp.message(f"🗣 You said:\n{transcription}\n\n🤖 Bot says:\n{reply_text}")
            msg.media(audio_url)


        except Exception as e:
            print("Error processing audio:", e)
            resp.message("Sorry, I couldn't process your voice message.")
    else:
        resp.message("Please send a voice message.")

    return str(resp)

if __name__ == "__main__":
    app.run(debug=True, port=5008)
