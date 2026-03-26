import './LandingPage.css'

function LandingPage({ onGetStarted }) {
  return (
    <div className="landing-page">
      <nav className="landing-nav">
        <div className="nav-logo">
          <img src="https://img.freepik.com/premium-vector/health-care-medical-logo-vector-design_990473-2554.jpg" alt="MediCare AI Logo" className="logo-icon" />
          <span>MediCare AI</span>
        </div>
        <button className="nav-login-btn" onClick={onGetStarted}>
          Login / Sign Up
        </button>
      </nav>

      <section className="hero-section">
        <div className="hero-content">
          <h1 className="hero-title">
            Your AI-Powered <span className="highlight">Health Assistant</span>
          </h1>
          <p className="hero-subtitle">
            Get instant medical guidance, symptom analysis, and doctor recommendations 24/7
          </p>
          <button className="cta-button" onClick={onGetStarted}>
            Get Started Free
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <polyline points="9 18 15 12 9 6"/>
            </svg>
          </button>
          <div className="hero-features">
            <div className="hero-feature-item">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <polyline points="20 6 9 17 4 12"/>
              </svg>
              <span>No credit card required</span>
            </div>
            <div className="hero-feature-item">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <polyline points="20 6 9 17 4 12"/>
              </svg>
              <span>Instant access</span>
            </div>
          </div>
        </div>
        <div className="hero-image">
          <div className="hero-card">
            <img 
              src="https://www.nejm.org/pb-assets/images/editorial/featuredTopics/ai-in-medicine/AI-Series-Banner_420x280-1680108167940.jpg" 
              alt="AI in Medicine" 
              className="hero-banner"
            />
          </div>
        </div>
      </section>

      <section className="features-section">
        <h2 className="section-title">Why Choose MediCare AI?</h2>
        <div className="features-grid">
          <div className="feature-card">
            <div className="feature-icon-wrapper">
              <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/>
              </svg>
            </div>
            <h3>AI-Powered Analysis</h3>
            <p>Advanced machine learning algorithms analyze your symptoms and provide accurate health assessments</p>
          </div>
          <div className="feature-card">
            <div className="feature-icon-wrapper">
              <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
              </svg>
            </div>
            <h3>Multi-Language Support</h3>
            <p>Communicate in English, Tamil, or Tanglish - we understand your language</p>
          </div>
          <div className="feature-card">
            <div className="feature-icon-wrapper">
              <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"/>
                <path d="M19 10v2a7 7 0 0 1-14 0v-2"/>
                <line x1="12" y1="19" x2="12" y2="23"/>
                <line x1="8" y1="23" x2="16" y2="23"/>
              </svg>
            </div>
            <h3>Voice Assistant</h3>
            <p>Speak naturally and get voice responses - hands-free health consultation</p>
          </div>
          <div className="feature-card">
            <div className="feature-icon-wrapper">
              <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/>
                <circle cx="12" cy="10" r="3"/>
              </svg>
            </div>
            <h3>Doctor Finder</h3>
            <p>Locate nearby doctors and hospitals with ratings and directions</p>
          </div>
          <div className="feature-card">
            <div className="feature-icon-wrapper">
              <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <rect x="3" y="11" width="18" height="11" rx="2" ry="2"/>
                <path d="M7 11V7a5 5 0 0 1 10 0v4"/>
              </svg>
            </div>
            <h3>100% Confidential</h3>
            <p>Your health data is encrypted and secure - complete privacy guaranteed</p>
          </div>
          <div className="feature-card">
            <div className="feature-icon-wrapper">
              <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <circle cx="12" cy="12" r="10"/>
                <polyline points="12 6 12 12 16 14"/>
              </svg>
            </div>
            <h3>24/7 Available</h3>
            <p>Access medical guidance anytime, anywhere - no waiting rooms</p>
          </div>
        </div>
      </section>

      <section className="how-it-works">
        <h2 className="section-title">How It Works</h2>
        <div className="steps-container">
          <div className="step">
            <div className="step-number">1</div>
            <div className="step-icon">
              <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
              </svg>
            </div>
            <h3>Describe Symptoms</h3>
            <p>Tell us what you're experiencing through chat or voice</p>
          </div>
          <div className="step-arrow">
            <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <polyline points="9 18 15 12 9 6"/>
            </svg>
          </div>
          <div className="step">
            <div className="step-number">2</div>
            <div className="step-icon">
              <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/>
              </svg>
            </div>
            <h3>AI Analysis</h3>
            <p>Our AI analyzes your symptoms and medical history</p>
          </div>
          <div className="step-arrow">
            <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <polyline points="9 18 15 12 9 6"/>
            </svg>
          </div>
          <div className="step">
            <div className="step-number">3</div>
            <div className="step-icon">
              <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M4.8 2.3A.3.3 0 1 0 5 2H4a2 2 0 0 0-2 2v5a6 6 0 0 0 6 6v0a6 6 0 0 0 6-6V4a2 2 0 0 0-2-2h-1a.2.2 0 1 0 .3.3"/>
                <path d="M8 15v1a6 6 0 0 0 6 6v0a6 6 0 0 0 6-6v-4"/>
                <circle cx="20" cy="10" r="2"/>
              </svg>
            </div>
            <h3>Get Guidance</h3>
            <p>Receive diagnosis, care recommendations, and doctor referrals</p>
          </div>
        </div>
      </section>

      <section className="stats-section">
        <div className="stat">
          <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/>
            <circle cx="9" cy="7" r="4"/>
            <path d="M23 21v-2a4 4 0 0 0-3-3.87"/>
            <path d="M16 3.13a4 4 0 0 1 0 7.75"/>
          </svg>
          <h3>10,000+</h3>
          <p>Consultations</p>
        </div>
        <div className="stat">
          <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/>
          </svg>
          <h3>95%</h3>
          <p>Accuracy Rate</p>
        </div>
        <div className="stat">
          <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <circle cx="12" cy="12" r="10"/>
            <polyline points="12 6 12 12 16 14"/>
          </svg>
          <h3>24/7</h3>
          <p>Availability</p>
        </div>
        <div className="stat">
          <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
          </svg>
          <h3>3</h3>
         <p>languages</p>
          <p>Supported</p>
        </div>
      </section>

      <section className="cta-section">
        <h2>Ready to Get Started?</h2>
        <p>Join thousands of users who trust MediCare AI for their health needs</p>
        <button className="cta-button-large" onClick={onGetStarted}>
          Start Free Consultation
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <polyline points="9 18 15 12 9 6"/>
          </svg>
        </button>
        <p className="disclaimer">
          ⚠️ Disclaimer: This is an AI assistant for informational purposes only. 
          Always consult qualified healthcare professionals for medical advice.
        </p>
      </section>

      <footer className="landing-footer">
        <p>© 2024 MediCare AI. All rights reserved.</p>
      </footer>
    </div>
  )
}

export default LandingPage
