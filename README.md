# hack_tools
some hack tools

## Tools

| Tool | Location | Description |
|------|----------|-------------|
| hex_sid_to_string | `hex-sid-to-string/` | Convert a binary/hex SID to the standard string format (`S-1-5-21-...`) |
| LDAP Sensitive Attribute Scanner | `ldap-sensitive-scanner/` | Scan LDAP (AD) for user objects with sensitive attributes |
| KerHash | `kerhash/` | Kerberos RC4 NTLM hash spray tool (uses Impacket `getTGT.py`) |

## Usage

### hex_sid_to_string

```bash
python hex-sid-to-string/hex_sid_to_string.py 0x010500000000000515000000...
```

See [hex-sid-to-string/README.md](hex-sid-to-string/README.md) for details.

### LDAP Sensitive Attribute Scanner

```bash
pip install ldap3
python ldap-sensitive-scanner/LDAPSensitiveScanner.py 10.129.11.11 -b "DC=cascade,DC=local"
```

See [ldap-sensitive-scanner/README.md](ldap-sensitive-scanner/README.md) for options (authenticated binds, custom keywords, deleted objects).

### KerHash

```bash
pip install impacket
python kerhash/KerHash.py -d htb.local -u users.txt -p hashes.txt --delay 1
```

Valid `user:hash` combinations are appended to `valid.txt`. See [kerhash/README.md](kerhash/README.md) for details.
