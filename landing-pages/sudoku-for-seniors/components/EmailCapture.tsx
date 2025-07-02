import React, { useState } from 'react';

interface EmailCaptureProps {
  onSuccess: () => void;
}

const EmailCapture: React.FC<EmailCaptureProps> = ({ onSuccess }) => {
  const [email, setEmail] = useState('');
  const [firstName, setFirstName] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      // ConvertKit API endpoint (to be configured with actual form ID)
      const response = await fetch('/api/subscribe', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email,
          firstName,
          tags: ['sudoku-for-seniors', 'lead-magnet'],
        }),
      });

      if (!response.ok) {
        throw new Error('Subscription failed');
      }

      // Track conversion
      if (typeof window !== 'undefined' && (window as any).gtag) {
        (window as any).gtag('event', 'conversion', {
          'send_to': 'AW-XXXXXXXXX/XXXXXXXXX', // Replace with actual conversion ID
          'value': 0.0,
          'currency': 'USD'
        });
      }

      // Facebook Pixel tracking
      if (typeof window !== 'undefined' && (window as any).fbq) {
        (window as any).fbq('track', 'Lead', {
          value: 0.0,
          currency: 'USD',
        });
      }

      onSuccess();
    } catch (err) {
      setError('Something went wrong. Please try again.');
    } finally {
      setLoading(false);
    }
  };

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

      {error && (
        <p className="text-red-600 text-sm">{error}</p>
      )}

      <button
        type="submit"
        disabled={loading}
        className={`w-full py-4 text-lg font-semibold rounded-lg transition ${
          loading
            ? 'bg-gray-400 cursor-not-allowed'
            : 'bg-blue-600 hover:bg-blue-700 text-white'
        }`}
      >
        {loading ? 'Processing...' : 'Get My Free Puzzles →'}
      </button>

      <p className="text-sm text-gray-600 text-center">
        We respect your privacy. Unsubscribe at any time.
      </p>
    </form>
  );
};

export default EmailCapture;