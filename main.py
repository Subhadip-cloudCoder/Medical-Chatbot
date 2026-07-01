import subprocess
import sys
import os

if __name__ == "__main__":
    print("Starting Medical Chatbot Interface...")
    
    # Dynamically find the path to app.py in the root directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    app_path = os.path.join(script_dir, "streamlit_app.py")
    
    try:
        # Run streamlit as a subprocess
        subprocess.run([sys.executable, "-m", "streamlit", "run", app_path])
    except KeyboardInterrupt:
        print("\nShutting down application...")