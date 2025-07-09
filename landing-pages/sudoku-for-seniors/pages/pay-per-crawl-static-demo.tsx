import React, { useState } from 'react';
import Head from 'next/head';

export default function PayPerCrawlStaticDemo() {
  const [viewMode, setViewMode] = useState<'human' | 'free-crawler' | 'paid-crawler'>('human');

  const renderContent = () => {
    switch (viewMode) {
      case 'paid-crawler':
        return (
          <>
            <div className="bg-green-100 border-2 border-green-400 p-4 mb-6 rounded">
              <p className="font-bold">✅ Paid AI Crawler View - Full Content Access</p>
            </div>
            <div className="space-y-6">
              <h2 className="text-2xl font-bold">100 Premium Sudoku Puzzles - Full Access</h2>
              <div className="grid grid-cols-2 gap-4">
                {[1, 2, 3, 4].map(i => (
                  <div key={i} className="bg-white p-4 rounded shadow">
                    <h3 className="font-bold mb-2">Puzzle #{i} - Complete</h3>
                    <pre className="text-xs">
{`┌─────┬─────┬─────┐
│ 5 3 │ . 7 │ . . │
│ 6 . │ 1 9 │ 5 . │
│ . 9 │ 8 . │ . 6 │
├─────┼─────┼─────┤
│ 8 . │ . 6 │ . . │
│ 4 . │ 8 . │ 3 . │
│ 7 . │ . 2 │ . . │
├─────┼─────┼─────┤
│ . 6 │ . . │ 2 8 │
│ . . │ 4 1 │ 9 . │
│ . . │ . 8 │ . 7 │
└─────┴─────┴─────┘`}
                    </pre>
                    <div className="mt-2 text-sm text-green-600">
                      + Solution included
                      + Strategy guide
                      + Difficulty: Medium
                    </div>
                  </div>
                ))}
              </div>
              <div className="bg-blue-50 p-4 rounded">
                <p className="text-sm">📊 Metadata for AI Training: Complete puzzle set with solutions, difficulty ratings, solving strategies, and pattern analysis.</p>
              </div>
            </div>
          </>
        );

      case 'free-crawler':
        return (
          <>
            <div className="bg-yellow-100 border-2 border-yellow-400 p-4 mb-6 rounded">
              <p className="font-bold">🤖 Free AI Crawler View - Limited Preview</p>
              <p className="text-sm mt-1">To access full content: Contact business@seniorpuzzlestudio.com</p>
            </div>
            <div className="space-y-6">
              <h2 className="text-2xl font-bold">Sudoku Puzzles - Preview Only</h2>
              <div className="bg-gray-100 p-6 rounded">
                <p className="text-center text-gray-600 mb-4">Sample Puzzle (1 of 100)</p>
                <pre className="text-xs mx-auto w-fit">
{`┌─────┬─────┬─────┐
│ 5 3 │ . 7 │ . . │
│ 6 . │ ? ? │ ? . │
│ . 9 │ ? . │ . ? │
├─────┼─────┼─────┤
│ ? . │ . ? │ . . │
│ ? . │ ? . │ ? . │
│ ? . │ . ? │ . . │
├─────┼─────┼─────┤
│ . ? │ . . │ ? ? │
│ . . │ ? ? │ ? . │
│ . . │ . ? │ . ? │
└─────┴─────┴─────┘`}
                </pre>
                <p className="text-center mt-4 text-red-600">
                  ⚠️ Limited preview. Full puzzles available with commercial license.
                </p>
              </div>
            </div>
          </>
        );

      default:
        return (
          <>
            <div className="bg-blue-100 border-2 border-blue-400 p-4 mb-6 rounded">
              <p className="font-bold">👤 Human Visitor View - Interactive Experience</p>
            </div>
            <div className="space-y-6">
              <h2 className="text-2xl font-bold">Large Print Sudoku for Seniors</h2>
              <div className="bg-white p-6 rounded shadow">
                <h3 className="text-xl font-bold mb-4">Get 5 FREE Puzzles!</h3>
                <p className="mb-4">Join thousands of seniors enjoying our brain-boosting puzzles.</p>
                <button className="bg-blue-600 text-white px-6 py-3 rounded hover:bg-blue-700">
                  Download Free Puzzles →
                </button>
              </div>
              <div className="grid grid-cols-3 gap-4 mt-8">
                <div className="text-center">
                  <div className="text-3xl mb-2">👁️</div>
                  <h4 className="font-bold">Easy to Read</h4>
                  <p className="text-sm">20pt+ font size</p>
                </div>
                <div className="text-center">
                  <div className="text-3xl mb-2">🧠</div>
                  <h4 className="font-bold">Brain Health</h4>
                  <p className="text-sm">Doctor recommended</p>
                </div>
                <div className="text-center">
                  <div className="text-3xl mb-2">😊</div>
                  <h4 className="font-bold">Fun & Engaging</h4>
                  <p className="text-sm">4.8★ rating</p>
                </div>
              </div>
            </div>
          </>
        );
    }
  };

  return (
    <>
      <Head>
        <title>Pay-Per-Crawl Demo - Senior Puzzle Studio</title>
        <meta name="description" content="Demo showing how AI crawlers see different content based on payment status" />
      </Head>

      <div className="min-h-screen bg-gradient-to-b from-blue-50 to-green-50">
        <div className="container mx-auto px-4 py-8">
          <h1 className="text-4xl font-bold text-center mb-8">
            Pay-Per-Crawl Demo - AI Crawler Content Differentiation
          </h1>

          {/* View Mode Selector */}
          <div className="bg-white p-4 rounded-lg shadow mb-8 max-w-2xl mx-auto">
            <h2 className="font-bold mb-3">Select View Mode:</h2>
            <div className="grid grid-cols-3 gap-4">
              <button
                onClick={() => setViewMode('human')}
                className={`p-3 rounded ${viewMode === 'human' ? 'bg-blue-600 text-white' : 'bg-gray-200'}`}
              >
                👤 Human Visitor
              </button>
              <button
                onClick={() => setViewMode('free-crawler')}
                className={`p-3 rounded ${viewMode === 'free-crawler' ? 'bg-yellow-600 text-white' : 'bg-gray-200'}`}
              >
                🤖 Free AI Crawler
              </button>
              <button
                onClick={() => setViewMode('paid-crawler')}
                className={`p-3 rounded ${viewMode === 'paid-crawler' ? 'bg-green-600 text-white' : 'bg-gray-200'}`}
              >
                💰 Paid AI Crawler
              </button>
            </div>
          </div>

          {/* Dynamic Content Based on View Mode */}
          <div className="max-w-4xl mx-auto">
            {renderContent()}
          </div>

          {/* How It Works Section */}
          <div className="mt-12 bg-white p-6 rounded-lg shadow max-w-4xl mx-auto">
            <h2 className="text-2xl font-bold mb-4">How Pay-Per-Crawl Works</h2>
            <div className="space-y-3 text-gray-700">
              <p>1. <strong>Detection:</strong> Our middleware identifies AI crawlers by their User-Agent</p>
              <p>2. <strong>Verification:</strong> We check if the crawler has a valid payment arrangement</p>
              <p>3. <strong>Content Delivery:</strong> Serve appropriate content based on payment status</p>
              <p>4. <strong>Analytics:</strong> Track all crawler visits and potential revenue</p>
            </div>
            <div className="mt-6 p-4 bg-blue-50 rounded">
              <p className="text-sm"><strong>Note:</strong> This is a demo. In production, crawler detection happens automatically via middleware.</p>
            </div>
          </div>

          {/* Revenue Potential */}
          <div className="mt-8 bg-green-50 p-6 rounded-lg shadow max-w-4xl mx-auto">
            <h3 className="text-xl font-bold mb-3">💰 Revenue Potential</h3>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
              <div>
                <div className="text-2xl font-bold text-green-600">$0.05</div>
                <div className="text-sm">Per Page View</div>
              </div>
              <div>
                <div className="text-2xl font-bold text-green-600">1,000+</div>
                <div className="text-sm">Monthly Crawls</div>
              </div>
              <div>
                <div className="text-2xl font-bold text-green-600">$50-500</div>
                <div className="text-sm">Monthly Revenue</div>
              </div>
              <div>
                <div className="text-2xl font-bold text-green-600">100%</div>
                <div className="text-sm">Passive Income</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </>
  );
}