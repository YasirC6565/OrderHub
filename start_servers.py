#!/usr/bin/env python3
"""
Start both backend and frontend servers locally with better error handling
This script will keep servers running and restart them if they crash
"""
import subprocess
import sys
import os
import time
import signal
from pathlib import Path

# Store process references
backend_process = None
frontend_process = None
running = True

def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully"""
    global running
    print("\n\n🛑 Shutting down servers...")
    running = False
    stop_servers()
    sys.exit(0)

def stop_servers():
    """Stop both servers"""
    global backend_process, frontend_process
    
    if backend_process:
        try:
            backend_process.terminate()
            backend_process.wait(timeout=5)
            print("✅ Backend stopped")
        except:
            try:
                backend_process.kill()
            except:
                pass
    
    if frontend_process:
        try:
            frontend_process.terminate()
            frontend_process.wait(timeout=5)
            print("✅ Frontend stopped")
        except:
            try:
                frontend_process.kill()
            except:
                pass

def start_backend():
    """Start the FastAPI backend server (without --reload to prevent crashes)"""
    print("🚀 Starting FastAPI backend server on http://localhost:8000")
    print("   - Health check: http://localhost:8000/")
    print("   - API docs: http://localhost:8000/docs")
    print("   - Note: Server runs without auto-reload for stability")
    
    return subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"],
        cwd=Path(__file__).parent
    )

def start_frontend():
    """Start the frontend server"""
    print("🚀 Starting frontend server on http://localhost:3000")
    print("   - Frontend: http://localhost:3000/")
    print("   - History: http://localhost:3000/history")
    
    return subprocess.Popen(
        [sys.executable, "serve_frontend.py"],
        cwd=Path(__file__).parent
    )

def monitor_process(process, name):
    """Monitor a process and restart if it crashes"""
    if process is None:
        return False
    if process.poll() is not None:
        exit_code = process.returncode
        print(f"⚠️  {name} process has stopped (exit code: {exit_code})")
        return False
    return True

def main():
    global backend_process, frontend_process, running
    
    # Set up signal handler for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    base_path = Path(__file__).parent
    
    print("=" * 60)
    print("OrderHub Local Development Servers")
    print("=" * 60)
    print()
    
    # Start backend
    backend_process = start_backend()
    time.sleep(3)  # Give backend time to start
    
    # Start frontend
    frontend_process = start_frontend()
    time.sleep(2)  # Give frontend time to start
    
    print()
    print("✅ Both servers are running!")
    print("   Press Ctrl+C to stop both servers")
    print("=" * 60)
    print()
    
    # Wait for processes (they will run until Ctrl+C)
    try:
        while running:
            # Check if processes are still running
            backend_alive = monitor_process(backend_process, "Backend")
            frontend_alive = monitor_process(frontend_process, "Frontend")
            
            # If either process died and we're still running, restart it
            if running and not backend_alive:
                print("🔄 Restarting backend...")
                backend_process = start_backend()
                time.sleep(3)
            
            if running and not frontend_alive:
                print("🔄 Restarting frontend...")
                frontend_process = start_frontend()
                time.sleep(2)
            
            time.sleep(2)  # Check every 2 seconds
            
    except KeyboardInterrupt:
        pass
    finally:
        stop_servers()
        print("✅ All servers stopped")

if __name__ == "__main__":
    main()

