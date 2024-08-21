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

app = Flask(__name__)
CORS(app)

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
        log.info(f"Payload: {data}")
        fifo_queue.put(data)
    
    log.info("Queueing payload data")
    while not fifo_queue.empty():
        queued_data = fifo_queue.get() 
        response = requests.post(reciever_url, json=queued_data)

    if response.status_code == 200:
        log.success("Successfully sent")
        return jsonify({'message': 'File successfully uploaded and processed'}), 200
    
    log.error(f"Failed to send data. Response text: {response.text}, Response status code: {response.status_code}")
    return jsonify({'error': 'Failed to send data', 'details': response.text}), response.status_code

