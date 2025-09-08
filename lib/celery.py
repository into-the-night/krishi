from celery import Celery
from celery.schedules import crontab
import httpx
from firebase_admin import messaging
from agent.bot import Bot
from config.settings import settings
from lib.db import get_all_locations

# Initialize Celery
app = Celery('krishi', broker=settings.celery_broker_url)
bot = Bot()

# Configure periodic tasks
app.conf.beat_schedule = {
    'check-weather-alerts': {
        'task': 'tasks.check_weather_alerts',
        'schedule': crontab(hour=6, minute=0),  # Run at 6 AM every day
    },
}

@app.task
def check_weather_alerts():
    """Fetch weather alerts and send notifications"""
    
    try:
        # Get all unique locations
        locations = get_all_locations()
        if not locations:
            return "No weather checks"

        for location in locations:
            # Fetch weather data
            weather_url = f"http://api.weatherapi.com/v1/alerts.json?q={location.district},{location.state}"
            
            with httpx.Client() as client:
                response = client.get(weather_url)
                
                if response.status_code == 200:
                    weather_data = response.json()
                    
                    alert_data = weather_data['alerts']['alert']

                    # Send notification if there's an alert
                    if alert_data:
                        # TODO: translate acc to preference
                        # alert_message = bot.create_notification_message(alert_data)
                        message = messaging.Message(
                            notification=messaging.Notification(
                                title="Krishi Weather Alert",
                                body=alert_data.get('headline'),
                            ),
                            topic=location.firebase_topic,
                        )
                        
                        try:
                            messaging.send(message)
                            print(f"Alert sent to topic {location.firebase_topic}")
                        except Exception as e:
                            print(f"Error sending notification: {e}")
        return "Weather alerts check completed"
    except Exception as e:
        print(f"Exception ocurred {e}")

# # For testing - send immediate alert
# @app.task
# def send_test_alert(location_id: str):
#     """Send a test weather alert for a specific location"""
#     db = SessionLocal()
    
#     try:
#         location = db.query(Location).filter(Location.openweather_id == location_id).first()
        
#         if location:
#             message = messaging.Message(
#                 notification=messaging.Notification(
#                     title="Krishi Test Alert",
#                     body=f"This is a test weather alert for {location.city}, {location.state}",
#                 ),
#                 topic=location.firebase_topic,
#             )
            
#             messaging.send(message)
#             return f"Test alert sent to {location.firebase_topic}"
#         else:
#             return "Location not found"
    
#     finally:
#         db.close()
