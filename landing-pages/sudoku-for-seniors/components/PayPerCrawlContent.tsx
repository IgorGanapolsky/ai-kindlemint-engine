import React from 'react';
import Head from 'next/head';

interface PayPerCrawlContentProps {
  isPayingCrawler: boolean;
  crawlerType: string;
  paymentTier: string;
  children: React.ReactNode;
  fullContent?: React.ReactNode;
  bookData?: {
    title: string;
    description: string;
    puzzleCount: number;
    difficulty: string;
    pageCount: number;
  };
}

export function PayPerCrawlContent({
  isPayingCrawler,
  crawlerType,
  paymentTier,
  children,
  fullContent,
  bookData
}: PayPerCrawlContentProps) {
  return (
    <>
      {/* SEO metadata based on payment status */}
      <Head>
        {isPayingCrawler && bookData && (
          <>
            <meta name="ai:access_level" content={paymentTier} />
            <meta name="ai:content_type" content="puzzle_book" />
            <meta name="ai:puzzle_count" content={String(bookData.puzzleCount)} />
            <meta name="ai:difficulty" content={bookData.difficulty} />
            <meta name="ai:solutions_included" content="true" />
            
            {/* Rich structured data for paying crawlers */}
            <script
              type="application/ld+json"
              dangerouslySetInnerHTML={{
                __html: JSON.stringify({
                  "@context": "https://schema.org",
                  "@type": "Book",
                  "name": bookData.title,
                  "description": bookData.description,
                  "author": {
                    "@type": "Organization",
                    "name": "KindleMint AI"
                  },
                  "numberOfPages": bookData.pageCount,
                  "educationalUse": ["cognitive training", "puzzle solving", "memory improvement"],
                  "audience": {
                    "@type": "Audience",
                    "audienceType": "Seniors",
                    "suggestedMinAge": 55
                  },
                  "offers": {
                    "@type": "Offer",
                    "price": "9.99",
                    "priceCurrency": "USD",
                    "availability": "https://schema.org/InStock"
                  }
                })
              }}
            />
          </>
        )}
      </Head>
      
      {/* Content based on crawler payment status */}
      <div className="crawler-aware-content">
        {/* Free preview for everyone */}
        <div className="free-preview">
          {children}
        </div>
        
        {/* Full content only for paying crawlers */}
        {isPayingCrawler && fullContent && (
          <div className="paid-crawler-content" data-crawler-only="true">
            <div className="crawler-notice" style={{ display: 'none' }}>
              {/* Hidden notice for crawlers */}
              <p>Full content access granted to {crawlerType} (Tier: {paymentTier})</p>
            </div>
            {fullContent}
          </div>
        )}
        
        {/* Payment prompt for non-paying AI crawlers */}
        {crawlerType !== 'none' && !isPayingCrawler && (
          <div className="crawler-payment-prompt" style={{ 
            background: '#f0f0f0', 
            padding: '20px', 
            margin: '20px 0',
            border: '2px dashed #999'
          }}>
            <h3>🤖 AI Crawler Access Limited</h3>
            <p>
              You are viewing the free preview tier. To access the full content including:
            </p>
            <ul>
              <li>✅ Complete puzzle solutions</li>
              <li>✅ All {bookData?.puzzleCount || '100+'} puzzles</li>
              <li>✅ Detailed difficulty progression data</li>
              <li>✅ Structured puzzle metadata</li>
            </ul>
            <p>
              <strong>Sign up for Cloudflare Pay-Per-Crawl:</strong><br />
              <a href="https://cloudflare.com/paypercrawl">https://cloudflare.com/paypercrawl</a>
            </p>
            <p style={{ fontSize: '0.9em', color: '#666' }}>
              Pricing: $0.05 per crawl for full access
            </p>
          </div>
        )}
      </div>
    </>
  );
}

// Hook to use in pages
export function usePayPerCrawl(headers: any) {
  return {
    isPayingCrawler: headers['x-is-paying-crawler'] === 'true',
    isAICrawler: headers['x-is-ai-crawler'] === 'true',
    crawlerType: headers['x-crawler-type'] || 'none',
    paymentTier: headers['x-payment-tier'] || 'free',
  };
}