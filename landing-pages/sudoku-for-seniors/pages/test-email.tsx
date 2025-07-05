import React, { useState } from 'react';
import Head from 'next/head';

export default function TestEmail() {
  const [status, setStatus] = useState('');
  const [logs, setLogs] = useState<string[]>([]);

  const addLog = (message: string) => {
    setLogs(prev => [...prev, message]);
    console.log(message);
  };

  const testEmailJS = async () => {
    setStatus('Testing...');
    setLogs([]);
    
    try {
      addLog('Starting EmailJS test...');
      
      const emailjs = await import('@emailjs/browser');
      addLog('EmailJS loaded successfully');
      
      const serviceId = 'service_dg09m9v';
      const templateId = 'template_sfmcwjx';
      const publicKey = '_FNTxijL8nl5Fmgzf';
      
      addLog(`Service ID: ${serviceId}`);
      addLog(`Template ID: ${templateId}`);
      addLog(`Public Key: ${publicKey.substring(0, 10)}...`);
      
      // Test with minimal parameters
      const testParams = {
        to_email: 'test@example.com',
        from_email: 'test@example.com',
        user_email: 'test@example.com',
        email: 'test@example.com',
        to_name: 'Test User',
        from_name: 'Test User', 
        user_name: 'Test User',
        name: 'Test User',
        message: 'This is a test message',
        user_message: 'This is a test message',
        subject: 'Test Email from Sudoku Landing Page'
      };
      
      addLog('Sending test email with parameters:');
      addLog(JSON.stringify(testParams, null, 2));
      
      const response = await emailjs.send(
        serviceId,
        templateId,
        testParams,
        publicKey
      );
      
      addLog('SUCCESS! Response:');
      addLog(JSON.stringify(response, null, 2));
      setStatus('Success! Check logs below');
      
    } catch (error: any) {
      addLog('ERROR! Details:');
      addLog(error.message || 'Unknown error');
      addLog(JSON.stringify(error, null, 2));
      setStatus('Error - see logs below');
    }
  };

  return (
    <>
      <Head>
        <title>EmailJS Test Page</title>
      </Head>
      
      <div className="min-h-screen bg-gray-100 p-8">
        <div className="max-w-4xl mx-auto">
          <h1 className="text-3xl font-bold mb-8">EmailJS Debug Test</h1>
          
          <div className="bg-white rounded-lg shadow p-6 mb-6">
            <h2 className="text-xl font-semibold mb-4">Test EmailJS Configuration</h2>
            
            <button
              onClick={testEmailJS}
              className="bg-blue-600 text-white px-6 py-3 rounded hover:bg-blue-700"
            >
              Send Test Email
            </button>
            
            {status && (
              <p className={`mt-4 font-semibold ${status.includes('Success') ? 'text-green-600' : 'text-red-600'}`}>
                Status: {status}
              </p>
            )}
          </div>
          
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold mb-4">Debug Logs</h2>
            <pre className="bg-gray-100 p-4 rounded overflow-auto text-sm">
              {logs.length === 0 ? 'No logs yet. Click the button above to test.' : logs.join('\n')}
            </pre>
          </div>
          
          <div className="mt-6 bg-blue-50 rounded-lg p-6">
            <h3 className="font-semibold mb-2">What to check:</h3>
            <ol className="list-decimal list-inside space-y-2 text-sm">
              <li>Go to <a href="https://dashboard.emailjs.com" target="_blank" className="text-blue-600 underline">EmailJS Dashboard</a></li>
              <li>Check if your service "service_dg09m9v" is active</li>
              <li>Check your email template "template_sfmcwjx" parameters</li>
              <li>Make sure your template uses one of these variables: {`{{user_email}}, {{to_email}}, {{from_email}}`}</li>
              <li>Check your EmailJS email history for sent/failed emails</li>
              <li>Verify your daily limit hasn't been exceeded (200/month free)</li>
            </ol>
          </div>
        </div>
      </div>
    </>
  );
}