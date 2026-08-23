"""English Learner — Entry Point.

Run this file to start the web application:
    python app.py

The server will be available at http://localhost:5000
and also on your local network at http://<your-ip>:5000
"""

from app import create_app

application = create_app()

if __name__ == "__main__":
    print("\n" + "=" * 50)
    print("  English Learner")
    print("=" * 50)
    print("  Open in browser: http://localhost:5000")
    print("=" * 50 + "\n")

    application.run(host="0.0.0.0", port=5000, debug=True)
