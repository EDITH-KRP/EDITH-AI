import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import './App.css';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Language codes for speech recognition
const SPEECH_LANGUAGE_CODES = {
  english: 'en-IN',
  hindi: 'hi-IN',
  kannada: 'kn-IN',
  tamil: 'ta-IN',
  telugu: 'te-IN',
  malayalam: 'ml-IN'
};

// Voice prompts for different languages
const VOICE_PROMPTS = {
  english: "Say product name, quantity, and price. For example: 'Fresh tomatoes, 1 kg, 50 rupees'",
  hindi: "उत्पाद का नाम, मात्रा और मूल्य बताएं। उदाहरण: 'ताजा टमाटर, 1 किलो, 50 रुपए'",
  kannada: "ಉತ್ಪಾದನೆಯ ಹೆಸರು, ಪ್ರಮಾಣ ಮತ್ತು ಬೆಲೆಯನ್ನು ಹೇಳಿ। ಉದಾಹರಣೆ: 'ತಾಜಾ ಟೊಮೇಟೊ, 1 ಕಿಲೋ, 50 ರೂಪಾಯಿ'",
  tamil: "தயாரிப்பு பெயர், அளவு மற்றும் விலையைச் சொல்லுங்கள். எடுத்துக்காட்டு: 'புதிய தக்காளி, 1 கிலோ, 50 ரூபாய்'",
  telugu: "ఉత్పత్తి పేరు, పరిమాణం మరియు ధరను చెప్పండి। ఉదాహరణ: 'తాజా టమాటాలు, 1 కిలో, 50 రూపాయలు'",
  malayalam: "ഉൽപ്പന്ന നാമം, അളവ്, വിലയെക്കുറിച്ച് പറയുക. ഉദാഹരണം: 'പുതിയ തക്കാളി, 1 കിലോ, 50 രൂപ'"
};

// Voice button component
const VoiceButton = ({ isRecording, onStartRecording, onStopRecording, isSupported, language, content, onTestVoice }) => {
  const [isAnimating, setIsAnimating] = useState(false);

  useEffect(() => {
    if (isRecording) {
      setIsAnimating(true);
    } else {
      setIsAnimating(false);
    }
  }, [isRecording]);

  if (!isSupported) {
    return (
      <div className="voice-not-supported">
        <p>🎙️ Voice input not supported in this browser</p>
        <p>Please try Chrome, Edge, or Safari</p>
      </div>
    );
  }

  return (
    <div className="voice-button-container">
      <button 
        className={`voice-button ${isRecording ? 'recording' : ''} ${isAnimating ? 'pulse' : ''}`}
        onClick={isRecording ? onStopRecording : onStartRecording}
        type="button"
      >
        {isRecording ? '🔴 Stop Recording' : '🎙️ Start Voice Input'}
      </button>
      
      <button 
        className="voice-demo-button"
        onClick={onTestVoice}
        type="button"
      >
        🧪 Test Voice Demo
      </button>
      
      <div className="voice-prompt">
        <p>{VOICE_PROMPTS[language] || VOICE_PROMPTS.english}</p>
        <p className="voice-tip">💡 Click "Test Voice Demo" to see how it works!</p>
      </div>
    </div>
  );
};

// Voice transcript display component
const VoiceTranscript = ({ transcript, isRecording, content }) => {
  if (!transcript && !isRecording) return null;

  return (
    <div className="voice-transcript">
      <h4>🎙️ {content.voice_input || 'Voice Input'}:</h4>
      <div className="transcript-content">
        {transcript || (isRecording ? `${content.listening || 'Listening'}...` : '')}
      </div>
      {isRecording && (
        <div className="voice-animation">
          <div className="voice-wave"></div>
          <div className="voice-wave"></div>
          <div className="voice-wave"></div>
        </div>
      )}
    </div>
  );
};

