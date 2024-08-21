import React from 'react';
import './WinningNumbers.css';

const WinningNumbers = ({ allDraws }) => {
  // Function to determine trends and assign colors
  const getNumberClass = (drawIndex, number) => {
    let classes = 'number';
    let isConsecutive = false;
    let isRepeated = false;

    const winningNumbers = [
      allDraws[drawIndex].number1,
      allDraws[drawIndex].number2,
      allDraws[drawIndex].number3,
      allDraws[drawIndex].number4,
      allDraws[drawIndex].number5,
      allDraws[drawIndex].number6,
      allDraws[drawIndex].number7,
      allDraws[drawIndex].bonus_number,
    ];

    if (drawIndex > 0) {
      const prevWinningNumbers = [
        allDraws[drawIndex - 1].number1,
        allDraws[drawIndex - 1].number2,
        allDraws[drawIndex - 1].number3,
        allDraws[drawIndex - 1].number4,
        allDraws[drawIndex - 1].number5,
        allDraws[drawIndex - 1].number6,
        allDraws[drawIndex - 1].number7,
        allDraws[drawIndex - 1].bonus_number,
      ];
      if (prevWinningNumbers.includes(number)) {
        isRepeated = true;
      }
    }

    if (drawIndex + 1 < allDraws.length) {
      const nextWinningNumbers = [
        allDraws[drawIndex + 1].number1,
        allDraws[drawIndex + 1].number2,
        allDraws[drawIndex + 1].number3,
        allDraws[drawIndex + 1].number4,
        allDraws[drawIndex + 1].number5,
        allDraws[drawIndex + 1].number6,
        allDraws[drawIndex + 1].number7,
        allDraws[drawIndex + 1].bonus_number,
      ];
      if (nextWinningNumbers.includes(number)) {
        isRepeated = true;
      }
    }

    winningNumbers.forEach((drawNumber) => {
      if (drawNumber === number + 1 || drawNumber === number - 1) {
        isConsecutive = true;
      }
    });

    if (isConsecutive) {
      classes += ' consecutive';
    }

    if (isRepeated) {
      classes += ' repeated';
    }

    return classes;
  };

  return (
    <div className="winning-numbers">
      {allDraws.map((draw, drawIndex) => (
        <div key={drawIndex} className="draw">
          <h2>Draw Date: {new Date(draw.draw_date).toLocaleDateString()}</h2>
          <div className="numbers">
            <span className={getNumberClass(drawIndex, draw.number1)}>{draw.number1}</span>
            <span className={getNumberClass(drawIndex, draw.number2)}>{draw.number2}</span>
            <span className={getNumberClass(drawIndex, draw.number3)}>{draw.number3}</span>
            <span className={getNumberClass(drawIndex, draw.number4)}>{draw.number4}</span>
            <span className={getNumberClass(drawIndex, draw.number5)}>{draw.number5}</span>
            <span className={getNumberClass(drawIndex, draw.number6)}>{draw.number6}</span>
            <span className={getNumberClass(drawIndex, draw.number7)}>{draw.number7}</span>
            <span className={getNumberClass(drawIndex, draw.bonus_number)}>Bonus: {draw.bonus_number}</span>
          </div>
        </div>
      ))}
    </div>
  );
};

export default WinningNumbers;
