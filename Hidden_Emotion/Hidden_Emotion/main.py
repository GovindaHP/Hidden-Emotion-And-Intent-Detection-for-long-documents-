import os
import sys
import webbrowser
import threading
import time
import uvicorn

# Automatically add backend directory to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.join(current_dir, "backend")

if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

# Import the FastAPI app directly
from app.main import app

def open_browser():
    """Wait 1.5 seconds for the server to spin up, then open browser automatically."""
    time.sleep(1.5)
    try:
        webbrowser.open("http://localhost:8000")
    except Exception:
        pass

if __name__ == "__main__":
    print("\n" + "=" * 65)
    print("   SENTIMENTAL - Hidden Emotion & Intent Detection System")
    print("=" * 65)
    print(" Server is starting...")
    print(" Web Interface: http://localhost:8000")
    print(" Press CTRL+C to stop the server anytime.")
    print("=" * 65 + "\n")

    threading.Thread(target=open_browser, daemon=True).start()

    # Pass the app object directly to uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
