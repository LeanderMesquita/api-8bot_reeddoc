from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
import pandas as pd 
import requests
import os 
from logger import log
from dotenv import load_dotenv
import queue
from concurrent.futures import ThreadPoolExecutor, as_completed

app = Flask(__name__)
CORS(app)

load_dotenv()
reciever_url = os.getenv('RECIEVER_URL')
max_workers = os.cpu_count()

def send_to_receiver(reciever_url, data):
    try:
        response = requests.post(reciever_url, json=data)
        text = response.text if response.text != '' else 'OK'
        log.info(f"Received response: {response.status_code}, {text}")
        return response
    except Exception as e:
        log.error(f"Failed to send data. Error: {e}")
        return None

def chunk_data(data, size):
    return [data[i:i + size] for i in range(0, len(data), size)]

def process_payload(chunk):
    return {"payload": [{"method": "POST", "body": data} for data in chunk]}

@app.route('/format', methods=['POST'])
def format_doc():
    if 'file' not in request.files:
        log.error("No file part")
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    if file.filename == '':
        log.error("No file selected")
        return jsonify({'error': 'No file selected'}), 400
    
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext != '.xlsx': return jsonify({'error': 'incorrect file type'}), 406

    
    filename = secure_filename(file.filename)
    log.info(f"Received file: {filename}")
    
    df = pd.read_excel(file, dtype=str)

    array_data = df.where(pd.notnull(df), None).to_dict(orient="records")

    chunked_data = chunk_data(array_data, 500)

    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        payloads = list(executor.map(process_payload, chunked_data))

    log.info("Queueing payload data")
    
    fifo_queue = queue.Queue()
    for payload in payloads:
        fifo_queue.put(payload)

    log.info(f"Sending to receiver url: {reciever_url}")
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = []
        while not fifo_queue.empty():
            queued_data = fifo_queue.get()
            futures.append(executor.submit(send_to_receiver, reciever_url, queued_data))
        
        for future in as_completed(futures):
            response = future.result()
        
            if response.status_code != 201:
               
                log.error(f"Failed to send data. Response text: {response.text}, Response status code: {response.status_code}")
                return jsonify({'error': 'Failed to send data', 'details': response.text}), response.status_code
    
    log.success("Successfully sent")
    return jsonify({'message': 'File successfully uploaded and processed'}), 200
