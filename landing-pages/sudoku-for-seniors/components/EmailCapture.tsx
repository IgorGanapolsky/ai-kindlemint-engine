import React, { useState } from 'react';
import emailjs from '@emailjs/browser';

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
      // EmailJS service (FREE - 200 emails/month)
      const templateParams = {
        to_email: email,
        from_name: firstName,
        message: 'New subscriber for Sudoku for Seniors 75+',
        reply_to: email,
        download_link: `${window.location.origin}/downloads/5-free-sudoku-puzzles.pdf`
      };

      // Send welcome email with lead magnet
      await emailjs.send(
        process.env.NEXT_PUBLIC_EMAILJS_SERVICE_ID || 'your_service_id',
        process.env.NEXT_PUBLIC_EMAILJS_TEMPLATE_ID || 'your_template_id',
        templateParams,
        process.env.NEXT_PUBLIC_EMAILJS_PUBLIC_KEY || 'your_public_key'
      );

      // Also save to GitHub (free backup)
      if (process.env.NEXT_PUBLIC_GITHUB_TOKEN) {
        await fetch('/api/github-subscriber', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ email, firstName, timestamp: new Date().toISOString() })
        });
      }

      // Track conversion
      if (typeof window !== 'undefined' && (window as any).gtag) {
        (window as any).gtag('event', 'conversion', {
          'send_to': 'AW-XXXXXXXXX/XXXXXXXXX',
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
      console.error('Email capture error:', err);
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