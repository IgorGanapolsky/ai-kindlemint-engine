import React, { useEffect, useState } from 'react';

interface CrawlerStats {
  totalCrawls: number;
  paidCrawls: number;
  earnings: number;
  conversionRate: string;
  averageEarningsPerCrawl: string;
  topCrawlers: Array<{ type: string; count: number }>;
  lastUpdated: string;
}

export function PayPerCrawlDashboard() {
  const [stats, setStats] = useState<CrawlerStats | null>(null);
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    const fetchStats = async () => {
      try {
        const response = await fetch('/api/crawler-analytics');
        const data = await response.json();
        setStats(data);
      } catch (error) {
        console.error('Failed to fetch crawler stats:', error);
      } finally {
        setLoading(false);
      }
    };
    
    fetchStats();
    // Refresh every 30 seconds
    const interval = setInterval(fetchStats, 30000);
    
    return () => clearInterval(interval);
  }, []);
  
  if (loading) {
    return <div className="text-center p-4">Loading analytics...</div>;
  }
  
  if (!stats) {
    return <div className="text-center p-4">No data available</div>;
  }
  
  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <h2 className="text-2xl font-bold mb-6">🤖 Pay-Per-Crawl Analytics</h2>
      
      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
        <div className="bg-blue-50 rounded p-4">
          <div className="text-sm text-gray-600">Total Earnings</div>
          <div className="text-2xl font-bold text-blue-600">
            ${stats.earnings.toFixed(2)}
          </div>
        </div>
        
        <div className="bg-green-50 rounded p-4">
          <div className="text-sm text-gray-600">Paid Crawls</div>
          <div className="text-2xl font-bold text-green-600">
            {stats.paidCrawls}
          </div>
        </div>
        
        <div className="bg-purple-50 rounded p-4">
          <div className="text-sm text-gray-600">Conversion Rate</div>
          <div className="text-2xl font-bold text-purple-600">
            {stats.conversionRate}
          </div>
        </div>
        
        <div className="bg-yellow-50 rounded p-4">
          <div className="text-sm text-gray-600">Avg per Crawl</div>
          <div className="text-2xl font-bold text-yellow-600">
            {stats.averageEarningsPerCrawl}
          </div>
        </div>
      </div>
      
      {/* Crawler Breakdown */}
      <div className="mb-8">
        <h3 className="text-lg font-semibold mb-4">Top Crawlers</h3>
        {stats.topCrawlers.length > 0 ? (
          <div className="space-y-2">
            {stats.topCrawlers.map((crawler, index) => (
              <div key={crawler.type} className="flex items-center justify-between bg-gray-50 rounded p-3">
                <div className="flex items-center">
                  <span className="text-2xl mr-3">
                    {index === 0 ? '🥇' : index === 1 ? '🥈' : index === 2 ? '🥉' : '🤖'}
                  </span>
                  <span className="font-medium">{crawler.type}</span>
                </div>
                <span className="text-gray-600">{crawler.count} crawls</span>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-gray-500">No crawler data yet</p>
        )}
      </div>
      
      {/* Revenue Projection */}
      <div className="bg-gradient-to-r from-green-50 to-blue-50 rounded p-4">
        <h3 className="text-lg font-semibold mb-2">💰 Revenue Projection</h3>
        <div className="grid grid-cols-3 gap-4 text-sm">
          <div>
            <div className="text-gray-600">Daily (projected)</div>
            <div className="font-bold">${(stats.earnings * 24).toFixed(2)}</div>
          </div>
          <div>
            <div className="text-gray-600">Monthly (projected)</div>
            <div className="font-bold">${(stats.earnings * 24 * 30).toFixed(2)}</div>
          </div>
          <div>
            <div className="text-gray-600">Yearly (projected)</div>
            <div className="font-bold">${(stats.earnings * 24 * 365).toFixed(2)}</div>
          </div>
        </div>
      </div>
      
      {/* Last Updated */}
      <div className="mt-4 text-xs text-gray-500 text-right">
        Last updated: {new Date(stats.lastUpdated).toLocaleString()}
      </div>
    </div>
  );
}

// Mini dashboard for embedding in pages
export function PayPerCrawlMiniDashboard() {
  const [earnings, setEarnings] = useState<number>(0);
  
  useEffect(() => {
    fetch('/api/crawler-analytics')
      .then(res => res.json())
      .then(data => setEarnings(data.earnings))
      .catch(() => setEarnings(0));
  }, []);
  
  return (
    <div className="inline-flex items-center bg-green-100 rounded-full px-3 py-1 text-sm">
      <span className="mr-2">💰</span>
      <span className="font-semibold">${earnings.toFixed(2)}</span>
      <span className="ml-1 text-gray-600">earned</span>
    </div>
  );
}