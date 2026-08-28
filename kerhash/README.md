# KerHash

Kerberos RC4 NTLM Hash Spray Tool

## Features

- NTLM hash spraying over Kerberos (TCP/88)
- Uses Impacket `getTGT.py`
- User and hash file support
- Delay control between attempts
- Valid credential logging to `valid.txt`

## Installation

```bash
pip install impacket
```

## Usage

```bash
python3 KerHash.py \
  -d htb.local \
  -u users.txt \
  -p hashes.txt \
  --delay 1
```

- `-d, --domain`  – target domain name (e.g. `htb.local`)
- `-u, --users`   – file with one username per line
- `-p, --hashes`  – file with one NTLM hash per line
- `--delay`       – delay in seconds between attempts (default: 1)
