import React, { useState, useEffect, useRef } from 'react';
import './App.css';

const API_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

// Authentication context
const AuthContext = React.createContext();

// Custom hook for authentication
const useAuth = () => {
  const context = React.useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

// Advanced Voice Recognition Hook with EDITH-AI integration
const useVoiceRecognition = () => {
  const [isListening, setIsListening] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [language, setLanguage] = useState('en-US');
  const [voiceSupported, setVoiceSupported] = useState(false);
  const recognitionRef = useRef(null);

  // Enhanced language configuration with regional support
  const languageConfig = {
    'en-US': { name: 'English', code: 'en-IN', apiCode: 'en' },
    'hi-IN': { name: 'हिंदी', code: 'hi-IN', apiCode: 'hi' },
    'kn-IN': { name: 'ಕನ್ನಡ', code: 'kn-IN', apiCode: 'kn' },
    'ta-IN': { name: 'தமிழ்', code: 'ta-IN', apiCode: 'ta' },
    'te-IN': { name: 'తెలుగు', code: 'te-IN', apiCode: 'te' }
  };

  useEffect(() => {
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
      setVoiceSupported(true);
      initializeSpeechRecognition();
    } else {
      setVoiceSupported(false);
      console.error('Speech recognition not supported in this browser');
    }
  }, [language]);

  const initializeSpeechRecognition = () => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    const recognition = new SpeechRecognition();
    
    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.lang = languageConfig[language]?.code || 'en-US';
    recognition.maxAlternatives = 1;

    recognition.onresult = (event) => {
      const finalTranscript = event.results[0][0].transcript;
      setTranscript(finalTranscript);
      console.log('Voice input:', finalTranscript);
    };

    recognition.onerror = (event) => {
      console.error('Speech recognition error:', event.error);
      setIsListening(false);
    };

    recognition.onend = () => {
      setIsListening(false);
    };

    recognition.onstart = () => {
      setIsListening(true);
    };

    recognitionRef.current = recognition;
  };

  const startListening = () => {
    if (recognitionRef.current && voiceSupported) {
      setTranscript('');
      try {
        recognitionRef.current.start();
      } catch (error) {
        console.error('Error starting recognition:', error);
        setIsListening(false);
      }
    }
  };

  const stopListening = () => {
    if (recognitionRef.current) {
      try {
        recognitionRef.current.stop();
      } catch (error) {
        console.error('Error stopping recognition:', error);
      }
      setIsListening(false);
    }
  };

  const getLanguageCode = () => {
    return languageConfig[language]?.apiCode || 'en';
  };

  return {
    isListening,
    transcript,
    startListening,
    stopListening,
    setLanguage,
    voiceSupported,
    getLanguageCode,
    languageConfig
  };
};

// Enhanced Text-to-speech hook with multilingual support
const useTextToSpeech = () => {
  const [isSpeaking, setIsSpeaking] = useState(false);
  const synthRef = useRef(null);

  useEffect(() => {
    if ('speechSynthesis' in window) {
      synthRef.current = window.speechSynthesis;
    }
  }, []);

  const speak = (text, lang = 'en-US') => {
    if ('speechSynthesis' in window && synthRef.current) {
      // Cancel any ongoing speech
      synthRef.current.cancel();
      
      const utterance = new SpeechSynthesisUtterance(text);
      
      // Set language based on input
      const langMapping = {
        'en': 'en-US',
        'hi': 'hi-IN',
        'kn': 'kn-IN',
        'ta': 'ta-IN',
        'te': 'te-IN'
      };
      
      utterance.lang = langMapping[lang] || lang;
      utterance.rate = 0.9;
      utterance.pitch = 1.0;
      utterance.volume = 1.0;
      
      utterance.onstart = () => setIsSpeaking(true);
      utterance.onend = () => setIsSpeaking(false);
      utterance.onerror = (event) => {
        console.error('Speech synthesis error:', event.error);
        setIsSpeaking(false);
      };
      
      synthRef.current.speak(utterance);
    }
  };

  const stop = () => {
    if ('speechSynthesis' in window && synthRef.current) {
      synthRef.current.cancel();
      setIsSpeaking(false);
    }
  };

  return { speak, stop, isSpeaking };
};

