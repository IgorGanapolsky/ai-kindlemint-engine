import type { NextApiRequest, NextApiResponse } from 'next';

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse
) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  const { email, firstName, timestamp } = req.body;
  const githubToken = process.env.NEXT_PUBLIC_GITHUB_TOKEN;
  const githubRepo = process.env.NEXT_PUBLIC_GITHUB_REPO;

  if (!email || !githubToken || !githubRepo) {
    return res.status(400).json({ error: 'Missing required data' });
  }

  try {
    // Save subscriber to GitHub repository as JSON file
    const subscriberData = {
      email,
      firstName,
      timestamp,
      source: 'sudoku-for-seniors-landing',
      leadMagnet: '5-free-sudoku-puzzles',
      userAgent: req.headers['user-agent'] || 'unknown'
    };

    const fileName = `subscribers/${timestamp.replace(/[:.]/g, '-')}-${email.replace('@', '-at-')}.json`;
    const content = Buffer.from(JSON.stringify(subscriberData, null, 2)).toString('base64');

    const githubResponse = await fetch(
      `https://api.github.com/repos/${githubRepo}/contents/${fileName}`,
      {
        method: 'PUT',
        headers: {
          'Authorization': `token ${githubToken}`,
          'Content-Type': 'application/json',
          'Accept': 'application/vnd.github.v3+json',
        },
        body: JSON.stringify({
          message: `Add new subscriber: ${email}`,
          content,
          committer: {
            name: 'Sudoku Landing Page',
            email: 'noreply@sudokufor75plus.com'
          }
        })
      }
    );

    if (!githubResponse.ok) {
      const errorData = await githubResponse.json();
      console.error('GitHub API error:', errorData);
      throw new Error(`GitHub API failed: ${githubResponse.status}`);
    }

    console.log('Subscriber saved to GitHub:', email);

    return res.status(200).json({ 
      success: true,
      message: 'Subscriber data backed up to GitHub',
    });
  } catch (error) {
    console.error('GitHub backup error:', error);
    // Don't fail the whole process if GitHub backup fails
    return res.status(200).json({ 
      success: true,
      message: 'Subscription processed (backup failed but that\'s OK)',
      warning: 'GitHub backup unavailable'
    });
  }
}