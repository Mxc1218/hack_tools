#!/usr/bin/env python3
"""
LDAP 敏感属性扫描器
自动检测用户对象中可能包含密码或异常信息的属性（如属性名包含 pwd, password, legacy, secret 等关键词）
用法示例:
  # 匿名连接
  python3 ldap_sensitive_attrs.py 10.129.11.11 -b "DC=cascade,DC=local"
  # 认证连接
  python3 ldap_sensitive_attrs.py 10.129.11.11 -b "DC=cascade,DC=local" -u "CN=r.thompson,OU=Users,OU=UK,DC=cascade,DC=local" -p "rY4n5eva"
  # 自定义关键词
  python3 ldap_sensitive_attrs.py 10.129.11.11 -b "DC=cascade,DC=local" -k "pwd,password,legacy,secret"
"""

import argparse
from ldap3 import Server, Connection, ALL, SUBTREE

# 默认敏感属性关键词（不区分大小写）
DEFAULT_KEYWORDS = ["pwd", "password", "legacy", "secret", "key", "cred", "pass"]

# 标准属性，即使包含关键词也忽略（不区分大小写）
EXCLUDE_ATTRS = ["badpasswordtime", "badpwdcount", "pwdlastset"]

def is_sensitive(attr_name, keywords):
    """检查属性名是否包含关键词且不在排除列表中"""
    lower = attr_name.lower()
    if lower in EXCLUDE_ATTRS:
        return False
    for kw in keywords:
        if kw.lower() in lower:
            return True
    return False

def main():
    parser = argparse.ArgumentParser(description="LDAP 敏感属性扫描器")
    parser.add_argument("server", help="LDAP 服务器 IP 或域名")
    parser.add_argument("-b", "--base-dn", required=True, help="搜索基准 DN，如 DC=cascade,DC=local")
    parser.add_argument("-u", "--user", help="绑定用户的 DN (留空则匿名绑定)")
    parser.add_argument("-p", "--password", help="绑定用户的密码")
    parser.add_argument("-f", "--filter", default="(objectClass=user)", help="LDAP 过滤器 (默认用户)")
    parser.add_argument("-k", "--keywords", help="敏感关键词，逗号分隔 (默认: pwd,password,legacy,secret,key,cred,pass)")
    parser.add_argument("--page-size", type=int, default=500, help="分页大小")
    parser.add_argument("--include-deleted", action="store_true", help="包括已删除对象")
    parser.add_argument("--show-all-attrs", action="store_true", help="显示所有属性（不过滤）")
    args = parser.parse_args()

    # 解析关键词
    if args.keywords:
        keywords = [k.strip() for k in args.keywords.split(",") if k.strip()]
    else:
        keywords = DEFAULT_KEYWORDS

    # 服务器连接
    server = Server(args.server, get_info=ALL)
    try:
        if args.user and args.password:
            conn = Connection(server, user=args.user, password=args.password, auto_bind=True)
        else:
            conn = Connection(server, auto_bind=True)
    except Exception as e:
        print(f"[-] 连接失败: {e}")
        exit(1)

    # 控制：包括已删除对象
    controls = []
    if args.include_deleted:
        controls.append(("1.2.840.113556.1.4.417", True, None))  # Show Deleted Objects

    print(f"[*] 正在搜索 {args.base_dn}，过滤器: {args.filter}")
    try:
        conn.search(
            search_base=args.base_dn,
            search_filter=args.filter,
            search_scope=SUBTREE,
            attributes=["*"],        # 获取全部属性
            paged_size=args.page_size,
            size_limit=0,
            controls=controls
        )
    except Exception as e:
        print(f"[-] 搜索失败: {e}")
        exit(1)

    if len(conn.entries) == 0:
        print("[-] 未找到匹配的对象。")
        exit(0)

    found_any = False
    for entry in conn.entries:
        dn = entry.entry_dn
        username = ""
        # 尝试获取常见用户名属性
        if "sAMAccountName" in entry:
            username = str(entry["sAMAccountName"])
        elif "cn" in entry:
            username = str(entry["cn"])
        elif "name" in entry:
            username = str(entry["name"])

        sensitive_attrs = {}
        for attr in entry.entry_attributes:
            # 如果指定显示所有属性，则全部输出，但默认只过滤敏感属性
            if args.show_all_attrs:
                sensitive_attrs[attr] = entry[attr].values
            elif is_sensitive(attr, keywords):
                sensitive_attrs[attr] = entry[attr].values

        if sensitive_attrs:
            found_any = True
            print(f"\n[+] 用户: {username}  (DN: {dn})")
            for attr, vals in sensitive_attrs.items():
                print(f"    {attr}: {vals}")

    if not found_any:
        print("[*] 未发现包含敏感属性的用户。")

    conn.unbind()

if __name__ == "__main__":
    main()
