# mac-changer
A command-line tool written in Python that changes the MAC address of a network interface on Linux and verifies that the change worked.

It uses the `ip` command (iproute2) to make the change and reads the result back from the system to confirm it.

Features:

- Changes the MAC address of a chosen network interface
- Validates the MAC address format before doing anything
- Shows the current MAC address before changing it
- Checks for root privileges and a Linux system before starting
- Brings the interface back up afterwards if it was up before
- Verifies the new MAC address after the change
- Prints clear error messages and exits with an error code on failure

Requirements:

- Linux
- Python 3
- The `ip` command (`iproute2`)
- Root privileges (`sudo`)

Installation:

```bash
git clone https://github.com/YOUR-USERNAME/mac-address-changer.git
cd mac-address-changer
```
:Usage

```bash
sudo python3 mac_changer.py -i INTERFACE -m NEW_MAC
```

| Option | Description |
|---|---|
| `-i`, `--interface` | The network interface to change (for example `wlo1` or `eth0`) |
| `-m`, `--mac` | The new MAC address, in the format `XX:XX:XX:XX:XX:XX` |

To list your network interfaces:

```bash
ip link show
```

Example:

```bash
sudo python3 mac_changer.py -i wlo1 -m 02:11:22:33:44:55
```

Output:

```
[+] Current MAC: aa:bb:cc:dd:ee:ff
[+] Changing MAC address on wlo1 to 02:11:22:33:44:55
[+] MAC address successfully changed to 02:11:22:33:44:55
```

How It Works:

1. Reads the command-line arguments with `argparse` and checks the MAC format with a regular expression.
2. Checks that the system is Linux, that the script runs as root, and that the `ip` command exists.
3. Reads the interface's current MAC address and its state (up or down).
4. Brings the interface down, sets the new MAC address, and brings the interface back up if it was up before.
5. Reads the MAC address again and compares it with the requested one.

 Security Notes:

- Commands are run with `subprocess.run` using a list of arguments, not a shell string, so the input cannot be used to run extra commands.
- The MAC format is checked with `fullmatch`, so the entire input must match `XX:XX:XX:XX:XX:XX`.

Limitations

- Works on Linux only.
- The change is temporary and usually lasts until the interface is reset or the system restarts. It does not change the hardware MAC address.
- Some network drivers and virtual interfaces do not allow MAC address changes.
- The connection may drop briefly while the change is applied.
- NetworkManager may reset the address when the network reconnects.
- Use a MAC address that starts with an even first byte (for example `02:...`). Addresses starting with an odd first byte are multicast addresses and are rejected by the system.

