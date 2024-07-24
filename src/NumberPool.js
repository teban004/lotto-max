import React, { useEffect, useState } from 'react';
import './NumberPool.css';

const NumberPool = ({ allDraws }) => {
  const [numberStats, setNumberStats] = useState([]);

  useEffect(() => {
    const calculateNumberStats = () => {
        const numberMap = new Map();

        allDraws.forEach((draw, drawIndex) => {
        const numbers = [
            draw.number1,
            draw.number2,
            draw.number3,
            draw.number4,
            draw.number5,
            draw.number6,
            draw.number7,
            draw.bonus_number,
        ];

        numbers.forEach((number) => {
            if (!numberMap.has(number)) {
            numberMap.set(number, {
                frequency: 0,
                lastAppearance: drawIndex,
            });
            }
            const numStats = numberMap.get(number);
            numStats.frequency += 1;
            numStats.lastAppearance = drawIndex;
        });
        });

        const statsArray = Array.from(numberMap, ([number, stats]) => ({
        number,
        ...stats,
        }));

        statsArray.sort((a, b) => {
        if (a.frequency === b.frequency) {
            return a.lastAppearance - b.lastAppearance;
        }
        return b.frequency - a.frequency;
        });

        setNumberStats(statsArray);
    };

    calculateNumberStats();
  }, [allDraws]);

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
            <th>Last Appearance</th>
          </tr>
        </thead>
        <tbody>
          {numberStats.map((numStat) => (
            <tr key={numStat.number} style={{ backgroundColor: getColorForFrequency(numStat.frequency) }}>
              <td className={'number'}>{numStat.number}</td>
              <td>{numStat.frequency}</td>
              <td>{numStat.lastAppearance}</td>
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
