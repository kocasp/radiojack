## Run everything in Python environment mode
```
to enter python env
`source ~/.env/bin/activate`

to quit it
`deactivate`

more info:
https://www.raspberrypi.com/documentation/computers/os.html#install-python-libraries-using-pip

-----------

for MAC:

python3 -m venv path/to/venv
source path/to/venv/bin/activate
python3 -m pip install xyz
```

## Start Server with
python3 flask_server.py

# Run keyboard play/pause received from radio fix
python3 key_block.py

## Open chromium in kiosk mode with
DISPLAY=:0 unclutter -idle 0 -jitter 9999 & DISPLAY=:0 chromium-browser --kiosk --disable-gpu --no-sandbox http://127.0.0.1:5000

# Run microphone service
python3 mic.py