// Language configuration
const languages = {
  'en-US': { name: 'English', code: 'en' },
  'hi-IN': { name: 'हिंदी', code: 'hi' },
  'kn-IN': { name: 'ಕನ್ನಡ', code: 'kn' },
  'te-IN': { name: 'తెలుగు', code: 'te' }
};

// Homepage component
const Homepage = () => {
  const [showLogin, setShowLogin] = useState(false);
  const [showSignup, setShowSignup] = useState(false);

  return (
    <div className="homepage">
      {/* Hero Section */}
      <section className="hero">
        <div className="hero-content">
          <div className="hero-text">
            <h1 className="hero-title">
              Voice-First AI Commerce
              <span className="highlight">for Rural Vendors</span>
            </h1>
            <p className="hero-subtitle">
              Empower your business with multilingual AI assistance. Manage inventory, 
              connect with customers, and grow your sales - all with your voice.
            </p>
            <div className="hero-buttons">
              <button 
                className="btn btn-primary"
                onClick={() => setShowSignup(true)}
              >
                Start Selling
              </button>
              <button 
                className="btn btn-secondary"
                onClick={() => setShowLogin(true)}
              >
                I'm a Buyer
              </button>
            </div>
          </div>
          <div className="hero-image">
            <img 
              src="https://images.unsplash.com/photo-1734255287995-7c09dbc99613" 
              alt="Rural vendor"
              className="hero-img"
            />
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="features">
        <div className="container">
          <h2 className="section-title">Features Built for You</h2>
          <div className="features-grid">
            <div className="feature-card">
              <div className="feature-icon">🎙️</div>
              <h3>Voice Commands</h3>
              <p>Add products, update prices, and manage inventory with simple voice commands in your language.</p>
            </div>
            <div className="feature-card">
              <div className="feature-icon">🧠</div>
              <h3>AI Suggestions</h3>
              <p>Get smart pricing recommendations and business insights powered by AI.</p>
            </div>
            <div className="feature-card">
              <div className="feature-icon">📱</div>
              <h3>Real-time Sync</h3>
              <p>Instant inventory updates between seller and buyer dashboards.</p>
            </div>
            <div className="feature-card">
              <div className="feature-icon">🌐</div>
              <h3>Multilingual</h3>
              <p>Support for Hindi, Kannada, Telugu, and other regional languages.</p>
            </div>
          </div>
        </div>
      </section>

      {/* How it Works Section */}
      <section className="how-it-works">
        <div className="container">
          <h2 className="section-title">How It Works</h2>
          <div className="steps">
            <div className="step">
              <div className="step-number">1</div>
              <h3>Sign Up</h3>
              <p>Create your account as a seller or buyer</p>
            </div>
            <div className="step">
              <div className="step-number">2</div>
              <h3>Voice Setup</h3>
              <p>Choose your language and start speaking</p>
            </div>
            <div className="step">
              <div className="step-number">3</div>
              <h3>Start Trading</h3>
              <p>Add products, connect with customers, grow your business</p>
            </div>
          </div>
        </div>
      </section>

      {/* Testimonials Section */}
      <section className="testimonials">
        <div className="container">
          <h2 className="section-title">What Our Users Say</h2>
          <div className="testimonials-grid">
            <div className="testimonial">
              <p>"This app changed how I sell vegetables. I can update prices while serving customers!"</p>
              <div className="testimonial-author">- Ravi Kumar, Tomato Seller</div>
            </div>
            <div className="testimonial">
              <p>"Finding fresh produce is so easy now. The voice search helps me order quickly."</p>
              <div className="testimonial-author">- Priya Sharma, Customer</div>
            </div>
          </div>
        </div>
      </section>

      {/* Login/Signup Modals */}
      {showLogin && (
        <LoginModal 
          onClose={() => setShowLogin(false)} 
          onSwitchToSignup={() => {
            setShowLogin(false);
            setShowSignup(true);
          }}
        />
      )}
      {showSignup && (
        <SignupModal 
          onClose={() => setShowSignup(false)} 
          onSwitchToLogin={() => {
            setShowSignup(false);
            setShowLogin(true);
          }}
        />
      )}
    </div>
  );
};

