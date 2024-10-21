import requests
from src.logger.logger import log

def send_to_receiver(receiver_url, data):
    try:
        return requests.post(receiver_url, json=data)
    except Exception as e:
        log.error(f"Failed to send data. Error: {e}")
        return None
