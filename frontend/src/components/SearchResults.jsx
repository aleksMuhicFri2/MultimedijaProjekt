import React from 'react';
import './SearchResults.css';
import SpiderGraph, { SpiderGraphLegend } from './SpiderGraph';

function SearchResults({ results, loading, error, meta }) {
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
        <p>No municipalities match your criteria.</p>
        <p style={{ fontSize: '0.85rem', color: '#6B7280', marginTop: '0.5rem' }}>
          Try adjusting your budget, commute time, or other filters.
        </p>
      </div>
    );
  }

  const topResults = results.slice(0, 5);
  const hasCommuteInfo = topResults.some(r => r.commute_info);
  const hasCommuteScores = topResults.some(r => 
    r.category_scores?.commute !== null && r.category_scores?.commute > 0
  );
  
  // Check commute data source
  const hasGoogleMapsCommute = topResults.some(r => r.commute_info?.source === 'google_maps');

  const showCommuteWarning = meta?.commute_filter_requested && !meta?.commute_filter_applied;
  
  // More specific warning messages
  let commuteWarningText = "";
  if (showCommuteWarning) {
    if (meta?.workplace_found === false) {
      commuteWarningText = "Workplace municipality not found. Please check your selection.";
    } else {
      commuteWarningText = "Could not apply commute filter.";
    }
  }

  return (
    <div className="search-results">
      <div className="results-header">
        <h2>Top {topResults.length} Matches</h2>

        {showCommuteWarning && (
          <p className="results-warning">{commuteWarningText}</p>
        )}

        {hasCommuteInfo && !showCommuteWarning && (
          <p style={{ fontSize: '0.9rem', color: '#10B981', fontWeight: 600 }}>
            ✓ Commute times calculated
            {hasGoogleMapsCommute && (
              <span style={{ 
                marginLeft: '0.5rem',
                fontSize: '0.8rem',
                background: '#DBEAFE',
                color: '#1D4ED8',
                padding: '2px 8px',
                borderRadius: 4
              }}>
                via Google Maps
              </span>
            )}
          </p>
        )}
        
        <p style={{ color: '#6B7280', fontSize: '0.9rem' }}>
          Found {results.length} municipalities matching your criteria
        </p>
      </div>

      {/* Spider Graph with new categories */}
      <div style={{
        background: '#fff',
        border: '1px solid #E5E7EB',
        borderRadius: 12,
        padding: '1.5rem',
        marginBottom: '1.5rem'
      }}>
        <h3 style={{ fontSize: '1rem', fontWeight: 600, marginBottom: '1rem', color: '#374151' }}>
          Score Comparison
        </h3>
        <SpiderGraph results={topResults} maxCities={5} height={350} />
        <div style={{ marginTop: '1rem' }}>
          <SpiderGraphLegend hasCommute={hasCommuteScores} />
        </div>
      </div>

      <div className="results-list">
        {topResults.map((result, index) => (
          <ResultCard key={result.city?.code || index} result={result} rank={index + 1} />
        ))}
      </div>
    </div>
  );
}

