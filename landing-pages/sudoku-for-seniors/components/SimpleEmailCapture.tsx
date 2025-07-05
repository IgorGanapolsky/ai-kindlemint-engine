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
    // Using correct credentials from EmailJS dashboard
    const serviceId = 'service_i3qck4d';
    const templateId = 'template_sfmcwjx'; // TODO: Get correct template ID
    const publicKey = '_FNTxijL8nl5Fmgzf';
    
    console.log('Attempting to send email via EmailJS...', {
      serviceId,
      templateId,
      email,
      firstName
    });
    
    if (serviceId && templateId && publicKey) {
      try {
        // Dynamic import EmailJS to avoid build issues
        const emailjs = await import('@emailjs/browser');
        
        // Using standard EmailJS template parameter names
        const templateParams = {
          user_email: email,  // Standard parameter name for recipient email
          user_name: firstName,  // Standard parameter name for user's name
          to_email: email,  // Alternative standard parameter name
          from_name: firstName,  // Keep this as fallback
          message: `New subscriber: ${firstName} (${email})`,  // Standard message parameter
          user_message: `New subscriber: ${firstName} (${email})`  // Alternative message parameter
        };
        
        console.log('Sending EmailJS with template parameters:', templateParams);
        
        const response = await emailjs.send(
          serviceId,
          templateId,
          templateParams,
          publicKey
        );
        
        console.log('EmailJS SUCCESS! Email sent successfully:', {
          status: response.status,
          text: response.text
        });
      } catch (err) {
        console.error('EmailJS FAILED! Detailed error:', {
          error: err,
          message: err instanceof Error ? err.message : 'Unknown error',
          details: JSON.stringify(err, null, 2)
        });
        console.log('Continuing despite email send failure...');
      }
    } else {
      console.error('EmailJS credentials missing:', { serviceId, templateId, publicKey });
    }
    
    // Show success
    setSubmitted(true);
    
    // Show success message immediately
    setTimeout(() => {
      onSuccess();
    }, 500);
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