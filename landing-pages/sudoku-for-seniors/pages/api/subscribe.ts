import type { NextApiRequest, NextApiResponse } from 'next';

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse
) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  const { email, firstName } = req.body;

  if (!email) {
    return res.status(400).json({ error: 'Email is required' });
  }

  try {
    // This endpoint is now mainly for logging/analytics
    // EmailJS handles the actual email sending on the frontend
    
    console.log('New subscriber:', {
      email,
      firstName,
      timestamp: new Date().toISOString(),
      source: 'sudoku-for-seniors-landing',
    });

    return res.status(200).json({ 
      success: true,
      message: 'Successfully processed subscription',
    });
  } catch (error) {
    console.error('Subscription processing error:', error);
    return res.status(500).json({ 
      error: 'Failed to process subscription' 
    });
  }
}