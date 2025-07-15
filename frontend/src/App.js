import React, { useState, useEffect, useRef } from 'react';
import './App.css';

const App = () => {
  const [products, setProducts] = useState([]);
  const [isListening, setIsListening] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [response, setResponse] = useState('');
  const [language, setLanguage] = useState('en');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [lowStockAlerts, setLowStockAlerts] = useState([]);
  const [voiceSupported, setVoiceSupported] = useState(false);
  
  const recognitionRef = useRef(null);
  const synthRef = useRef(null);

  const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

  const languageConfig = {
    'en': { name: 'English', code: 'en-IN' },
    'hi': { name: 'हिंदी', code: 'hi-IN' },
    'kn': { name: 'ಕನ್ನಡ', code: 'kn-IN' },
    'ta': { name: 'தமிழ்', code: 'ta-IN' },
    'te': { name: 'తెలుగు', code: 'te-IN' }
  };

  useEffect(() => {
    initializeSpeechRecognition();
    initializeSpeechSynthesis();
    loadProducts();
  }, []);

  useEffect(() => {
    if (recognitionRef.current) {
      recognitionRef.current.lang = languageConfig[language].code;
    }
  }, [language]);

  const initializeSpeechRecognition = () => {
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
      setVoiceSupported(true);
    } else {
      setVoiceSupported(false);
      setError('Voice recognition not supported in this browser');
    }
  };

  const initializeSpeechSynthesis = () => {
    if ('speechSynthesis' in window) {
      synthRef.current = window.speechSynthesis;
    }
  };

  const loadProducts = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${BACKEND_URL}/api/products`);
      const data = await response.json();
      setProducts(data.products || []);
      setLowStockAlerts(data.low_stock_alerts || []);
    } catch (err) {
      setError('Failed to load products');
    } finally {
      setLoading(false);
    }
  };

  const processVoiceCommand = async (command) => {
    setLoading(true);
    setError('');
    
    try {
      const response = await fetch(`${BACKEND_URL}/api/voice-command`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          command: command,
          language: language
        }),
      });
      
      const data = await response.json();
      
      if (response.ok) {
        setResponse(JSON.stringify(data, null, 2));
        loadProducts(); // Refresh products list
        
        // Speak the response
        speakResponse(data);
      } else {
        setError(data.detail || 'Command processing failed');
      }
    } catch (err) {
      setError('Failed to process command');
    } finally {
      setLoading(false);
    }
  };

  const speakResponse = (data) => {
    if (!synthRef.current) return;
    
    let textToSpeak = '';
    
    if (data.message) {
      textToSpeak = data.message;
    } else if (data.product) {
      const breakdown = data.breakdown;
      textToSpeak = `${data.product} ${data.quantity} kg added at ₹${data.price_per_kg} per kg`;
      
      if (data.low_stock) {
        textToSpeak += '. Low stock alert!';
      }
    } else if (data.products) {
      textToSpeak = `You have ${data.total_products} products in inventory`;
      if (data.low_stock_alerts.length > 0) {
        textToSpeak += `. Warning: ${data.low_stock_alerts.length} products are low in stock`;
      }
    }
    
    if (textToSpeak) {
      // Stop any ongoing speech
      synthRef.current.cancel();
      
      const utterance = new SpeechSynthesisUtterance(textToSpeak);
      utterance.lang = languageConfig[language].code;
      utterance.rate = 0.8;
      utterance.pitch = 1;
      synthRef.current.speak(utterance);
    }
  };

  const startListening = () => {
    if (!voiceSupported) {
      setError('Voice recognition not supported in this browser');
      return;
    }

    if (recognitionRef.current && !isListening) {
      setTranscript('');
      setError('');
      setResponse('');
      
      try {
        recognitionRef.current.start();
      } catch (err) {
        setError('Failed to start voice recognition');
        console.error('Voice recognition error:', err);
      }
    }
  };

  const stopListening = () => {
    if (recognitionRef.current && isListening) {
      recognitionRef.current.stop();
    }
  };

  const formatPrice = (price) => {
    return `₹${price}`;
  };

  const ProductCard = ({ product }) => (
    <div className={`product-card ${product.low_stock ? 'low-stock' : ''}`}>
      <div className="product-header">
        <h3>{product.product}</h3>
        <div className="product-meta">
          <span className="quantity">{product.quantity} kg</span>
          <span className="price">{formatPrice(product.price_per_kg)}/kg</span>
        </div>
      </div>
      
      {product.low_stock && (
        <div className="stock-alert">
          ⚠️ Low Stock Alert
        </div>
      )}
      
      <div className="price-breakdown">
        <div className="breakdown-item">
          <span>1 kg</span>
          <span>{formatPrice(product.breakdown['1kg'])}</span>
        </div>
        <div className="breakdown-item">
          <span>½ kg</span>
          <span>{formatPrice(product.breakdown.half_kg)}</span>
        </div>
        <div className="breakdown-item">
          <span>¼ kg</span>
          <span>{formatPrice(product.breakdown.quarter_kg)}</span>
        </div>
      </div>
    </div>
  );

  return (
    <div className="app">
      <div className="container">
        <header className="header">
          <h1>🎤 Voice Catalog</h1>
          <p>Inventory management made simple</p>
        </header>

        <div className="controls">
          <div className="language-selector">
            <select 
              value={language} 
              onChange={(e) => setLanguage(e.target.value)}
              className="language-select"
            >
              {Object.entries(languageConfig).map(([code, config]) => (
                <option key={code} value={code}>{config.name}</option>
              ))}
            </select>
          </div>

          <div className="voice-section">
            <button
              className={`voice-btn ${isListening ? 'listening' : ''}`}
              onClick={isListening ? stopListening : startListening}
              disabled={loading || !voiceSupported}
            >
              {isListening ? '🛑 Stop' : '🎤 Speak'}
            </button>
            
            {isListening && (
              <div className="listening-indicator">
                <div className="pulse"></div>
                <span>Listening...</span>
              </div>
            )}
          </div>
        </div>

        {transcript && (
          <div className="transcript-section">
            <h3>Voice Command:</h3>
            <div className="transcript">{transcript}</div>
          </div>
        )}

        {error && (
          <div className="error-message">
            {error}
          </div>
        )}

        {loading && (
          <div className="loading">
            <div className="spinner"></div>
            <span>Processing...</span>
          </div>
        )}

        <div className="examples">
          <h3>Try saying:</h3>
          <div className="example-commands">
            <div>"Add 5 kg tomato at ₹50"</div>
            <div>"Update tomato price to ₹60"</div>
            <div>"Remove 2 kg onions"</div>
            <div>"List all products"</div>
          </div>
        </div>

        {lowStockAlerts.length > 0 && (
          <div className="stock-alerts">
            <h3>⚠️ Low Stock Alerts</h3>
            <div className="alerts-list">
              {lowStockAlerts.map((product, index) => (
                <div key={index} className="alert-item">
                  <strong>{product.product}</strong> - Only {product.quantity} kg left
                </div>
              ))}
            </div>
          </div>
        )}

        <div className="products-section">
          <div className="section-header">
            <h2>Inventory ({products.length} products)</h2>
            <button 
              onClick={loadProducts}
              className="refresh-btn"
              disabled={loading}
            >
              🔄 Refresh
            </button>
          </div>

          <div className="products-grid">
            {products.length === 0 ? (
              <div className="no-products">
                <p>No products in inventory</p>
                <p>Use voice commands to add products</p>
              </div>
            ) : (
              products.map((product, index) => (
                <ProductCard key={index} product={product} />
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default App;