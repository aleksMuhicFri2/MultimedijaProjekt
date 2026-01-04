import React, { useEffect, useState } from "react";
import SloveniaMap from "./components/SloveniaMap";
import MunicipalityPanel from "./components/MunicipalityPanel";
import AttributePicker from "./components/AttributePicker";
import SearchResults from "./components/SearchResults";
import "./App.css";

function App() {
  const [selectedCode, setSelectedCode] = useState(null);
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [viewMode, setViewMode] = useState('map'); // 'map' or 'search'
  const [searchResults, setSearchResults] = useState(null);
  const [searchLoading, setSearchLoading] = useState(false);
  const [searchError, setSearchError] = useState(null);
  const [searchMeta, setSearchMeta] = useState(null);

  useEffect(() => {
    if (!selectedCode) return;

    setLoading(true);
    setData(null);
    setError(null);

    fetch(`http://localhost:5000/api/municipality/${selectedCode}`)
      .then((r) => {
        if (!r.ok) throw new Error(`HTTP ${r.status}`);
        return r.json();
      })
      .then(responseData => {
        console.log('Municipality data received:', responseData);
        console.log('Population breakdown:', {
          young: responseData.population_young,
          working: responseData.population_working,
          old: responseData.population_old,
          total: responseData.population_total
        });
        console.log('Area:', responseData.area_km2);
        console.log('Density:', responseData.population_density);
        setData(responseData);
      })
      .catch(err => {
        console.error('Failed to fetch municipality:', err);
        setError(err.message);
      })
      .finally(() => setLoading(false));
  }, [selectedCode]);

  const handleSearch = async (criteria) => {
    console.log('Search criteria:', criteria);
    
    setSearchLoading(true);
    setSearchError(null);
    setSearchResults(null);
    
    try {
      const response = await fetch('http://localhost:5000/api/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ...criteria, limit: 20 })
      });
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }
      
      const data = await response.json();
      setSearchResults(data.results);
      setSearchMeta(data.meta || null);
      // Store suggestions from backend
      if (data.suggestions) {
        setSearchMeta(prev => ({ ...prev, suggestions: data.suggestions }));
      }
    } catch (err) {
      console.error('Search failed:', err);
      setSearchError(err.message);
    } finally {
      setSearchLoading(false);
    }
  };

  const toggleView = () => {
    setViewMode(prev => prev === 'map' ? 'search' : 'map');
  };

  return (
    <div className="app-container">
      {/* Enhanced Title Section */}
      <header className="app-title">
        <h1>Slovenian Municipalities Explorer</h1>
        <p className="subtitle">Interactive Real Estate & Demographic Analysis</p>
        
        {/* View Toggle Button */}
        <div className="view-toggle-container">
          <button className="view-toggle-btn" onClick={toggleView}>
            {viewMode === 'map' ? 'Find Best Municipality' : 'Back to Map'}
          </button>
        </div>
      </header>

      {/* Main Content with Modern Layout */}
      <div className="main-content">
        {/* Map Section - Always Visible */}
        <div className="map-section">
          <SloveniaMap
            selectedCode={selectedCode}
            onSelectMunicipality={setSelectedCode}
          />
        </div>

        {/* Right Panel - Toggle between Data and Attribute Picker */}
        {viewMode === 'map' ? (
          <div className="data-section">
            {loading && (
              <div className="loading-state">
                <div className="spinner"></div>
                <p>Loading municipality data...</p>
              </div>
            )}
            
            {error && (
              <div className="error-state">
                <span className="error-icon">⚠️</span>
                <p>Error: {error}</p>
              </div>
            )}
            
            {!data && !loading && !error && (
              <div className="empty-state">
                <span className="icon">📍</span>
                <h3>Select a Municipality</h3>
                <p>Click on any region on the map to view detailed statistics</p>
              </div>
            )}
            
            {data && !error && <MunicipalityPanel data={data} />}
          </div>
        ) : (
          <>
            <AttributePicker onSearch={handleSearch} />
            <SearchResults 
              results={searchResults} 
              loading={searchLoading} 
              error={searchError} 
              meta={searchMeta}
              suggestions={searchMeta?.suggestions}
            />
          </>
        )}
      </div>
    </div>
  );
}

export default App;