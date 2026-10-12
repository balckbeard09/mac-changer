import argparse
import os
import re
import shutil
import subprocess
import sys


MAC_PATTERN = re.compile(r"(?:[0-9a-fA-F]{2}:){5}[0-9a-fA-F]{2}")


def get_arguments():
    parser = argparse.ArgumentParser(
        description="Change and verify a network interface's MAC address."
    )

    parser.add_argument(
        "-i", "--interface",
        required=True,
        help="Network interface to modify"
    )

    parser.add_argument(
        "-m", "--mac",
        dest="new_mac",
        required=True,
        help="New MAC address"
    )

    options = parser.parse_args()

    if not MAC_PATTERN.fullmatch(options.new_mac):
        parser.error("Invalid MAC address format. Use XX:XX:XX:XX:XX:XX.")

    return options


def run_command(command):
    return subprocess.run(
        command,
        capture_output=True,
        text=True,
        check=False
    )


def get_interface_info(interface):
    result = run_command(["ip", "-o", "link", "show", "dev", interface])

    if result.returncode != 0:
        raise RuntimeError(
            result.stderr.strip() or f"Interface '{interface}' not found."
        )

    mac_match = re.search(
        r"\blink/ether\s+([0-9a-fA-F:]{17})",
        result.stdout
    )

    if not mac_match:
        raise RuntimeError("Unable to read the interface's MAC address.")

    flags_match = re.search(r"<([^>]*)>", result.stdout)

    if not flags_match:
        raise RuntimeError("Unable to determine the interface state.")

    flags = flags_match.group(1).split(",")

    return mac_match.group(1), "UP" in flags


def change_mac(interface, new_mac):
    if not sys.platform.startswith("linux"):
        raise RuntimeError("This script supports Linux only.")

    if os.geteuid() != 0:
        raise RuntimeError("Run this script with sudo.")

    if not shutil.which("ip"):
        raise RuntimeError("The 'ip' command is required.")

    current_mac, was_up = get_interface_info(interface)

    if current_mac.lower() == new_mac.lower():
        print(f"[!] {interface} already uses {current_mac}.")
        return

    print(f"[+] Current MAC: {current_mac}")
    print(f"[+] Changing MAC address on {interface} to {new_mac}")

    down_result = run_command(
        ["ip", "link", "set", "dev", interface, "down"]
    )

    if down_result.returncode != 0:
        raise RuntimeError(
            down_result.stderr.strip() or "Failed to bring interface down."
        )

    change_result = None

    try:
        change_result = run_command(
            ["ip", "link", "set", "dev", interface, "address", new_mac]
        )

        if change_result.returncode != 0:
            raise RuntimeError(
                change_result.stderr.strip() or "Failed to change MAC address."
            )

    finally:
        if was_up:
            up_result = run_command(
                ["ip", "link", "set", "dev", interface, "up"]
            )

            if up_result.returncode != 0:
                raise RuntimeError(
                    up_result.stderr.strip()
                    or "Failed to restore the interface's original state."
                )

    updated_mac, _ = get_interface_info(interface)

    if change_result is None or change_result.returncode != 0:
        raise RuntimeError("MAC address change failed.")

    if updated_mac.lower() != new_mac.lower():
        raise RuntimeError(
            f"Verification failed. Current MAC address: {updated_mac}"
        )

    print(f"[+] MAC address successfully changed to {updated_mac}")


def main():
    options = get_arguments()

    try:
        change_mac(options.interface, options.new_mac)
    except (RuntimeError, OSError) as error:
        print(f"[-] {error}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
