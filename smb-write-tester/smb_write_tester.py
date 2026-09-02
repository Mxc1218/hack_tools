#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SMB 共享可写性检测工具（递归探测子目录，无挂载）
支持匿名/认证，带超时和深度限制，结果导出 CSV。
"""

import subprocess
import sys
import os
import tempfile
import csv
import re

def get_subdirs(ip, share, user=None, password=None, path='', timeout=10):
    """
    通过 smbclient 列出指定路径下的所有子目录。
    返回子目录名称列表（相对路径），超时或失败返回空列表。
    """
    target = f"//{ip}/{share}"
    cmd = ["smbclient", target]
    if user and password:
        cmd.extend(["-U", f"{user}%{password}"])
    else:
        cmd.append("-N")
    # 构造 smb 命令：先 cd，再 ls
    if path:
        smb_cmd = f'cd "{path}"; ls'
    else:
        smb_cmd = "ls"
    cmd.extend(["-c", smb_cmd, "-t", str(timeout)])

    try:
        proc = subprocess.run(cmd, stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE, timeout=timeout+2)
        if proc.returncode != 0:
            err = proc.stderr.decode().strip()
            if err:
                print(f"      ⚠️ 列出目录失败: {err[:50]}...")
            return []
        output = proc.stdout.decode('utf-8', errors='ignore')
    except subprocess.TimeoutExpired:
        print(f"      ⏱️ 列出目录超时 (> {timeout}s)，跳过")
        return []
    except Exception as e:
        print(f"      ⚠️ 列出目录异常: {e}")
        return []

    dirs = []
    for line in output.splitlines():
        line = line.rstrip()
        if not line:
            continue
        # 匹配模式：名称 + 空白 + D + 空白 + 数字
        m = re.match(r'^(.+?)\s+([DA])\s+\d+', line)
        if m:
            name = m.group(1).strip()
            typ = m.group(2)
            if typ == 'D' and name not in ('.', '..'):
                dirs.append(name)
    return dirs

def test_smb_write(ip, share, user=None, password=None, subpath='', timeout=10):
    """
    尝试在指定子目录（subpath）上传测试文件。
    返回 (是否可写, 错误信息)
    """
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
        f.write("SMB Write Test")
        local_path = f.name

    target = f"//{ip}/{share}"
    cmd = ["smbclient", target]
    if user and password:
        cmd.extend(["-U", f"{user}%{password}"])
    else:
        cmd.append("-N")

    if subpath:
        smb_cmd = f'cd "{subpath}"; put {local_path} test_write.txt'
    else:
        smb_cmd = f"put {local_path} test_write.txt"
    cmd.extend(["-c", smb_cmd, "-t", str(timeout)])

    try:
        proc = subprocess.run(cmd, stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE, timeout=timeout+2)
        if proc.returncode == 0:
            # 上传成功，立即删除远程测试文件
            clean_cmd = ["smbclient", target]
            if user and password:
                clean_cmd.extend(["-U", f"{user}%{password}"])
            else:
                clean_cmd.append("-N")
            if subpath:
                clean_cmd.extend(["-c", f'cd "{subpath}"; rm test_write.txt', "-t", str(timeout)])
            else:
                clean_cmd.extend(["-c", "rm test_write.txt", "-t", str(timeout)])
            subprocess.run(clean_cmd, stdout=subprocess.DEVNULL,
                           stderr=subprocess.DEVNULL, timeout=timeout+2)
            return True, "可写"
        else:
            error = proc.stderr.decode().strip()
            if "ACCESS_DENIED" in error:
                return False, "权限拒绝"
            return False, error
    except subprocess.TimeoutExpired:
        return False, "超时"
    except Exception as e:
        return False, f"异常: {e}"
    finally:
        try:
            os.unlink(local_path)
        except:
            pass

def explore_share(ip, share, user=None, password=None, base_path='', depth=0, max_depth=2):
    """
    递归探测共享下的子目录，返回可写子目录列表。
    depth 当前深度，max_depth 最大探测深度。
    """
    writable_dirs = []
    if depth >= max_depth:
        return writable_dirs

    subdirs = get_subdirs(ip, share, user, password, base_path)
    if not subdirs:
        return writable_dirs

    for d in subdirs:
        full_sub = f"{base_path}/{d}" if base_path else d
        print(f"      📁 测试子目录: {full_sub}")
        ok, info = test_smb_write(ip, share, user, password, full_sub)
        if ok:
            print(f"         ✅ 可写！")
            writable_dirs.append((full_sub, info))
        else:
            print(f"         ❌ 不可写 ({info})")
        # 递归进入更深层
        deeper = explore_share(ip, share, user, password, full_sub, depth+1, max_depth)
        writable_dirs.extend(deeper)
    return writable_dirs

def main():
    if len(sys.argv) < 2:
        print(f"用法: {sys.argv[0]} <共享列表.csv>")
        print("CSV格式示例:")
        print('10.10.10.103,Department Shares,guest,')
        print('10.10.10.103,Public,admin,pass123')
        sys.exit(1)

    input_file = sys.argv[1]
    all_results = []

    with open(input_file, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        for row in reader:
            if not row or row[0].strip().startswith('#'):
                continue
            fields = [col.strip() for col in row]
            if len(fields) < 2:
                continue
            ip = fields[0]
            share = fields[1]
            user = fields[2] if len(fields) > 2 and fields[2] else None
            password = fields[3] if len(fields) > 3 and fields[3] else None

            print(f"\n📂 扫描共享: //{ip}/{share}")
            if user and password:
                print(f"   使用用户: {user}")
            else:
                print("   匿名登录")

            # 测试根目录
            print("   📁 测试根目录: /")
            root_ok, root_info = test_smb_write(ip, share, user, password)
            if root_ok:
                print(f"   ✅ 根目录可写: //{ip}/{share}")
                all_results.append((f"//{ip}/{share}", root_ok, root_info))
            else:
                print(f"   ❌ 根目录不可写 ({root_info})")

            # 递归探测子目录
            print("   🔍 开始探测子目录（深度限制2层）...")
            writable_subs = explore_share(ip, share, user, password, max_depth=2)
            if writable_subs:
                print(f"   ✅ 发现 {len(writable_subs)} 个可写子目录:")
                for sub, info in writable_subs:
                    full_path = f"//{ip}/{share}/{sub}"
                    print(f"      - {full_path}")
                    all_results.append((full_path, True, info))
            else:
                print("   ❌ 未发现可写子目录（在限定深度内）")

    # 保存结果
    out_file = "smb_write_results.csv"
    with open(out_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["共享路径", "可写", "详细信息"])
        for target, writable, info in all_results:
            writer.writerow([target, "是" if writable else "否", info])

    print(f"\n📄 结果已保存到 {out_file}")

if __name__ == "__main__":
    main()
