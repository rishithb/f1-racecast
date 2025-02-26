# filepath: /Users/rishithbandi/repos/f1-racecast/backend/main.py
from fastapi import FastAPI
from urllib.request import urlopen
import json

app = FastAPI()

@app.get("/car_data")
def get_car_data(driver_number: int, session_key: int, speed: int):
    url = f'https://api.openf1.org/v1/car_data?driver_number={driver_number}&session_key={session_key}&speed>={speed}'
    response = urlopen(url)
    data = json.loads(response.read().decode('utf-8'))
    return data

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")