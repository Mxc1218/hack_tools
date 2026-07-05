# LDAPSensitiveScanner-
a tools be used to check  LDAP  for sensitive attributes
# LDAP Sensitive Attribute Scanner

A Python script that queries LDAP (Active Directory or other LDAP-compatible servers) to find user objects with potentially sensitive attributes. It filters attribute names based on keywords (default: `pwd`, `password`, `legacy`, `secret`, `key`, `cred`, `pass`) while excluding common noise attributes like `badPasswordTime`, `pwdLastSet`, and `badPwdCount`.

## Features
- **Keyword-based detection** – automatically discovers non-standard or suspicious attributes.
- **Exclusion list** – skips standard AD timestamp/count attributes to reduce noise.
- **Configurable keywords** – supply custom comma-separated keywords.
- **Supports anonymous and authenticated binds**.
- **Option to include deleted objects (Recycle Bin)** via Microsoft Show Deleted control.

## Installation
```bash
pip install ldap3
# Anonymous scan
python ldap_sensitive_attrs.py 10.129.11.11 -b "DC=cascade,DC=local"

# Authenticated scan with custom keywords
python ldap_sensitive_attrs.py 10.129.11.11 -b "DC=cascade,DC=local" \
  -u "CN=user,OU=Users,DC=cascade,DC=local" -p "password" \
  -k "legacy,pwd,custom"

# Include deleted objects (requires permissions)
python ldap_sensitive_attrs.py 10.129.11.11 -b "CN=Deleted Objects,DC=cascade,DC=local" \
  -u "CN=admin,DC=cascade,DC=local" -p "adminpass" --include-deleted
  [+] User: r.thompson  (DN: CN=r.thompson,OU=Users,OU=UK,DC=cascade,DC=local)
    cascadeLegacyPwd: ['clk0bjVldmE=']