// Login modal component
const LoginModal = ({ onClose, onSwitchToSignup }) => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const { login } = useAuth();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const response = await fetch(`${API_URL}/api/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, password }),
      });

      const data = await response.json();

      if (response.ok) {
        login(data.token, data.user);
        onClose();
      } else {
        setError(data.detail || 'Login failed');
      }
    } catch (err) {
      setError('Network error. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="modal-overlay">
      <div className="modal">
        <div className="modal-header">
          <h2>Login</h2>
          <button className="close-btn" onClick={onClose}>×</button>
        </div>
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>Email</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </div>
          <div className="form-group">
            <label>Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </div>
          {error && <div className="error-message">{error}</div>}
          <button type="submit" className="btn btn-primary" disabled={loading}>
            {loading ? 'Logging in...' : 'Login'}
          </button>
        </form>
        <p className="switch-auth">
          Don't have an account? 
          <button className="link-btn" onClick={onSwitchToSignup}>
            Sign up
          </button>
        </p>
      </div>
    </div>
  );
};

// Signup modal component
const SignupModal = ({ onClose, onSwitchToLogin }) => {
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [role, setRole] = useState('seller');
  const [language, setLanguage] = useState('en');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const { login } = useAuth();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const response = await fetch(`${API_URL}/api/auth/signup`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ username, email, password, role, language }),
      });

      const data = await response.json();

      if (response.ok) {
        login(data.token, data.user);
        onClose();
      } else {
        setError(data.detail || 'Signup failed');
      }
    } catch (err) {
      setError('Network error. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="modal-overlay">
      <div className="modal">
        <div className="modal-header">
          <h2>Sign Up</h2>
          <button className="close-btn" onClick={onClose}>×</button>
        </div>
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>Username</label>
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
            />
          </div>
          <div className="form-group">
            <label>Email</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </div>
          <div className="form-group">
            <label>Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </div>
          <div className="form-group">
            <label>I am a</label>
            <select value={role} onChange={(e) => setRole(e.target.value)}>
              <option value="seller">Seller</option>
              <option value="consumer">Buyer</option>
            </select>
          </div>
          <div className="form-group">
            <label>Preferred Language</label>
            <select value={language} onChange={(e) => setLanguage(e.target.value)}>
              <option value="en">English</option>
              <option value="hi">हिंदी</option>
              <option value="kn">ಕನ್ನಡ</option>
              <option value="te">తెలుగు</option>
            </select>
          </div>
          {error && <div className="error-message">{error}</div>}
          <button type="submit" className="btn btn-primary" disabled={loading}>
            {loading ? 'Creating Account...' : 'Sign Up'}
          </button>
        </form>
        <p className="switch-auth">
          Already have an account? 
          <button className="link-btn" onClick={onSwitchToLogin}>
            Login
          </button>
        </p>
      </div>
    </div>
  );
};

// Voice command component
const VoiceCommands = ({ onCommandProcessed }) => {
  const { isListening, transcript, startListening, stopListening, setLanguage } = useVoiceRecognition();
  const { speak } = useTextToSpeech();
  const [processing, setProcessing] = useState(false);
  const [selectedLanguage, setSelectedLanguage] = useState('en-US');
  const { user } = useAuth();

  const handleLanguageChange = (lang) => {
    setSelectedLanguage(lang);
    setLanguage(lang);
  };

  const processCommand = async (command) => {
    if (!command.trim()) return;

    setProcessing(true);
    try {
      const response = await fetch(`${API_URL}/api/voice/process`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({
          command,
          language: languages[selectedLanguage]?.code || 'en',
          seller_id: user?.id
        })
      });

      const data = await response.json();
      
      if (response.ok) {
        speak(data.message, selectedLanguage);
        onCommandProcessed(data);
      } else {
        throw new Error(data.detail || 'Failed to process command');
      }
    } catch (error) {
      console.error('Voice command error:', error);
      speak('Sorry, I could not process that command.', selectedLanguage);
    } finally {
      setProcessing(false);
    }
  };

  useEffect(() => {
    if (transcript && !isListening) {
      processCommand(transcript);
    }
  }, [transcript, isListening]);

  return (
    <div className="voice-commands">
      <div className="voice-controls">
        <div className="language-selector">
          <label>Language:</label>
          <select 
            value={selectedLanguage} 
            onChange={(e) => handleLanguageChange(e.target.value)}
          >
            {Object.entries(languages).map(([code, lang]) => (
              <option key={code} value={code}>{lang.name}</option>
            ))}
          </select>
        </div>
        
        <button 
          className={`voice-btn ${isListening ? 'listening' : ''}`}
          onClick={isListening ? stopListening : startListening}
          disabled={processing}
        >
          {isListening ? '🔴 Stop' : '🎙️ Start Voice'}
        </button>
      </div>

      {transcript && (
        <div className="transcript">
          <strong>You said:</strong> {transcript}
        </div>
      )}

      {processing && (
        <div className="processing">
          <div className="spinner"></div>
          Processing command...
        </div>
      )}

      <div className="voice-examples">
        <h4>Try saying:</h4>
        <ul>
          <li>"Add 5 kg tomatoes at ₹40"</li>
          <li>"Update onion price to ₹35"</li>
          <li>"Remove 2 kg potatoes"</li>
          <li>"What's my current stock?"</li>
        </ul>
      </div>
    </div>
  );
};

// Seller dashboard component
const SellerDashboard = () => {
  const [products, setProducts] = useState([]);
  const [orders, setOrders] = useState([]);
  const [suggestions, setSuggestions] = useState('');
  const [showAddProduct, setShowAddProduct] = useState(false);
  const [loading, setLoading] = useState(true);
  const { user } = useAuth();

  const loadData = async () => {
    try {
      const [productsRes, ordersRes, suggestionsRes] = await Promise.all([
        fetch(`${API_URL}/api/products`, {
          headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
        }),
        fetch(`${API_URL}/api/orders`, {
          headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
        }),
        fetch(`${API_URL}/api/suggestions`, {
          headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
        })
      ]);

      const [productsData, ordersData, suggestionsData] = await Promise.all([
        productsRes.json(),
        ordersRes.json(),
        suggestionsRes.json()
      ]);

      setProducts(productsData.products || []);
      setOrders(ordersData.orders || []);
      setSuggestions(suggestionsData.suggestions || '');
    } catch (error) {
      console.error('Error loading data:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleCommandProcessed = (data) => {
    // Reload data after voice command
    loadData();
  };

  if (loading) {
    return <div className="loading">Loading your dashboard...</div>;
  }

  return (
    <div className="dashboard seller-dashboard">
      <div className="dashboard-header">
        <h1>Seller Dashboard</h1>
        <p>Welcome back, {user?.username}!</p>
      </div>

      <div className="dashboard-content">
        <div className="dashboard-sidebar">
          <VoiceCommands onCommandProcessed={handleCommandProcessed} />
          
          <div className="ai-suggestions">
            <h3>AI Suggestions</h3>
            <div className="suggestions-content">
              {suggestions || 'Loading suggestions...'}
            </div>
          </div>
        </div>

        <div className="dashboard-main">
          <div className="stats-cards">
            <div className="stat-card">
              <h3>Total Products</h3>
              <div className="stat-value">{products.length}</div>
            </div>
            <div className="stat-card">
              <h3>Pending Orders</h3>
              <div className="stat-value">{orders.filter(o => o.status === 'pending').length}</div>
            </div>
            <div className="stat-card">
              <h3>Low Stock Items</h3>
              <div className="stat-value">{products.filter(p => p.quantity < 2).length}</div>
            </div>
          </div>

          <div className="products-section">
            <div className="section-header">
              <h2>Your Products</h2>
              <button 
                className="btn btn-primary"
                onClick={() => setShowAddProduct(true)}
              >
                Add Product
              </button>
            </div>

            <div className="products-grid">
              {products.map(product => (
                <ProductCard key={product._id} product={product} isOwner={true} />
              ))}
            </div>
          </div>

          <div className="orders-section">
            <h2>Recent Orders</h2>
            <div className="orders-list">
              {orders.map(order => (
                <OrderCard key={order._id} order={order} />
              ))}
            </div>
          </div>
        </div>
      </div>

      {showAddProduct && (
        <AddProductModal 
          onClose={() => setShowAddProduct(false)} 
          onProductAdded={loadData}
        />
      )}
    </div>
  );
};

// Consumer dashboard component
const ConsumerDashboard = () => {
  const [products, setProducts] = useState([]);
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);
  const { user } = useAuth();

  const loadData = async () => {
    try {
      const [productsRes, ordersRes] = await Promise.all([
        fetch(`${API_URL}/api/products`, {
          headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
        }),
        fetch(`${API_URL}/api/orders`, {
          headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
        })
      ]);

      const [productsData, ordersData] = await Promise.all([
        productsRes.json(),
        ordersRes.json()
      ]);

      setProducts(productsData.products || []);
      setOrders(ordersData.orders || []);
    } catch (error) {
      console.error('Error loading data:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  if (loading) {
    return <div className="loading">Loading marketplace...</div>;
  }

  return (
    <div className="dashboard consumer-dashboard">
      <div className="dashboard-header">
        <h1>Marketplace</h1>
        <p>Welcome, {user?.username}!</p>
      </div>

      <div className="dashboard-content">
        <div className="products-section">
          <h2>Available Products</h2>
          <div className="products-grid">
            {products.map(product => (
              <ProductCard 
                key={product._id} 
                product={product} 
                isOwner={false}
                onOrderPlaced={loadData}
              />
            ))}
          </div>
        </div>

        <div className="orders-section">
          <h2>Your Orders</h2>
          <div className="orders-list">
            {orders.map(order => (
              <OrderCard key={order._id} order={order} />
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

// Product card component
const ProductCard = ({ product, isOwner, onOrderPlaced }) => {
  const [showOrderModal, setShowOrderModal] = useState(false);

  const priceBreakdown = {
    "1kg": product.price_per_unit,
    "1/2kg": Math.round(product.price_per_unit / 2),
    "1/4kg": Math.round(product.price_per_unit / 4)
  };

  return (
    <div className="product-card">
      {product.image_base64 && (
        <img 
          src={`data:image/png;base64,${product.image_base64}`} 
          alt={product.name}
          className="product-image"
        />
      )}
      
      <div className="product-info">
        <h3>{product.name}</h3>
        <p className="product-quantity">
          Available: {product.quantity} {product.unit}
        </p>
        
        <div className="price-breakdown">
          <div className="price-item">
            <span>1 {product.unit}</span>
            <span>₹{priceBreakdown["1kg"]}</span>
          </div>
          <div className="price-item">
            <span>1/2 {product.unit}</span>
            <span>₹{priceBreakdown["1/2kg"]}</span>
          </div>
          <div className="price-item">
            <span>1/4 {product.unit}</span>
            <span>₹{priceBreakdown["1/4kg"]}</span>
          </div>
        </div>

        {product.description && (
          <p className="product-description">{product.description}</p>
        )}

        <div className="product-actions">
          {isOwner ? (
            <button className="btn btn-secondary">Edit</button>
          ) : (
            <button 
              className="btn btn-primary"
              onClick={() => setShowOrderModal(true)}
              disabled={product.quantity <= 0}
            >
              {product.quantity <= 0 ? 'Out of Stock' : 'Order Now'}
            </button>
          )}
        </div>
      </div>

      {showOrderModal && (
        <OrderModal 
          product={product}
          onClose={() => setShowOrderModal(false)}
          onOrderPlaced={onOrderPlaced}
        />
      )}
    </div>
  );
};

// Order card component
const OrderCard = ({ order }) => {
  return (
    <div className="order-card">
      <div className="order-info">
        <h4>Order #{order._id.slice(-6)}</h4>
        <p>Quantity: {order.quantity}</p>
        <p>Total: ₹{order.total_price}</p>
        <p>Status: <span className={`status ${order.status}`}>{order.status}</span></p>
      </div>
    </div>
  );
};

// Add product modal
const AddProductModal = ({ onClose, onProductAdded }) => {
  const [name, setName] = useState('');
  const [quantity, setQuantity] = useState('');
  const [unit, setUnit] = useState('kg');
  const [pricePerUnit, setPricePerUnit] = useState('');
  const [description, setDescription] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const response = await fetch(`${API_URL}/api/products`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({
          name,
          quantity: parseFloat(quantity),
          unit,
          price_per_unit: parseFloat(pricePerUnit),
          description,
          tags: [],
          seller_id: '',
          language: 'en'
        })
      });

      const data = await response.json();

      if (response.ok) {
        onProductAdded();
        onClose();
      } else {
        setError(data.detail || 'Failed to add product');
      }
    } catch (err) {
      setError('Network error. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="modal-overlay">
      <div className="modal">
        <div className="modal-header">
          <h2>Add New Product</h2>
          <button className="close-btn" onClick={onClose}>×</button>
        </div>
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>Product Name</label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              required
            />
          </div>
          <div className="form-group">
            <label>Quantity</label>
            <input
              type="number"
              step="0.1"
              value={quantity}
              onChange={(e) => setQuantity(e.target.value)}
              required
            />
          </div>
          <div className="form-group">
            <label>Unit</label>
            <select value={unit} onChange={(e) => setUnit(e.target.value)}>
              <option value="kg">kg</option>
              <option value="piece">piece</option>
              <option value="bunch">bunch</option>
              <option value="packet">packet</option>
            </select>
          </div>
          <div className="form-group">
            <label>Price per {unit}</label>
            <input
              type="number"
              step="0.01"
              value={pricePerUnit}
              onChange={(e) => setPricePerUnit(e.target.value)}
              required
            />
          </div>
          <div className="form-group">
            <label>Description</label>
            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              rows="3"
            />
          </div>
          {error && <div className="error-message">{error}</div>}
          <button type="submit" className="btn btn-primary" disabled={loading}>
            {loading ? 'Adding Product...' : 'Add Product'}
          </button>
        </form>
      </div>
    </div>
  );
};

// Order modal
const OrderModal = ({ product, onClose, onOrderPlaced }) => {
  const [quantity, setQuantity] = useState(1);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const { user } = useAuth();

  const totalPrice = quantity * product.price_per_unit;

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const response = await fetch(`${API_URL}/api/orders`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({
          product_id: product._id,
          quantity,
          consumer_id: user?.id,
          seller_id: product.seller_id,
          total_price: totalPrice
        })
      });

      const data = await response.json();

      if (response.ok) {
        onOrderPlaced();
        onClose();
      } else {
        setError(data.detail || 'Failed to place order');
      }
    } catch (err) {
      setError('Network error. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="modal-overlay">
      <div className="modal">
        <div className="modal-header">
          <h2>Place Order</h2>
          <button className="close-btn" onClick={onClose}>×</button>
        </div>
        <div className="order-summary">
          <h3>{product.name}</h3>
          <p>Available: {product.quantity} {product.unit}</p>
          <p>Price: ₹{product.price_per_unit} per {product.unit}</p>
        </div>
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>Quantity ({product.unit})</label>
            <input
              type="number"
              min="0.1"
              max={product.quantity}
              step="0.1"
              value={quantity}
              onChange={(e) => setQuantity(parseFloat(e.target.value))}
              required
            />
          </div>
          <div className="total-price">
            <strong>Total: ₹{totalPrice.toFixed(2)}</strong>
          </div>
          {error && <div className="error-message">{error}</div>}
          <button type="submit" className="btn btn-primary" disabled={loading}>
            {loading ? 'Placing Order...' : 'Place Order'}
          </button>
        </form>
      </div>
    </div>
  );
};

// Main App component
const App = () => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem('token');
    const userData = localStorage.getItem('user');
    
    if (token && userData) {
      try {
        setUser(JSON.parse(userData));
      } catch (error) {
        console.error('Error parsing user data:', error);
        localStorage.removeItem('token');
        localStorage.removeItem('user');
      }
    }
    setLoading(false);
  }, []);

  const login = (token, userData) => {
    localStorage.setItem('token', token);
    localStorage.setItem('user', JSON.stringify(userData));
    setUser(userData);
  };

  const logout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    setUser(null);
  };

  if (loading) {
    return <div className="loading">Loading...</div>;
  }

  return (
    <AuthContext.Provider value={{ user, login, logout }}>
      <div className="app">
        <header className="app-header">
          <div className="header-content">
            <h1 className="logo">VoiceCart AI</h1>
            {user && (
              <div className="user-info">
                <span>Welcome, {user.username}</span>
                <button className="btn btn-outline" onClick={logout}>
                  Logout
                </button>
              </div>
            )}
          </div>
        </header>

        <main className="app-main">
          {!user ? (
            <Homepage />
          ) : user.role === 'seller' ? (
            <SellerDashboard />
          ) : (
            <ConsumerDashboard />
          )}
        </main>
      </div>
    </AuthContext.Provider>
  );
};

export default App;