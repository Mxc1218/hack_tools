#!/usr/bin/env python3
import sys
import struct


def sid_to_str(sid: bytes) -> str:
    """
    将二进制 SID 转换为标准字符串格式。
    """
    revision = sid[0]
    sub_id_count = sid[1]
    # 读取 48 位标识符颁发机构 (IAV)
    iav = struct.unpack('>Q', b'\x00\x00' + sid[2:8])[0]
    # 读取各个子权限
    sub_ids = [
        struct.unpack('<I', sid[8 + 4 * i:12 + 4 * i])[0]
        for i in range(sub_id_count)
    ]
    return 'S-{}-{}-{}'.format(revision, iav, '-'.join(map(str, sub_ids)))


def prepare_sid(sid_hex: str) -> str:
    """
    处理十六进制输入（可能含 0x 前缀），返回标准 SID 字符串。
    """
    if sid_hex.startswith(('0x', '0X')):
        hex_str = sid_hex[2:]
    else:
        hex_str = sid_hex
    sid_bytes = bytes.fromhex(hex_str)
    return sid_to_str(sid_bytes)


def main():
    if len(sys.argv) != 2:
        print("Usage: python sid_converter.py <hex_sid>")
        print("Example: python sid_converter.py 0x010500000000000515000000...")
        sys.exit(1)

    hex_input = sys.argv[1]
    try:
        standard_sid = prepare_sid(hex_input)
        print(standard_sid)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
