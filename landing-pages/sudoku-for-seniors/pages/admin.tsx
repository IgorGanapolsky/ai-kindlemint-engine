import React, { useState, useEffect } from 'react';
import Head from 'next/head';

export default function Admin() {
  const [subscribers, setSubscribers] = useState<any[]>([]);

  useEffect(() => {
    const data = JSON.parse(localStorage.getItem('sudoku_subscribers') || '[]');
    setSubscribers(data);
  }, []);

  const exportCSV = () => {
    const csv = 'First Name,Email,Date\n' + 
      subscribers.map(s => `${s.firstName},${s.email},${s.timestamp}`).join('\n');
    
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'sudoku-subscribers.csv';
    a.click();
  };

  return (
    <>
      <Head>
        <title>Sudoku Subscribers Admin</title>
      </Head>

      <div className="min-h-screen bg-gray-100 p-8">
        <div className="max-w-6xl mx-auto">
          <h1 className="text-3xl font-bold mb-8">Subscriber List</h1>
          
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex justify-between items-center mb-4">
              <p className="text-lg">Total Subscribers: {subscribers.length}</p>
              <button 
                onClick={exportCSV}
                className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
              >
                Export CSV
              </button>
            </div>
            
            <table className="w-full">
              <thead>
                <tr className="border-b">
                  <th className="text-left p-2">First Name</th>
                  <th className="text-left p-2">Email</th>
                  <th className="text-left p-2">Date</th>
                </tr>
              </thead>
              <tbody>
                {subscribers.map((sub, idx) => (
                  <tr key={idx} className="border-b">
                    <td className="p-2">{sub.firstName}</td>
                    <td className="p-2">{sub.email}</td>
                    <td className="p-2">{new Date(sub.timestamp).toLocaleDateString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </>
  );
}