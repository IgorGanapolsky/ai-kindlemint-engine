import type { NextApiRequest, NextApiResponse } from 'next';

const CONVERTKIT_API_KEY = process.env.CONVERTKIT_API_KEY;
const CONVERTKIT_FORM_ID = process.env.CONVERTKIT_FORM_ID;

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse
) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  const { email, firstName, tags } = req.body;

  if (!email) {
    return res.status(400).json({ error: 'Email is required' });
  }

  try {
    // Subscribe to ConvertKit
    const response = await fetch(
      `https://api.convertkit.com/v3/forms/${CONVERTKIT_FORM_ID}/subscribe`,
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          api_key: CONVERTKIT_API_KEY,
          email,
          first_name: firstName,
          tags,
        }),
      }
    );

    if (!response.ok) {
      throw new Error('ConvertKit subscription failed');
    }

    const data = await response.json();

    // Log to our analytics/database (to be implemented)
    console.log('New subscriber:', {
      email,
      firstName,
      timestamp: new Date().toISOString(),
      source: 'sudoku-for-seniors-landing',
    });

    // Trigger lead magnet delivery (to be implemented with email automation)
    // This would typically be handled by ConvertKit automation

    return res.status(200).json({ 
      success: true,
      message: 'Successfully subscribed',
    });
  } catch (error) {
    console.error('Subscription error:', error);
    return res.status(500).json({ 
      error: 'Failed to subscribe. Please try again.' 
    });
  }
}