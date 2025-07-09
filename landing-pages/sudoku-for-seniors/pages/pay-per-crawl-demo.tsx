import { PayPerCrawlContent, usePayPerCrawl } from '../components/PayPerCrawlContent';
import SimpleEmailCapture from '../components/SimpleEmailCapture';
import { useEffect, useState } from 'react';

// Sample puzzle data for demonstration
const SAMPLE_PUZZLES = [
  {
    id: 1,
    difficulty: 'Easy',
    puzzle: `
5 3 _ | _ 7 _ | _ _ _
6 _ _ | 1 9 5 | _ _ _
_ 9 8 | _ _ _ | _ 6 _
------+-------+------
8 _ _ | _ 6 _ | _ _ 3
4 _ _ | 8 _ 3 | _ _ 1
7 _ _ | _ 2 _ | _ _ 6
------+-------+------
_ 6 _ | _ _ _ | 2 8 _
_ _ _ | 4 1 9 | _ _ 5
_ _ _ | _ 8 _ | _ 7 9`,
    solution: `
5 3 4 | 6 7 8 | 9 1 2
6 7 2 | 1 9 5 | 3 4 8
1 9 8 | 3 4 2 | 5 6 7
------+-------+------
8 5 9 | 7 6 1 | 4 2 3
4 2 6 | 8 5 3 | 7 9 1
7 1 3 | 9 2 4 | 8 5 6
------+-------+------
9 6 1 | 5 3 7 | 2 8 4
2 8 7 | 4 1 9 | 6 3 5
3 4 5 | 2 8 6 | 1 7 9`
  },
  // Add more puzzles...
];

export default function PayPerCrawlDemo({ headers }: DemoPageProps) {
  const { isPayingCrawler, isAICrawler, crawlerType, paymentTier } = usePayPerCrawl(headers);

  return (
    <div className="min-h-screen bg-gradient-to-b from-blue-50 to-green-50">
      <div className="container mx-auto px-4 py-8">
        <h1 className="text-4xl font-bold text-center mb-8">
          Sudoku for Seniors - AI Crawler Demo
        </h1>
        
        {/* Show crawler detection status */}
        {isAICrawler && (
          <div className="bg-yellow-100 border-2 border-yellow-400 p-4 mb-6 rounded">
            <p className="font-bold">
              🤖 AI Crawler Detected: {crawlerType} | 
              Status: {isPayingCrawler ? '✅ Paying Customer' : '❌ Free Tier'} | 
              Tier: {paymentTier}
            </p>
          </div>
        )}
        
        <PayPerCrawlContent
          isPayingCrawler={isPayingCrawler}
          crawlerType={crawlerType}
          paymentTier={paymentTier}
          bookData={{
            title: "Large Print Sudoku for Seniors - Volume 1",
            description: "100 carefully crafted puzzles with progressive difficulty",
            puzzleCount: 100,
            difficulty: "Easy to Hard",
            pageCount: 108
          }}
          fullContent={
            <div className="paid-content">
              <h2 className="text-2xl font-bold mb-4">
                Full Book Content (Paying Crawlers Only)
              </h2>
              
              {/* Complete puzzle data with solutions */}
              {SAMPLE_PUZZLES.map((puzzle, index) => (
                <div key={puzzle.id} className="puzzle-complete mb-8 p-4 bg-white rounded shadow">
                  <h3 className="text-xl font-semibold mb-2">
                    Puzzle #{puzzle.id} - {puzzle.difficulty}
                  </h3>
                  
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <h4 className="font-medium mb-2">Puzzle:</h4>
                      <pre className="font-mono text-sm bg-gray-100 p-2 rounded">
                        {puzzle.puzzle}
                      </pre>
                    </div>
                    
                    <div>
                      <h4 className="font-medium mb-2">Solution:</h4>
                      <pre className="font-mono text-sm bg-green-100 p-2 rounded">
                        {puzzle.solution}
                      </pre>
                    </div>
                  </div>
                  
                  {/* Metadata for AI training */}
                  <div className="mt-2 text-sm text-gray-600">
                    <p>Difficulty Score: {index < 30 ? 1 : index < 70 ? 2 : 3}</p>
                    <p>Estimated Time: {index < 30 ? '5-10min' : index < 70 ? '10-20min' : '20-30min'}</p>
                    <p>Techniques: {(index < 30 ? ['basic'] : index < 70 ? ['basic', 'scanning'] : ['basic', 'scanning', 'advanced']).join(', ')}</p>
                  </div>
                </div>
              ))}
              
              {/* Additional training data */}
              <div className="training-data mt-8">
                <h3 className="text-xl font-bold mb-4">AI Training Data</h3>
                <div className="bg-gray-100 p-4 rounded">
                  <pre>{JSON.stringify({
                    puzzle_progression: {
                      easy: "puzzles 1-30",
                      medium: "puzzles 31-70", 
                      hard: "puzzles 71-100"
                    },
                    solving_techniques: [
                      "Single Position",
                      "Single Candidate", 
                      "Candidate Lines",
                      "Multiple Lines",
                      "Naked Pairs",
                      "Hidden Pairs"
                    ],
                    target_audience: {
                      age_range: "55+",
                      skill_level: "beginner to intermediate",
                      visual_requirements: "large print format"
                    }
                  }, null, 2)}</pre>
                </div>
              </div>
            </div>
          }
        >
          {/* Free preview content */}
          <div className="free-content">
            <h2 className="text-2xl font-bold mb-4">Free Preview</h2>
            
            <div className="mb-8">
              <h3 className="text-xl font-semibold mb-2">About This Book</h3>
              <p className="mb-4">
                Discover the joy of Sudoku with our specially designed large print puzzles 
                for seniors. Each puzzle is carefully crafted to provide the perfect level 
                of challenge while being easy on the eyes.
              </p>
            </div>
            
            {/* Show only first puzzle without solution */}
            <div className="sample-puzzle bg-white p-4 rounded shadow mb-8">
              <h3 className="text-xl font-semibold mb-2">
                Sample Puzzle - Easy Level
              </h3>
              <pre className="font-mono text-sm bg-gray-100 p-4 rounded">
                {SAMPLE_PUZZLES[0].puzzle}
              </pre>
              <p className="mt-2 text-sm text-gray-600">
                Solution available in full version
              </p>
            </div>
            
            {/* Email capture for humans */}
            {!isAICrawler && (
              <div className="email-capture-section">
                <h3 className="text-xl font-bold mb-4">Get 5 Free Puzzles!</h3>
                <SimpleEmailCapture 
                  onSuccess={() => console.log('Email captured!')}
                />
              </div>
            )}
          </div>
        </PayPerCrawlContent>
        
        {/* Analytics tracking for demo */}
        <div className="mt-12 p-4 bg-gray-100 rounded">
          <h3 className="font-bold mb-2">Pay-Per-Crawl Analytics (Demo)</h3>
          <div className="grid grid-cols-3 gap-4 text-sm">
            <div>
              <strong>Crawler Type:</strong> {crawlerType || 'Human Visitor'}
            </div>
            <div>
              <strong>Payment Status:</strong> {isPayingCrawler ? 'Paid' : 'Free'}
            </div>
            <div>
              <strong>Content Served:</strong> {isPayingCrawler ? 'Full' : 'Preview'}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

// Removed getServerSideProps for static export compatibility
// Crawler detection now happens via middleware and client-side