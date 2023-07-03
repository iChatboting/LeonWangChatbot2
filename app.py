#pip install openai
#pip install gradio
#pip install pyttsx3
#pip install langdetect
#pip install openai gradio pyttsx3 langdetect
#pip install google-cloud-texttospeech
#pip install --upgrade google-cloud-texttospeech
#pip install python-dotenv

import langdetect
import gradio as gr
import openai
import pyttsx3

from dotenv import load_dotenv
import os
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

#openai.api_key = ""

conversation = [
        {"role": "system", "content": "You are an intelligent professor."},
        ]

def transcribe(audio):
    print(audio)

#   Whisper API
    audio_file = open(audio, "rb")
    transcript = openai.Audio.transcribe("whisper-1", audio_file)

#   ChatGPT API
    conversation.append({"role": "user", "content": transcript["text"]})

    response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=conversation
    )

    system_message = response["choices"][0]["message"]["content"]
    conversation.append({"role": "assistant", "content": system_message})

#   Language detection
    import langdetect
    detected_lang = langdetect.detect(transcript["text"])
    
#   Define a dictionary to map the detected language to language code and voice name
    language_dict = {
        "fr": ("fr-FR", "fr-FR-Wavenet-A"),
        "zh": ("cmn-CN", "cmn-CN-Wavenet-C"),
        "ja": ("ja-JP", "ja-JP-Neural2-D"),
    }


#   Set the language and voice for Google TTS based on the detected language
    if detected_lang in language_dict:
        language_code, voice_name = language_dict[detected_lang]
    else:
        language_code = "en-US"
        voice_name = "en-US-Wavenet-D"

#   generate speech from system_message using Google Cloud Text-to-Speech API
    from google.oauth2 import service_account
    credentials = service_account.Credentials.from_service_account_file("D:/ChatGPTApps/LeoWang2/key.json")

    from google.cloud import texttospeech
    client = texttospeech.TextToSpeechClient(credentials=credentials)
    synthesis_input = texttospeech.SynthesisInput(text=system_message)
    voice = texttospeech.VoiceSelectionParams(
        language_code=language_code, name=voice_name
    )
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3
    )
    response = client.synthesize_speech(
        input=synthesis_input, voice=voice, audio_config=audio_config
    )

#   return the audio file as Gradio output
    import uuid

#   save the audio content to a file
    with open("output.mp3", "wb") as out:
        out.write(response.audio_content)
    print('Audio content written to file "output.mp3"')

# return the path to the saved file as Gradio output
    return "output.mp3"


#   Gradio output
bot = gr.Interface(fn=transcribe, inputs=gr.Audio(source="microphone", type="filepath"), outputs="audio")
bot.launch(share=True)

