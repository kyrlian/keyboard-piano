# keyboard_piano.py
import sys
import time
import argparse
try:
    import tomllib  # Python 3.11+
except Exception:
    import tomli as tomllib
from mido import Message, open_output, get_output_names
from pynput import keyboard

def load_config(path):
    with open(path, "rb") as f:
        cfg = tomllib.load(f)
    bindings = {}
    for b in cfg.get("binding", []):
        key = b["key"]
        bindings[key] = {
            "note": int(b["note"]),
            "velocity": int(b.get("velocity", 100)),
            "channel": int(b.get("channel", 0))
        }
    return bindings

def choose_port():
    names = get_output_names()
    if not names:
        print("No MIDI outputs found. Install a virtual MIDI port or connect a device.")
        sys.exit(1)
    if len(names) == 1:
        return names[0]
    print("Available MIDI outputs:")
    for i, n in enumerate(names):
        print(f"{i}: {n}")
    idx = int(input("Choose output index: "))
    return names[idx]

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--config", "-c", default="config.toml")
    args = p.parse_args()

    bindings = load_config(args.config)
    port_name = choose_port()
    out = open_output(port_name)

    pressed = set()

    def on_press(key):
        try:
            char = key.char
        except AttributeError:
            return
        if char in bindings and char not in pressed:
            b = bindings[char]
            out.send(Message('note_on', note=b["note"], velocity=b["velocity"], channel=b["channel"]))
            pressed.add(char)

    def on_release(key):
        try:
            char = key.char
        except AttributeError:
            return
        if char in bindings and char in pressed:
            b = bindings[char]
            out.send(Message('note_off', note=b["note"], velocity=0, channel=b["channel"]))
            pressed.discard(char)
        if key == keyboard.Key.esc:
            # stop
            return False

    print("Starting keyboard piano. Press Esc to quit.")
    with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()

if __name__ == "__main__":
    main()
