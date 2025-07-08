import { NextApiRequest, NextApiResponse } from 'next';

// In-memory storage for demo (use database in production)
let crawlerStats = {
  totalCrawls: 0,
  paidCrawls: 0,
  earnings: 0,
  crawlerTypes: {} as Record<string, number>,
  lastUpdated: new Date().toISOString(),
};

export default function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method === 'POST') {
    // Track crawler access
    const { crawlerType, isPaid, tier } = req.body;
    
    crawlerStats.totalCrawls++;
    if (isPaid) {
      crawlerStats.paidCrawls++;
      // Calculate earnings based on tier
      const earnings = tier === 'premium' ? 0.25 : tier === 'standard' ? 0.10 : 0.05;
      crawlerStats.earnings += earnings;
    }
    
    // Track crawler types
    crawlerStats.crawlerTypes[crawlerType] = (crawlerStats.crawlerTypes[crawlerType] || 0) + 1;
    crawlerStats.lastUpdated = new Date().toISOString();
    
    return res.status(200).json({ success: true });
  }
  
  if (req.method === 'GET') {
    // Return analytics data
    const data = {
      ...crawlerStats,
      conversionRate: crawlerStats.totalCrawls > 0 
        ? ((crawlerStats.paidCrawls / crawlerStats.totalCrawls) * 100).toFixed(2) + '%'
        : '0%',
      averageEarningsPerCrawl: crawlerStats.paidCrawls > 0
        ? '$' + (crawlerStats.earnings / crawlerStats.paidCrawls).toFixed(3)
        : '$0',
      topCrawlers: Object.entries(crawlerStats.crawlerTypes)
        .sort(([,a], [,b]) => b - a)
        .slice(0, 5)
        .map(([type, count]) => ({ type, count })),
    };
    
    return res.status(200).json(data);
  }
  
  return res.status(405).json({ error: 'Method not allowed' });
}