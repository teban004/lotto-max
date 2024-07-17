import React from 'react';
import './WinningNumbers.css';

const WinningNumbers = ({ allDraws }) => {
    console.log(allDraws);

    // Function to determine trends and assign colors
    const getNumberClass = (drawIndex, number) => {
        let classes = 'number';
        let isConsecutive = false;
        let isRepeated = false;

        if( drawIndex > 0 ) {
            let prev_winning_numbers = [allDraws[drawIndex-1].number1, allDraws[drawIndex-1].number2, allDraws[drawIndex-1].number3, allDraws[drawIndex-1].number4, allDraws[drawIndex-1].number5, allDraws[drawIndex-1].number6, allDraws[drawIndex-1].number7, allDraws[drawIndex-1].bonus_number];
            if( prev_winning_numbers.includes(number)) {
                isRepeated = true;
            }
        }
        if( drawIndex < allDraws.length-1 ) {
            let next_winning_numbers = [allDraws[drawIndex+1].number1, allDraws[drawIndex+1].number2, allDraws[drawIndex+1].number3, allDraws[drawIndex+1].number4, allDraws[drawIndex+1].number5, allDraws[drawIndex+1].number6, allDraws[drawIndex+1].number7, allDraws[drawIndex+1].bonus_number];
            if( next_winning_numbers.includes(number)) {
                isRepeated = true;
            }
        }

        let winning_numbers = [allDraws[drawIndex].number1, allDraws[drawIndex].number2, allDraws[drawIndex].number3, allDraws[drawIndex].number4, allDraws[drawIndex].number5, allDraws[drawIndex].number6, allDraws[drawIndex].number7, allDraws[drawIndex].bonus_number];
        winning_numbers.forEach((drawNumber, numberIndex) => {
            if( (drawNumber === number + 1) || (drawNumber === number - 1)) {
                isConsecutive = true;
            }
        });

        if( isConsecutive ) {
            classes += ' consecutive';
        }

        if( isRepeated ) {
            classes += ' repeated';
        }

        return classes;
    };

    // Identify trends such as repeated and consecutive numbers
    const identifyTrends = (draws) => {
    let repeatedNumbers = [];
    let consecutiveNumbers = [];

    draws.forEach((draw, index) => {
        if( index > 0 ) {
            let winning_numbers = [draw.number1, draw.number2, draw.number3, draw.number4, draw.number5, draw.number6, draw.number7, draw.bonus_number]
            let prev_winning_set = index>0 ? draws[index - 1] : []
            let prev_winning_numbers = [
                prev_winning_set.number1,
                prev_winning_set.number2,
                prev_winning_set.number3,
                prev_winning_set.number4,
                prev_winning_set.number5,
                prev_winning_set.number6,
                prev_winning_set.number7,
                prev_winning_set.bonus_number
            ]
            winning_numbers.forEach((winning_number, numIndex) => {
                // Check for repeated numbers
                if (index > 0 && prev_winning_numbers.includes(winning_number)) {
                repeatedNumbers.push(winning_number);
                }
                // Check for consecutive numbers in the same draw
                if( (numIndex > 0 && winning_number === winning_numbers[numIndex - 1] + 1)
                    || (numIndex < winning_numbers.length && winning_number === winning_numbers[numIndex + 1] - 1)) {
                consecutiveNumbers.push(winning_number);
                }
            });
        }
    });

    return { repeatedNumbers, consecutiveNumbers };
    };

  const trends = identifyTrends(allDraws);

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
