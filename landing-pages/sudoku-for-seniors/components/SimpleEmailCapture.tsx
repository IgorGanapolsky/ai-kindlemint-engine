import React, { useState } from 'react';

interface EmailCaptureProps {
  onSuccess: () => void;
}

const SimpleEmailCapture: React.FC<EmailCaptureProps> = ({ onSuccess }) => {
  const [email, setEmail] = useState('');
  const [firstName, setFirstName] = useState('');
  const [submitted, setSubmitted] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    // Store in localStorage as backup
    const subscribers = JSON.parse(localStorage.getItem('sudoku_subscribers') || '[]');
    subscribers.push({
      email,
      firstName,
      timestamp: new Date().toISOString()
    });
    localStorage.setItem('sudoku_subscribers', JSON.stringify(subscribers));
    
    // Send email via EmailJS (FREE for 200 emails/month)
    const serviceId = process.env.NEXT_PUBLIC_EMAILJS_SERVICE_ID;
    const templateId = process.env.NEXT_PUBLIC_EMAILJS_TEMPLATE_ID;
    const publicKey = process.env.NEXT_PUBLIC_EMAILJS_PUBLIC_KEY;
    
    if (serviceId && templateId && publicKey) {
      try {
        // Dynamic import EmailJS to avoid build issues
        const emailjs = await import('@emailjs/browser');
        await emailjs.send(
          serviceId,
          templateId,
          {
            from_name: firstName,
            from_email: email,
            to_name: 'KindleMint Team',
            message: `New subscriber: ${firstName} (${email})`
          },
          publicKey
        );
      } catch (err) {
        console.log('EmailJS send failed, but continuing...', err);
      }
    }
    
    // Show success
    setSubmitted(true);
    
    // Trigger download immediately
    const link = document.createElement('a');
    link.href = '/downloads/5-free-sudoku-puzzles.pdf';
    link.download = '5-free-sudoku-puzzles.pdf';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    
    // Show success after download starts
    setTimeout(() => {
      onSuccess();
    }, 500);
  };

  if (submitted) {
    return (
      <div className="text-center p-6 bg-green-50 rounded-lg">
        <h3 className="text-2xl font-bold text-green-800 mb-4">Success!</h3>
        <p className="text-lg text-gray-700 mb-4">
          Your free puzzles are downloading...
        </p>
        <a 
          href="/downloads/5-free-sudoku-puzzles.pdf"
          download
          className="inline-block bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700"
        >
          Click here if download doesn't start
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
        className="w-full py-4 text-lg font-semibold rounded-lg bg-blue-600 hover:bg-blue-700 text-white"
      >
        Get My Free Puzzles →
      </button>

      <p className="text-sm text-gray-600 text-center">
        We respect your privacy. Unsubscribe at any time.
      </p>
    </form>
  );
};

export default SimpleEmailCapture;