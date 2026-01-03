import React from "react";
import { useNavigate } from "react-router-dom";

function SearchResultsPage({ results, criteria }) {
  const navigate = useNavigate();

  if (!results || results.length === 0) {
    return (
      <div className="results-page">
        <div className="results-page-header">
          <button className="back-button-inline" onClick={() => navigate('/')}>
            ← Back to Search
          </button>
          <div className="results-header-content">
            <h1>Your Perfect City Matches</h1>
            <p className="results-subtitle">
              No cities found matching your criteria. Please adjust your search.
            </p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="results-page">
      {/* Header */}
      <div className="results-page-header">
        <button className="back-button-inline" onClick={() => navigate('/')}>
          ← Back to Search
        </button>
        <div className="results-header-content">
          <h1>Your Perfect City Matches</h1>
          <p className="results-subtitle">
            Found {results.length} cities matching your criteria
            {criteria?.workplace_city_code && (
              <span className="criteria-badge">
                Near workplace
              </span>
            )}
            {criteria?.search_type === 'rent' && (
              <span className="criteria-badge">
                Budget: {criteria.max_monthly_rent?.toLocaleString()} €/mo
              </span>
            )}
            {criteria?.search_type === 'purchase' && (
              <span className="criteria-badge">
                Budget: {criteria.max_purchase_price?.toLocaleString()} €
              </span>
            )}
          </p>
        </div>
      </div>

      {/* Results List */}
      <div className="results-list">
        {results.map((result, index) => (
          <DetailedResultCard key={result.city.code} result={result} rank={index + 1} />
        ))}
      </div>
    </div>
  );
}

function DetailedResultCard({ result, rank }) {
  const { city, final_score, category_scores, commute_info } = result;

  const getScoreColor = (score) => {
    if (score >= 80) return '#10B981';
    if (score >= 60) return '#F59E0B';
    return '#EF4444';
  };

  const getRankBadge = (rank) => {
    if (rank === 1) return { emoji: '', text: 'Best Match' };
    if (rank === 2) return { emoji: '', text: 'Second Best' };
    if (rank === 3) return { emoji: '', text: 'Third Best' };
    return { emoji: `#${rank}`, text: `Rank ${rank}` };
  };

  const rankInfo = getRankBadge(rank);

  return (
    <div className="detailed-result-card">
      {/* Header Section */}
      <div className="detailed-card-header">
        <div className="rank-info">
          <div className="rank-badge-large">{rankInfo.emoji}</div>
          <span className="rank-text">{rankInfo.text}</span>
        </div>
        <h2>{city.name}</h2>
        <div className="final-score" style={{ color: getScoreColor(final_score) }}>
          {final_score.toFixed(1)} / 100
        </div>
      </div>

      {/* Price Overview */}
      <div className="detailed-price-section">
        <h3>Estimated Costs</h3>
        
        {/* Check if we have ANY price data */}
        {!city.rent?.avg_rent_m2 && !city.prices?.apartment?.avg_price_m2 && !city.prices?.house?.avg_price_m2 ? (
          <div style={{ 
            padding: '1rem', 
            background: '#FEF3C7', 
            border: '1px solid #FCD34D',
            borderRadius: '8px',
            color: '#92400E',
            textAlign: 'center'
          }}>
            No pricing data available for this municipality
          </div>
        ) : (
          <div className="price-grid">
            {city.rent?.avg_rent_m2 && (
              <div className="price-item">
                <div className="price-label">Monthly Rent (60m²)</div>
                <div className="price-value">
                  ~{Math.round(city.rent.avg_rent_m2 * 60).toLocaleString()} €
                </div>
                <div className="price-detail">{city.rent.avg_rent_m2.toFixed(2)} €/m²</div>
              </div>
            )}
            {city.prices?.apartment?.avg_price_m2 && (
              <div className="price-item">
                <div className="price-label">Buy Apartment (70m²)</div>
                <div className="price-value">
                  ~{Math.round(city.prices.apartment.avg_price_m2 * 70).toLocaleString()} €
                </div>
                <div className="price-detail">{Math.round(city.prices.apartment.avg_price_m2).toLocaleString()} €/m²</div>
              </div>
            )}
            {city.prices?.house?.avg_price_m2 && (
              <div className="price-item">
                <div className="price-label">Buy House (100m²)</div>
                <div className="price-value">
                  ~{Math.round(city.prices.house.avg_price_m2 * 100).toLocaleString()} €
                </div>
                <div className="price-detail">{Math.round(city.prices.house.avg_price_m2).toLocaleString()} €/m²</div>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Commute Info */}
      {commute_info && (
        <div className="detailed-commute-section">
          <h3>Commute to {commute_info.workplace_name}</h3>
          <div className="commute-grid">
            <div className="commute-stat">
              <div className="commute-icon">Distance</div>
              <div className="commute-value">{commute_info.distance_km} km</div>
              <div className="commute-label">Distance</div>
            </div>
            <div className="commute-stat">
              <div className="commute-icon">One Way</div>
              <div className="commute-value">{commute_info.one_way_time} min</div>
              <div className="commute-label">One Way</div>
            </div>
            <div className="commute-stat highlight">
              <div className="commute-icon">Daily</div>
              <div className="commute-value">{commute_info.daily_time} min</div>
              <div className="commute-label">Daily Total</div>
            </div>
          </div>
        </div>
      )}

      {/* Demographics */}
      <div className="detailed-demographics-section">
        <h3>Population</h3>
        <div className="demographics-grid">
          <div className="demo-stat">
            <div className="demo-icon">Young</div>
            <div className="demo-value">{city.population_young?.toLocaleString()}</div>
            <div className="demo-label">Young (0-14)</div>
          </div>
          <div className="demo-stat">
            <div className="demo-icon">Working</div>
            <div className="demo-value">{city.population_working?.toLocaleString()}</div>
            <div className="demo-label">Working (15-64)</div>
          </div>
          <div className="demo-stat">
            <div className="demo-icon">Old</div>
            <div className="demo-value">{city.population_old?.toLocaleString()}</div>
            <div className="demo-label">Old (65+)</div>
          </div>
          <div className="demo-stat total">
            <div className="demo-icon">Total</div>
            <div className="demo-value">{city.population_total?.toLocaleString()}</div>
            <div className="demo-label">Total Population</div>
          </div>
        </div>
      </div>

      {/* Category Scores */}
      <div className="detailed-scores-section">
        <h3>Score Breakdown</h3>
        <div className="scores-list">
          {Object.entries(category_scores).map(([category, score]) => {
            if (score === null || score === undefined) return null;

            const categoryInfo = {
              'affordability': { icon: '', name: 'Affordability' },
              'demographics': { icon: '', name: 'Demographics Match' },
              'transportation': { icon: '', name: 'Transportation' },
              'healthcare': { icon: '', name: 'Healthcare' },
              'education': { icon: '', name: 'Education' },
              'weather': { icon: '', name: 'Weather' },
              'price_diversity': { icon: '', name: 'Housing Options' },
              'market_liquidity': { icon: '', name: 'Market Activity' }
            }[category] || { icon: '', name: category };

            return (
              <div key={category} className="score-item">
                <div className="score-item-header">
                  <span className="score-item-name">{categoryInfo.name}</span>
                  <span className="score-item-value" style={{ color: getScoreColor(score) }}>
                    {score}/100
                  </span>
                </div>
                <div className="score-item-bar">
                  <div className="score-item-fill" style={{ width: `${score}%`, backgroundColor: getScoreColor(score) }}></div>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Market Info */}
      {(city.prices?.apartment?.deals_count || city.rent?.deals_count_rent) && (
        <div className="detailed-market-section">
          <h3>Market Activity</h3>
          <div className="market-stats">
            {city.prices?.apartment?.deals_count !== undefined && (
              <div className="market-stat">
                <span>Apartment Deals:</span>
                <strong>{city.prices.apartment.deals_count}</strong>
              </div>
            )}
            {city.prices?.house?.deals_count !== undefined && (
              <div className="market-stat">
                <span>House Deals:</span>
                <strong>{city.prices.house.deals_count}</strong>
              </div>
            )}
            {city.rent?.deals_count_rent !== undefined && (
              <div className="market-stat">
                <span>Rental Deals:</span>
                <strong>{city.rent.deals_count_rent}</strong>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

export default SearchResultsPage;