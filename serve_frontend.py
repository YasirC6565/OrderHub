#!/usr/bin/env python3
"""
Simple HTTP server that serves index.html for all routes (SPA support)
"""
import http.server
import socketserver
import os
from pathlib import Path

PORT = 3000
DIRECTORY = Path(__file__).parent / "frontend"

class SPAHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(DIRECTORY), **kwargs)
    
    def end_headers(self):
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        super().end_headers()
    
    def do_GET(self):
        # Get the requested path
        requested_path = self.path.split('?')[0]  # Remove query string
        
        # Check if it's a request for a file (has extension and is not root)
        path_parts = requested_path.split('/')
        last_part = path_parts[-1] if path_parts else ''
        has_extension = '.' in last_part and last_part != ''
        
        # If it's a file request (like .css, .js, .png, etc.), serve normally
        if has_extension and requested_path != '/':
            # Let the parent class handle file serving
            return super().do_GET()
        
        # For all other routes, serve index.html
        # This handles /submit, /history, /, etc.
        self.path = '/index.html'
        return super().do_GET()
    
    def log_message(self, format, *args):
        # Custom logging to see what's being requested
        print(f"{self.address_string()} - {format % args}")

if __name__ == "__main__":
    os.chdir(DIRECTORY)
    with socketserver.TCPServer(("", PORT), SPAHandler) as httpd:
        print(f"🚀 SPA Server running at http://localhost:{PORT}/")
        print(f"   - http://localhost:{PORT}/submit")
        print(f"   - http://localhost:{PORT}/history")
        print("   Press Ctrl+C to stop")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n✅ Server stopped")
