from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
import fastf1
import numpy as np
import pandas as pd
from fastapi.middleware.cors import CORSMiddleware
from fastapi.encoders import jsonable_encoder
from urllib.request import urlopen
import json
import asyncio

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

async def stream_data():
    """Streams telemetry data dynamically based on actual time gaps."""
    try:
        session = fastf1.get_session(2024, 'Bahrain', 'Q')
        session.load()
        fast_max = session.laps.pick_driver('VER').pick_fastest()
        max_car_data = fast_max.get_car_data()
        
        # Load data into memory
        data_points = []
        for i in range(len(max_car_data['Time']) - 1):
            current_time = pd.to_timedelta(max_car_data['Time'].iloc[i])
            next_time = pd.to_timedelta(max_car_data['Time'].iloc[i + 1])
            current_rpm = int(max_car_data['RPM'].iloc[i])
            next_rpm = int(max_car_data['RPM'].iloc[i + 1])
            current_speed = int(max_car_data['Speed'].iloc[i])
            next_speed = int(max_car_data['Speed'].iloc[i + 1])
            
            # Calculate the number of steps for interpolation
            num_steps = int((next_time - current_time).total_seconds() * 10)  # 10 steps per second
            
            for step in range(num_steps):
                interpolated_time = current_time + (next_time - current_time) * (step / num_steps)
                interpolated_speed = int(current_speed + (next_speed - current_speed) * (step / num_steps))
                interpolated_rpm = int(current_rpm + (next_rpm - current_rpm) * (step / num_steps))
                
                row_dict = {
                    "Time": f"{interpolated_time.total_seconds():.3f}",
                    "Speed": interpolated_speed,
                    "RPM": interpolated_rpm
                }
                data_points.append(row_dict)

        # Add the last data point
        row_dict = {
            "Time": f"{pd.to_timedelta(max_car_data['Time'].iloc[-1]).total_seconds():.3f}",
            "Speed": int(max_car_data['Speed'].iloc[-1]),
            "RPM": int(max_car_data['RPM'].iloc[-1])
        }
        data_points.append(row_dict)

        # Stream data to frontend
        for row_dict in data_points:
            yield f"data: {json.dumps(row_dict)}\n\n"
            await asyncio.sleep(0.1)  # 10 updates per second
        
    except Exception as e:
        print(f"Error in stream_data: {e}")
        yield f"data: {json.dumps({'error': str(e)})}\n\n"

@app.get("/stream")
async def stream():
    return StreamingResponse(stream_data(), media_type="text/event-stream")

@app.get("/car_data")
def get_car_data(driver_number: int, session_key: int, speed: int):
    url = f'https://api.openf1.org/v1/car_data?driver_number=55&session_key=9159&speed>=315'
    response = urlopen(url)
    data = json.loads(response.read().decode('utf-8'))
    return data

@app.get("/max")
def get_max():
    session = fastf1.get_session(2024, 'Bahrain', 'Q')
    session.load()
    print(session)
    fast_max = session.laps.pick_driver('VER').pick_fastest()
    max_car_data = fast_max.get_car_data()
    TIME = [f"{pd.to_timedelta(t).total_seconds():.3f}" for t in max_car_data['Time']]  # Convert to string with 3 decimal places
    SPEED = max_car_data['Speed']
    SPEED_LIST = [int(s) for s in SPEED]  # Convert to int
    fastest_lap_dict = {
        k: (None if pd.isna(v) or v in [np.inf, -np.inf] else int(v) if isinstance(v, (np.integer, np.int64)) else float(v) if isinstance(v, (np.floating, np.float64)) else v) 
        for k, v in fast_max.to_dict().items()
    }

    data = [{
        "first_name": "Max",
        "last_name": "Verstappen",
        "short_name": "VER",
        "fastest_lap": fastest_lap_dict,
        "time": TIME,
        "speed": SPEED_LIST
    }]

    return jsonable_encoder(data)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")