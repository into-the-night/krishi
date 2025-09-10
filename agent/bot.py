from google.genai import Client
from PIL import Image
from config.settings import settings
import requests
import time
from lib.db import audio_to_supabase

client = Client(api_key=settings.gemini_api_key,)

class Bot:
    def __init__(self):
        self.client = client
        self.deepgram_api_key = settings.deepgram_api_key
        self.stt_url = "https://api.deepgram.com/v1/listen"
        self.tts_url = "https://api.deepgram.com/v1/speak"

    def analyse_output(self, diagnosis_result, image: Image, language: str = "en"):
        """
        Analyse the output from a plant disease and pest detection model and provide a detailed analysis of the plant disease and/or pest and ways to cure the disease and pest to a farmer in a friendly and easy to understand manner.
        """
        disease_predictions = diagnosis_result[0]['model_1_predictions']['predictions']
        pest_predictions = diagnosis_result[0]['predictions']['predictions']

        prompt = f"""You are a farming expert that has knowledge about various plant diseases.
        You are given an output from a plant disease and pest detection model, along with the input image.
        You need to do the following-
        1.examine the result and provide a detailed analysis of the plant disease and/or pest to a farmer,
        2.Provide a few economical ways to cure the disease and/or pest.
        respond in a concise and easy to understand manner.
        The analysis MUST be in the following language {language}. 
        The model result is as follows:
        Disease Model Predictions: {[f"{disease_prediction.get('class')} with confidence {disease_prediction.get('confidence')}" for disease_prediction in disease_predictions]}
        Pest Model Predictions: {[f"{pest_prediction.get('class')} with confidence {pest_prediction.get('confidence')}" for pest_prediction in pest_predictions]}
        """
        image = Image.open(image)
        response = self.client.models.generate_content(
            model="gemini-2.0-flash",
            contents=[prompt, image]
        )
        return response.text

    def chat(self, history: list, language: str = "en"):
        """
        Chat with a bot and provide a response to the farmer in a friendly and easy to understand manner.
        """
        conversation_context = ""
        if history:
            for msg in history:
                role = msg.get('role', 'user')
                content = msg.get('content', '')
                conversation_context += f"{role.capitalize()}: {content}\n\n"
        
        prompt = f"""You are a farming expert that has knowledge about crop planting and agricultural practices.
        You are having a conversation with a farmer.
        You are to provide a response to the farmer in a  Concise, friendly and easy to understand manner.
        The response MUST be in the following language: {language}.
        
        Here is the conversation history:
        {conversation_context}
        
        Please provide a helpful response to the farmer's latest message, taking into account the conversation context.
        """
        
        response = self.client.models.generate_content(
            model="gemini-2.0-flash",
            contents=[prompt]
        )
        return response.text
    
    #stt
    def speech_to_text(self, audio_bytes: bytes, mimetype: str = "audio/wav", language: str = None) -> str:
        """convert speech to text using deepgram STT."""
        headers = {
            "Authorization": f"Token {self.deepgram_api_key}",
            "Content-Type": mimetype
        }
        params = {"model": "nova-2"}
        if language:
            params["language"]= language 
        response = requests.post(self.stt_url, headers=headers,params=params, data=audio_bytes)
        response.raise_for_status()
        data = response.json()
        return data["results"]["channels"][0]["alternatives"][0]["transcript"]
    
    #tts
    def text_to_speech(self, text: str, model: str = "aura-2-thalia-en") -> bytes:
        """convert text to speech audio using deepgram TTS."""
        headers = {
            "Authorization": f"Token {self.deepgram_api_key}",
            "Content-Type": "application/json"
        }
        payload = {"text": text}
        resp = requests.post(f"{self.tts_url}?model={model}", headers=headers, json=payload)
        resp.raise_for_status()
        return resp.content
    
    def voice_chat(self, audio_bytes:bytes, user_id:str, mimetype: str= "audio/wav", language: str="en-US"):
        """chat using voice input and output."""
        user_text = self.speech_to_text(audio_bytes, mimetype, language)
        
        history = [{"role": "user", "content": user_text}]
        reply_text = self.chat(history, language)

        reply_audio = self.text_to_speech(reply_text)

        #saving audio to supabase
        user_audio_url= audio_to_supabase(audio_bytes, f"{user_id}_input_{int(time.time())}.wav", mimetype)
        bot_audio_url = audio_to_supabase(reply_audio, f"{user_id}_reply_{int(time.time())}.mp3", "audio/mpeg")


        return{
            "user_query": user_text,
            "bot_reply": reply_text,
            "user_audio_url": user_audio_url,
            "bot_audio_url": bot_audio_url,
        }


    def create_notification_message(self, alert_data: dict, language: str = "en"):
        """
        Create a notification message from the alert data.
        """
        prompt = f"""You are a farming expert that has knowledge about crop planting and agricultural practices.
        You are given an alert data from the weather api.
        You need to create a notification message from the alert data in a friendly and easy to understand manner.
        The notification message MUST be in the following language: {language}.
        The alert data is as follows:
        {alert_data}
        """
        response = self.client.models.generate_content(
            model="gemini-2.0-flash",
            contents=[prompt]
        )
        return response.text