// Language selector component
const LanguageSelector = ({ currentLanguage, onLanguageChange, languages }) => {
  return (
    <div className="language-selector">
      <select 
        value={currentLanguage} 
        onChange={(e) => onLanguageChange(e.target.value)}
        className="language-select"
      >
        {languages.map(lang => (
          <option key={lang} value={lang}>
            {lang.charAt(0).toUpperCase() + lang.slice(1)}
          </option>
        ))}
      </select>
    </div>
  );
};

// Product input form component
// Product input form component
const ProductInputForm = ({ onSubmit, isLoading, content, currentLanguage, onVoiceInput }) => {
  const [formData, setFormData] = useState({
    name: '',
    quantity: '',
    price: '',
    additional_info: ''
  });

  const [isRecording, setIsRecording] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [isVoiceSupported, setIsVoiceSupported] = useState(false);
  const [voiceError, setVoiceError] = useState('');
  const recognitionRef = useRef(null);

  useEffect(() => {
    // Check if speech recognition is supported
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    setIsVoiceSupported(!!SpeechRecognition);

    if (SpeechRecognition) {
      const recognition = new SpeechRecognition();
      recognition.continuous = true;
      recognition.interimResults = true;
      recognition.lang = SPEECH_LANGUAGE_CODES[currentLanguage] || 'en-IN';

      recognition.onresult = (event) => {
        let finalTranscript = '';
        let interimTranscript = '';

        for (let i = event.resultIndex; i < event.results.length; i++) {
          const transcript = event.results[i][0].transcript;
          if (event.results[i].isFinal) {
            finalTranscript += transcript;
          } else {
            interimTranscript += transcript;
          }
        }

        const fullTranscript = finalTranscript + interimTranscript;
        setTranscript(fullTranscript);

        // Parse voice input when final result is received
        if (finalTranscript) {
          parseVoiceInput(finalTranscript);
        }
      };

      recognition.onerror = (event) => {
        console.error('Speech recognition error:', event.error);
        setVoiceError(`Voice recognition error: ${event.error}`);
        setIsRecording(false);
      };

      recognition.onend = () => {
        setIsRecording(false);
      };

      recognitionRef.current = recognition;
    }

    return () => {
      if (recognitionRef.current) {
        recognitionRef.current.stop();
      }
    };
  }, [currentLanguage]);

  const parseVoiceInput = (voiceText) => {
    try {
      // Enhanced parsing logic for Indian language patterns
      const text = voiceText.toLowerCase();
      
      // Price extraction patterns
      const pricePatterns = [
        /(\d+)\s*(?:rupees?|रुपए|रूपये|ರೂಪಾಯಿ|ரூபாய்|రూபாயలు|രൂപ)/i,
        /(?:price|मूल्य|ಬೆಲೆ|விலை|ధర|വില)[:\s]*(\d+)/i,
        /(\d+)\s*(?:rs|₹)/i
      ];

      // Quantity extraction patterns
      const quantityPatterns = [
        /(\d+(?:\.\d+)?)\s*(?:kg|kilogram|किलो|ಕಿಲೋ|கிலோ|కిలో|കിലോ)/i,
        /(\d+(?:\.\d+)?)\s*(?:piece|pieces|pcs|पीस|ಪೀಸ್|பீஸ்|పీస్|പീസ്)/i,
        /(\d+(?:\.\d+)?)\s*(?:liter|litre|लीटर|ಲೀಟರ್|லிட்டர்|లీటర్|ലിറ്റർ)/i,
        /(?:quantity|मात्रा|ಪ್ರಮಾಣ|அளவு|పరిమాణం|അളവ്)[:\s]*(\d+(?:\.\d+)?)\s*(\w+)/i
      ];

      let extractedPrice = '';
      let extractedQuantity = '';
      let extractedName = voiceText;

      // Extract price
      for (const pattern of pricePatterns) {
        const match = text.match(pattern);
        if (match) {
          extractedPrice = match[1];
          break;
        }
      }

      // Extract quantity
      for (const pattern of quantityPatterns) {
        const match = text.match(pattern);
        if (match) {
          if (match[2]) {
            extractedQuantity = `${match[1]} ${match[2]}`;
          } else {
            extractedQuantity = match[0];
          }
          break;
        }
      }

      // Extract product name (remove price and quantity mentions)
      let cleanName = voiceText;
      if (extractedPrice) {
        cleanName = cleanName.replace(new RegExp(`\\b${extractedPrice}\\s*(?:rupees?|रुपए|रूपये|ರೂಪಾಯಿ|ரூபாய்|రూபாயలు|രൂപ|rs|₹)\\b`, 'gi'), '');
      }
      if (extractedQuantity) {
        cleanName = cleanName.replace(new RegExp(extractedQuantity.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'), 'gi'), '');
      }
      cleanName = cleanName.replace(/(?:price|मूल्य|ಬೆಲೆ|விலை|ధర|വില)[:\s]*\d+/gi, '');
      cleanName = cleanName.replace(/(?:quantity|मात्रा|ಪ್ರಮಾಣ|அளவு|పరిమాణం|അളവ്)[:\s]*[\d\s\w]+/gi, '');
      cleanName = cleanName.trim();

      // Update form data
      setFormData(prev => ({
        ...prev,
        name: cleanName || prev.name,
        quantity: extractedQuantity || prev.quantity,
        price: extractedPrice || prev.price
      }));

      // Call callback if provided
      if (onVoiceInput) {
        onVoiceInput({
          name: cleanName,
          quantity: extractedQuantity,
          price: extractedPrice,
          fullText: voiceText
        });
      }

    } catch (error) {
      console.error('Error parsing voice input:', error);
      setVoiceError('Error parsing voice input');
    }
  };

  const startRecording = () => {
    if (recognitionRef.current && !isRecording) {
      setTranscript('');
      setVoiceError('');
      recognitionRef.current.lang = SPEECH_LANGUAGE_CODES[currentLanguage] || 'en-IN';
      recognitionRef.current.start();
      setIsRecording(true);
    }
  };

  const stopRecording = () => {
    if (recognitionRef.current && isRecording) {
      recognitionRef.current.stop();
      setIsRecording(false);
    }
  };

  const testVoiceDemo = () => {
    // Demo voice inputs for different languages
    const demoInputs = {
      english: "Fresh tomatoes 1 kg 50 rupees",
      hindi: "टमाटर 1 किलो 50 रुपए",
      kannada: "ಟೊಮೇಟೊ 1 ಕಿಲೋ 50 ರೂಪಾಯಿ",
      tamil: "தக்காளி 1 கிலோ 50 ரூபாய்",
      telugu: "టమాటాలు 1 కిలో 50 రూపాయలు",
      malayalam: "തക്കാളി 1 കിലോ 50 രൂപ"
    };

    const demoText = demoInputs[currentLanguage] || demoInputs.english;
    setTranscript(demoText);
    parseVoiceInput(demoText);
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (formData.name && formData.quantity && formData.price) {
      onSubmit(formData);
    }
  };

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  return (
    <div className="product-form-container">
      <VoiceButton 
        isRecording={isRecording}
        onStartRecording={startRecording}
        onStopRecording={stopRecording}
        isSupported={isVoiceSupported}
        language={currentLanguage}
        content={content}
        onTestVoice={testVoiceDemo}
      />
      
      {voiceError && (
        <div className="voice-error">
          <p>❌ {voiceError}</p>
          <p>💡 Make sure to allow microphone access when prompted</p>
        </div>
      )}
      
      <VoiceTranscript 
        transcript={transcript}
        isRecording={isRecording}
        content={content}
      />

      <form onSubmit={handleSubmit} className="product-form">
        <div className="form-group">
          <label htmlFor="name">{content.product_name}</label>
          <input
            type="text"
            id="name"
            name="name"
            value={formData.name}
            onChange={handleChange}
            placeholder={content.product_name}
            required
          />
        </div>

        <div className="form-row">
          <div className="form-group">
            <label htmlFor="quantity">{content.quantity}</label>
            <input
              type="text"
              id="quantity"
              name="quantity"
              value={formData.quantity}
              onChange={handleChange}
              placeholder="1 kg"
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="price">{content.price}</label>
            <input
              type="number"
              id="price"
              name="price"
              value={formData.price}
              onChange={handleChange}
              placeholder="50"
              required
            />
          </div>
        </div>

        <div className="form-group">
          <label htmlFor="additional_info">{content.additional_info}</label>
          <textarea
            id="additional_info"
            name="additional_info"
            value={formData.additional_info}
            onChange={handleChange}
            placeholder={content.additional_info}
            rows="3"
          />
        </div>

        <button type="submit" disabled={isLoading} className="submit-btn">
          {isLoading ? content.processing : content.generate_listing}
        </button>
      </form>
    </div>
  );
};

// Product listing display component
const ProductListing = ({ listing, content }) => {
  return (
    <div className="product-listing">
      <div className="listing-header">
        <h3>✅ {content.product_listing}</h3>
      </div>

      <div className="listing-content">
        <div className="product-basic-info">
          <div className="info-item">
            <span className="icon">🛒</span>
            <span className="label">Product:</span>
            <span className="value">{listing.name}</span>
          </div>
          <div className="info-item">
            <span className="icon">⚖️</span>
            <span className="label">Quantity:</span>
            <span className="value">{listing.quantity}</span>
          </div>
          <div className="info-item">
            <span className="icon">💰</span>
            <span className="label">Price:</span>
            <span className="value">₹{listing.price}</span>
          </div>
        </div>

        <div className="price-breakdown">
          <h4>🔁 {content.price_breakdown}:</h4>
          <div className="breakdown-items">
            {Object.entries(listing.price_breakdown).map(([quantity, price]) => (
              <div key={quantity} className="breakdown-item">
                <span>{quantity}:</span>
                <span>₹{price}</span>
              </div>
            ))}
          </div>
        </div>

        <div className="description">
          <h4>📝 {content.description}:</h4>
          <p>{listing.description}</p>
        </div>

        <div className="tags-category">
          <div className="tags">
            <h4>🏷️ {content.tags}:</h4>
            <div className="tag-list">
              {listing.tags.map((tag, index) => (
                <span key={index} className="tag">{tag}</span>
              ))}
            </div>
          </div>

          <div className="category">
            <h4>📁 {content.category}:</h4>
            <p>{listing.category}</p>
          </div>
        </div>
      </div>
    </div>
  );
};

// Main App component
function App() {
  const [currentLanguage, setCurrentLanguage] = useState('english');
  const [availableLanguages, setAvailableLanguages] = useState([]);
  const [languageContent, setLanguageContent] = useState({});
  const [sessionId, setSessionId] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [currentListing, setCurrentListing] = useState(null);
  const [allListings, setAllListings] = useState([]);
  const [showAllListings, setShowAllListings] = useState(false);
  const [error, setError] = useState('');

  // Initialize app
  useEffect(() => {
    initializeApp();
  }, []);

  // Load language content when language changes
  useEffect(() => {
    if (currentLanguage) {
      loadLanguageContent(currentLanguage);
    }
  }, [currentLanguage]);

  // Load listings when session changes
  useEffect(() => {
    if (sessionId) {
      loadListings();
    }
  }, [sessionId]);

  const initializeApp = async () => {
    try {
      // Generate session ID
      const newSessionId = 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
      setSessionId(newSessionId);

      // Load available languages
      const response = await axios.get(`${API}/languages`);
      setAvailableLanguages(response.data.languages);
      
      // Load initial language content
      await loadLanguageContent('english');
    } catch (error) {
      console.error('Failed to initialize app:', error);
      setError('Failed to initialize app');
    }
  };

  const loadLanguageContent = async (language) => {
    try {
      const response = await axios.get(`${API}/language/${language}`);
      setLanguageContent(response.data.content);
    } catch (error) {
      console.error('Failed to load language content:', error);
      setError('Failed to load language content');
    }
  };

  const loadListings = async () => {
    try {
      const response = await axios.get(`${API}/listings/${sessionId}`);
      setAllListings(response.data);
    } catch (error) {
      console.error('Failed to load listings:', error);
    }
  };

  const handleLanguageChange = (newLanguage) => {
    setCurrentLanguage(newLanguage);
    setError('');
  };

  const handleVoiceInput = (voiceData) => {
    console.log('Voice input received:', voiceData);
    // Additional voice input handling can be added here
  };

  const handleProductSubmit = async (formData) => {
    setIsLoading(true);
    setError('');
    
    try {
      const productData = {
        ...formData,
        price: parseFloat(formData.price),
        language: currentLanguage,
        session_id: sessionId
      };

      const response = await axios.post(`${API}/generate-listing`, productData);
      setCurrentListing(response.data);
      await loadListings(); // Reload all listings
    } catch (error) {
      console.error('Failed to generate listing:', error);
      setError(languageContent.error_occurred || 'An error occurred');
    } finally {
      setIsLoading(false);
    }
  };

  const handleClearAllListings = async () => {
    try {
      await axios.delete(`${API}/listings/${sessionId}`);
      setAllListings([]);
      setCurrentListing(null);
      setShowAllListings(false);
    } catch (error) {
      console.error('Failed to clear listings:', error);
      setError('Failed to clear listings');
    }
  };

  const toggleShowAllListings = () => {
    setShowAllListings(!showAllListings);
  };

  return (
    <div className="app">
      <header className="app-header">
        <div className="header-content">
          <h1>{languageContent.app_title || 'Digital Catalog Agent'}</h1>
          <p className="subtitle">{languageContent.subtitle || 'Create professional product listings with AI'}</p>
          <div className="voice-indicator">
            <span className="voice-icon">🎙️</span>
            <span className="voice-text">{languageContent.voice_enabled || 'Voice Enabled'}</span>
          </div>
          
          <LanguageSelector 
            currentLanguage={currentLanguage}
            onLanguageChange={handleLanguageChange}
            languages={availableLanguages}
          />
        </div>
      </header>

      <main className="app-main">
        {error && (
          <div className="error-message">
            <p>{error}</p>
          </div>
        )}

        <div className="input-section">
          <ProductInputForm 
            onSubmit={handleProductSubmit}
            isLoading={isLoading}
            content={languageContent}
            currentLanguage={currentLanguage}
            onVoiceInput={handleVoiceInput}
          />
        </div>

        {currentListing && (
          <div className="current-listing">
            <ProductListing 
              listing={currentListing} 
              content={languageContent}
            />
          </div>
        )}

        {allListings.length > 0 && (
          <div className="listings-section">
            <div className="listings-header">
              <button 
                onClick={toggleShowAllListings}
                className="toggle-listings-btn"
              >
                {showAllListings ? 'Hide' : 'Show'} {languageContent.my_listings} ({allListings.length})
              </button>
              
              <button 
                onClick={handleClearAllListings}
                className="clear-all-btn"
              >
                {languageContent.clear_all}
              </button>
            </div>

            {showAllListings && (
              <div className="all-listings">
                {allListings.map((listing) => (
                  <ProductListing 
                    key={listing.id}
                    listing={listing} 
                    content={languageContent}
                  />
                ))}
              </div>
            )}
          </div>
        )}

        {allListings.length === 0 && !currentListing && !isLoading && (
          <div className="empty-state">
            <p>{languageContent.no_listings || 'No listings found'}</p>
          </div>
        )}
      </main>
    </div>
  );
}

export default App;