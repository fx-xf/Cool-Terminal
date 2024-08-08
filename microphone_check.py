import sounddevice as sd

def print_device_info():
    print("Input devices:")
    for device in sd.query_devices():
        if device['max_input_channels'] > 0:
            print(f"  {device['name']}: {device['default_samplerate']}")

print_device_info()
