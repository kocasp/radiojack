python3 flask_server.py
DISPLAY=:0 chromium-browser --kiosk --disable-gpu --no-sandbox http://127.0.0.1:5000
DISPLAY=:0 unclutter --timeout 0 --jitter 9999