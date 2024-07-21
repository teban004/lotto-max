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
            <tr key={numStat.number} className={getRowClass(numStat)}>
              <td>{numStat.number}</td>
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
