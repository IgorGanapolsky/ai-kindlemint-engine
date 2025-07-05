import path from 'path';
import fs from 'fs';

export default function handler(req, res) {
  try {
    // Use process.cwd() for Vercel compatibility
    const pdfPath = path.join(process.cwd(), 'public', 'downloads', '5-free-sudoku-puzzles.pdf');
    
    // Check if file exists
    if (!fs.existsSync(pdfPath)) {
      return res.status(404).json({ error: 'PDF not found' });
    }
    
    // Read the PDF file
    const pdfBuffer = fs.readFileSync(pdfPath);
    
    // Set proper headers for PDF
    res.setHeader('Content-Type', 'application/pdf');
    res.setHeader('Content-Disposition', 'inline; filename="5-free-sudoku-puzzles.pdf"');
    res.setHeader('Cache-Control', 'public, max-age=0, must-revalidate');
    
    // Send the PDF buffer
    res.status(200).send(pdfBuffer);
  } catch (error) {
    console.error('PDF serve error:', error);
    res.status(500).json({ error: 'Failed to serve PDF' });
  }
}