import React, { useState, useEffect } from 'react';

function AttributePicker({ onSearch }) {
  const [criteria, setCriteria] = useState({
    search_type: 'rent',
    max_monthly_rent: 1000,
    max_purchase_price: 200000,
    desired_m2: 60,
    property_type: 'apartment',
    life_stage: 'young_professional',
    has_car: false,
    workplace_city_code: '',
    max_commute_minutes: 60,
    weights: {
      affordability: 10,
      demographics: 5,
      transportation: 5,
      healthcare: 5,
      education: 5,
      weather: 3,
      price_diversity: 7,
      market_liquidity: 5
    }
  });

  const [allCities, setAllCities] = useState([]);
  const [loadingCities, setLoadingCities] = useState(true);

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
<<<<<<< HEAD
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
=======
    setCriteria(prev => ({ ...prev, [field]: value }));
>>>>>>> 422758504451562949a3ea51caba1fdac5ede881
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
      <div className="picker-header">
        <h2>Find Your Perfect City</h2>
        <p>Set your preferences and priorities</p>
      </div>

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

        {/* Life Stage */}
        <div className="form-group">
          <label>Life Stage</label>
          <select
            value={criteria.life_stage}
            onChange={(e) => handleChange('life_stage', e.target.value)}
            className="life-stage-select"
          >
            <option value="student">Student</option>
            <option value="young_professional">Young Professional</option>
            <option value="young_family">Young Family</option>
            <option value="established_family">Established Family</option>
            <option value="retiree">Retiree</option>
          </select>
        </div>

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
<<<<<<< HEAD
            {allCities.map(city => {
              const code3 = String(city.code).padStart(3, '0');
              return (
                <option key={code3} value={code3}>
                  {city.name} {city.region ? `(${city.region})` : ''}
                </option>
              );
            })}
=======
            {allCities.map(city => (
              <option key={city.code} value={city.code}>
                {city.name} {city.region ? `(${city.region})` : ''}
              </option>
            ))}
>>>>>>> 422758504451562949a3ea51caba1fdac5ede881
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
          <h3 style={{ marginBottom: '1rem', fontSize: '1.1rem', color: '#374151' }}>
            Priority Weights
          </h3>
          
          {Object.entries(criteria.weights).map(([category, value]) => {
            const getCategoryDisplay = (cat) => {
              const displays = {
                'affordability': { icon: '', name: 'Affordability' },
                'demographics': { icon: '', name: 'Demographics Match' },
                'transportation': { icon: '', name: 'Transportation' },
                'healthcare': { icon: '', name: 'Healthcare Access' },
                'education': { icon: '', name: 'Education Facilities' },
                'weather': { icon: '', name: 'Weather Quality' },
                'price_diversity': { icon: '', name: 'Housing Options' },
                'market_liquidity': { icon: '', name: 'Market Activity' }
              };
              return displays[cat] || { icon: '', name: cat.replace('_', ' ') };
            };

            const display = getCategoryDisplay(category);

            return (
              <div key={category} style={{ marginBottom: '1rem' }}>
                <label style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                  <span>
                    {display.name}
                    {category === 'transportation' && criteria.workplace_city_code && (
                      <span style={{ fontSize: '0.75rem', color: '#2563EB', marginLeft: '0.5rem' }}>
                        (includes commute)
                      </span>
                    )}
                  </span>
                  <span className="importance-value">{value}/10</span>
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
