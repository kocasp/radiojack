## Instructions how to enter pip3 env mode to run Python commands
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

## Start application by running all following processes:
python3 flask_server.py

python3 key_block.py

DISPLAY=:0 unclutter-xfixes -idle 0 & DISPLAY=:0 chromium-browser --kiosk --disable-gpu --no-sandbox http://127.0.0.1:5000

python3 mic.py
