import { useState, useEffect } from 'react';
import './SymptomCards.css';

const API_BASE = (import.meta.env.VITE_API_URL || '').replace(/\/api$/, '');

export default function SymptomCards({ onComplete }) {
  const [flow, setFlow] = useState([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [answers, setAnswers] = useState({});
  const [showFollowup, setShowFollowup] = useState(false);
  const [result, setResult] = useState(null);

  useEffect(() => {
    fetch(`${API_BASE}/api/symptom-flow?message=${encodeURIComponent(window.lastUserMessage || '')}`)
      .then(r => r.json())
      .then(data => setFlow(data.flow));
  }, []);

  const handleAnswer = (id, value) => {
    const newAnswers = { ...answers, [id]: value };
    setAnswers(newAnswers);

    const current = flow[currentIndex];
    if (current.followup && current.followup[value]) {
      setShowFollowup(true);
    } else {
      next();
    }
  };

  const handleFollowup = (value) => {
    const current = flow[currentIndex];
    setAnswers({ ...answers, [`${current.id}_followup`]: value });
    setShowFollowup(false);
    next();
  };

  const next = () => {
    if (currentIndex < flow.length - 1) {
      setCurrentIndex(currentIndex + 1);
    } else {
      // Pass answers to parent for analysis
      if (onComplete) {
        onComplete(answers);
      }
    }
  };

  if (!flow.length) return <div className="loading-flow">Analyzing your symptoms...</div>;

  const current = flow[currentIndex];
  const followup = showFollowup && current.followup[answers[current.id]];

  return (
    <div className="symptom-cards">
      <div className="progress">{currentIndex + 1} / {flow.length}</div>
      
      <div className="card">
        <h3>{followup ? followup.question : current.question}</h3>
        
        {!followup && current.type === 'yesno' && (
          <div className="buttons">
            <button onClick={() => handleAnswer(current.id, 'yes')}>Yes</button>
            <button onClick={() => handleAnswer(current.id, 'no')}>No</button>
          </div>
        )}

        {!followup && current.type === 'choice' && (
          <div className="options">
            {current.options.map(opt => (
              <button key={opt} onClick={() => handleAnswer(current.id, opt)}>{opt}</button>
            ))}
          </div>
        )}

        {!followup && current.type === 'multichoice' && (
          <div className="multi">
            {current.options.map(opt => (
              <label key={opt}>
                <input type="checkbox" onChange={(e) => {
                  const selected = answers[current.id] || [];
                  setAnswers({
                    ...answers,
                    [current.id]: e.target.checked 
                      ? [...selected, opt] 
                      : selected.filter(s => s !== opt)
                  });
                }} />
                {opt}
              </label>
            ))}
            <button onClick={next}>Next</button>
          </div>
        )}

        {followup && followup.type === 'choice' && (
          <div className="options">
            {followup.options.map(opt => (
              <button key={opt} onClick={() => handleFollowup(opt)}>{opt}</button>
            ))}
          </div>
        )}

        {followup && followup.type === 'multichoice' && (
          <div className="multi">
            {followup.options.map(opt => (
              <label key={opt}>
                <input type="checkbox" onChange={(e) => {
                  const selected = answers[`${current.id}_followup`] || [];
                  setAnswers({
                    ...answers,
                    [`${current.id}_followup`]: e.target.checked 
                      ? [...selected, opt] 
                      : selected.filter(s => s !== opt)
                  });
                }} />
                {opt}
              </label>
            ))}
            <button onClick={() => { setShowFollowup(false); next(); }}>Next</button>
          </div>
        )}
      </div>
    </div>
  );
}
