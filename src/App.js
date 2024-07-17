import React, { useState, useEffect } from 'react';
import axios from 'axios';
import WinningNumbers from './WinningNumbers';
import './App.css';

const App = () => {
  const [winningNumbers, setWinningNumbers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchWinningNumbers = async () => {
      try {
        const response = await axios.get('http://estebanarrangoiz.com:5000/api/winning-numbers');
        setWinningNumbers(response.data);
      } catch (error) {
        setError(error.message);
      } finally {
        setLoading(false);
      }
    };
    
    fetchWinningNumbers();
  }, []);

  if (loading) {
    return <div>Loading...</div>;
  }

  if (error) {
    return <div>Error: {error}</div>;
  }

  return (
    <div className="App">
      <h1>Lotto Max Winning Numbers</h1>
      <WinningNumbers allDraws={winningNumbers} />
    </div>
  );
};

export default App;

