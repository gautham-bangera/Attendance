import threading
import time
import bluetooth  # requires pybluez

class BluetoothScanner:
    def __init__(self, interval=5):
        self.interval = interval
        self.devices = []  # List of (addr, name)
        self.running = False
        self.thread = None

    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self._scan_loop, daemon=True)
        self.thread.start()

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join(timeout=1)

    def get_devices(self):
        return self.devices

    def _scan_loop(self):
        while self.running:
            try:
                # discover_devices returns list of addresses or tuples depending on lookup_names
                detected = bluetooth.discover_devices(duration=4, lookup_names=True, flush_cache=True, lookup_class=False)
                # detected is list of (addr, name)
                self.devices = detected
            except Exception as e:
                print(f"BT Scan Error: {e}")
            
            # Wait for next interval
            for _ in range(self.interval):
                if not self.running: break
                time.sleep(1)