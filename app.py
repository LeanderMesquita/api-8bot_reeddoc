from functools import partial
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
receiver_url = os.getenv('RECEIVER_URL')
chunk_size_env = os.getenv('CHUNK_SIZE')
chunk_size = int(chunk_size_env)
max_workers = os.cpu_count()


@app.route('/import', methods=['POST'])
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

    if not request.form['resource_type']:
        return jsonify({'error': 'no body content'}), 400

    filename = secure_filename(file.filename)
    log.info(f"Received file: {filename}")
    
    df = pd.read_excel(file, dtype=str)
    array_data = df.where(pd.notnull(df), None).to_dict(orient="records")
    chunked_data = chunk_data(array_data, chunk_size)

    log.info(f"MAX_WORKERS: {max_workers}")
    log.info(f"CHUNK SIZE: {chunk_size}")
    log.info(f"DATAFRAME SIZE: {len(df)}")
    
    partial_process_payload = partial(process_payload, resource_type=request.form['resource_type'])


    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        payloads = list(executor.map(partial_process_payload, chunked_data))
    
    log.info("Queueing payload data")
    
    fifo_queue = queue.Queue()
    for payload in payloads:
        fifo_queue.put(payload)

    log.info(f"Sending to receiver url: {receiver_url}")
    all_responses = []
    all_status_codes = []
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = []
        while not fifo_queue.empty():
            log.info("Receiving queued data")
            queued_data = fifo_queue.get()
            futures.append(executor.submit(send_to_receiver, receiver_url, queued_data))

        for future in as_completed(futures):
            try:
                response = future.result()
                if response.status_code != 202:
                    try:
                        details_json = json.loads(response.text)
                    except json.JSONDecodeError:
                        details_json = {"error": "Invalid JSON response", "response_text": response.text}

                    all_responses.append({
                        'error': 'Failed to send data',
                        'status_code': response.status_code,
                        'details': details_json
                    })
                else:
                    all_responses.append({'message': 'Success', "details": {"accepted": "true"}, 'status_code': response.status_code})

                all_status_codes = [response.get("status_code") for response in all_responses if "status_code" in response]

            except Exception as e:
                log.error(f"Exception occurred during send_to_receiver: {str(e)}")
                all_responses.append({
                    'error': 'Exception occurred during processing',
                    'details': str(e)
                })

    all_responses.append({"http_codes": all_status_codes})
    log.success(f"Finished processing! response codes: {all_status_codes}")
    return jsonify({"responses": all_responses}), 207


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)