import pyttsx3
import speech_recognition as sr
import webbrowser
from google import genai
from google.genai import types
import json

r = sr.Recognizer()
client = genai.Client(api_key= "AIzaSyBa0pSnwcBrl0gWY1nsjnakyvqlYGtVJ7U")
input_cmd = ""
cmd_dict = {}

COMMAND_SCHEMA = types.Schema(
    type=types.Type.OBJECT,
    properties={
        "command": types.Schema(
            type=types.Type.STRING,
            description="The best-suited command: 'OPEN_WEBSITE'or 'PLAY_SONG'.",
            enum=['OPEN_WEBSITE', 'PLAY_SONG'] 
        ),
        "name": types.Schema(
            type=types.Type.STRING,
            description="The name of the website or the song user has asked about"
        ),
        "link": types.Schema(
            type =types.Type.STRING,
            description="The link of the song or the website"
        )
    },
    required=["command", "name", "link"]
)

SYSTEM_PROMPT = """
You are a command mapping AI. Your sole function is to map user input to one of the following structured commands.

Commands:
* **OPEN_WEBSITE**: If the user asks to open a website (e.g., 'Go to Wikipedia').
* **PLAY_SONG**: If the user asks to play a song (e.g., 'Play my favorite rock anthem').

You MUST find the name and the correct URL (link) for the request and return ONLY the JSON object.

**Output Format Constraint:** You MUST respond ONLY with a JSON object that strictly adheres to the provided schema. Do not include any conversational text, explanations, or markdown fences.
"""

config = types.GenerateContentConfig(
        system_instruction=SYSTEM_PROMPT,
        response_mime_type="application/json",
        response_schema=COMMAND_SCHEMA,
        temperature=0.1
    )

def  listen(to=5, ptl=7): 
    try:
        with sr.Microphone() as source:
            print("Listening...")
            audio = r.listen(source, timeout= to, phrase_time_limit= ptl )
        print("recognizing...")
        global input_cmd 
        input_cmd = r.recognize_google(audio)
    except:
        input_cmd = ""

def get_cmd():
    global cmd_dict
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=[input_cmd],
            config=config
        )
        
        cmd_dict = json.loads(response.text)
    
    except Exception as e:
        print(f"An error occurred: {e}")
        return {"error": str(e), "command": "ERROR"}

def process_cmd():
    if cmd_dict['command'] == "OPEN_WEBSITE":
        speak(f"Opening Website {cmd_dict["name"]}")
    if cmd_dict['command'] == "PLAY_SONG":
        speak(f"Playing song {cmd_dict["name"]}")
    webbrowser.open(cmd_dict["link"])

def speak(text, voice=0):
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')
    engine.setProperty('voice', voices[voice].id)
    engine.say(text)
    engine.runAndWait()
    engine.stop()

if __name__ == "__main__":
    speak("Initializing Jarvis", 1)
    while True:
        listen(10,2)
        if input_cmd.lower() == "jarvis":
            print("Jarvis activated!")
            speak("Jarvis Activated")
            listen(3,7)
            get_cmd()
            process_cmd()
        if input_cmd.lower() == "exit":
            speak("Closing Program", 1)
            break
        