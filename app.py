from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
import pandas as pd 
import os 
from src.functions.chunk_data import chunk_data
from src.functions.process_payload import process_payload
from src.functions.send_to_receiver import send_to_receiver
from src.logger.logger import log
from dotenv import load_dotenv
import queue
from concurrent.futures import ThreadPoolExecutor, as_completed
import json

app = Flask(__name__)
CORS(app)

load_dotenv()
reciever_url = os.getenv('RECIEVER_URL')
max_workers = os.cpu_count()


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
    
    ##
    
    df = pd.read_excel(file, dtype=str)
    array_data = df.where(pd.notnull(df), None).to_dict(orient="records")
    chunked_data = chunk_data(array_data, 100)

    ##
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        payloads = list(executor.map(process_payload, chunked_data))
    
    log.info("Queueing payload data")
    
    fifo_queue = queue.Queue()
    for payload in payloads:
        fifo_queue.put(payload)

    log.info(f"Sending to receiver url: {reciever_url}")
    
    all_responses = []
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = []
        while not fifo_queue.empty():
            queued_data = fifo_queue.get()
            futures.append(executor.submit(send_to_receiver, reciever_url, queued_data))
        
        for future in as_completed(futures):
            response = future.result()
        
            if response.status_code != 202:
                details_json = json.loads(response.text)
                all_responses.append({'error': 'Failed to send data', 'details': details_json})
            else:
                all_responses.append({'message': 'Success', "details": {"accepted": "true"}})
    

    log.success("Successfully sent")
    return jsonify({"responses": all_responses}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)