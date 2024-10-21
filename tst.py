import os
import queue
from dotenv import load_dotenv
import pandas as pd
from src.logger.logger import log
import time

load_dotenv()
reciever_url = os.getenv('RECIEVER_URL')
start_time = time.time()

file = "c:/Users/Leander Mesquita/Downloads/generated_collaborators_2000_unique_emails_v2.xlsx"

df = pd.read_excel(file, dtype=str)
array_data = df.where(pd.notnull(df), None).to_dict(orient="records")
    
def chunk_data(data, size): return [data[i:i + size] for i in range(0, len(data), size)]

chunked_data=chunk_data(array_data, 500)

payloads = [{"payload": [{"method": "POST", "body": data} for data in chunk]} for chunk in chunked_data]


log.info(f"Número de payloads gerados: {len(payloads)}")
for i, payload in enumerate(payloads):
    log.info(f"Payload {i+1} contém {len(payload['payload'])} registros.")

end_time = time.time()
exec_time = end_time - start_time
print(exec_time)
print(min(10, len(array_data)))
