# Script to prompt additional information about each contact. 
# Accepts speech and transcribes this into notes.

import json
import os
import speech_recognition as sr
from gtts import gTTS
import playsound
import tempfile

def text_to_speech(text, filename="temp_audio.mp3"):
    """Converts text to speech and saves it to a file."""
    tts = gTTS(text)
    tts.save(filename)
    return filename

def play_audio(filepath):
    """Plays an audio file."""
    playsound.playsound(filepath)

def record_and_transcribe():
    """Records audio and transcribes it."""
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Speak now...")
        recognizer.pause_threshold = 2.0 #sets the pause threshold to 1 second.
        audio = recognizer.listen(source, phrase_time_limit=10)

    try:
        print("Transcribing...")
        text = recognizer.recognize_google(audio)
        print(f"You said: {text}")
        return text
    except sr.UnknownValueError:
        print("Speech recognition could not understand audio")
        return None
    except sr.RequestError as e:
        print(f"Could not request results from Google Speech Recognition service; {e}")
        return None

def get_contact_names(filename="contacts_data.json"):
    """
    Reads a JSON file, iterates through the contacts, and extracts their display names.

    Args:
    filename (str, optional): The name of the JSON file.
    Defaults to "contacts_data.json".

    Returns:
    list: A list of display names for each contact.
    """

    display_names = []  # Initialize as empty list
    try:
        with open(filename, 'r') as f:
            data = json.load(f)

        if "connections" in data and isinstance(data["connections"], list):
            for contact in data["connections"]:
                if "names" in contact and isinstance(contact["names"], list):
                    #Access the first element in the names list
                    name_data = contact["names"][0]
                    if "display_name" in name_data:
                        display_names.append(name_data["display_name"])
                    else:
                        display_names.append("Unknown Contact")  # Or handle missing name as needed
                else:
                    display_names.append("Unknown Contact")  # Or handle missing names as needed
        else:
            print("Error: 'connections' key not found or is not a list in the JSON data.")
            return None

    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
        return None
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON in file '{filename}'.")
        return None

    return display_names
    
# Get the display names
names = get_contact_names()
output_dir = 'contact_notes'

# Print the display names
if names:
    for name in names:
        prompt = f"Tell me something about {name}."
        audio_file = text_to_speech(prompt)
        play_audio(audio_file)
        os.remove(audio_file) #clean up temp file
        transcription = record_and_transcribe()
        
        if transcription:
            filename = os.path.join(output_dir, f"{name.replace(' ', '_')}.txt")
            with open(filename, 'w') as f:
                f.write(transcription)
            print(f"Transcription saved to {filename}")
