// filepath: /Users/rishithbandi/repos/f1-racecast/frontend/racecast/src/components/CarData.js
import React, { useState, useEffect } from 'react';
import axios from 'axios';

const TestData = () => {
  const [data, setData] = useState(null);

  useEffect(() => {
    axios.get('http://127.0.0.1:8000/car_data', {
      params: {
        driver_number: 55,
        session_key: 9159,
        speed: 315
      }
    })
    .then(response => {
      setData(response.data);
    })
    .catch(error => {
      console.error('There was an error fetching the data!', error);
    });
  }, []);

  return (
    <div>
      <h1>Test Data</h1>
      {data ? (
        <pre>{JSON.stringify(data, null, 2)}</pre>
      ) : (
        <p>Testing...</p>
      )}
    </div>
  );
};

export default TestData;