# Whatsapp_Chatbot
* Developed a Flask-based WhatsApp voice chatbot that enables real-time voice communication with an AI assistant using Twilio's WhatsApp sandbox. 
* The bot receives voice messages in OGG/Opus format, securely downloads and converts them to WAV using ffmpeg, and transcribes the audio using OpenAI’s Whisper API.
* It then generates context-aware responses via LangChain and GPT-4o-mini, converts the replies to speech using gTTS, and sends them back to the user as audio messages.
* The system is deployed locally using ngrok for secure webhook exposure.


