# Hardware Setup Commands

Commands for hardware integrations — Raspberry Pi networking and ESP32-P4 audio capture via serial.

---

## Raspberry Pi — Static IP

Edit `/etc/dhcpcd.conf` and add the following block, then reboot:

```
interface wlan0
static ip_address=192.168.1.50/24
static routers=192.168.1.1
static domain_name_servers=8.8.8.8
```

---

## ESP32-P4 Audio Recording via Raspberry Pi

### 1. Confirm the ESP32 is connected

```bash
lsusb
```

### 2. Check which serial port the ESP32 is on

```bash
ls /dev/ttyACM*
# Expected output: /dev/ttyACM0
```

### 3. Configure the serial port (raw mode, no echo)

```bash
stty -F /dev/ttyACM0 raw -echo
```

### 4. Capture raw audio data to a file

```bash
cat /dev/ttyACM0 > audio.raw
```

### 5. Play the captured audio on the Pi

```bash
ffplay -f s32le -ar 48000 -ac 1 audio.raw
```
