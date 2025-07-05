import React, { useState } from 'react';

interface EmailCaptureProps {
  onSuccess: () => void;
}

const SimpleEmailCapture: React.FC<EmailCaptureProps> = ({ onSuccess }) => {
  const [email, setEmail] = useState('');
  const [firstName, setFirstName] = useState('');
  const [submitted, setSubmitted] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    e.stopPropagation();
    
    if (isSubmitting) return;
    
    setIsSubmitting(true);
    
    // Store subscriber data immediately
    const subscribers = JSON.parse(localStorage.getItem('sudoku_subscribers') || '[]');
    subscribers.push({
      email,
      firstName,
      timestamp: new Date().toISOString()
    });
    localStorage.setItem('sudoku_subscribers', JSON.stringify(subscribers));
    
    // Show success immediately - no waiting for API calls
    setSubmitted(true);
    setIsSubmitting(false);
    
    // Send notification in background (non-blocking)
    fetch('https://formspree.io/f/movwqlnq', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        email: email,
        name: firstName,
        _subject: '🧩 New Sudoku Lead from Landing Page!',
        message: `New lead magnet signup: ${firstName} (${email}) - INSTANT PDF DOWNLOAD GIVEN!`
      })
    }).then(() => {
      console.log('✅ Lead notification sent!');
    }).catch((error) => {
      console.log('❌ Notification failed but user still gets PDF:', error);
    });
  };

  if (submitted) {
    return (
      <div className="text-center p-6 bg-green-50 rounded-lg border-2 border-green-200">
        <h3 className="text-2xl font-bold text-green-800 mb-4">🎉 SUCCESS!</h3>
        <p className="text-lg text-gray-700 mb-6">
          Hi <strong>{firstName}</strong>! Your free puzzles are ready for download:
        </p>
        
        <div className="bg-white p-6 rounded-lg shadow-lg mb-6">
          <h4 className="text-xl font-semibold mb-4 text-gray-800">
            📥 Get Your 5 FREE Brain-Boosting Puzzles
          </h4>
          
          <a 
            href="/downloads/5-free-sudoku-puzzles.pdf"
            download="5-Free-Brain-Boosting-Sudoku-Puzzles.pdf"
            className="inline-block bg-blue-600 text-white px-8 py-4 rounded-lg hover:bg-blue-700 font-semibold text-lg mb-4 transform hover:scale-105 transition-all duration-200 shadow-lg"
          >
            📄 DOWNLOAD YOUR PUZZLES NOW
          </a>
          
          <div className="text-sm text-gray-600 space-y-2">
            <p>✅ 5 Large Print Sudoku Puzzles</p>
            <p>✅ Easy on your eyes (20pt+ font)</p>
            <p>✅ Solutions included</p>
            <p>✅ Perfect for daily brain exercise</p>
          </div>
        </div>

        <div className="bg-blue-50 p-4 rounded-lg border border-blue-200">
          <h5 className="font-semibold text-blue-800 mb-2">💰 Want 100 MORE Puzzles?</h5>
          <p className="text-sm text-blue-700 mb-3">
            Get our complete "Large Print Sudoku Masters Volume 1" with 100 puzzles for just <strong>$8.99!</strong>
          </p>
          <p className="text-xs text-blue-600">
            📧 We'll email you the special offer link shortly at: <strong>{email}</strong>
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
        className="w-full py-4 text-lg font-semibold rounded-lg bg-blue-600 hover:bg-blue-700 text-white disabled:bg-gray-400 disabled:cursor-not-allowed transform hover:scale-105 transition-all duration-200"
      >
        {isSubmitting ? 'Getting Your Puzzles...' : '🧩 Get My FREE Puzzles Now!'}
      </button>

      <p className="text-sm text-gray-600 text-center">
        ✅ Instant download • No spam • No credit card required
      </p>
    </form>
  );
};

export default SimpleEmailCapture;