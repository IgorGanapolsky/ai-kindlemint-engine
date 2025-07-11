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
    
    try {
      // Send to Formspree
      const response = await fetch('https://formspree.io/f/movwqlnq', {
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
        setTimeout(() => {
          onSuccess();
        }, 500);
      } else {
        throw new Error(`Formspree error: ${response.status}`);
      }
    } catch (error) {
      console.error('❌ Form submission failed:', error);
      alert('Something went wrong. Please try again or email us directly at support@saasgrowthdispatch.com');
    } finally {
      setIsSubmitting(false);
    }
  };

  if (submitted) {
    return (
      <div className="text-center p-6 bg-green-50 rounded-lg">
        <h3 className="text-2xl font-bold text-green-800 mb-4">Success!</h3>
        <p className="text-lg text-gray-700">
          Thank you for subscribing! Check your email for your free puzzles.
        </p>
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