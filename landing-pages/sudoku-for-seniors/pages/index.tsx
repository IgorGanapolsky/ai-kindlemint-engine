import React, { useState } from 'react';
import Head from 'next/head';
import EmailCapture from '../components/EmailCapture';
import Analytics from '../components/Analytics';

export default function Home() {
  const [showThankYou, setShowThankYou] = useState(false);

  return (
    <>
      <Head>
        <title>Large Print Sudoku for Seniors | Free Brain-Boosting Puzzles</title>
        <meta name="description" content="Get 5 FREE large print Sudoku puzzles designed specifically for seniors. Easy on the eyes, challenging for the mind!" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="icon" href="/favicon.ico" />
      </Head>
      
      <Analytics />

      <div className="min-h-screen bg-gradient-to-b from-blue-50 to-white">
        {/* Hero Section */}
        <header className="container mx-auto px-6 py-12">
          <div className="text-center max-w-4xl mx-auto">
            <h1 className="text-5xl md:text-6xl font-bold text-gray-900 mb-6">
              Large Print Sudoku
              <span className="block text-blue-600 mt-2">For Seniors</span>
            </h1>
            
            <p className="text-xl md:text-2xl text-gray-700 mb-8 leading-relaxed">
              Finally, Sudoku puzzles you can actually see! 
              <span className="block mt-2">No more squinting. No more eye strain.</span>
            </p>

            {/* Trust Indicators */}
            <div className="flex flex-wrap justify-center gap-8 mb-12">
              <div className="text-center">
                <div className="text-3xl font-bold text-blue-600">20pt+</div>
                <div className="text-gray-600">Font Size</div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold text-blue-600">4,000+</div>
                <div className="text-gray-600">Happy Solvers</div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold text-blue-600">4.8★</div>
                <div className="text-gray-600">Average Rating</div>
              </div>
            </div>

            {/* Main CTA */}
            {!showThankYou ? (
              <div className="bg-white rounded-lg shadow-xl p-8 max-w-2xl mx-auto">
                <h2 className="text-3xl font-semibold mb-4 text-gray-900">
                  Get 5 FREE Brain-Boosting Puzzles
                </h2>
                <p className="text-lg text-gray-700 mb-6">
                  Join thousands of seniors who start their day with mental exercise!
                </p>
                <SimpleEmailCapture onSuccess={() => setShowThankYou(true)} />
              </div>
            ) : (
              <div className="bg-green-50 rounded-lg shadow-xl p-8 max-w-2xl mx-auto">
                <h2 className="text-3xl font-semibold mb-4 text-green-800">
                  Success! Check Your Email
                </h2>
                <p className="text-lg text-gray-700">
                  Your free puzzles are on their way. You'll also receive our weekly 
                  "Puzzle of the Week" to keep your mind sharp!
                </p>
              </div>
            )}
          </div>
        </header>

        {/* Benefits Section */}
        <section className="container mx-auto px-6 py-16">
          <h2 className="text-3xl font-bold text-center mb-12 text-gray-900">
            Why Seniors Love Our Puzzles
          </h2>
          
          <div className="grid md:grid-cols-3 gap-8 max-w-5xl mx-auto">
            <div className="text-center">
              <div className="text-5xl mb-4">👁️</div>
              <h3 className="text-xl font-semibold mb-2">Easy on the Eyes</h3>
              <p className="text-gray-700">Extra-large print with high contrast. 
              No more headaches from squinting at tiny numbers.</p>
            </div>
            
            <div className="text-center">
              <div className="text-5xl mb-4">🧠</div>
              <h3 className="text-xl font-semibold mb-2">Brain Health</h3>
              <p className="text-gray-700">Studies show Sudoku helps maintain 
              cognitive function and memory as we age.</p>
            </div>
            
            <div className="text-center">
              <div className="text-5xl mb-4">😊</div>
              <h3 className="text-xl font-semibold mb-2">Pure Enjoyment</h3>
              <p className="text-gray-700">Progressive difficulty means you'll 
              always have the perfect challenge level.</p>
            </div>
          </div>
        </section>

        {/* Social Proof */}
        <section className="bg-gray-50 py-16">
          <div className="container mx-auto px-6">
            <h2 className="text-3xl font-bold text-center mb-12 text-gray-900">
              What Other Seniors Are Saying
            </h2>
            
            <div className="grid md:grid-cols-2 gap-8 max-w-4xl mx-auto">
              <div className="bg-white p-6 rounded-lg shadow">
                <p className="text-gray-700 mb-4 italic">
                  "Finally, puzzles I can actually see! I've tried so many 
                  'large print' books that weren't really large at all. These 
                  are perfect."
                </p>
                <p className="font-semibold">- Margaret, age 78</p>
              </div>
              
              <div className="bg-white p-6 rounded-lg shadow">
                <p className="text-gray-700 mb-4 italic">
                  "My doctor recommended brain exercises, and these puzzles 
                  are exactly what I needed. I do one every morning with my coffee."
                </p>
                <p className="font-semibold">- Robert, age 82</p>
              </div>
            </div>
          </div>
        </section>

        {/* Final CTA */}
        {!showThankYou && (
          <section className="container mx-auto px-6 py-16">
            <div className="bg-blue-600 rounded-lg p-8 text-center text-white max-w-2xl mx-auto">
              <h2 className="text-3xl font-bold mb-4">
                Start Your Brain Training Today
              </h2>
              <p className="text-xl mb-6">
                Get your 5 FREE puzzles instantly - no credit card required
              </p>
              <button 
                onClick={() => document.querySelector('#email-capture')?.scrollIntoView({ behavior: 'smooth' })}
                className="bg-white text-blue-600 px-8 py-4 rounded-lg font-semibold text-lg hover:bg-gray-100 transition"
              >
                Get Free Puzzles Now →
              </button>
            </div>
          </section>
        )}

        {/* Footer */}
        <footer className="bg-gray-900 text-white py-8">
          <div className="container mx-auto px-6 text-center">
            <p>&copy; 2025 KindleMint Publishing. All rights reserved.</p>
            <p className="mt-2 text-gray-400">
              Dedicated to creating accessible puzzles for seniors everywhere.
            </p>
          </div>
        </footer>
      </div>
    </>
  );
}