def process_payload(chunk):
    return {"payload": [{"method": "POST", "body": data} for data in chunk]}