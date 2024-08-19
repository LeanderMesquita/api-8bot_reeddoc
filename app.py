from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
import pandas as pd 
import requests
import json
import os 
from logger import log
from dotenv import load_dotenv


app = Flask(__name__)
CORS(app)

@app.route('/format', methods=['POST'])
def format_doc():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    filename = secure_filename(file.filename)
    log.info(f"Recieved file: {filename}")
    
    df = pd.read_excel(file, dtype=str)
    data = json.dumps(df.to_dict(orient="records"), ensure_ascii=False, indent=4)
    
    load_dotenv()
    reciever_url = os.getenv('RECIEVER_URL')
    
    response = requests.post(reciever_url, json=data)
    
    if response.status_code == 200:
        return jsonify({'message': 'File successfully uploaded and processed'}), 200
    
    return jsonify({'error': 'Failed to send data', 'details': response.text}), response.status_code
    
