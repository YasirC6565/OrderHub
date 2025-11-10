#!/usr/bin/env node
/**
 * Build script for Vercel deployment
 * Injects API_BASE_URL environment variable into index.html
 */
const fs = require('fs');
const path = require('path');

const apiBaseUrl = process.env.API_BASE_URL || 'https://your-railway-app.up.railway.app';
const htmlPath = path.join(__dirname, 'frontend', 'index.html');

if (fs.existsSync(htmlPath)) {
  let html = fs.readFileSync(htmlPath, 'utf8');
  
  // Replace the placeholder API URL in the meta tag
  html = html.replace(
    /<meta name="api-base-url" content="" id="api-base-url-meta">/,
    `<meta name="api-base-url" content="${apiBaseUrl}" id="api-base-url-meta">`
  );
  
  // Also replace the default fallback URL
  html = html.replace(
    /return 'https:\/\/your-railway-app\.up\.railway\.app';/,
    `return '${apiBaseUrl}';`
  );
  
  fs.writeFileSync(htmlPath, html, 'utf8');
  console.log(`✅ Injected API_BASE_URL: ${apiBaseUrl}`);
} else {
  console.error(`❌ HTML file not found at: ${htmlPath}`);
  process.exit(1);
}

