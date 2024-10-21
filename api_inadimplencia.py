import uvicorn
from pydantic import BaseModel
import httpie
from fastapi import FastAPI
import json

app = FastAPI()

json_file = 'data/informacoes_inadimplencia.json'

@app.get('/')
def read_root():
    with open(json_file, 'r') as f:
        data = json.load(f)
    
    return data

if __name__ == "__main__":
    # Executar o servidor FastAPI
    uvicorn.run(app, host="127.0.0.1", port=8000)