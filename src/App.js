import React, { useEffect, useState } from 'react';
import WinningNumbers from './WinningNumbers';
import './App.css';

const App = () => {
  const [winningNumbers, setWinningNumbers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchWinningNumbers = async () => {
      try {
        const response = await fetch('http://estebanarrangoiz.com:5000/api/winning-numbers'); // Changed to relative path for better security
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        setWinningNumbers(data);
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
      <header className="App-header">
        <h1>Lotto Max Winning Numbers</h1>
      </header>
      <main>
        <WinningNumbers allDraws={winningNumbers} />
      </main>
    </div>
  );
};

export default App;
