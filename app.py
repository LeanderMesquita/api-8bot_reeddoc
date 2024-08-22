from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
import pandas as pd 
import requests
import json
import os 
from logger import log
from dotenv import load_dotenv
import queue
from concurrent.futures import ThreadPoolExecutor, as_completed
from tenacity import retry, stop_after_attempt, wait_fixed


app = Flask(__name__)
CORS(app)

@retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
def send_to_receiver(reciever_url, data):
    try:
        log.info(f"Sending data: {data}")
        response = requests.post(reciever_url, json=data)
        #log.info(f"Received response: {response.status_code}, {response.text}")
        #response.raise_for_status()
        return response
    except Exception as e:
        log.error(f"Failed to send data. Error: {e}")
        return None

@app.route('/format', methods=['POST'])
def format_doc():
    if 'file' not in request.files:
        log.error("No file part")
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    if file.filename == '':
        log.error("No file selected")
        return jsonify({'error': 'No file selected'}), 400
    
    filename = secure_filename(file.filename)
    log.info(f"Received file: {filename}")
    
    df = pd.read_excel(file, dtype=str)
    array_data = df.where(pd.notnull(df), None).to_dict(orient="records")
      
    load_dotenv()
    reciever_url = os.getenv('RECIEVER_URL')
    log.info(f"Sending to receiver url: {reciever_url}")
    
 
    fifo_queue = queue.Queue()
    for data in array_data:
        fifo_queue.put(data)
    
    log.info("Queueing payload data")
    
    
    max_workers = min(10, len(array_data))  
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = []
        while not fifo_queue.empty():
            queued_data = fifo_queue.get()
            futures.append(executor.submit(send_to_receiver, reciever_url, queued_data))
        
       
        for future in as_completed(futures):
            response = future.result()
            if response and response.status_code != 200:
                log.error(f"Failed to send data. Response text: {response.text}, Response status code: {response.status_code}")
                return jsonify({'error': 'Failed to send data', 'details': response.text}), response.status_code
    
    log.success("Successfully sent")
    return jsonify({'message': 'File successfully uploaded and processed'}), 200
