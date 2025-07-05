import React, { useState, useEffect } from 'react';
import emailjs from '@emailjs/browser';

interface EmailCaptureProps {
  onSuccess: () => void;
}

const EmailCapture: React.FC<EmailCaptureProps> = ({ onSuccess }) => {
  const [email, setEmail] = useState('');
  const [firstName, setFirstName] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  // Initialize EmailJS with public key
  useEffect(() => {
    const publicKey = process.env.NEXT_PUBLIC_EMAILJS_PUBLIC_KEY;
    if (publicKey) {
      emailjs.init(publicKey);
      console.log('EmailJS initialized with key:', publicKey.substring(0, 5) + '...');
    } else {
      console.error('EmailJS public key not found!');
    }
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      // EmailJS service (FREE - 200 emails/month)
      const serviceId = process.env.NEXT_PUBLIC_EMAILJS_SERVICE_ID;
      const templateId = process.env.NEXT_PUBLIC_EMAILJS_TEMPLATE_ID;
      
      console.log('Attempting to send email with:', {
        serviceId,
        templateId,
        email,
        firstName
      });

      const templateParams = {
        to_email: email,
        from_name: firstName,
        message: 'New subscriber for Sudoku for Seniors',
        reply_to: email,
        download_link: `${window.location.origin}/downloads/5-free-sudoku-puzzles.pdf`
      };

      // Send welcome email with lead magnet (don't pass public key here)
      const result = await emailjs.send(
        serviceId || 'your_service_id',
        templateId || 'your_template_id',
        templateParams
      );
      
      console.log('EmailJS success:', result);

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
    } catch (err: any) {
      console.error('Email capture error:', err);
      console.error('Error details:', err.message || err);
      setError(err.message || 'Something went wrong. Please try again.');
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