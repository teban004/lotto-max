import React, { useEffect, useState } from 'react';
import { BrowserRouter as Router, Route, Link, Routes } from 'react-router-dom';
import WinningNumbers from './WinningNumbers';
import NumberPool from './NumberPool';
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
        <Router>
            <div className="App">
            <header className="App-header">
                <h1>Lotto Max Winning Numbers</h1>
                <nav>
                    <Link to="/">Winning Numbers</Link>
                    <Link to="/number-pool">Number Pool</Link>
                </nav>
            </header>
            <main>
                <Routes>
                    <Route path="/winning-numbers" element={<WinningNumbers allDraws={winningNumbers} />} />
                    <Route path="/" element={<WinningNumbers allDraws={winningNumbers} />} />
                    <Route path="/number-pool" element={<NumberPool allDraws={winningNumbers} />} />
                </Routes>
            </main>
            </div>
        </Router>
    );
};

export default App;
