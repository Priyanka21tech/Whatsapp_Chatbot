# Whatsapp_Chatbot
To use this bot, you must configure the WhatsApp sandbox environment in your Twilio account.

Features
* Accepts voice notes via WhatsApp (OGG/Opus format)
* Downloads and converts audio securely to WAV using ffmpeg
* Transcribes audio with OpenAI Whisper API
* Generates conversational replies using LangChain + GPT-4o-mini
* Converts responses to speech with gTTS and replies as audio
* Deployed locally using ngrok for webhook integration

# Tech Stacks
* Backend: Flask
* AI & LLM: OpenAI Whisper API, LangChain, GPT-4o-mini
* Audio Processing: ffmpeg, gTTS
* Messaging Platform: Twilio WhatsApp Sandbox
* Deployment: ngrok (for local testing)

# Create a .env file in the root directory with the following credentials:
TWILIO_ACCOUNT_SID=your_account_sid
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_PHONE_NUMBER=your_twilio_sandbox_number
OPENAI_API_KEY=your_openai_api_key
CONTENT_SID=your_content_sid
PHONE=your_verified_phone_number

# Install dependencies:
# pip install flask twilio requests openai python-dotenv langchain_openai langchain_core

# run : 
python AudioWp3.py


