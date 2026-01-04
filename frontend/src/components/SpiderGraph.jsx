/**
 * Spider/Radar Graph Component for Municipality Comparison
 * 
 * Visualizes multiple municipalities across scoring dimensions:
 * - Affordability: Lower prices = higher score
 * - Market Activity: More deals = higher score
 * - Population Vitality: Higher working-age % = higher score
 * - Healthcare: Higher IOZ coverage = higher score
 * - Housing Diversity: More property types = higher score
 * - Commute: Shorter commute to workplace = higher (when workplace set)
 * 
 * All axes are normalized 0-100 for fair comparison.
 */

import React, { useMemo } from 'react';
import { Radar } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  RadialLinearScale,
  PointElement,
  LineElement,
  Filler,
  Tooltip,
  Legend
} from 'chart.js';

ChartJS.register(
  RadialLinearScale,
  PointElement,
  LineElement,
  Filler,
  Tooltip,
  Legend
);

// Color palette for different cities
const COLORS = [
  { bg: 'rgba(16, 185, 129, 0.2)', border: '#10B981', name: 'Emerald' },
  { bg: 'rgba(59, 130, 246, 0.2)', border: '#3B82F6', name: 'Blue' },
  { bg: 'rgba(245, 158, 11, 0.2)', border: '#F59E0B', name: 'Amber' },
  { bg: 'rgba(139, 92, 246, 0.2)', border: '#8B5CF6', name: 'Violet' },
  { bg: 'rgba(236, 72, 153, 0.2)', border: '#EC4899', name: 'Pink' },
];

// Axis configuration matching backend scoring categories
const AXIS_CONFIG = {
  affordability: {
    label: 'Affordability',
    description: 'Lower prices relative to budget = higher score'
  },
  market_activity: {
    label: 'Market Activity',
    description: 'More property deals = more options'
  },
  population_vitality: {
    label: 'Population',
    description: 'Higher working-age population %'
  },
  healthcare: {
    label: 'Healthcare',
    description: 'IOZ (personal doctor) coverage'
  },
  housing_diversity: {
    label: 'Housing Options',
    description: 'Variety of property types available'
  },
  commute: {
    label: 'Commute',
    description: 'Shorter commute to workplace (Google Maps)'
  }
};

function SpiderGraph({ results, maxCities = 5, showLegend = true, height = 400 }) {
  const graphData = useMemo(() => {
    if (!results || results.length === 0) {
      return null;
    }

    // Take top N cities
    const topResults = results.slice(0, maxCities);

    // Determine which axes to show (exclude commute if all null)
    const hasCommute = topResults.some(r => {
      const score = r.category_scores?.commute;
      return score !== null && score !== undefined && score > 0;
    });

    const axes = [
      'affordability',
      'market_activity',
      'population_vitality',
      'healthcare',
      'housing_diversity',
    ];
    
    if (hasCommute) {
      axes.push('commute');
    }

    const labels = axes.map(key => AXIS_CONFIG[key]?.label || key);

    const datasets = topResults.map((result, index) => {
      const scores = result.category_scores || {};
      const color = COLORS[index % COLORS.length];

      return {
        label: result.city?.name || `City ${index + 1}`,
        data: axes.map(key => {
          const score = scores[key];
          return typeof score === 'number' && score > 0 ? score : 0;
        }),
        backgroundColor: color.bg,
        borderColor: color.border,
        pointBackgroundColor: color.border,
        pointBorderColor: '#fff',
        pointHoverBackgroundColor: '#fff',
        pointHoverBorderColor: color.border,
        borderWidth: 2,
        pointRadius: 4,
        pointHoverRadius: 6,
      };
    });

    return { labels, datasets, axes };
  }, [results, maxCities]);

  if (!graphData) {
    return (
      <div style={{
        height,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        background: '#F9FAFB',
        borderRadius: 12,
        color: '#6B7280'
      }}>
        No data available for comparison
      </div>
    );
  }

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: showLegend,
        position: 'bottom',
        labels: {
          usePointStyle: true,
          padding: 20,
          font: { size: 12 }
        }
      },
      tooltip: {
        callbacks: {
          label: (context) => {
            const axisKey = graphData.axes[context.dataIndex];
            const description = AXIS_CONFIG[axisKey]?.description || '';
            return [
              `${context.dataset.label}: ${context.raw.toFixed(1)}`,
              `(${description})`
            ];
          }
        }
      }
    },
    scales: {
      r: {
        beginAtZero: true,
        min: 0,
        max: 100,
        ticks: {
          stepSize: 20,
          font: { size: 10 },
          backdropColor: 'transparent'
        },
        pointLabels: {
          font: { size: 11, weight: 500 },
          color: '#374151'
        },
        grid: {
          color: 'rgba(0, 0, 0, 0.1)'
        },
        angleLines: {
          color: 'rgba(0, 0, 0, 0.1)'
        }
      }
    }
  };

  return (
    <div style={{ height, position: 'relative' }}>
      <Radar data={graphData} options={options} />
    </div>
  );
}

// Legend explaining what each axis means
export function SpiderGraphLegend({ hasCommute = false }) {
  const axesToShow = ['affordability', 'market_activity', 'population_vitality', 'healthcare', 'housing_diversity'];
  if (hasCommute) axesToShow.push('commute');

  return (
    <div style={{
      display: 'grid',
      gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
      gap: '0.75rem',
      padding: '1rem',
      background: '#F9FAFB',
      borderRadius: 8,
      fontSize: '0.85rem'
    }}>
      {axesToShow.map(key => {
        const config = AXIS_CONFIG[key];
        return (
          <div key={key} style={{ display: 'flex', alignItems: 'flex-start', gap: '0.5rem' }}>
            <span style={{ 
              fontWeight: 600, 
              color: '#374151',
              minWidth: '100px'
            }}>
              {config.label}:
            </span>
            <span style={{ color: '#6B7280' }}>
              {config.description}
            </span>
          </div>
        );
      })}
    </div>
  );
}

export default SpiderGraph;
