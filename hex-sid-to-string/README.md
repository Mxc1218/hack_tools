# hex_sid_to_string

Convert a binary/hex SID to the standard string format (e.g. `S-1-5-21-...`).

Active Directory stores SIDs (Security Identifiers) in binary form, and tools like BloodHound, ldapsearch, or AD enumeration scripts often dump them as hex. This script decodes the binary structure (revision, identifier authority, sub-authorities) and prints the human-readable string form.

## Features

- Accepts hex input with or without the `0x` prefix
- Handles multi-sub-authority SIDs (e.g. the 4-5 sub-authority layout typical of AD domain SIDs)

## Usage

```bash
python hex_sid_to_string.py <hex_sid>
```

### Examples

```bash
# With 0x prefix
python hex_sid_to_string.py 0x010500000000000515000000A065CF7E70B1B16310DCA96CF401000000

# Without 0x prefix
python hex_sid_to_string.py 010500000000000515000000A065CF7E70B1B16310DCA96CF401000000
```

Example output:

```
S-1-5-21-2127521184-1604012920-1887927527-500
```

## Notes

- The script takes exactly one argument; a bare `0x010500...` hex string is the common input from AD tooling.
- Invalid input prints an error to stderr and exits with code 1.
