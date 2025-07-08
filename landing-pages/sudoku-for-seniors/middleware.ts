import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

// Known AI crawler user agents
const AI_CRAWLERS = [
  'GPTBot',           // OpenAI
  'ChatGPT-User',     // ChatGPT browsing
  'Claude-Web',       // Anthropic Claude
  'Bard',             // Google Bard
  'bingbot',          // Microsoft Bing
  'Googlebot',        // Google (may be AI training)
  'facebookexternalhit', // Meta AI
  'Twitterbot',       // Twitter/X
];

export function middleware(request: NextRequest) {
  const userAgent = request.headers.get('user-agent') || '';
  
  // Check if request is from a known AI crawler
  const isAICrawler = AI_CRAWLERS.some(bot => 
    userAgent.toLowerCase().includes(bot.toLowerCase())
  );
  
  // Check if this is a paying crawler (Cloudflare header)
  const isPayingCrawler = request.headers.get('cf-paypercrawl-verified') === 'true';
  const crawlerType = request.headers.get('cf-paypercrawl-bot');
  const paymentTier = request.headers.get('cf-paypercrawl-tier') || 'free';
  
  // Add crawler info to request headers for pages to use
  const requestHeaders = new Headers(request.headers);
  requestHeaders.set('x-is-ai-crawler', isAICrawler ? 'true' : 'false');
  requestHeaders.set('x-is-paying-crawler', isPayingCrawler ? 'true' : 'false');
  requestHeaders.set('x-crawler-type', crawlerType || 'none');
  requestHeaders.set('x-payment-tier', paymentTier);
  
  // Log crawler access for analytics
  if (isAICrawler) {
    console.log(`AI Crawler detected: ${userAgent} - Paying: ${isPayingCrawler}`);
  }
  
  // For non-paying AI crawlers, add rate limiting headers
  if (isAICrawler && !isPayingCrawler) {
    const response = NextResponse.next({
      request: {
        headers: requestHeaders,
      },
    });
    
    // Add payment prompt header
    response.headers.set('X-Payment-Required', 'Sign up at cloudflare.com/paypercrawl for full access');
    response.headers.set('X-Crawl-Limit', '10 pages per day for free tier');
    
    return response;
  }
  
  return NextResponse.next({
    request: {
      headers: requestHeaders,
    },
  });
}

export const config = {
  matcher: [
    /*
     * Match all request paths except for the ones starting with:
     * - api (API routes)
     * - _next/static (static files)
     * - _next/image (image optimization files)
     * - favicon.ico (favicon file)
     */
    '/((?!api|_next/static|_next/image|favicon.ico).*)',
  ],
};