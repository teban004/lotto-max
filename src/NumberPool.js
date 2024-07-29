  import React, { useEffect, useState } from 'react';
import './NumberPool.css';

const NumberPool = () => {
  const [numberStats, setNumberStats] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchNumberStats = async () => {
      try {
        const statsArray = [];
        for (let number = 1; number <= 50; number++) {
          const response = await fetch(`http://estebanarrangoiz.com:5000/api/stats/${number}`);
          if (!response.ok) {
            throw new Error(`Error fetching stats for number ${number}`);
          }
          const data = await response.json();
          statsArray.push({
            number,
            frequency: parseInt(data.freq, 10),
          });
        }

        // Sort the statsArray by frequency (descending)
        statsArray.sort((a, b) => b.frequency - a.frequency);

        setNumberStats(statsArray);
      } catch (error) {
        console.error("Error fetching number stats:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchNumberStats();
  }, []);

  const getColorForFrequency = (frequency) => {
    // Normalize frequency to a value between 0 and 1
    const maxFrequency = Math.max(...numberStats.map(stat => stat.frequency));
    const normalized = frequency / maxFrequency;
    const hue = (normalized) * 120; // 120 is green, 0 is red, and -60 is blue in HSL

    // Convert hue to RGB
    const [r, g, b] = hslToRgb(hue / 360, 1, 0.5);
    return `rgb(${r}, ${g}, ${b})`;
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
            <th>Number</th>
            <th>Frequency</th>
          </tr>
        </thead>
        <tbody>
          {numberStats.map((numStat) => (
            <tr key={numStat.number} style={{ backgroundColor: getColorForFrequency(numStat.frequency) }}>
              <td className={'number'}>{numStat.number}</td>
              <td>{numStat.frequency}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

const getRowClass = (numStat) => {
    if (numStat.frequency > 2) {
      return 'high-frequency';
    } else if (numStat.frequency > 1) {
      return 'medium-frequency';
    } else {
      return 'low-frequency';
    }
};

export default NumberPool;
