const express = require('express');
const Groq = require('groq-sdk');
const axios = require('axios');
const router = express.Router();

const groq = new Groq({ apiKey: process.env.GROQ_API_KEY });

router.get('/symptom-flow', async (req, res) => {
  try {
    const { message } = req.query;

    // Generate dynamic symptom flow based on initial message
    const completion = await groq.chat.completions.create({
      messages: [
        {
          role: 'system',
          content: `Generate a symptom assessment flow as JSON array. Each question should have:
          - id: unique identifier
          - question: the question text
          - type: "yesno", "choice", or "multichoice"
          - options: array of options (for choice/multichoice)
          - followup: optional nested questions based on answers
          
          Create 5-7 relevant questions based on the user's initial symptom. Return ONLY valid JSON array.`
        },
        {
          role: 'user',
          content: `User mentioned: "${message}". Generate symptom assessment questions.`
        }
      ],
      model: 'llama-3.3-70b-versatile',
      temperature: 0.7,
      max_tokens: 1500,
      response_format: { type: 'json_object' }
    });

    const result = JSON.parse(completion.choices[0]?.message?.content || '{}');
    
    // Default flow if AI doesn't return proper format
    const defaultFlow = [
      { id: 'fever', question: 'Do you have a fever?', type: 'yesno' },
      { id: 'duration', question: 'How long have you had these symptoms?', type: 'choice', options: ['Less than 24 hours', '1-3 days', '3-7 days', 'More than a week'] },
      { id: 'severity', question: 'How severe is your discomfort?', type: 'choice', options: ['Mild', 'Moderate', 'Severe', 'Very Severe'] },
      { id: 'other_symptoms', question: 'Do you have any other symptoms?', type: 'multichoice', options: ['Headache', 'Cough', 'Fatigue', 'Body aches', 'Nausea', 'None'] },
      { id: 'medical_history', question: 'Do you have any chronic medical conditions?', type: 'yesno' }
    ];

    res.json({ flow: result.flow || defaultFlow });
  } catch (error) {
    console.error('Symptom flow error:', error);
    // Return default flow on error
    res.json({
      flow: [
        { id: 'fever', question: 'Do you have a fever?', type: 'yesno' },
        { id: 'duration', question: 'How long have you had these symptoms?', type: 'choice', options: ['Less than 24 hours', '1-3 days', '3-7 days', 'More than a week'] },
        { id: 'severity', question: 'How severe is your discomfort?', type: 'choice', options: ['Mild', 'Moderate', 'Severe', 'Very Severe'] },
        { id: 'other_symptoms', question: 'Do you have any other symptoms?', type: 'multichoice', options: ['Headache', 'Cough', 'Fatigue', 'Body aches', 'Nausea', 'None'] }
      ]
    });
  }
});

router.post('/symptom-collect', async (req, res) => {
  try {
    const { answers, language } = req.body;

    const symptomsText = Object.entries(answers)
      .map(([key, value]) => `${key}: ${Array.isArray(value) ? value.join(', ') : value}`)
      .join('\n');

    const completion = await groq.chat.completions.create({
      messages: [
        {
          role: 'system',
          content: `Analyze symptoms and return JSON with: severity, urgency, summary, assessment, recommendation`
        },
        {
          role: 'user',
          content: `Symptoms:\n${symptomsText}`
        }
      ],
      model: 'llama-3.3-70b-versatile',
      temperature: 0.5,
      max_tokens: 1000,
      response_format: { type: 'json_object' }
    });

    const analysis = JSON.parse(completion.choices[0]?.message?.content || '{}');
    res.json(analysis);
  } catch (error) {
    console.error('Symptom collect error:', error);
    res.status(500).json({ error: 'Failed to analyze symptoms' });
  }
});

router.post('/chat', async (req, res) => {
  try {
    const { message } = req.body;

    const completion = await groq.chat.completions.create({
      messages: [
        {
          role: 'system',
          content: `You are a professional, empathetic, and knowledgeable Medical AI Assistant. Your goal is to help users understand their health symptoms while prioritizing safety and accuracy.
          
          Guidelines:
          - For greetings (hi, hello, hey, etc.), respond warmly and ask how you can assist with their health today.
          - For ANY mention of symptoms (e.g., pain, fever, cough, nausea, etc.), respond with the exact string "TRIGGER_SYMPTOM_CARDS" to initiate a structured assessment.
          - For general medical inquiries, provide clear, concise, and evidence-based information.
          - ALWAYS include a disclaimer: "This is for informational purposes only and not a substitute for professional medical advice, diagnosis, or treatment."
          - Keep responses professional yet accessible.
          - If the user seems to be in an emergency (e.g., chest pain, difficulty breathing), immediately advise calling emergency services (911/112).`
        },
        {
          role: 'user',
          content: message
        }
      ],
      model: 'llama-3.3-70b-versatile',
      temperature: 0.6,
      max_tokens: 250
    });

    const response = completion.choices[0]?.message?.content || 'I apologize, I could not process that.';

    if (response.includes('TRIGGER_SYMPTOM_CARDS')) {
      return res.json({
        trigger_cards: true,
        response: 'Let me help you assess your symptoms. Please answer a few questions.'
      });
    }

    res.json({
      trigger_cards: false,
      response
    });
  } catch (error) {
    console.error('Chat error:', error);
    res.status(500).json({ error: 'Chat processing failed' });
  }
});

