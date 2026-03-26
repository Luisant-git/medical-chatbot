import { useState, useEffect, useRef } from 'react'
import axios from 'axios'

const API_BASE = (import.meta.env.VITE_API_URL || '').replace(/\/api$/, '');
import './ChatBot.css'
import SymptomCards from './SymptomCards'

function ChatBot({ onLogout }) {
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [showSymptomCards, setShowSymptomCards] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const [userLocation, setUserLocation] = useState(null)
  const [doctors, setDoctors] = useState([])
  const [showDoctors, setShowDoctors] = useState(false)
  const [isRecording, setIsRecording] = useState(false)
  const [isSpeaking, setIsSpeaking] = useState(false)
  const [voiceMode, setVoiceMode] = useState(false)
  const messagesEndRef = useRef(null)
  const recognitionRef = useRef(null)
  const synthRef = useRef(window.speechSynthesis)

  useEffect(() => {
    // Initialize speech recognition
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition
      recognitionRef.current = new SpeechRecognition()
      recognitionRef.current.continuous = false
      recognitionRef.current.interimResults = false
      recognitionRef.current.lang = 'en-US'

      recognitionRef.current.onresult = (event) => {
        const transcript = event.results[0][0].transcript
        setInput(transcript)
        setIsRecording(false)
      }

      recognitionRef.current.onerror = () => {
        setIsRecording(false)
      }

      recognitionRef.current.onend = () => {
        setIsRecording(false)
      }
    }
  }, [])

  useEffect(() => {
    addMessage('bot', 'Hello! I\'m your medical diagnosis assistant. How can I help you today?')
    getUserLocation()
  }, [])

  const getUserLocation = () => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          setUserLocation({
            lat: position.coords.latitude,
            lng: position.coords.longitude
          })
          console.log('Location detected:', position.coords.latitude, position.coords.longitude)
        },
        (error) => {
          console.log('Location error:', error)
          addMessage('bot', '📍 Location access denied. Doctor recommendations will be limited.')
        }
      )
    } else {
      addMessage('bot', '📍 Location not supported by your browser.')
    }
  }

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const addMessage = (sender, text, data = null) => {
    setMessages(prev => [...prev, { sender, text, data, timestamp: new Date() }])
    
    // Auto-speak bot messages only if voice mode is ON
    if (sender === 'bot' && voiceMode) {
      speakText(text)
    }
  }

  const speakText = (text) => {
    if ('speechSynthesis' in window) {
      synthRef.current.cancel()
      const utterance = new SpeechSynthesisUtterance(text)
      utterance.rate = 1
      utterance.pitch = 1
      utterance.volume = 1
      utterance.onstart = () => setIsSpeaking(true)
      utterance.onend = () => setIsSpeaking(false)
      synthRef.current.speak(utterance)
    }
  }

  const stopSpeaking = () => {
    if ('speechSynthesis' in window) {
      synthRef.current.cancel()
      setIsSpeaking(false)
    }
  }

  const startRecording = () => {
    if (recognitionRef.current) {
      setIsRecording(true)
      recognitionRef.current.start()
    }
  }

  const stopRecording = () => {
    if (recognitionRef.current) {
      recognitionRef.current.stop()
      setIsRecording(false)
    }
  }

  const requestLocation = () => {
    if (navigator.geolocation) {
      setIsLoading(true);
      navigator.geolocation.getCurrentPosition(
        (position) => {
          const loc = {
            lat: position.coords.latitude,
            lng: position.coords.longitude
          };
          setUserLocation(loc);
          setIsLoading(false);
          addMessage('bot', '📍 Location confirmed. I can now search for the nearest hospitals for you.');
        },
        (error) => {
          setIsLoading(false);
          console.error('Location error:', error);
          addMessage('bot', '⚠️ Location access denied. Please enable it in your browser settings to find nearby care.');
        }
      );
    } else {
      addMessage('bot', '❌ Geolocation is not supported by your browser.');
    }
  };

  const handleSend = async () => {
    if (!input.trim()) return

    addMessage('user', input)
    setInput('')
    setIsLoading(true)

    try {
      const response = await axios.post(`${API_BASE}/api/chat`, { message: input })
      
      setIsLoading(false)
      
      // Check if API wants to trigger symptom cards
      if (response.data.trigger_cards) {
        window.lastUserMessage = input
        setShowSymptomCards(true)
      } else {
        addMessage('bot', response.data.response)
      }
    } catch (error) {
      console.error('Chat error:', error)
      setIsLoading(false)
      addMessage('bot', 'Error: Please make sure Flask is running on port 5000')
    }
  }

  const clearChat = () => {
    setMessages([{ sender: 'bot', text: 'Hello! I\'m your medical diagnosis assistant. How can I help you today?', timestamp: new Date() }])
    setDoctors([])
    setShowDoctors(false)
  }

  const handleSymptomComplete = async (result) => {
    setShowSymptomCards(false)
    setIsLoading(true)

    try {
      console.log('Symptom answers:', result)
      
      const response = await axios.post(`${API_BASE}/api/symptom-analyze`, {
        answers: result,
        location: userLocation
      })

      setIsLoading(false)
      const data = response.data
      
      console.log('Analysis result:', data)

      // Use the structured data directly for the result card
      const introMessage = `I have analyzed your symptoms and generated a health assessment for you.`
      
      addMessage('bot', introMessage, {
        urgency: data.urgency || 'medium',
        severity: data.severity || 'MODERATE',
        summary: data.summary || ['Symptom analysis completed'],
        assessment: data.assessment || data.severity_reasoning || 'Based on your symptoms, please monitor your condition.',
        recommendation: data.recommendation || 'Please consult a healthcare professional if symptoms persist.',
        conditions: data.conditions,
        actions: data.actions,
        home_care: data.home_care,
        warning_signs: data.warning_signs,
        specialty: data.specialty
      })

      // Show doctor recommendations if urgency is medium or higher
      if (data.doctors && data.doctors.length > 0) {
        setDoctors(data.doctors)
        setShowDoctors(true)
        addMessage('bot', `🏥 Found ${data.doctors.length} nearby doctors/hospitals with 4+ star ratings.`)
      } else if (['medium', 'high', 'emergency'].includes(data.urgency) && userLocation) {
        addMessage('bot', '🔍 Searching for nearby doctors...')
        searchDoctors(data.specialty || 'hospital')
      }
    } catch (error) {
      console.error('Analysis error:', error)
      console.error('Error details:', error.response?.data)
      setIsLoading(false)
      addMessage('bot', 'Error analyzing symptoms. Please try again or describe your symptoms in the chat.')
    }
  }

  const searchDoctors = async (specialty) => {
    if (!userLocation) {
      addMessage('bot', '📍 Please enable location access to find nearby doctors.')
      return
    }

    try {
      const response = await axios.post(`${API_BASE}/api/find-doctors`, {
        location: userLocation,
        specialty: specialty
      })

      if (response.data.doctors && response.data.doctors.length > 0) {
        setDoctors(response.data.doctors)
        setShowDoctors(true)
      } else {
        addMessage('bot', '❌ No nearby doctors found. Try expanding your search radius.')
      }
    } catch (error) {
      console.error('Doctor search error:', error)
      addMessage('bot', '❌ Error finding doctors. Please try again.')
    }
  }

  return (
    <div className="chat-container">
      <div className="chat-header">
        <img src="https://img.freepik.com/premium-vector/health-care-medical-logo-vector-design_990473-2554.jpg" alt="Logo" className="logo" />
        <div className="title-section">
          <h1>Medical Diagnosis Assistant</h1>
          <p>Welcome to Medical Diagnosis Assistant!</p>
        </div>
        <button 
          className={`voice-mode-toggle ${voiceMode ? 'active' : ''}`}
          onClick={() => setVoiceMode(!voiceMode)}
          title={voiceMode ? 'Voice Mode ON' : 'Voice Mode OFF'}
        >
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            {voiceMode ? (
              <>
                <polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"/>
                <path d="M15.54 8.46a5 5 0 0 1 0 7.07"/>
                <path d="M19.07 4.93a10 10 0 0 1 0 14.14"/>
              </>
            ) : (
              <>
                <polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"/>
                <line x1="23" y1="9" x2="17" y2="15"/>
                <line x1="17" y1="9" x2="23" y2="15"/>
              </>
            )}
          </svg>
        </button>
        <button 
          className="clear-chat-btn"
          onClick={clearChat}
          title="Clear Chat"
        >
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M3 6h18"/>
            <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
          </svg>
        </button>
        <button 
          className="logout-btn"
          onClick={onLogout}
          title="Logout"
        >
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/>
            <polyline points="16 17 21 12 16 7"/>
            <line x1="21" y1="12" x2="9" y2="12"/>
          </svg>
        </button>
      </div>

      <div className="messages">
        {messages.map((msg, idx) => (
          <div key={idx} className={`message ${msg.sender}`}>
            <div className="message-content">
              {msg.sender === 'bot' && msg.text && msg.text.length > 300 ? (
                <div className="info-card">
                  {msg.text.split('\n').map((line, i) => {
                    if (line.trim().match(/^\d+\./)) {
                      return <div key={i} className="info-point">{line.trim()}</div>
                    } else if (line.trim().startsWith('*')) {
                      return <div key={i} className="info-subpoint">{line.trim()}</div>
                    } else if (line.trim()) {
                      return <p key={i}>{line.trim()}</p>
                    }
                    return null
                  })}
                </div>
              ) : (
                <p>{msg.text || ''}</p>
              )}
              {msg.data && msg.data.urgency && (
                <div className={`assessment-card ${msg.data.urgency}`}>
                  <div className="assessment-hero">
                    <div className="hero-status">
                      <div className="status-indicator">
                        <span className="pulse-dot"></span>
                        <span className="urgency-label">{(msg.data.urgency || 'medium').toUpperCase()} RISK</span>
                      </div>
                      <h3>Health Assessment</h3>
                    </div>
                    <div className="severity-score">
                      <svg viewBox="0 0 36 36" className="circular-chart">
                        <path className="circle-bg" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" />
                        <path className="circle" strokeDasharray={`${msg.data.severity_score * 10 || 50}, 100`} d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" />
                        <text x="18" y="20.35" className="percentage">{msg.data.severity_score || 5}</text>
                      </svg>
                      <span>Severity</span>
                    </div>
                  </div>
                  
                  <div className="assessment-body">
                    <div className="findings-grid">
                      {msg.data.summary && msg.data.summary.map((s, i) => (
                        <div key={i} className="finding-tag">
                          <span className="tag-icon">✓</span>
                          {s}
                        </div>
                      ))}
                    </div>

                    <div className="conditions-section">
                      <h4>Potential Conditions</h4>
                      {msg.data.conditions && msg.data.conditions.map((c, i) => (
                        <div key={i} className="condition-row">
                          <div className="condition-info">
                            <span className="condition-name">{c.name}</span>
                            <span className="condition-prob">{c.probability}</span>
                          </div>
                          <div className="progress-bar-bg">
                            <div className="progress-bar-fill" style={{ width: c.probability }}></div>
                          </div>
                        </div>
                      ))}
                    </div>

                    <div className="care-grid">
                      <div className="care-column">
                        <h4>Immediate Care</h4>
                        <ul>
                          {msg.data.actions && msg.data.actions.map((a, i) => <li key={i}>{a}</li>)}
                          {msg.data.home_care && msg.data.home_care.map((h, i) => <li key={i}>{h}</li>)}
                        </ul>
                      </div>
                      <div className="care-column warnings">
                        <h4>⚠️ Warning Signs</h4>
                        <ul>
                          {msg.data.warning_signs && msg.data.warning_signs.map((w, i) => <li key={i}>{w}</li>)}
                        </ul>
                      </div>
                    </div>
                  </div>

                  <div className="recommendation-panel">
                    <div className="doctor-badge">
                      <span className="dr-icon">👨‍⚕️</span>
                    </div>
                    <div className="recommendation-content">
                      <p>{msg.data.recommendation}</p>
                      <div className="specialty-match">
                        <span className="match-label">Recommended:</span>
                        <strong>{msg.data.specialty || 'General Care'}</strong>
                      </div>
                      
                      {!userLocation && (
                        <button className="location-request-btn" onClick={requestLocation}>
                          📍 Enable Location to Find Nearest Hospital
                        </button>
                      )}
                    </div>
                  </div>
                </div>
              )}
            </div>
            <span className="timestamp">
              {msg.timestamp.toLocaleTimeString()}
            </span>
          </div>
        ))}
        {isLoading && (
          <div className="message bot">
            <div className="message-content">
              <div className="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {showSymptomCards && (
        <div className="modal-overlay">
          <SymptomCards onComplete={handleSymptomComplete} />
        </div>
      )}

      {showDoctors && doctors.length > 0 && (
        <div className="care-overlay">
          <div className="care-panel">
            <div className="care-header">
              <div className="care-title">
                <span className="care-icon">
                  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#10b981" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M19 14c1.66 0 3-1.34 3-3V5c0-1.66-1.34-3-3-3H5C3.34 2 2 3.34 2 5v6c0 1.66 1.34 3 3 3"/>
                    <path d="M5 14v7a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1v-7"/>
                    <path d="M10 9h4"/>
                    <path d="M12 7v4"/>
                  </svg>
                </span>
                <div>
                  <h3>Nearby Medical Care</h3>
                  <p>Based on your current symptoms & location</p>
                </div>
              </div>
              <button className="close-care" onClick={() => setShowDoctors(false)}>
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
                </svg>
              </button>
            </div>
            
            <div className="care-list">
              {doctors.map((doctor, idx) => (
                <div key={idx} className="care-card">
                  <div className="care-status-badge">
                    <span className={doctor.open_now ? 'open' : 'closed'}>
                      {doctor.open_now ? 'AVAILABLE' : 'CLOSED'}
                    </span>
                  </div>
                  
                  <div className="care-info">
                    <div className="care-main">
                      <h4>{doctor.name}</h4>
                      <div className="care-rating">
                        <span className="rating-star">
                          <svg width="14" height="14" viewBox="0 0 24 24" fill="#f59e0b" stroke="#f59e0b" strokeWidth="2">
                            <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>
                          </svg>
                        </span>
                        <span className="rating-value">{doctor.rating}</span>
                        <span className="rating-count">({doctor.total_ratings || 0})</span>
                      </div>
                    </div>
                    
                    <div className="care-details">
                      <div className="detail-item">
                        <span className="icon">
                          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                            <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/>
                            <circle cx="12" cy="10" r="3"/>
                          </svg>
                        </span>
                        <p>{doctor.address}</p>
                      </div>
                      <div className="detail-item">
                        <span className="icon">
                          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                            <path d="m20 9.5-1.5 1.5M14 6.5l-1.5-1.5M3 21l3-3M21 3l-3 3M16 11l-5 5M11 16l-5 5m10-10L21 3m-5 8L3 21m8-5L14 19M16 11l-3-3M8 13l-3-3"/>
                          </svg>
                        </span>
                        <p>{doctor.distance} away</p>
                      </div>
                      {doctor.phone && doctor.phone !== 'N/A' && (
                        <div className="detail-item">
                          <span className="icon">
                            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                              <path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l2.18-2.18a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"/>
                            </svg>
                          </span>
                          <p>{doctor.phone}</p>
                        </div>
                      )}
                    </div>
                  </div>
                  
                  <div className="care-actions">
                    {doctor.maps_url && (
                      <a href={doctor.maps_url} target="_blank" rel="noopener noreferrer" className="action-link maps">
                        Directions
                      </a>
                    )}
                    {doctor.booking_url ? (
                      <a href={doctor.booking_url} target="_blank" rel="noopener noreferrer" className="action-link book">
                        Book Now
                      </a>
                    ) : (
                      <button className="action-link call">Call Hospital</button>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      <div className="input-area">
        <button 
          className={`voice-btn ${isRecording ? 'recording' : ''}`}
          onClick={isRecording ? stopRecording : startRecording}
          title={isRecording ? 'Stop Recording' : 'Start Voice Input'}
          disabled={!recognitionRef.current}
        >
          {isRecording ? (
            <i className="bi bi-mic-mute"></i>
          ) : (
            <i className="bi bi-mic"></i>
          )}
        </button>
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && handleSend()}
          placeholder={isRecording ? '🎤 Listening...' : 'Type your message...'}
        />
        {isSpeaking && voiceMode && (
          <button 
            className="speaker-btn active"
            onClick={stopSpeaking}
            title="Stop Speaking"
          >
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"/>
              <line x1="23" y1="9" x2="17" y2="15"/>
              <line x1="17" y1="9" x2="23" y2="15"/>
            </svg>
          </button>
        )}
        <button onClick={handleSend}>
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <line x1="22" y1="2" x2="11" y2="13"/>
            <polygon points="22 2 15 22 11 13 2 9 22 2"/>
          </svg>
        </button>
      </div>
    </div>
  )
}

export default ChatBot
