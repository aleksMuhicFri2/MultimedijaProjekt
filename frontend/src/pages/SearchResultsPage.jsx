import React from "react";
import { useNavigate } from "react-router-dom";
<<<<<<< HEAD
import { Radar } from 'react-chartjs-2';
import { Chart as ChartJS, RadialLinearScale, PointElement, LineElement, Filler, Tooltip, Legend } from 'chart.js';

ChartJS.register(RadialLinearScale, PointElement, LineElement, Filler, Tooltip, Legend);
=======
>>>>>>> 422758504451562949a3ea51caba1fdac5ede881

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

<<<<<<< HEAD
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

=======
>>>>>>> 422758504451562949a3ea51caba1fdac5ede881
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
<<<<<<< HEAD
            Showing top {topCities.length} of {results.length} cities matching your criteria
=======
            Found {results.length} cities matching your criteria
>>>>>>> 422758504451562949a3ea51caba1fdac5ede881
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

<<<<<<< HEAD
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
=======
      {/* Results List */}
      <div className="results-list">
        {results.map((result, index) => (
>>>>>>> 422758504451562949a3ea51caba1fdac5ede881
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

<<<<<<< HEAD
      {/* Price Overview (API values only; no assumed m² totals) */}
      <div className="detailed-price-section">
        <h3>Pricing</h3>

        {!city.rent?.avg_rent_m2 && !city.prices?.apartment?.avg_price_m2 && !city.prices?.house?.avg_price_m2 ? (
          <div style={{ padding: '1rem', background: '#FEF3C7', border: '1px solid #FCD34D', borderRadius: '8px', color: '#92400E', textAlign: 'center' }}>
=======
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
>>>>>>> 422758504451562949a3ea51caba1fdac5ede881
            No pricing data available for this municipality
          </div>
        ) : (
          <div className="price-grid">
            {city.rent?.avg_rent_m2 && (
              <div className="price-item">
<<<<<<< HEAD
                <div className="price-label">Rent</div>
                <div className="price-value">{city.rent.avg_rent_m2.toFixed(2)} €/m²</div>
                {city.rent?.deals_count_rent !== undefined && (
                  <div className="price-detail">Deals: {city.rent.deals_count_rent}</div>
                )}
              </div>
            )}

            {city.prices?.apartment?.avg_price_m2 && (
              <div className="price-item">
                <div className="price-label">Apartment</div>
                <div className="price-value">{Math.round(city.prices.apartment.avg_price_m2).toLocaleString()} €/m²</div>
                {city.prices?.apartment?.deals_count !== undefined && (
                  <div className="price-detail">Deals: {city.prices.apartment.deals_count}</div>
                )}
              </div>
            )}

            {city.prices?.house?.avg_price_m2 && (
              <div className="price-item">
                <div className="price-label">House</div>
                <div className="price-value">{Math.round(city.prices.house.avg_price_m2).toLocaleString()} €/m²</div>
                {city.prices?.house?.deals_count !== undefined && (
                  <div className="price-detail">Deals: {city.prices.house.deals_count}</div>
                )}
=======
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
>>>>>>> 422758504451562949a3ea51caba1fdac5ede881
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