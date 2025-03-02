import React, { useState, useEffect } from 'react';
import axios from 'axios';

const TestData = () => {
  const [carData, setCarData] = useState(null);
  const [fastData, setFastData] = useState(null);
  const [latestTelemetry, setLatestTelemetry] = useState({ Time: '', Speed: '' });

  useEffect(() => {
    console.log('Making request to backend...');
    axios.get('http://127.0.0.1:8000/car_data', {
      params: {
        driver_number: 55,
        session_key: 9159,
        speed: 315
      }
    })
    .then(response => {
      setCarData(response.data);
    })
    .catch(error => {
      console.error('There was an error fetching the data!', error);
    });
  }, []);

  useEffect(() => {
    console.log('Getting FastF1 data...');
    axios.get('http://127.0.0.1:8000/max')
    .then(response2 => {
      console.log('FastF1 response received: ', response2.data);
      setFastData(response2.data);
    })
    .catch(error => {
      console.error('There was an error fetching the FastF1 data!', error);
    });
  }, []);

  useEffect(() => {
    const eventSource = new EventSource("http://127.0.0.1:8000/stream");

    eventSource.onmessage = (event) => {
      const newData = JSON.parse(event.data);
      setLatestTelemetry(newData);
      console.log('New telemetry data received: ', newData);
    };

    eventSource.onerror = (error) => {
      console.error("EventSource failed:", error);
      eventSource.close();
    };

    return () => {
      eventSource.close();
    };
  }, []);

  return (
    <div>
      <h1>Test Data</h1>
      <div>
        <h1>Telemetry Data</h1>
        <p>Time: {latestTelemetry.Time}</p>
        <p>Speed: {latestTelemetry.Speed}</p>
        <p>RPM: {latestTelemetry.RPM}</p>
      </div>
    </div>
  );
};

export default TestData;