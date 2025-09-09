from google.genai import Client
from PIL import Image
from config.settings import settings

client = Client(api_key=settings.gemini_api_key)

class Bot:
    def __init__(self):
        self.client = client

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
        The analsysi MUST be in the following language {language}. 
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