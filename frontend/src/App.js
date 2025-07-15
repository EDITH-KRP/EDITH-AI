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
  
  const recognitionRef = useRef(null);
  const synthRef = useRef(null);

  const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

  useEffect(() => {
    // Initialize speech recognition
    if ('webkitSpeechRecognition' in window) {
      recognitionRef.current = new window.webkitSpeechRecognition();
      recognitionRef.current.continuous = false;
      recognitionRef.current.interimResults = false;
      recognitionRef.current.lang = language === 'kn' ? 'kn-IN' : language === 'hi' ? 'hi-IN' : 'en-IN';
      
      recognitionRef.current.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        setTranscript(transcript);
        processVoiceCommand(transcript);
      };
      
      recognitionRef.current.onend = () => {
        setIsListening(false);
      };
      
      recognitionRef.current.onerror = (event) => {
        setError('Speech recognition error: ' + event.error);
        setIsListening(false);
      };
    }

    // Initialize speech synthesis
    if ('speechSynthesis' in window) {
      synthRef.current = window.speechSynthesis;
    }

    // Load products on mount
    loadProducts();
  }, [language]);

  const loadProducts = async () => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/products`);
      const data = await response.json();
      setProducts(data.products || []);
      setLowStockAlerts(data.low_stock_alerts || []);
    } catch (err) {
      setError('Failed to load products');
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
    
    if (data.product) {
      const breakdown = data.breakdown;
      if (language === 'kn' && data.message_kn) {
        textToSpeak = data.message_kn;
      } else if (language === 'hi' && data.message_hi) {
        textToSpeak = data.message_hi;
      } else {
        textToSpeak = `${data.product} ${data.quantity} kg added at ₹${data.price_per_kg} per kg. 1 kg costs ₹${breakdown['1kg']}, half kg costs ₹${breakdown.half_kg}, quarter kg costs ₹${breakdown.quarter_kg}`;
      }
      
      if (data.low_stock) {
        textToSpeak += '. Alert: Low stock remaining!';
      }
    } else if (data.products) {
      textToSpeak = `You have ${data.total_products} products in inventory.`;
      if (data.low_stock_alerts.length > 0) {
        textToSpeak += ` Warning: ${data.low_stock_alerts.length} products are low in stock.`;
      }
    } else if (data.message) {
      textToSpeak = data.message;
    }
    
    if (textToSpeak) {
      const utterance = new SpeechSynthesisUtterance(textToSpeak);
      utterance.lang = language === 'kn' ? 'kn-IN' : language === 'hi' ? 'hi-IN' : 'en-IN';
      utterance.rate = 0.8;
      synthRef.current.speak(utterance);
    }
  };

  const startListening = () => {
    if (recognitionRef.current && !isListening) {
      setIsListening(true);
      setTranscript('');
      setError('');
      recognitionRef.current.start();
    }
  };

  const stopListening = () => {
    if (recognitionRef.current && isListening) {
      recognitionRef.current.stop();
      setIsListening(false);
    }
  };

  const formatPrice = (price) => {
    return `₹${price}`;
  };

  const ProductCard = ({ product }) => (
    <div className={`product-card ${product.low_stock ? 'low-stock' : ''}`}>
      <div className="product-header">
        <h3>🛒 {product.product}</h3>
        {product.low_stock && (
          <span className="low-stock-badge">⚠️ Low Stock</span>
        )}
      </div>
      
      <div className="product-details">
        <div className="quantity-price">
          <span className="quantity">⚖️ {product.quantity} kg</span>
          <span className="price">💰 {formatPrice(product.price_per_kg)}/kg</span>
        </div>
        
        <div className="price-breakdown">
          <h4>📊 Price Breakdown:</h4>
          <div className="breakdown-grid">
            <div className="breakdown-item">
              <span>1 kg:</span>
              <span>{formatPrice(product.breakdown['1kg'])}</span>
            </div>
            <div className="breakdown-item">
              <span>½ kg:</span>
              <span>{formatPrice(product.breakdown.half_kg)}</span>
            </div>
            <div className="breakdown-item">
              <span>¼ kg:</span>
              <span>{formatPrice(product.breakdown.quarter_kg)}</span>
            </div>
          </div>
        </div>
        
        {product.description && (
          <div className="description">
            <strong>📝 Description:</strong> {product.description}
          </div>
        )}
        
        <div className="category-tags">
          <span className="category">📂 {product.category}</span>
        </div>
      </div>
    </div>
  );

  return (
    <div className="app">
      <div className="container">
        <header className="header">
          <h1>🎤 Voice Catalog Assistant</h1>
          <p className="subtitle">Voice-powered inventory management for rural vendors</p>
        </header>

        <div className="controls">
          <div className="language-selector">
            <label>🌐 Language:</label>
            <select 
              value={language} 
              onChange={(e) => setLanguage(e.target.value)}
              className="language-select"
            >
              <option value="en">English</option>
              <option value="hi">हिंदी (Hindi)</option>
              <option value="kn">ಕನ್ನಡ (Kannada)</option>
            </select>
          </div>

          <div className="voice-controls">
            <button
              className={`voice-btn ${isListening ? 'listening' : ''}`}
              onClick={isListening ? stopListening : startListening}
              disabled={loading}
            >
              {isListening ? '🛑 Stop' : '🎤 Start Voice'}
            </button>
            
            {isListening && (
              <div className="listening-indicator">
                <span className="pulse"></span>
                Listening...
              </div>
            )}
          </div>
        </div>

        {transcript && (
          <div className="transcript-section">
            <h3>🗣️ Voice Command:</h3>
            <div className="transcript">{transcript}</div>
          </div>
        )}

        <div className="example-commands">
          <h3>📝 Example Commands:</h3>
          <div className="command-grid">
            <div className="command-item">💼 "Add 5 kg tomato at ₹50"</div>
            <div className="command-item">💰 "Update tomato price to ₹60"</div>
            <div className="command-item">📦 "Remove 2 kg onions"</div>
            <div className="command-item">🗑️ "Delete banana"</div>
            <div className="command-item">📋 "List all products"</div>
          </div>
        </div>

        {error && (
          <div className="error-message">
            ⚠️ {error}
          </div>
        )}

        {loading && (
          <div className="loading">
            <div className="spinner"></div>
            Processing command...
          </div>
        )}

        {response && (
          <div className="response-section">
            <h3>📱 System Response:</h3>
            <pre className="response">{response}</pre>
          </div>
        )}

        {lowStockAlerts.length > 0 && (
          <div className="stock-alerts">
            <h3>🔔 Stock Alerts:</h3>
            {lowStockAlerts.map((product, index) => (
              <div key={index} className="alert-item">
                ⚠️ {product.product} - Only {product.quantity} kg left! Restock soon.
              </div>
            ))}
          </div>
        )}

        <div className="products-section">
          <div className="products-header">
            <h2>📦 Current Inventory ({products.length} products)</h2>
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
                <p>🛒 No products in inventory</p>
                <p>Try saying: "Add 5 kg tomato at ₹50"</p>
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