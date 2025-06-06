import time
from evdev import InputDevice, list_devices, ecodes, categorize
from select import select

TARGET_NAME = "Generic AB13X USB Audio"  # Your device name

def find_device():
    for path in list_devices():
        try:
            dev = InputDevice(path)
            if dev.name == TARGET_NAME:
                return dev
        except:
            continue
    return None

device = None

print("Waiting for device...")

while True:
    if device is None:
        device = find_device()
        if device:
            try:
                device.grab()
                print(f"Device connected: {device.name} ({device.path})")
            except Exception as e:
                print(f"Failed to grab device: {e}")
                device = None
        else:
            time.sleep(1)
            continue

    try:
        r, _, _ = select([device.fd], [], [], 0.5)
        if device.fd in r:
            for event in device.read():
                if event.type == ecodes.EV_KEY:
                    key_event = categorize(event)
                    print(f"Blocked: {key_event.keycode} ({key_event.keystate})")
    except OSError as e:
        print("Device disconnected. Waiting to reconnect...")
        try:
            device.ungrab()
        except:
            pass
        device = None
        time.sleep(1)
    except KeyboardInterrupt:
        print("Interrupted. Exiting...")
        try:
            if device:
                device.ungrab()
        except:
            pass
        break

