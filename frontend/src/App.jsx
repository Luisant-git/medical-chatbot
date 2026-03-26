import { useState, useEffect } from 'react'
import './App.css'
import Login from './Login'
import LandingPage from './LandingPage'
import HomePage from './HomePage'
import ChatBot from './ChatBot'

function App() {
  const [showLanding, setShowLanding] = useState(true)
  const [user, setUser] = useState(null)
  const [showHome, setShowHome] = useState(true)

  useEffect(() => {
    // Check if user is already logged in
    const savedUser = localStorage.getItem('user')
    const token = localStorage.getItem('token')
    if (savedUser && token) {
      setUser(JSON.parse(savedUser))
      setShowLanding(false)
    }
  }, [])

  const handleLogin = (userData) => {
    setUser(userData)
  }

  const handleLogout = () => {
    localStorage.removeItem('user')
    localStorage.removeItem('token')
    setUser(null)
    setShowHome(true)
    setShowLanding(true)
  }

  return (
    <div className={`app ${!showHome && user ? 'chat-active' : ''}`}>
      {showLanding ? (
        <LandingPage onGetStarted={() => setShowLanding(false)} />
      ) : !user ? (
        <Login onLogin={handleLogin} />
      ) : showHome ? (
        <HomePage onStartConsultation={() => setShowHome(false)} />
      ) : (
        <ChatBot user={user} onLogout={handleLogout} />
      )}
    </div>
  )
}

export default App
