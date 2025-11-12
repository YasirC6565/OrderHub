#!/usr/bin/env python3
"""
Start both backend and frontend servers locally
"""
import subprocess
import sys
import os
import time
from pathlib import Path

def start_backend():
    """Start the FastAPI backend server"""
    print("🚀 Starting FastAPI backend server on http://localhost:8000")
    print("   - Health check: http://localhost:8000/")
    print("   - API docs: http://localhost:8000/docs")
    return subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"],
        cwd=Path(__file__).parent
    )

def start_frontend():
    """Start the frontend server"""
    print("\n🚀 Starting frontend server on http://localhost:3000")
    print("   - Frontend: http://localhost:3000/")
    print("   - History: http://localhost:3000/history")
    print("\n✅ Both servers are running!")
    print("   Press Ctrl+C to stop both servers\n")
    return subprocess.Popen(
        [sys.executable, "serve_frontend.py"],
        cwd=Path(__file__).parent
    )

if __name__ == "__main__":
    try:
        # Start backend
        backend_process = start_backend()
        time.sleep(2)  # Give backend a moment to start
        
        # Start frontend
        frontend_process = start_frontend()
        
        # Wait for both processes
        try:
            backend_process.wait()
            frontend_process.wait()
        except KeyboardInterrupt:
            print("\n\n🛑 Stopping servers...")
            backend_process.terminate()
            frontend_process.terminate()
            backend_process.wait()
            frontend_process.wait()
            print("✅ Servers stopped")
    except Exception as e:
        print(f"❌ Error starting servers: {e}")
        sys.exit(1)

