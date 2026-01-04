import React from "react";
import { useNavigate } from "react-router-dom";
import { Radar } from 'react-chartjs-2';
import { Chart as ChartJS, RadialLinearScale, PointElement, LineElement, Filler, Tooltip, Legend } from 'chart.js';

ChartJS.register(RadialLinearScale, PointElement, LineElement, Filler, Tooltip, Legend);

function SearchResultsPage({ results, criteria, meta, suggestions }) {
  const navigate = useNavigate();

  // No results - show helpful message
  if (!results || results.length === 0) {
    return (
      <div className="results-page">
        <div className="results-page-header">
          <button className="back-button-inline" onClick={() => navigate('/')}>
            ← Back to Search
          </button>
          <div className="results-header-content">
            <h1>No Cities Match Your Criteria</h1>
            <p className="results-subtitle">
              Your requirements are too strict. Here's what happened:
            </p>
          </div>
        </div>

        {/* Filter breakdown */}
        {meta && (
          <div style={{ 
            margin: '2rem auto', 
            maxWidth: '600px', 
            padding: '1.5rem', 
            background: '#FEF3C7', 
            borderRadius: '12px',
            border: '1px solid #FCD34D'
          }}>
            <h3 style={{ color: '#92400E', marginBottom: '1rem' }}>📊 Filter Breakdown</h3>
            <div style={{ display: 'grid', gap: '0.5rem', fontSize: '0.95rem' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span>Total municipalities:</span>
                <strong>{meta.total_cities || 212}</strong>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span>After budget & commute filters:</span>
                <strong style={{ color: meta.after_budget_commute_filter === 0 ? '#DC2626' : '#059669' }}>
                  {meta.after_budget_commute_filter || 0}
                </strong>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span>After minimum score requirements:</span>
                <strong style={{ color: meta.after_score_filter === 0 ? '#DC2626' : '#059669' }}>
                  {meta.after_score_filter || 0}
                </strong>
              </div>
            </div>

            {/* Show applied thresholds */}
            {meta.thresholds_applied && Object.keys(meta.thresholds_applied).length > 0 && (
              <div style={{ marginTop: '1rem', paddingTop: '1rem', borderTop: '1px solid #FCD34D' }}>
                <h4 style={{ color: '#92400E', marginBottom: '0.5rem', fontSize: '0.9rem' }}>
                  Your minimum requirements:
                </h4>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
                  {Object.entries(meta.thresholds_applied).map(([category, threshold]) => {
                    const names = {
                      affordability: 'Affordability',
                      market_activity: 'Market Activity',
                      population_vitality: 'Demographics',
                      healthcare: 'Healthcare',
                      housing_diversity: 'Housing Options',
                      commute: 'Commute'
                    };
                    return (
                      <span key={category} style={{
                        background: '#FDE68A',
                        padding: '0.25rem 0.75rem',
                        borderRadius: '999px',
                        fontSize: '0.85rem',
                        color: '#92400E'
                      }}>
                        {names[category] || category} ≥ {threshold}
                      </span>
                    );
                  })}
                </div>
              </div>
            )}
          </div>
        )}

        {/* Suggestions */}
        {suggestions && suggestions.length > 0 && (
          <div style={{ 
            margin: '1rem auto', 
            maxWidth: '600px', 
            padding: '1.5rem', 
            background: '#DBEAFE', 
            borderRadius: '12px',
            border: '1px solid #93C5FD'
          }}>
            <h3 style={{ color: '#1E40AF', marginBottom: '1rem' }}>💡 Suggestions</h3>
            <ul style={{ margin: 0, paddingLeft: '1.5rem', color: '#1E3A8A' }}>
              {suggestions.map((suggestion, i) => (
                <li key={i} style={{ marginBottom: '0.5rem' }}>{suggestion}</li>
              ))}
            </ul>
          </div>
        )}

        <div style={{ textAlign: 'center', marginTop: '2rem' }}>
          <button 
            className="back-button-inline" 
            onClick={() => navigate('/')}
            style={{ 
              background: '#2563EB', 
              color: 'white', 
              padding: '0.75rem 2rem',
              borderRadius: '8px',
              border: 'none',
              cursor: 'pointer',
              fontSize: '1rem'
            }}
          >
            ← Adjust Your Search
          </button>
        </div>
      </div>
    );
  }

  // Prepare comparison data for top 5 cities
  const topCities = results.slice(0, 5);
  
  // Updated radar axes to match new backend scoring categories
  const radarAxes = [
    { key: 'affordability', label: 'Affordability' },
    { key: 'market_activity', label: 'Market Activity' },
    { key: 'population_vitality', label: 'Population' },
    { key: 'healthcare', label: 'Healthcare' },
    { key: 'housing_diversity', label: 'Housing Options' },
  ];

  // Add commute axis if any city has commute scores
  const hasCommute = topCities.some(r => 
    r.category_scores?.commute !== null && r.category_scores?.commute > 0
  );
  if (hasCommute) {
    radarAxes.push({ key: 'commute', label: 'Commute' });
  }

  const palette = [
    { bg: 'rgba(16, 185, 129, 0.18)', border: '#10B981' },
    { bg: 'rgba(59, 130, 246, 0.18)', border: '#3B82F6' },
    { bg: 'rgba(245, 158, 11, 0.18)', border: '#F59E0B' },
    { bg: 'rgba(139, 92, 246, 0.18)', border: '#8B5CF6' },
    { bg: 'rgba(236, 72, 153, 0.18)', border: '#EC4899' }
  ];

  const radarData = {
    labels: radarAxes.map(a => a.label),
    datasets: topCities.map((r, i) => {
      const c = palette[i % palette.length];
      const scores = r.category_scores || {};
      return {
        label: r.city.name,
        data: radarAxes.map(a => {
          const score = scores[a.key];
          return typeof score === 'number' ? score : 0;
        }),
        backgroundColor: c.bg,
        borderColor: c.border,
        pointBackgroundColor: c.border,
        borderWidth: 2
      };
    })
  };

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
            Showing top {topCities.length} of {results.length} cities matching your criteria
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

      {/* Comparison Charts Section */}
      <div style={{ margin: '2rem 0', padding: '2rem', background: 'white', borderRadius: '16px', boxShadow: '0 2px 8px rgba(0,0,0,0.1)' }}>
        <h2 style={{ fontSize: '1.5rem', fontWeight: 700, marginBottom: '2rem', color: '#1F2933' }}>
          City Comparison
        </h2>
        
        {/* Category Radar ONLY (remove bar charts so it’s not in the way) */}
        <div style={{ background: '#F9FAFB', padding: '1.5rem', borderRadius: '12px', border: '1px solid #E5E7EB' }}>
          <h4 style={{ fontSize: '1rem', fontWeight: 600, marginBottom: '1rem', color: '#374151' }}>
            Category Comparison (Top 5)
          </h4>
          <div style={{ height: '420px', display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
            <Radar data={radarData} options={{
              maintainAspectRatio: false,
              plugins: { legend: { position: 'bottom' } },
              scales: { r: { beginAtZero: true, max: 100, ticks: { stepSize: 20 } } }
            }} />
          </div>
        </div>
      </div>

      {/* Results List */}
      <div className="results-list">
        {topCities.map((result, index) => (
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
    if (rank === 1) return { emoji: '🥇', text: 'Best Match' };
    if (rank === 2) return { emoji: '🥈', text: 'Second Best' };
    if (rank === 3) return { emoji: '🥉', text: 'Third Best' };
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
        <h3>💰 Pricing</h3>

        {!city.avg_rent_m2 && !city.avg_price_m2_apartment && !city.avg_price_m2_house ? (
          <div style={{ padding: '1rem', background: '#FEF3C7', border: '1px solid #FCD34D', borderRadius: '8px', color: '#92400E', textAlign: 'center' }}>
            No pricing data available for this municipality
          </div>
        ) : (
          <div className="price-grid">
            {city.avg_rent_m2 && (
              <div className="price-item">
                <div className="price-label">🏠 Rent</div>
                <div className="price-value">{city.avg_rent_m2.toFixed(2)} €/m²</div>
                {city.deals_rent !== undefined && (
                  <div className="price-detail">{city.deals_rent} deals</div>
                )}
              </div>
            )}

            {city.avg_price_m2_apartment && (
              <div className="price-item">
                <div className="price-label">🏢 Apartment</div>
                <div className="price-value">{Math.round(city.avg_price_m2_apartment).toLocaleString()} €/m²</div>
                {city.deals_sale_apartment !== undefined && (
                  <div className="price-detail">{city.deals_sale_apartment} deals</div>
                )}
              </div>
            )}

            {city.avg_price_m2_house && (
              <div className="price-item">
                <div className="price-label">🏡 House</div>
                <div className="price-value">{Math.round(city.avg_price_m2_house).toLocaleString()} €/m²</div>
                {city.deals_sale_house !== undefined && (
                  <div className="price-detail">{city.deals_sale_house} deals</div>
                )}
              </div>
            )}
          </div>
        )}
      </div>

      {/* Commute Info */}
      {commute_info && !commute_info.is_same_city && (
        <div className="detailed-commute-section">
          <h3>🚗 Commute to {commute_info.workplace_name}</h3>
          <div className="commute-grid">
            <div className="commute-stat">
              <div className="commute-value">{commute_info.distance_km} km</div>
              <div className="commute-label">Distance</div>
            </div>
            <div className="commute-stat">
              <div className="commute-value">{Math.round(commute_info.one_way_time)} min</div>
              <div className="commute-label">One Way</div>
            </div>
            <div className="commute-stat highlight">
              <div className="commute-value">{Math.round(commute_info.daily_time)} min</div>
              <div className="commute-label">Daily Total</div>
            </div>
          </div>
          {commute_info.source === 'google_maps' && (
            <div style={{ fontSize: '0.75rem', color: '#6B7280', marginTop: '0.5rem', textAlign: 'center' }}>
              📍 Via Google Maps
            </div>
          )}
        </div>
      )}

      {/* Demographics */}
      <div className="detailed-demographics-section">
        <h3>👥 Population</h3>
        <div className="demographics-grid">
          <div className="demo-stat">
            <div className="demo-value">{city.population_young?.toLocaleString() || 'N/A'}</div>
            <div className="demo-label">Young (0-14)</div>
          </div>
          <div className="demo-stat">
            <div className="demo-value">{city.population_working?.toLocaleString() || 'N/A'}</div>
            <div className="demo-label">Working (15-64)</div>
          </div>
          <div className="demo-stat">
            <div className="demo-value">{city.population_old?.toLocaleString() || 'N/A'}</div>
            <div className="demo-label">Elderly (65+)</div>
          </div>
          <div className="demo-stat total">
            <div className="demo-value">{city.population_total?.toLocaleString() || 'N/A'}</div>
            <div className="demo-label">Total</div>
          </div>
        </div>
      </div>

      {/* Category Scores */}
      <div className="detailed-scores-section">
        <h3>📊 Score Breakdown</h3>
        <div className="scores-list">
          {Object.entries(category_scores || {}).map(([category, score]) => {
            if (score === null || score === undefined) return null;

            const categoryInfo = {
              'affordability': { icon: '💰', name: 'Affordability' },
              'market_activity': { icon: '📈', name: 'Market Activity' },
              'population_vitality': { icon: '👥', name: 'Demographics' },
              'healthcare': { icon: '🏥', name: 'Healthcare' },
              'housing_diversity': { icon: '🏠', name: 'Housing Options' },
              'commute': { icon: '🚗', name: 'Commute' }
            }[category] || { icon: '📌', name: category };

            return (
              <div key={category} className="score-item">
                <div className="score-item-header">
                  <span className="score-item-name">{categoryInfo.icon} {categoryInfo.name}</span>
                  <span className="score-item-value" style={{ color: getScoreColor(score) }}>
                    {Math.round(score)}/100
                  </span>
                </div>
                <div className="score-item-bar">
                  <div 
                    className="score-item-fill" 
                    style={{ width: `${score}%`, backgroundColor: getScoreColor(score) }}
                  />
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Additional Info */}
      {city.area_km2 && (
        <div style={{ 
          marginTop: '1rem', 
          padding: '0.75rem', 
          background: '#F3F4F6', 
          borderRadius: '8px',
          fontSize: '0.9rem',
          color: '#4B5563'
        }}>
          <strong>Area:</strong> {city.area_km2.toFixed(1)} km² 
          {city.population_density && (
            <span style={{ marginLeft: '1rem' }}>
              <strong>Density:</strong> {Math.round(city.population_density)} people/km²
            </span>
          )}
        </div>
      )}
    </div>
  );
}

export default SearchResultsPage;