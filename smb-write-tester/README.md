# SMB 共享可写性检测工具 (无挂载、递归探测)

这是一个用于**检测 SMB 共享中所有可写子目录**的 Python 脚本。  
它无需挂载（不需要 root 权限），直接通过 `smbclient` 协议远程探测，支持**匿名登录**和**带用户名密码的认证**，并能**递归遍历子目录**（可限制深度），找出所有可写入的路径。

## 🎯 适用场景

- 渗透测试中快速定位 SMB 共享的写权限目录
- 企业内网安全审计
- 自动化批量检测多个 SMB 共享
- 云函数 / 容器环境（无特权）下的 SMB 权限探测

## ✨ 特性

- ✅ 不依赖 `mount`，无需 root 权限
- ✅ 支持匿名登录（`-N`）和凭证认证（`-U`）
- ✅ 自动递归探测子目录（可配置最大深度）
- ✅ 每个目录测试超时保护（默认 10 秒），防止卡死
- ✅ 自动清理远程测试文件（成功写入后立即删除）
- ✅ 支持带空格的共享名（通过 CSV 格式输入）
- ✅ 详细日志输出，便于调试
- ✅ 结果导出为 CSV 文件

## 📋 依赖

- Python 3.6+
- `smbclient` 命令行工具（通常 `samba-client` 包提供）

### 安装 smbclient（Debian/Ubuntu/Kali）
```bash
sudo apt update
sudo apt install smbclient
```

## 🚀 使用方法

### 1. 准备输入文件（CSV 格式）

创建一个 `shares.csv` 文件，每行一个共享，用逗号分隔：
```csv
# 格式: IP,共享名,[用户名],[密码]
10.10.10.103,Department Shares,guest,
10.10.10.103,Public Share,admin,pass123
10.10.10.104,Share1,,
```

- 共享名可包含空格，无需转义。
- 用户名和密码为**可选字段**，留空表示匿名登录。
- 只提供用户名而不提供密码，则密码视为空字符串（部分服务器允许空密码）。

### 2. 运行脚本
```bash
python3 smb_write_tester.py shares.csv
```

### 3. 查看结果
- 控制台实时输出测试进度
- 结果保存在 `smb_write_results.csv`，包含所有可写目录的完整路径

## ⚙️ 可调参数

在脚本中可修改以下变量（位于函数调用处）：
- `timeout`：每个 SMB 操作的超时时间（默认 10 秒）
- `max_depth`：递归探测的最大深度（默认 2 层，即子目录的子目录）

## 📝 示例输出

```text
📂 扫描共享: //10.10.10.103/Department Shares
   匿名登录
   📁 测试根目录: /
   ❌ 根目录不可写 (NT_STATUS_ACCESS_DENIED)
   🔍 开始探测子目录（深度限制2层）...
      📁 测试子目录: HR
         ❌ 不可写 (NT_STATUS_ACCESS_DENIED)
      📁 测试子目录: Finance
         ✅ 可写！
      📁 测试子目录: Projects
         📁 测试子目录: Projects/Backup
            ✅ 可写！
   ✅ 发现 2 个可写子目录:
      - //10.10.10.103/Department Shares/Finance
      - //10.10.10.103/Department Shares/Projects/Backup
📄 结果已保存到 smb_write_results.csv
```

## ⚠️ 注意事项

- **授权使用**：仅对你有合法权限的系统进行测试，未经授权禁止扫描。
- **网络环境**：确保目标 SMB 服务器 445 端口可达。
- **性能**：若共享目录结构庞大，建议降低 `max_depth` 或增加 `timeout`。
- **空密码**：某些服务器可能拒绝空密码，此时请使用真实凭证或尝试 `-N` 匿名模式（脚本会自动处理）。

## 🔧 故障排除

| 问题 | 解决方法 |
|------|----------|
| `smbclient: command not found` | 安装 `smbclient` 包 |
| `Connection timed out` | 检查防火墙、网络连通性，适当增加 `timeout` 值 |
| `NT_STATUS_ACCESS_DENIED` | 凭证不足，尝试其他用户或匿名模式 |
| `Tree connect failed` | 共享名错误或不存在，检查 CSV 中的共享名 |

## 📜 许可证

MIT License

## 🤝 贡献

欢迎提交 Issue 和 Pull Request。

---

**作者**：Mxc1218  
**GitHub**：https://github.com/Mxc1218/hack_tools
