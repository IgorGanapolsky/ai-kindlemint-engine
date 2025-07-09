import React, { useEffect } from 'react';
import { useRouter } from 'next/router';

export default function PayPerCrawlDemo() {
  const router = useRouter();
  
  useEffect(() => {
    // Redirect to the static demo that works with S3
    router.push('/pay-per-crawl-static-demo');
  }, [router]);

  return (
    <div className="min-h-screen flex items-center justify-center">
      <div className="text-center">
        <h1 className="text-2xl font-bold mb-4">Redirecting to demo...</h1>
        <p className="text-gray-600">Taking you to the Pay-Per-Crawl static demo</p>
      </div>
    </div>
  );
}