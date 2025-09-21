import json
import wave
import uuid
from PIL import Image
from google.genai import Client, types
from deepgram import (
    DeepgramClient,
    PrerecordedOptions,
    FileSource,
)
from config.settings import settings
from lib.redis import Redis

client = Client(api_key=settings.gemini_api_key)
deepgram_client = DeepgramClient(api_key=settings.deepgram_api_key)
redis_client = Redis()

class Bot:
    def __init__(self):
        self.client = client
        self.deepgram_client = deepgram_client
        self.redis_client = redis_client

    async def analyse_output(self, diagnosis_result, image: str, language: str = "en"):
        """
        Analyse the output from a plant disease and pest detection model and provide a detailed analysis of the plant disease and/or pest and ways to cure the disease and pest to a farmer in a friendly and easy to understand manner.
        """
        disease_predictions = diagnosis_result[0]['model_2_predictions']['predictions']
        pest_predictions = diagnosis_result[0]['predictions']['predictions']

        prompt = f"""
            You are an experienced agricultural advisor with deep knowledge of plant pathology, entomology, and crop management. 
            You are given:
            1. The output of a plant disease and pest detection model, 
            2. The input image of the affected crop.

            Your task is to provide a structured, practical advisory for a small farmer:

            ### 1. Diagnosis
            - Identify the most likely disease(s) and/or pest(s) from the model predictions.
            - Briefly describe how this problem affects the crop (symptoms, spread, impact on yield).
            - Be concise but accurate. Limit this section to ~120 words.

            ### 2. Treatment & Recommendations
            - Recommend **specific, economical control measures**.
            - If chemicals are suitable:
            - Mention the **chemical name**, **formulation**, and **safe dilution ratio** (e.g., "Mix 2 ml of Imidacloprid 17.8% SL per liter of water").
            - Provide dosage instructions as well as the method which is to be used to apply the treatment(e.g., foliar spray, soil drench).
            - Include **safety precautions** (e.g., PPE, re-entry intervals).
            - If non-chemical or integrated pest management (IPM) options exist:
            - Suggest the most effective and low-cost alternatives (e.g., neem extract, cultural practices, resistant varieties).
            - Always prioritize **cost-effective, safe, and sustainable measures** for small farmers.

            ### 3. Language
            - The entire response MUST ONLY be in {"hindi" if language == "hi" else language}, simple and farmer-friendly.

            Model Results for Reference:
            - Disease Model Predictions: {[f"{disease_prediction.get('class')} with confidence {disease_prediction.get('confidence')}" for disease_prediction in disease_predictions]}
            - Pest Model Predictions: {[f"{pest_prediction.get('class')} with confidence {pest_prediction.get('confidence')}" for pest_prediction in pest_predictions]}
            """

        image = Image.open(image)
        response = await self.client.aio.models.generate_content(
            model="gemini-2.0-flash",
            contents=[prompt, image]
        )
        return response.text

    async def chat(self, history: list, language: str = "en"):
        """
        Chat with a bot and provide a response to the farmer in a friendly and easy to understand manner.
        """
        conversation_context = ""
        if history:
            for msg in history:
                role = msg.get('role', 'user')
                content = msg.get('content', '')
                conversation_context += f"{role.capitalize()}: {content}\n\n"
        
        prompt = f"""
            You are a farming expert that has knowledge about crop planting and agricultural practices. You understand every language.
            You are having a conversation with a farmer.
            You are to provide a response to the farmer in a VERY concise, friendly and easy to understand manner.
            The response MUST ONLY be in the following language: {"hindi" if language == "hi" else language}.
            
            Here is the conversation history:
            {conversation_context}
            
            Please provide a helpful response to the farmer's latest message, taking into account the conversation context.
            """
        
        response = await self.client.aio.models.generate_content(
            model="gemini-2.5-flash",
            contents=[prompt]
        )
        return response.text
    

    def speech_to_text(self, audio_bytes: bytes, language: str = "en") -> str:
        """convert speech to text using deepgram STT."""
        payload: FileSource = {
            "buffer": audio_bytes,
        }
        if language in ["hindi", "hi"]:
            language = "hi"
        elif language in ["english", "en"]:
            language = "en"
        else:
            return "Sorry I don't understand your language."
        response = self.deepgram_client.listen.rest.v("1").transcribe_file(
            source=payload,
            options=PrerecordedOptions(
                model="nova-2",
                smart_format=True,
                language=language,
            )
        )
        data = response.results.channels[0].alternatives[0].transcript
        return data
    

    async def text_to_speech(self, text: str) -> bytes:
        """Converts text to speech audio using gemini TTS, returns the file path of the saved audio"""
        response = await self.client.aio.models.generate_content(
            model="gemini-2.5-flash-preview-tts",
            contents=text,
            config=types.GenerateContentConfig(
                response_modalities=["AUDIO"],
                speech_config=types.SpeechConfig(
                    voice_config=types.VoiceConfig(
                        prebuilt_voice_config=types.PrebuiltVoiceConfig(
                        voice_name='Kore',
                        )
                    )
                ),
            )
        )
        data = response.candidates[0].content.parts[0].inline_data.data
        file_name = f"{str(uuid.uuid4())}.wav"

        def wave_file(filename, pcm, channels=1, rate=24000, sample_width=2):
            with wave.open(filename, "wb") as wf:
                wf.setnchannels(channels)
                wf.setsampwidth(sample_width)
                wf.setframerate(rate)
                wf.writeframes(pcm)
        wave_file(file_name, data)

        return file_name
    
    async def voice_chat(self, audio_bytes: bytes, user_id: str, language: str="en"):
        """chat using voice input and output."""
        user_text = self.speech_to_text(audio_bytes, language)
        user_message = {
            "role": "user",
            "content": user_text
        }
        self.redis_client.add_message(user_id, user_message)
        history = self.redis_client.get_recent_messages(user_id, limit=10)
        reply_text = await self.chat(history, language)

        assistant_message = {
            "role": "assistant",
            "content": reply_text
        }
        self.redis_client.add_message(user_id, assistant_message)

        return{
            "user_query": user_text,
            "bot_reply": reply_text,
            "user_audio_url": None,
            "bot_audio_url": None,
        }

    async def create_notification_message(self, alert_data: dict, language: str = "en"):
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
        response = await self.client.aio.models.generate_content(
            model="gemini-2.0-flash",
            contents=[prompt]
        )
        return response.text

    async def translate_market_data(self, records: dict, language: str = "hindi"):
        """
        Translate market data records to the given language.
        """
        prompt = f"""You are a translation expert that has knowledge about various languages.
        You are given market data records that need to be translated.
        You MUST translate ONLY the values of these specific fields to {language}:
        - state
        - district  
        - market
        - commodity
        - variety
        - grade
        
        DO NOT translate field names, dates, or prices.
        Return the data as valid JSON array maintaining the exact same structure.
        
        The market data is:
        {json.dumps(records, ensure_ascii=False)}
        
        Return ONLY the JSON array, no additional text or explanation.
        """
        
        try:
            response = await self.client.aio.models.generate_content(
                model="gemini-2.0-flash",
                contents=[prompt]
            )
            
            # Clean the response text to ensure it's valid JSON
            response_text = response.text.strip()
            # Remove markdown code blocks if present
            if response_text.startswith("```"):
                response_text = response_text.split("```")[1]
                if response_text.startswith("json"):
                    response_text = response_text[4:]
                response_text = response_text.strip()
            
            return json.loads(response_text)
        except json.JSONDecodeError as e:
            print(f"JSON decode error: {e}")
            print(f"Response text: {response.text}")
            # Return original records if translation fails
            return records
        except Exception as e:
            print(f"Translation error: {e}")
            # Return original records if any error occurs
            return records

    async def translate_weather_data(self, weather_data: dict, language: str = "hindi"):
        """
        Translate weather data to the given language.
        """
        prompt = f"""You are a translation expert that has knowledge about various languages.
        You are given weather data that need to be translated.
        You MUST translate ONLY the values of these specific fields to {language}:
        All the numerical values and text values in the weather data.
        """
        prompt += f"""
        The weather data is:
        {json.dumps(weather_data, ensure_ascii=False)}
        """
        try:
            response = await self.client.aio.models.generate_content(
                model="gemini-2.0-flash",
                    contents=[prompt]
                )
            # Clean the response text to ensure it's valid JSON
            response_text = response.text.strip()
            # Remove markdown code blocks if present
            if response_text.startswith("```"):
                response_text = response_text.split("```")[1]
                if response_text.startswith("json"):
                    response_text = response_text[4:]
                response_text = response_text.strip()
            return json.loads(response_text)  
        except Exception as e:
            print(f"Translation error: {e}")
            return weather_data
        
    async def translate_content(self, content: str, language: str = "hindi"):
        """
        Translate content to the given language.
        """
        prompt = f"""You are a translation expert that has knowledge about various languages.
        You are given content that need to be translated.
        The content MUST be in the following language: {language}.
        """
        prompt += f"""
        The content is:
        {content}
        """
        try:
            response = await self.client.aio.models.generate_content(
                model="gemini-2.0-flash",
                contents=[prompt]
            )
            response_text = response.text.strip()
            return response_text
        except Exception as e:
            print(f"Translation error: {e}")
            return content