import './HomePage.css'

function HomePage({ onStartConsultation }) {
  return (
    <div className="home-screen">
      <div className="home-content">
        <img src="https://img.freepik.com/premium-vector/health-care-medical-logo-vector-design_990473-2554.jpg" alt="Logo" className="home-logo" />
        <h1>Medical Diagnosis Assistant</h1>
        <p>AI-Powered Health Consultation Available 24/7</p>
        <div className="features">
          <div className="feature">
            <span className="feature-icon">🩺</span>
            <h3>Symptom Analysis</h3>
            <p>Get instant health assessments</p>
          </div>
          <div className="feature">
            <span className="feature-icon">⚡</span>
            <h3>Quick Response</h3>
            <p>AI-powered diagnosis in seconds</p>
          </div>
          <div className="feature">
            <span className="feature-icon">🔒</span>
            <h3>Confidential</h3>
            <p>Your health data is secure</p>
          </div>
        </div>
        <button className="start-btn" onClick={onStartConsultation}>
          Start Consultation
        </button>
      </div>
    </div>
  )
}

export default HomePage
