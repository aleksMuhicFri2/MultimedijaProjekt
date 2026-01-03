import React from 'react';
import './SearchResults.css';

function SearchResults({ results, loading, error }) {
  if (loading) {
    return (
      <div className="search-results loading">
        <div className="spinner"></div>
        <p>Filtering cities by commute time...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="search-results error">
        <span className="error-icon">⚠</span>
        <p>Error: {error}</p>
      </div>
    );
  }

  if (!results || results.length === 0) {
    return (
      <div className="search-results empty">
        <span className="icon">🔍</span>
        <h3>No Cities Found</h3>
        <p>No cities match your commute time criteria.</p>
        <p style={{ fontSize: '0.85rem', color: '#6B7280', marginTop: '0.5rem' }}>
          Try increasing max commute time or selecting a different workplace location.
        </p>
      </div>
    );
  }

  // Check if any results have commute info
  const hasCommuteInfo = results.some(r => r.commute_info);

  return (
    <div className="search-results">
      <div className="results-header">
        <h2>Top {results.length} Matches</h2>
        {hasCommuteInfo && (
          <p style={{ fontSize: '0.9rem', color: '#2563EB', fontWeight: 600 }}>
            ✓ All cities within commute range
          </p>
        )}
        <p>{results.length} cities found</p>
      </div>

      <div className="results-list">
        {results.map((result, index) => (
          <ResultCard key={result.city.code} result={result} rank={index + 1} />
        ))}
      </div>
    </div>
  );
}

function ResultCard({ result, rank }) {
  const { city, final_score, category_scores, commute_info } = result;

  const getScoreColor = (score) => {
    if (score >= 80) return '#10B981';
    if (score >= 60) return '#F59E0B';
    return '#EF4444';
  };

  const getRankMedal = (rank) => {
    if (rank === 1) return '🥇';
    if (rank === 2) return '🥈';
    if (rank === 3) return '🥉';
    return `#${rank}`;
  };

  // Calculate estimated monthly cost based on property type and space
  const getEstimatedCost = () => {
    const rent_m2 = city.rent?.avg_rent_m2;
    const apt_price_m2 = city.prices?.apartment?.avg_price_m2;
    const house_price_m2 = city.prices?.house?.avg_price_m2;

    return {
      monthly_rent: rent_m2 ? (rent_m2 * 60).toFixed(0) : null, // Assume 60m²
      apt_price: apt_price_m2 ? (apt_price_m2 * 70).toFixed(0) : null, // Assume 70m²
      house_price: house_price_m2 ? (house_price_m2 * 100).toFixed(0) : null // Assume 100m²
    };
  };

  const costs = getEstimatedCost();

  return (
    <div className="result-card">
      <div className="result-header">
        <div className="rank-badge">{getRankMedal(rank)}</div>
        <div className="city-info">
          <h3>{city.name}</h3>
          <p className="region">{city.region || 'Slovenia'}</p>
        </div>
        <div className="final-score" style={{ color: getScoreColor(final_score) }}>
          <div className="score-value">{final_score}</div>
          <div className="score-label">Score</div>
        </div>
      </div>

      {/* Price Summary - Separate line below header */}
      <div className="price-summary-row">
        {costs.monthly_rent && (
          <span className="price-tag">
            <span>Rent:</span>
            <span className="price-value">~{parseInt(costs.monthly_rent).toLocaleString()} €/mo</span>
          </span>
        )}
        {costs.apt_price && (
          <span className="price-tag">
            <span>Apartment:</span>
            <span className="price-value">~{parseInt(costs.apt_price).toLocaleString()} €</span>
          </span>
        )}
        {costs.house_price && (
          <span className="price-tag">
            <span>House:</span>
            <span className="price-value">~{parseInt(costs.house_price).toLocaleString()} €</span>
          </span>
        )}
      </div>

      <div className="result-body">
        {/* Commute Info */}
        {commute_info && (
          <div className="commute-info">
            <div className="commute-header">
              <span className="commute-icon">Commute</span>
              <span className="commute-title">to {commute_info.workplace_name}</span>
            </div>
            <div className="commute-details">
              <div className="commute-metric">
                <span className="metric-label">Distance</span>
                <span className="metric-value">{commute_info.distance_km} km</span>
              </div>
              <div className="commute-metric">
                <span className="metric-label">One Way</span>
                <span className="metric-value">{commute_info.one_way_time} min</span>
              </div>
              <div className="commute-metric">
                <span className="metric-label">Daily</span>
                <span className="metric-value" style={{ color: '#2563EB', fontWeight: 700 }}>
                  {commute_info.daily_time} min
                </span>
              </div>
            </div>
          </div>
        )}

        {/* Key Metrics */}
        <div className="key-metrics">
          {city.rent?.avg_rent_m2 && (
            <div className="metric">
              <span className="metric-icon">Rent</span>
              <span className="metric-value">{city.rent.avg_rent_m2.toFixed(2)} €/m²</span>
              <span className="metric-label">Rent</span>
            </div>
          )}
          
          {city.prices?.apartment?.avg_price_m2 && (
            <div className="metric">
              <span className="metric-icon">Apt</span>
              <span className="metric-value">{city.prices.apartment.avg_price_m2.toFixed(0)} €/m²</span>
              <span className="metric-label">Apt Price</span>
            </div>
          )}
          
          {city.population_total && (
            <div className="metric">
              <span className="metric-icon">Pop</span>
              <span className="metric-value">{city.population_total.toLocaleString()}</span>
              <span className="metric-label">Population</span>
            </div>
          )}
          
          {city.prices?.apartment?.deals_count !== undefined && (
            <div className="metric">
              <span className="metric-icon">Deals</span>
              <span className="metric-value">{city.prices.apartment.deals_count}</span>
              <span className="metric-label">Deals</span>
            </div>
          )}
        </div>

        {/* Category Scores */}
        <div className="category-scores">
          {Object.entries(category_scores).map(([category, score]) => {
            if (score === null || score === undefined) return null;
            
            const getCategoryName = (cat) => {
              const names = {
                'affordability': 'Affordability',
                'demographics': 'Demographics',
                'transportation': 'Transportation',
                'healthcare': 'Healthcare',
                'education': 'Education',
                'weather': 'Weather',
                'price_diversity': 'Housing Options',
                'market_liquidity': 'Market Activity'
              };
              return names[cat] || cat.replace('_', ' ');
            };
            
            return (
              <div key={category} className="category-score">
                <div className="category-header">
                  <span className="category-name">{getCategoryName(category)}</span>
                  <span className="category-value" style={{ color: getScoreColor(score) }}>
                    {score}
                  </span>
                </div>
                <div className="category-bar">
                  <div 
                    className="category-fill"
                    style={{ 
                      width: `${score}%`,
                      background: `linear-gradient(to right, ${getScoreColor(score)}, ${getScoreColor(score)}dd)`
                    }}
                  />
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}

export default SearchResults;
