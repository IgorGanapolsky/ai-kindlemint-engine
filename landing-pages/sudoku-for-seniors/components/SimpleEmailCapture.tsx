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
    
    // Send via Formspree (FREE for 50 submissions/month)
    try {      const response = await fetch('https://formspree.io/f/movwqlnq', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email: email,
          name: firstName,
          _subject: '🧩 New Sudoku Lead from Landing Page!',
          _replyto: email,
          message: `New lead magnet signup: ${firstName} (${email}) wants the 5 FREE Brain-Boosting Puzzles`
        })
      });

      if (response.ok) {
        console.log('✅ Formspree submission successful');
        
        // Store in localStorage as backup
        const subscribers = JSON.parse(localStorage.getItem('sudoku_subscribers') || '[]');
        subscribers.push({
          email,
          firstName,
          timestamp: new Date().toISOString(),
          source: 'formspree'
        });
        localStorage.setItem('sudoku_subscribers', JSON.stringify(subscribers));
        
        setSubmitted(true);
      } else {
        throw new Error(`Formspree error: ${response.status}`);
      }
    } catch (error) {
      console.error('❌ Form submission failed:', error);
      alert('Something went wrong. Please try again or email us directly at support@saasgrowthdispatch.com');
    } finally {
      setIsSubmitting(false);
    }  };

  if (submitted) {
    return (
      <div className="text-center p-6 bg-green-50 rounded-lg">
        <h3 className="text-2xl font-bold text-green-800 mb-4">Success!</h3>
        <p className="text-lg text-gray-700 mb-4">
          Thank you for subscribing! Click below to download your free puzzles.
        </p>
        <a 
          href="/api/download-pdf"
          download="5-free-sudoku-puzzles.pdf"
          className="inline-block bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 font-semibold"
        >
          📥 Download Your Free Puzzles
        </a>
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