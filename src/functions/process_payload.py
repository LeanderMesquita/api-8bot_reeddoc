def process_payload(chunk, resource_type):
    return {
        "payload": [{"method": "POST", "body": data} for data in chunk],
        "resourceType": resource_type
        }