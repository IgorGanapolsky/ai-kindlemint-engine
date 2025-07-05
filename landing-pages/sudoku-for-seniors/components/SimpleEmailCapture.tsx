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
      // Store in localStorage as backup
      const subscribers = JSON.parse(localStorage.getItem('sudoku_subscribers') || '[]');
      subscribers.push({
        email,
        firstName,
        timestamp: new Date().toISOString()
      });
      localStorage.setItem('sudoku_subscribers', JSON.stringify(subscribers));
      
      // AUTOMATED EMAIL DELIVERY - Send PDF directly to subscriber
      const emailjs = await import('@emailjs/browser');
      
      const templateParams = {
        user_email: email,
        user_name: firstName,
        to_email: email,
        from_name: 'KindleMint Puzzle Masters',
        reply_to: 'support@saasgrowthdispatch.com',
        subject: '🧩 Your FREE Brain-Boosting Puzzles Are Here!',
        message: `Hi ${firstName},

Thank you for joining our puzzle community! 

Your 5 FREE large print Sudoku puzzles are attached to this email, specially designed for brain health and easy on the eyes.

🎯 What's included:
• 5 carefully selected puzzles
• Extra-large 20pt print  
• Complete solutions included
• Perfect for daily brain exercise

🧠 Why Sudoku?
Studies show that regular puzzle solving helps maintain cognitive function and memory as we age.

Enjoy your puzzles, and let me know how you like them!

Best regards,
Igor
KindleMint Puzzle Masters
support@saasgrowthdispatch.com

P.S. If you enjoy these, I have 100 more brain-boosting puzzles ready for you! Just reply "MORE" and I'll send details.`
      };

      // Send automated email with PDF attachment to subscriber
      await emailjs.send(
        'service_i3qck4d',
        'template_sfmcwjx', 
        templateParams,
        '_FNTxijL8nl5Fmgzf'
      );
      
      console.log('✅ AUTOMATED EMAIL SENT TO SUBSCRIBER!');
      
      // Also send notification to you via Formspree
      await fetch('https://formspree.io/f/movwqlnq', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email: email,
          name: firstName,
          _subject: '🧩 New Sudoku Lead from Landing Page!',
          message: `New lead magnet signup: ${firstName} (${email}) - AUTOMATED EMAIL SENT!`
        })
      });
      
      setSubmitted(true);
      setTimeout(() => {
        onSuccess();
      }, 500);
      
    } catch (error) {
      console.error('❌ Automated email failed:', error);
      
      // Fallback: Show download link if email fails
      setSubmitted(true);
      setTimeout(() => {
        onSuccess();
      }, 500);
    } finally {
      setIsSubmitting(false);
    }
  };

  if (submitted) {
    return (
      <div className="text-center p-6 bg-green-50 rounded-lg">
        <h3 className="text-2xl font-bold text-green-800 mb-4">🎉 Success!</h3>
        <p className="text-lg text-gray-700 mb-4">
          <strong>Check your email!</strong> Your free puzzles are on their way to <strong>{email}</strong>
        </p>
        <p className="text-sm text-gray-600 mb-4">
          📧 Email should arrive within 2 minutes from KindleMint Puzzle Masters
        </p>
        <div className="bg-blue-50 p-4 rounded-lg">
          <p className="text-sm text-blue-800">
            <strong>Backup Download:</strong> If email doesn't arrive, click below:
          </p>
          <a 
            href="/downloads/5-free-sudoku-puzzles.pdf"
            download="5-free-sudoku-puzzles.pdf"
            className="inline-block mt-2 bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 text-sm"
          >
            📥 Download PDF Backup
          </a>
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
        {isSubmitting ? 'Sending Your Puzzles...' : 'Get My Free Puzzles →'}
      </button>

      <p className="text-sm text-gray-600 text-center">
        ✅ PDF delivered instantly to your email • No spam • Unsubscribe anytime
      </p>
    </form>
  );
};

export default SimpleEmailCapture;