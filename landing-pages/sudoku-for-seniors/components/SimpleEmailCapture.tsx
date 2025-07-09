import React, { useState } from 'react';

interface EmailCaptureProps {
  onSuccess: () => void;
}

const SimpleEmailCapture: React.FC<EmailCaptureProps> = ({ onSuccess }) => {
  const [email, setEmail] = useState('');
  const [firstName, setFirstName] = useState('');
  const [submitted, setSubmitted] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    
    // Store in localStorage as backup
    const subscribers = JSON.parse(localStorage.getItem('sudoku_subscribers') || '[]');
    subscribers.push({
      email,
      firstName,
      timestamp: new Date().toISOString()
    });
    localStorage.setItem('sudoku_subscribers', JSON.stringify(subscribers));
    
    // Send via Web3Forms (FREE for 250 submissions/month)
    try {
      const response = await fetch('https://api.web3forms.com/submit', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        },
        body: JSON.stringify({
          access_key: '64ecaccd-8852-423b-a8a4-4ccd74b0f1a7',
          email: email,
          name: firstName,
          subject: '🧩 New Sudoku Lead from Landing Page!',
          message: `New lead magnet signup: ${firstName} (${email}) wants the 5 FREE Brain-Boosting Puzzles`,
          from_name: 'AI KindleMint Engine',
          redirect: ''
        })
      });

      const result = await response.json();
      
      if (response.ok && result.success) {
        console.log('✅ Web3Forms submission successful');
        
        // Store in localStorage as backup
        const updatedSubscribers = JSON.parse(localStorage.getItem('sudoku_subscribers') || '[]');
        updatedSubscribers.push({
          email,
          firstName,
          timestamp: new Date().toISOString(),
          source: 'web3forms'
        });
        localStorage.setItem('sudoku_subscribers', JSON.stringify(updatedSubscribers));
        
        setSubmitted(true);
        onSuccess();
      } else {
        throw new Error(`Web3Forms error: ${result.message || response.status}`);
      }
    } catch (error) {
      console.error('❌ Form submission failed:', error);
      alert('Something went wrong. Please try again or email us directly at support@ai-kindlemint-engine.com');
    } finally {
      setIsSubmitting(false);
    }  };

  if (submitted) {
    // Auto-download the PDF after a brief delay
    if (typeof window !== 'undefined') {
      setTimeout(() => {
        // Create a temporary link element to force download
        const link = document.createElement('a');
        link.href = "/downloads/5-free-sudoku-puzzles.pdf";
        link.download = "5-free-sudoku-puzzles.pdf";
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
      }, 1000);
    }
    
    return (
      <div className="text-center p-6">
        <h3 className="text-2xl font-bold text-green-800 mb-4">✅ Success!</h3>
        <p className="text-lg text-gray-700 mb-4">
          <strong>Your puzzles are downloading now!</strong><br/>
          <span className="text-sm">Check your Downloads folder for "5-free-sudoku-puzzles.pdf"</span>
        </p>
        <div className="bg-blue-50 p-4 rounded-lg mb-4">
          <p className="text-sm text-gray-600">
            📧 <strong>Note:</strong> We've saved your email for future puzzle updates and special offers.
          </p>
        </div>
        <a
          href="/downloads/5-free-sudoku-puzzles.pdf"
          className="inline-block bg-blue-600 text-white px-6 py-2 rounded hover:bg-blue-700 mb-4"
          download="5-free-sudoku-puzzles.pdf"
        >
          📥 Download Again
        </a>
        
        {/* IMMEDIATE UPSELL - This is where we make money! */}
        <div className="mt-8 p-6 bg-yellow-50 border-2 border-yellow-400 rounded-lg">
          <h3 className="text-2xl font-bold text-gray-900 mb-2">
            🎉 WAIT! Special One-Time Offer
          </h3>
          <p className="text-lg mb-4">
            Get <strong>100 Premium Large Print Puzzles</strong> for just <strong>$4.99</strong>
            <br />
            <span className="text-sm text-gray-600 line-through">Regular Price: $14.99</span>
          </p>
          <p className="text-red-600 font-semibold mb-4">
            ⏰ This 70% discount expires when you leave this page!
          </p>
          <a
            href="https://iganapolsky.gumroad.com/l/hjybj"
            className="inline-block bg-green-600 text-white px-8 py-4 rounded-lg hover:bg-green-700 font-bold text-xl"
            target="_blank"
            rel="noopener noreferrer"
          >
            YES! I Want 100 Puzzles for $4.99 →
          </a>
          <p className="text-xs text-gray-500 mt-2">
            No subscription • Instant download • 30-day guarantee
          </p>
        </div>
      </div>
    );
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4" id="email-capture">
      <div>
        <input
          type="text"
          placeholder="Your First Name"
          value={firstName}
          onChange={(e) => setFirstName(e.target.value)}
          required
          className="w-full px-4 py-3 text-lg border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
      </div>
      
      <div>
        <input
          type="email"
          placeholder="Your Email Address"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
          className="w-full px-4 py-3 text-lg border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
      </div>

      <button
        type="submit"
        disabled={isSubmitting}
        className="w-full py-4 text-lg font-semibold rounded-lg bg-blue-600 hover:bg-blue-700 text-white disabled:bg-gray-400 disabled:cursor-not-allowed"
      >
        {isSubmitting ? 'Sending...' : 'Get My Free Puzzles →'}
      </button>

      <p className="text-sm text-gray-600 text-center">
        We respect your privacy. Unsubscribe at any time.
      </p>
    </form>
  );
};

export default SimpleEmailCapture;