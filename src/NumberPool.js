  import React, { useEffect, useState } from 'react';
import './NumberPool.css';

const NumberPool = () => {
    const [numberStats, setNumberStats] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchNumberStats = async () => {
        try {
            const response = await fetch(`http://estebanarrangoiz.com:5000/api/stats/`);
            if (!response.ok) {
                throw new Error(`Error fetching stats for numbers`);
            }
            const data = await response.json();
            let statsArray = data;

            setNumberStats(statsArray);
        } catch (error) {
            console.error("Error fetching numbers stats:", error);
        } finally {
            setLoading(false);
        }
        };

        fetchNumberStats();
  }, []);

  const getColorForCount = (hot_number) => {
    // Normalize frequency to a value between 0 and 1
    const maxFrequency = Math.max(...numberStats.map(stat => stat.hot_number));
    const minFrequency = Math.min(...numberStats.map(stat => stat.hot_number));
    const normalized = (hot_number-minFrequency) / (maxFrequency-minFrequency);
    const hue = (normalized) * 120; // 120 is green, 0 is red, and -60 is blue in HSL

   return getRowClass(normalized);
  };

  // Convert HSL to RGB (Hue between 0-1, Saturation and Lightness between 0-1)
  const hslToRgb = (h, s, l) => {
    let r, g, b;

    if (s === 0) {
      r = g = b = l; // achromatic
    } else {
      const hue2rgb = (p, q, t) => {
        if (t < 0) t += 1;
        if (t > 1) t -= 1;
        if (t < 1 / 6) return p + (q - p) * 6 * t;
        if (t < 1 / 2) return q;
        if (t < 2 / 3) return p + (q - p) * (2 / 3 - t) * 6;
        return p;
      };

      const q = l < 0.5 ? l * (1 + s) : l + s - l * s;
      const p = 2 * l - q;
      r = hue2rgb(p, q, h + 1 / 3);
      g = hue2rgb(p, q, h);
      b = hue2rgb(p, q, h - 1 / 3);
    }

    return [Math.round(r * 255), Math.round(g * 255), Math.round(b * 255)];
  };

  return (
    <div className="number-pool">
      <h2>Number Pool</h2>
      <table>
        <thead>
          <tr>
            <th>Num</th>
            <th className='disposable'>Count</th>
            <th>Last Draw Date</th>
            <th className='disposable'>Days from being winner</th>
            <th>Freq</th>
            <th>Hot number</th>
          </tr>
        </thead>
        <tbody>
          {numberStats.map((numStat) => (
            <tr key={numStat.number} className={getColorForCount(numStat.hot_number)}>
              <td className={'number'}>{numStat.number}</td>
              <td className='disposable'>{numStat.count}</td>
              <td>{numStat.last_draw_date.substring(0, 10)}</td>
              <td className='disposable'>{numStat.days_from_being_winner}</td>
              <td>{numStat.freq.toFixed(5)}</td>
              <td>{numStat.hot_number.toFixed(5)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

const getRowClass = (normalizedFreq) => {
    if (normalizedFreq > 0.95) {
      return 'frequency9';
    } else if (normalizedFreq > 0.90) {
      return 'frequency8';
    } else if (normalizedFreq > 0.85) {
      return 'frequency7';
    } else if (normalizedFreq > 0.80) {
      return 'frequency6';
    } else if (normalizedFreq > 0.75) {
      return 'frequency5';
    } else if (normalizedFreq > 0.65) {
      return 'frequency4';
    } else if (normalizedFreq > 0.50) {
      return 'frequency3';
    } else if (normalizedFreq > 0.35) {
      return 'frequency2';
    } else if (normalizedFreq > 0.20) {
      return 'frequency1';
    } else if (normalizedFreq >= 0) {
      return 'frequency0';
    } else {
      return 'unrated';
    }
};

export default NumberPool;