function ResultCard({ result, rank }) {
  const { city, final_score, category_scores, commute_info, ranking } = result;

  const getScoreColor = (score) => {
    if (score >= 75) return '#10B981';
    if (score >= 50) return '#F59E0B';
    if (score >= 25) return '#F97316';
    return '#EF4444';
  };

  const getRankMedal = (rank) => {
    if (rank === 1) return '🥇';
    if (rank === 2) return '🥈';
    if (rank === 3) return '🥉';
    return `#${rank}`;
  };

  // Category display config matching new backend
  const categoryConfig = {
    affordability: { name: 'Affordability', icon: '💰' },
    market_activity: { name: 'Market Activity', icon: '📊' },
    population_vitality: { name: 'Population', icon: '👥' },
    healthcare: { name: 'Healthcare', icon: '🏥' },
    housing_diversity: { name: 'Housing Options', icon: '🏠' },
    commute: { name: 'Commute', icon: '🚗' },
  };

  return (
    <div className="result-card">
      <div className="result-header">
        <div className="rank-badge">{getRankMedal(rank)}</div>
        <div className="city-info">
          <h3>{city?.name || 'Unknown'}</h3>
          {city?.region && <p className="region">{city.region}</p>}
          {ranking && (
            <span style={{ 
              fontSize: '0.75rem', 
              color: '#6B7280',
              background: '#F3F4F6',
              padding: '2px 8px',
              borderRadius: 4
            }}>
              Top {Math.round(100 - (ranking.percentile || 0))}%
            </span>
          )}
        </div>
        <div className="final-score" style={{ color: getScoreColor(final_score) }}>
          <div className="score-value">{final_score?.toFixed(1) || 'N/A'}</div>
          <div className="score-label">Score</div>
        </div>
      </div>

      <div className="result-body">
        {/* Commute Info with source indicator */}
        {commute_info && (
          <div className="commute-info">
            <div className="commute-header">
              <span className="commute-icon">🚗</span>
              <span className="commute-title">Commute to {commute_info.workplace_name}</span>
              {commute_info.source === 'google_maps' && (
                <span style={{ 
                  fontSize: '0.7rem', 
                  background: '#DBEAFE', 
                  color: '#1D4ED8',
                  padding: '2px 6px',
                  borderRadius: 4,
                  marginLeft: '0.5rem'
                }}>
                  Google Maps
                </span>
              )}
            </div>
            <div className="commute-details">
              <div className="commute-metric">
                <span className="metric-value">{commute_info.distance_km} km</span>
                <span className="metric-label">Distance</span>
              </div>
              <div className="commute-metric">
                <span className="metric-value">{commute_info.one_way_time || commute_info.commute_minutes} min</span>
                <span className="metric-label">One Way</span>
              </div>
              <div className="commute-metric highlight">
                <span className="metric-value" style={{ color: '#2563EB', fontWeight: 700 }}>
                  {commute_info.daily_time || commute_info.daily_commute} min
                </span>
                <span className="metric-label">Daily Total</span>
              </div>
            </div>
          </div>
        )}

        {/* Key Metrics */}
        <div className="key-metrics">
          {(city?.avg_rent_m2 || city?.rent?.avg_rent_m2) && (
            <div className="metric">
              <span className="metric-value">
                {(city.avg_rent_m2 || city.rent?.avg_rent_m2).toFixed(2)} €
              </span>
              <span className="metric-label">Rent/m²</span>
            </div>
          )}
          {(city?.avg_price_m2_apartment || city?.prices?.apartment?.avg_price_m2) && (
            <div className="metric">
              <span className="metric-value">
                {Math.round(city.avg_price_m2_apartment || city.prices?.apartment?.avg_price_m2).toLocaleString()} €
              </span>
              <span className="metric-label">Apt/m²</span>
            </div>
          )}
          {city?.population_total && (
            <div className="metric">
              <span className="metric-value">{city.population_total.toLocaleString()}</span>
              <span className="metric-label">Population</span>
            </div>
          )}
        </div>

        {/* Category Scores with new names */}
        <div className="category-scores">
          {Object.entries(category_scores || {}).map(([key, score]) => {
            if (score === null || score === undefined) return null;
            
            const config = categoryConfig[key] || { name: key, icon: '📌' };
            
            return (
              <div key={key} className="category-score">
                <div className="category-header">
                  <span className="category-name">{config.icon} {config.name}</span>
                  <span className="category-value" style={{ color: getScoreColor(score) }}>
                    {typeof score === 'number' ? score.toFixed(0) : score}
                  </span>
                </div>
                <div className="category-bar">
                  <div 
                    className="category-fill"
                    style={{ 
                      width: `${Math.min(100, score || 0)}%`,
                      background: getScoreColor(score)
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
