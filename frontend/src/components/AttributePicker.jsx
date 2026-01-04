import React, { useState, useEffect } from 'react';

function AttributePicker({ onSearch }) {
  const [criteria, setCriteria] = useState({
    search_type: 'rent',
    max_monthly_rent: 1000,
    max_purchase_price: 200000,
    desired_m2: 60,
    property_type: 'apartment',
    has_car: false,
    workplace_city_code: '',
    max_commute_minutes: 60,
    weights: {
      affordability: 0,
      demographics: 0,
      transportation: 0,
      healthcare: 0,
      education: 0,
      weather: 0,
      price_diversity: 0,
      market_liquidity: 0
    }
  });

  const [allCities, setAllCities] = useState([]);
  const [loadingCities, setLoadingCities] = useState(true);
  const [showInfoModal, setShowInfoModal] = useState(false);

  // Fetch all cities for workplace dropdown
  useEffect(() => {
    fetch('http://localhost:5000/api/municipalities/all')
      .then(res => res.json())
      .then(data => {
        setAllCities(data.cities || []);
        setLoadingCities(false);
      })
      .catch(err => {
        console.error('Failed to load cities:', err);
        setLoadingCities(false);
      });
  }, []);

  const handleChange = (field, value) => {
    setCriteria(prev => {
      if (field === 'workplace_city_code') {
        const normalized = value ? String(value).padStart(3, '0') : '';
        if (!normalized) {
          return { ...prev, workplace_city_code: '', max_commute_minutes: 60 };
        }
        return { ...prev, workplace_city_code: normalized };
      }

      return { ...prev, [field]: value };
    });
  };

  const handleWeightChange = (category, value) => {
    setCriteria(prev => ({
      ...prev,
      weights: {
        ...prev.weights,
        [category]: parseInt(value)
      }
    }));
  };

  const handleSubmit = () => {
    onSearch(criteria);
  };

  const getSliderStyle = (value, min, max) => {
    const percentage = ((value - min) / (max - min)) * 100;
    return {
      '--value': `${percentage}%`
    };
  };

  return (
    <div className="attribute-picker">
      <div className="picker-header" style={{ position: 'relative' }}>
        <h2>Find Your Perfect City</h2>
        <p>Set your preferences and priorities</p>
        <button
          type="button"
          className="info-button"
          onClick={() => setShowInfoModal(true)}
          title="How scores are calculated"
        >
          ℹ️ Info
        </button>
      </div>

      {/* Info Modal */}
      {showInfoModal && (
        <div className="info-modal-overlay" onClick={() => setShowInfoModal(false)}>
          <div className="info-modal" onClick={(e) => e.stopPropagation()}>
            <div className="info-modal-header">
              <h2>📊 How Scores Are Calculated</h2>
              <button className="close-modal-btn" onClick={() => setShowInfoModal(false)}>×</button>
            </div>
            <div className="info-modal-content">
              <section>
                <h3>💰 Affordability</h3>
                <p>
                  Measures how affordable properties are relative to your budget. 
                  Calculated by comparing the average price per m² in each municipality 
                  against your specified budget and desired space.
                </p>
                <ul>
                  <li><strong>For Rent:</strong> Monthly rent × 12 months compared to annual budget capacity</li>
                  <li><strong>For Purchase:</strong> Price per m² × desired space compared to your max budget</li>
                  <li>Score 100 = You can easily afford the desired space</li>
                  <li>Score 0 = Properties exceed your budget significantly</li>
                </ul>
              </section>

              <section>
                <h3>📊 Market Activity</h3>
                <p>
                  Indicates how active the real estate market is in each municipality.
                  Based on the number of property deals recorded in recent data.
                </p>
                <ul>
                  <li>Higher deal count = More options available</li>
                  <li>Normalized across all municipalities (highest gets 100)</li>
                  <li>Low activity might mean fewer choices but also less competition</li>
                </ul>
              </section>

              <section>
                <h3>👥 Demographics / Population Vitality</h3>
                <p>
                  Evaluates the age distribution of the population.
                  Favors municipalities with a higher percentage of working-age population (15-64).
                </p>
                <ul>
                  <li>Working-age % is the primary factor</li>
                  <li>Higher working population = More economic activity</li>
                  <li>Also considers total population and density</li>
                </ul>
              </section>

              <section>
                <h3>🏥 Healthcare</h3>
                <p>
                  Based on IOZ (Izbrani Osebni Zdravnik) coverage ratio - 
                  the percentage of residents who have access to a personal doctor.
                </p>
                <ul>
                  <li>IOZ Ratio × 100 = Healthcare score</li>
                  <li>Score 100 = Everyone has a personal doctor assigned</li>
                  <li>Data from ZZZS (Health Insurance Institute)</li>
                </ul>
              </section>

              <section>
                <h3>🏠 Housing Diversity</h3>
                <p>
                  Measures the variety of property types available (apartments, houses, rentals).
                  More diverse markets offer more choices for different needs.
                </p>
                <ul>
                  <li>Checks availability of: apartments for sale, houses for sale, rentals</li>
                  <li>Each category present adds to the diversity score</li>
                  <li>Also considers the balance between different types</li>
                </ul>
              </section>

              <section>
                <h3>🚗 Commute (when workplace is set)</h3>
                <p>
                  Calculated using Google Maps Distance Matrix API for accurate travel times.
                  Only shown when you specify a workplace location.
                </p>
                <ul>
                  <li><strong>Distance:</strong> Straight-line distance between municipalities</li>
                  <li><strong>Travel Time:</strong> Estimated driving time via Google Maps</li>
                  <li><strong>Daily Total:</strong> One-way time × 2</li>
                  <li>Municipalities exceeding max commute time are filtered out</li>
                  <li>Score 100 = Same city as workplace (0 commute)</li>
                  <li>Score decreases as commute time increases</li>
                </ul>
              </section>

              <section>
                <h3>⚙️ How Filtering Works</h3>
                <p>The search applies filters in two stages:</p>
                <ol>
                  <li><strong>Hard Filters:</strong> Budget and commute time constraints eliminate unsuitable cities</li>
                  <li><strong>Score Thresholds:</strong> Your minimum requirements (sliders) filter cities that don't meet the threshold</li>
                </ol>
                <p>
                  Setting a slider to 0 means "Any" - no minimum requirement for that category.
                  Setting it to 10 means the city must score 100 (perfect) in that category.
                </p>
              </section>

              <section>
                <h3>🎯 Final Score</h3>
                <p>
                  The overall score is a weighted combination of all category scores.
                  Cities are ranked by this final score after passing all filters.
                </p>
              </section>
            </div>
          </div>
        </div>
      )}

      <form onSubmit={(e) => { e.preventDefault(); handleSubmit(); }}>
        {/* Search Type */}
        <div className="form-group">
          <label>Looking to</label>
          <div className="search-type-toggle">
            <button
              type="button"
              className={`type-btn ${criteria.search_type === 'rent' ? 'active' : ''}`}
              onClick={() => handleChange('search_type', 'rent')}
            >
              Rent
            </button>
            <button
              type="button"
              className={`type-btn ${criteria.search_type === 'purchase' ? 'active' : ''}`}
              onClick={() => handleChange('search_type', 'purchase')}
            >
              Purchase
            </button>
          </div>
        </div>

        {/* Budget */}
        <div className="form-group">
          <label>
            {criteria.search_type === 'rent' ? 'Monthly Budget' : 'Purchase Budget'}
          </label>
          <div className="budget-input">
            <input
              type="number"
              value={criteria.search_type === 'rent' ? criteria.max_monthly_rent : criteria.max_purchase_price}
              onChange={(e) => handleChange(
                criteria.search_type === 'rent' ? 'max_monthly_rent' : 'max_purchase_price',
                parseInt(e.target.value) || 0
              )}
              min="0"
              step={criteria.search_type === 'rent' ? '100' : '10000'}
            />
            <span className="budget-currency">EUR</span>
          </div>
        </div>

        {/* Desired Space */}
        <div className="form-group">
          <label>Desired Space: {criteria.desired_m2} m²</label>
          <input
            type="range"
            min="30"
            max="150"
            value={criteria.desired_m2}
            onChange={(e) => handleChange('desired_m2', parseInt(e.target.value))}
            className="range-input"
            style={getSliderStyle(criteria.desired_m2, 30, 150)}
          />
        </div>

        {/* Property Type */}
        {criteria.search_type === 'purchase' && (
          <div className="form-group">
            <label>Property Type</label>
            <div className="search-type-toggle">
              <button
                type="button"
                className={`type-btn ${criteria.property_type === 'apartment' ? 'active' : ''}`}
                onClick={() => handleChange('property_type', 'apartment')}
              >
                Apartment
              </button>
              <button
                type="button"
                className={`type-btn ${criteria.property_type === 'house' ? 'active' : ''}`}
                onClick={() => handleChange('property_type', 'house')}
              >
                House
              </button>
            </div>
          </div>
        )}

        {/* Car Ownership */}
        <div className="form-group">
          <label>I own a car</label>
          <div className="toggle-switch">
            <label className="switch">
              <input
                type="checkbox"
                checked={criteria.has_car}
                onChange={(e) => handleChange('has_car', e.target.checked)}
              />
              <span className="slider-toggle"></span>
            </label>
            <span className="toggle-label">{criteria.has_car ? 'Yes' : 'No'}</span>
          </div>
        </div>

        {/* Workplace Location - NEW */}
        <div className="form-group">
          <label>I work in (optional)</label>
          <select
            value={criteria.workplace_city_code}
            onChange={(e) => handleChange('workplace_city_code', e.target.value)}
            className="life-stage-select"
            disabled={loadingCities}
          >
            <option value="">-- No workplace / Remote --</option>
            {allCities.map(city => {
              const code3 = String(city.code).padStart(3, '0');
              return (
                <option key={code3} value={code3}>
                  {city.name} {city.region ? `(${city.region})` : ''}
                </option>
              );
            })}
          </select>
        </div>

        {/* Max Commute Time */}
        {criteria.workplace_city_code && (
          <div className="form-group">
            <label>
              Max Commute Time: {criteria.max_commute_minutes} min (one way)
            </label>
            <input
              type="range"
              min="15"
              max="120"
              step="5"
              value={criteria.max_commute_minutes}
              onChange={(e) => handleChange('max_commute_minutes', parseInt(e.target.value))}
              className="range-input"
              style={getSliderStyle(criteria.max_commute_minutes, 15, 120)}
            />
            <div className="slider-labels-inline" style={{ marginTop: '0.5rem' }}>
              <span>15 min</span>
              <span style={{ color: '#2563EB', fontWeight: 600 }}>
                {Math.round(criteria.max_commute_minutes * 2)} min/day
              </span>
              <span>120 min</span>
            </div>
          </div>
        )}

        {/* Priority Weights */}
        <div className="form-group">
          <h3 style={{ marginBottom: '0.5rem', fontSize: '1.1rem', color: '#374151' }}>
            Minimum Requirements
          </h3>
          <p style={{ fontSize: '0.85rem', color: '#6B7280', marginBottom: '1rem' }}>
            Set minimum score thresholds (0 = no minimum, 10 = must score 100)
          </p>
          
          {Object.entries(criteria.weights).map(([category, value]) => {
            const getCategoryDisplay = (cat) => {
              const displays = {
                'affordability': { icon: '💰', name: 'Affordability', desc: 'Price level' },
                'demographics': { icon: '👥', name: 'Demographics', desc: 'Population match' },
                'transportation': { icon: '🚗', name: 'Transportation', desc: 'Commute score' },
                'healthcare': { icon: '🏥', name: 'Healthcare', desc: 'Medical access' },
                'education': { icon: '🎓', name: 'Education', desc: 'Schools nearby' },
                'weather': { icon: '☀️', name: 'Weather', desc: 'Climate quality' },
                'price_diversity': { icon: '🏠', name: 'Housing Options', desc: 'Property variety' },
                'market_liquidity': { icon: '📊', name: 'Market Activity', desc: 'Deal volume' }
              };
              return displays[cat] || { icon: '📌', name: cat.replace('_', ' '), desc: '' };
            };

            const display = getCategoryDisplay(category);
            const minScore = value * 10; // Convert weight to minimum score

            return (
              <div key={category} style={{ marginBottom: '1rem' }}>
                <label style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                  <span>
                    {display.icon} {display.name}
                    {category === 'transportation' && criteria.workplace_city_code && (
                      <span style={{ fontSize: '0.75rem', color: '#2563EB', marginLeft: '0.5rem' }}>
                        (includes commute)
                      </span>
                    )}
                  </span>
                  <span className="importance-value" style={{ 
                    color: value === 0 ? '#9CA3AF' : value >= 8 ? '#DC2626' : value >= 5 ? '#F59E0B' : '#10B981'
                  }}>
                    {value === 0 ? 'Any' : `Min: ${minScore}`}
                  </span>
                </label>
                <input
                  type="range"
                  min="0"
                  max="10"
                  value={value}
                  onChange={(e) => handleWeightChange(category, e.target.value)}
                  className="range-input"
                  style={getSliderStyle(value, 0, 10)}
                />
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.7rem', color: '#9CA3AF', marginTop: '2px' }}>
                  <span>No minimum</span>
                  <span>Must be perfect</span>
                </div>
              </div>
            );
          })}
        </div>

        {/* Search Button */}
        <div className="search-button-container">
          <button type="submit" className="search-now-btn">
            Search Now
          </button>
        </div>
      </form>
    </div>
  );
}

export default AttributePicker;
