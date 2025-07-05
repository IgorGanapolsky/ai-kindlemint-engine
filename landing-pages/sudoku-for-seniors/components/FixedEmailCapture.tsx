import React, { useState } from 'react';

interface EmailCaptureProps {
  onSuccess?: () => void; // Made optional so we don't have to call it
}

const FixedEmailCapture: React.FC<EmailCaptureProps> = ({ onSuccess }) => {
  const [email, setEmail] = useState('');
  const [firstName, setFirstName] = useState('');
  const [submitted, setSubmitted] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    e.stopPropagation();
    
    if (isSubmitting || submitted) return;
    
    console.log('🚀 Form submitted, processing...');
    setIsSubmitting(true);
    
    // Store subscriber data
    const subscribers = JSON.parse(localStorage.getItem('sudoku_subscribers') || '[]');
    subscribers.push({
      email,
      firstName,
      timestamp: new Date().toISOString()
    });
    localStorage.setItem('sudoku_subscribers', JSON.stringify(subscribers));
    console.log('💾 Data stored locally');
    
    // Show success IMMEDIATELY - no async waits
    setSubmitted(true);
    setIsSubmitting(false);
    console.log('✅ Success state set - should show download now');
    
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
        message: `FIXED VERSION: ${firstName} (${email}) - PDF DOWNLOAD WORKING!`
      })
    }).then(() => {
      console.log('📧 Notification sent to owner');
    }).catch((error) => {
      console.log('❌ Notification failed (but PDF still works):', error);
    });
    
    // DON'T CALL onSuccess() - that's what causes the flash!
  };

  // Show download interface if submitted
  if (submitted) {
    return (
      <div className="text-center p-8 bg-green-50 rounded-lg border-2 border-green-300">
        <h3 className="text-3xl font-bold text-green-800 mb-4">🎉 SUCCESS!</h3>
        <p className="text-xl text-gray-700 mb-6">
          Hi <strong>{firstName}</strong>! Your puzzles are ready:
        </p>
        
        <div className="bg-white p-6 rounded-lg shadow-lg mb-6 border">
          <h4 className="text-2xl font-semibold mb-4 text-gray-800">
            📥 Your 5 FREE Brain-Boosting Puzzles
          </h4>
          
          <a 
            href="/downloads/5-free-sudoku-puzzles.pdf"
            download="5-Free-Brain-Boosting-Sudoku-Puzzles.pdf"
            className="inline-block bg-blue-600 text-white px-8 py-4 rounded-lg hover:bg-blue-700 font-bold text-xl mb-4 transform hover:scale-105 transition-all duration-200 shadow-xl"
            onClick={() => console.log('📄 PDF download clicked')}
          >
            📄 DOWNLOAD PUZZLES NOW
          </a>
          
          <div className="text-sm text-gray-600 space-y-1 mt-4">
            <p>✅ 5 Large Print Sudoku Puzzles (20pt font)</p>
            <p>✅ Easy on your eyes with high contrast</p>
            <p>✅ Solutions included for checking</p>
            <p>✅ Perfect for daily brain exercise</p>
          </div>
        </div>

        <div className="bg-blue-50 p-6 rounded-lg border border-blue-300">
          <h5 className="font-bold text-blue-800 mb-2 text-lg">💰 Want 100 MORE Puzzles?</h5>
          <p className="text-blue-700 mb-2">
            Get our complete <strong>"Large Print Sudoku Masters Volume 1"</strong>
          </p>
          <p className="text-blue-700 mb-3">
            <strong>100 puzzles</strong> with progressive difficulty for just <strong className="text-2xl">$8.99!</strong>
          </p>
          <p className="text-sm text-blue-600">
            📧 Special offer coming to: <strong>{email}</strong>
          </p>
        </div>
      </div>
    );
  }

  // Show form if not submitted
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
        disabled={isSubmitting || submitted}
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

export default FixedEmailCapture;