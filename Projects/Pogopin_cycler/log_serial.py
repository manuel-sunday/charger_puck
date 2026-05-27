#!/usr/bin/env python3
"""
Logs live serial output from the cycle test to a CSV file.
Runs until the test completes or you press Ctrl+C.

Usage:
  pip install pyserial
  python3 log_serial.py              # auto-detects port
  python3 log_serial.py /dev/cu.xxx  # specify port
"""

import sys
import csv
import serial
import serial.tools.list_ports
from datetime import datetime

BAUD = 115200


def find_port():
    ports = list(serial.tools.list_ports.comports())
    for p in ports:
        if "usbserial" in p.device or "usbmodem" in p.device:
            return p.device
    if ports:
        return ports[0].device
    return None


def main():
    port = sys.argv[1] if len(sys.argv) > 1 else find_port()
    if not port:
        print("No serial port found. Plug in the Arduino or pass port as argument.")
        sys.exit(1)

    out_file = f"cycle_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    print(f"Connecting to {port} at {BAUD} baud...")
    print(f"Logging to {out_file}  (Ctrl+C to stop)\n")

    rows = 0
    with serial.Serial(port, BAUD, timeout=1) as ser, \
         open(out_file, "w", newline="") as f:

        writer = csv.writer(f)
        writer.writerow(["type", "cycle", "t_ms", "raw", "voltage_V"])

        try:
            while True:
                line = ser.readline().decode("utf-8", errors="replace").strip()
                if not line:
                    continue

                print(line)

                # DATA and CYCLE rows are already CSV: TYPE,cycle,t_ms,raw,voltage_V
                if line.startswith("DATA,") or line.startswith("CYCLE,"):
                    writer.writerow(line.split(","))
                    f.flush()
                    rows += 1

                # SPIKE rows: log as a separate row with voltage_V = spike diff
                elif line.startswith("SPIKE at cycle "):
                    # parse: "SPIKE at cycle N diff=X.XXXXV total_spikes=N"
                    try:
                        parts = line.split()
                        cycle = parts[3]
                        diff  = parts[4].split("=")[1].rstrip("V")
                        writer.writerow(["SPIKE", cycle, "", "", diff])
                        f.flush()
                        rows += 1
                    except Exception:
                        pass

                elif "Test complete" in line:
                    print("\nTest finished.")
                    break

        except KeyboardInterrupt:
            print("\nStopped by user.")

    print(f"Saved {rows} rows to {out_file}")


if __name__ == "__main__":
    main()
