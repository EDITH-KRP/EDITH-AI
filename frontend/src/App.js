import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

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
const ProductInputForm = ({ onSubmit, isLoading, content }) => {
  const [formData, setFormData] = useState({
    name: '',
    quantity: '',
    price: '',
    additional_info: ''
  });

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