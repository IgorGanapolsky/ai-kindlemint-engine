#!/bin/bash
# Set up GitHub Pages for free SEO traffic

# Create GitHub Pages repository
mkdir -p puzzle-seo-site
cd puzzle-seo-site

# Initialize git
git init

# Copy SEO content
cp ../seo_*.html .
cp ../generated_content/*.html . 2>/dev/null || true

# Create index
cat > index.html << 'EOF'
<!DOCTYPE html>
<html>
<head>
<title>Free Large Print Puzzles for Seniors</title>
<meta name="description" content="Download free large print puzzles perfect for seniors, memory care, and vision impaired individuals.">
</head>
<body>
<h1>Free Large Print Puzzle Collection</h1>
<ul>
<li><a href="seo_free-large-print-sudoku-pdf.html">Free Sudoku Puzzles</a></li>
<li><a href="seo_printable-puzzles-for-dementia-patients.html">Dementia Care Puzzles</a></li>
<li><a href="seo_brain-games-for-seniors-printable.html">Brain Games for Seniors</a></li>
</ul>
<p>Visit our main site: <a href="https://dvdyff0b2oove.cloudfront.net">Get All Puzzles</a></p>
</body>
</html>
EOF

# Create CNAME for custom domain (if you have one)
echo "puzzles.yourdomain.com" > CNAME

echo "✅ GitHub Pages site created"
echo "Next steps:"
echo "1. Create repo on GitHub: puzzle-seo-site"
echo "2. Push this folder to GitHub"
echo "3. Enable Pages in repo settings"
echo "4. Free SEO traffic starts flowing!"
