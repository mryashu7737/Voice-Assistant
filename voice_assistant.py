import speech_recognition as sr
import google.generativeai as genai
import pyttsx3
import PyQt5.QtWidgets as QtWidgets
import sys
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Configure Gemini API using environment variable
api_key = os.getenv('GEMINI_API_KEY')
if not api_key:
    raise ValueError("GEMINI_API_KEY not found in .env file")

genai.configure(api_key=api_key)

# Set up the model with safety settings
generation_config = {
    "temperature": 0.9,
    "top_p": 1,
    "top_k": 1,
    "max_output_tokens": 2048,
}

safety_settings = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
]

# Create a generative model and chat session
model = genai.GenerativeModel(
    model_name="gemini-1.5-pro",
    generation_config=generation_config,
    safety_settings=safety_settings
)

chat = model.start_chat(history=[])

# Speech recognizer and TTS engine
recognizer = sr.Recognizer()
engine = pyttsx3.init()

def get_voice_input():
    with sr.Microphone() as source:
        print("Listening...")
        audio = recognizer.listen(source)

    try:
        text = recognizer.recognize_google(audio)
        print(f"You said: {text}")
        return text
    except sr.UnknownValueError:
        print("Sorry, I could not understand.")
        return None
    except sr.RequestError as e:
        print(f"Could not request results from Google Speech Recognition service; {e}")
        return None

def get_gemini_response(prompt):
    try:
        response = chat.send_message(prompt)
        return response.text
    except Exception as e:
        print(f"Debug - Error details: {str(e)}")
        return f"Sorry, there was an error getting the response. Please check your API key and internet connection. Error: {str(e)}"


def speak(text):
    # Set properties
    voices = engine.getProperty('voices')
    
    # Try to find a female voice
    for voice in voices:
        if 'female' in voice.name.lower() or 'zira' in voice.name.lower():
            engine.setProperty('voice', voice.id)
            break
    else:
        # fallback to default if no female voice is found
        engine.setProperty('voice', voices[0].id)

    engine.setProperty('rate', 165)   # Set speaking rate (typical human range: 150–180)
    engine.setProperty('volume', 1.0) # Max volume

    engine.say(text)
    engine.runAndWait()

def main():
    # Initial greeting
    initial_response = (
        "Hello! I'm your sustainability assistant. I can help you understand and reduce your carbon footprint. "
        "Please tell me about your lifestyle or ask any specific questions about sustainability."
    )
    print(initial_response)
    speak(initial_response)
    text_display.setText(initial_response)

    while True:
        user_input = get_voice_input()
        if user_input:
            modified_input = user_input + ". Make it short and to the point. Make it more like human conversational stuff."
            gemini_response = get_gemini_response(modified_input)
            print(gemini_response)
            speak(gemini_response)
            text_display.setText(gemini_response)

def start_voice_input():
    main()

# PyQt5 GUI setup
app = QtWidgets.QApplication(sys.argv)
window = QtWidgets.QWidget()
window.setWindowTitle("Sustainability Assistant")
layout = QtWidgets.QVBoxLayout()

text_display = QtWidgets.QTextEdit()
layout.addWidget(text_display)

voice_button = QtWidgets.QPushButton("Start Voice Input")
voice_button.clicked.connect(start_voice_input)
layout.addWidget(voice_button)

window.setLayout(layout)
window.show()

sys.exit(app.exec_())