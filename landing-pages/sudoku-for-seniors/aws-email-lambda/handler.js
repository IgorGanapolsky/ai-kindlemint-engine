const AWS = require('aws-sdk');
const ses = new AWS.SES({ region: 'us-east-1' });

exports.sendEmail = async (event) => {
  const corsHeaders = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Access-Control-Allow-Methods': 'OPTIONS,POST'
  };

  // Handle preflight
  if (event.httpMethod === 'OPTIONS') {
    return {
      statusCode: 200,
      headers: corsHeaders,
      body: ''
    };
  }

  try {
    const { email, firstName } = JSON.parse(event.body);
    
    const params = {
      Source: 'noreply@sudokuforseniors.com', // You'll verify this domain in SES
      Destination: {
        ToAddresses: [email]
      },
      Message: {
        Subject: {
          Data: `Welcome ${firstName}! Your Free Sudoku Puzzles Are Here`
        },
        Body: {
          Html: {
            Data: `
              <h2>Welcome ${firstName}!</h2>
              <p>Thank you for joining our community of seniors who keep their minds sharp with Sudoku!</p>
              <p><strong>Download your 5 FREE puzzles here:</strong></p>
              <p><a href="https://sudokuforseniors.com/downloads/5-free-sudoku-puzzles.pdf" style="background: #2563eb; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; display: inline-block;">Download Free Puzzles</a></p>
              <p>You'll also receive our weekly "Puzzle of the Week" to keep your brain active!</p>
              <p>Happy solving!</p>
              <p>- The Sudoku for Seniors Team</p>
            `
          }
        }
      }
    };
    
    await ses.sendEmail(params).promise();
    
    return {
      statusCode: 200,
      headers: corsHeaders,
      body: JSON.stringify({ success: true })
    };
  } catch (error) {
    console.error('Error:', error);
    return {
      statusCode: 500,
      headers: corsHeaders,
      body: JSON.stringify({ error: 'Failed to send email' })
    };
  }
};