router.post('/symptom-analyze', async (req, res) => {
  try {
    const { answers, location } = req.body;

    const symptomsText = Object.entries(answers)
      .map(([key, value]) => `${key}: ${value}`)
      .join(', ');

    const completion = await groq.chat.completions.create({
      messages: [
        {
          role: 'system',
          content: `You are a medical AI assistant. Analyze the symptoms provided and generate a comprehensive assessment in JSON format.
          
          Required JSON Fields:
          - severity: "LOW", "MODERATE", "HIGH", or "EMERGENCY"
          - severity_score: number 1-10
          - urgency: "low", "medium", "high", or "emergency"
          - severity_reasoning: detailed explanation ofなぜ this severity was chosen
          - conditions: array of objects { name, probability (0-100%), evidence }
          - actions: array of strings for immediate steps
          - home_care: array of strings for non-urgent tips
          - warning_signs: array of strings indicating when to seek urgent help
          - specialty: the most relevant medical specialist (e.g., Cardiologist, Dermatologist)
          - summary: short list of key findings
          - assessment: structured overview of the situation
          - recommendation: direct advice (always mention consulting a doctor)
          
          Context: The user provided their symptoms through a structured questionnaire.
          Respond ONLY with valid JSON, ensuring medical accuracy and a professional tone.`
        },
        {
          role: 'user',
          content: `Analyze these symptoms and provide the assessment: ${symptomsText}`
        }
      ],
      model: 'llama-3.3-70b-versatile',
      temperature: 0.4,
      max_tokens: 2000,
      response_format: { type: 'json_object' }
    });

    const analysis = JSON.parse(completion.choices[0]?.message?.content || '{}');
    res.json(analysis);
  } catch (error) {
    console.error('Analysis error:', error);
    res.status(500).json({ error: 'Symptom analysis failed' });
  }
});

router.post('/find-doctors', async (req, res) => {
  try {
    const { location, specialty } = req.body;
    
    if (!location || !location.lat || !location.lng) {
      return res.status(400).json({ error: 'Location coordinates required' });
    }

    const apiKey = process.env.GOOGLE_MAPS_API_KEY;
    
    if (!apiKey) {
      console.warn('GOOGLE_MAPS_API_KEY is missing in backend .env');
      // Falling back to a "realistic-looking" mock if no key, 
      // but clearly indicating it's waiting for configuration
      return res.json({
        doctors: [
          {
            name: '⚠️ API Key Needed',
            rating: 5.0,
            address: 'Add GOOGLE_MAPS_API_KEY to your .env to see real nearby hospitals.',
            distance: '0 km',
            open_now: true,
            maps_url: '#'
          }
        ]
      });
    }

    const searchQuery = specialty ? `${specialty} or Hospital` : 'Hospital';
    const radius = 10000; // Expanded to 10km
    
    // Google Places Text Search (more reliable for specific specialties)
    const response = await axios.get(
      `https://maps.googleapis.com/maps/api/place/textsearch/json`, {
        params: {
          query: searchQuery,
          location: `${location.lat},${location.lng}`,
          radius: radius,
          key: apiKey,
          type: 'hospital'
        }
      }
    );

    const places = response.data.results || [];
    
    // Map Google results to our frontend format
    const doctors = places.slice(0, 5).map(place => {
      return {
        name: place.name,
        rating: place.rating || 4.0,
        total_ratings: place.user_ratings_total || 0,
        address: place.formatted_address || place.vicinity,
        distance: 'Local Area', 
        phone: 'N/A', 
        open_now: place.opening_hours ? place.opening_hours.open_now : true,
        maps_url: `https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(place.name)}&query_place_id=${place.place_id}`,
        booking_url: null
      };
    });

    res.json({ doctors });
  } catch (error) {
    console.error('Doctor search error:', error.message);
    res.status(500).json({ error: 'Search failed' });
  }
});

module.exports = router;
