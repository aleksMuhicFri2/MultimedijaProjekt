import React, { useState } from "react";
import "./SearchPanel.css";

function SearchPanel({ onSearch, onReset, searchResults, onSelectResult }) {
  const [preferences, setPreferences] = useState({
    budget: 50000,
    hasCar: false,
    healthImportance: 5,
    educationImportance: 5,
    employmentImportance: 5,
    cultureImportance: 5,
    safetyImportance: 5,
    populationPreference: "medium",
  });

  const handleChange = (field, value) => {
    setPreferences((prev) => ({ ...prev, [field]: value }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    onSearch(preferences);
  };

  const handleReset = () => {
    setPreferences({
      budget: 50000,
      hasCar: false,
      healthImportance: 5,
      educationImportance: 5,
      employmentImportance: 5,
      cultureImportance: 5,
      safetyImportance: 5,
      populationPreference: "medium",
    });
    onReset();
  };

  // Show results if they exist
  if (searchResults && searchResults.topMatches) {
    const topMatches = searchResults.topMatches.slice(0, 5);

    return (
      <div className="search-panel">
        <div className="search-header">
          <h2>🎯 Best Matches Found!</h2>
          <p>
            Showing top {topMatches.length} of {searchResults.topMatches.length}{" "}
            municipalities
          </p>
        </div>

        <div className="results-list">
          {topMatches.map((result, index) => (
            <div
              key={result.code}
              className={`result-card rank-${index + 1}`}
              onClick={() => onSelectResult(result.code)}
            >
              <div className="result-rank">
                <span className="rank-number">#{index + 1}</span>
                {index === 0 && (
                  <span className="best-badge">🏆 Best Match</span>
                )}
              </div>
              <div className="result-content">
                <h3>{result.name}</h3>
                <div className="match-score">
                  <div className="score-bar">
                    <div
                      className="score-fill"
                      style={{ width: `${result.matchScore}%` }}
                    ></div>
                  </div>
                  <span className="score-text">{result.matchScore}% Match</span>
                </div>
                <div className="result-highlights">
                  {result.highlights?.map((highlight, idx) => (
                    <span key={idx} className="highlight-tag">
                      {highlight}
                    </span>
                  ))}
                </div>
              </div>
              <div className="result-arrow">→</div>
            </div>
          ))}
        </div>

        <div className="button-group">
          <button type="button" onClick={handleReset} className="btn-secondary">
            🔄 New Search
          </button>
        </div>
      </div>
    );
  }

  // Show search form
  return (
    <div className="search-panel">
      <div className="search-header">
        <h2>🔍 Find Your Perfect Municipality</h2>
        <p>Customize your preferences to discover the ideal place to live</p>
      </div>

      <form onSubmit={handleSubmit} className="search-form">
        {/* Budget */}
        <div className="form-group">
          <label htmlFor="budget">
            💰 Monthly Budget
            <span className="value-display">
              €{preferences.budget.toLocaleString()}
            </span>
          </label>
          <input
            type="range"
            id="budget"
            min="20000"
            max="150000"
            step="5000"
            value={preferences.budget}
            onChange={(e) => handleChange("budget", Number(e.target.value))}
            className="slider"
          />
          <div className="range-labels">
            <span>€20k</span>
            <span>€150k</span>
          </div>
        </div>

        {/* Car Ownership */}
        <div className="form-group checkbox-group">
          <label className="checkbox-label">
            <input
              type="checkbox"
              checked={preferences.hasCar}
              onChange={(e) => handleChange("hasCar", e.target.checked)}
            />
            <span className="checkbox-custom"></span>
            🚗 I own a car
          </label>
        </div>

        {/* Population Preference */}
        <div className="form-group">
          <label>🏘️ City Size Preference</label>
          <div className="radio-group">
            {["small", "medium", "large"].map((size) => (
              <label key={size} className="radio-label">
                <input
                  type="radio"
                  name="population"
                  value={size}
                  checked={preferences.populationPreference === size}
                  onChange={(e) =>
                    handleChange("populationPreference", e.target.value)
                  }
                />
                <span className="radio-custom"></span>
                {size.charAt(0).toUpperCase() + size.slice(1)}
              </label>
            ))}
          </div>
        </div>

        {/* Importance Sliders */}
        <div className="importance-section">
          <h3>Priority Factors</h3>
          <p className="section-subtitle">
            Rate how important each factor is to you (1-10)
          </p>

          {[
            { key: "healthImportance", label: "Healthcare", icon: "🏥" },
            { key: "educationImportance", label: "Education", icon: "🎓" },
            { key: "employmentImportance", label: "Employment", icon: "💼" },
            { key: "cultureImportance", label: "Culture & Recreation", icon: "🎭" },
            { key: "safetyImportance", label: "Safety", icon: "🛡️" },
          ].map(({ key, label, icon }) => (
            <div key={key} className="form-group">
              <label htmlFor={key}>
                {icon} {label}
                <span className="value-display">{preferences[key]}/10</span>
              </label>
              <input
                type="range"
                id={key}
                min="1"
                max="10"
                value={preferences[key]}
                onChange={(e) => handleChange(key, Number(e.target.value))}
                className="slider importance-slider"
              />
              <div className="range-labels">
                <span>Low</span>
                <span>High</span>
              </div>
            </div>
          ))}
        </div>

        {/* Action Buttons */}
        <div className="button-group">
          <button type="submit" className="btn-primary">
            🎯 Find Best Match
          </button>
          <button type="button" onClick={handleReset} className="btn-secondary">
            🔄 Reset Filters
          </button>
        </div>
      </form>
    </div>
  );
}

export default SearchPanel;
