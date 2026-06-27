# 🛡️ 网络安全实用小脚本

三个纯 Python 脚本，无需安装第三方依赖，标准库即开即用。用于日常安全自查、运维巡检、学习参考。

> 📅 最后更新：2026-06-27  
> ⚠️ 仅用于授权的安全自查和教育用途

---

## 📦 脚本清单

| 脚本 | 功能 | 用法 |
|------|------|------|
| `port-scanner.py` | TCP 端口扫描 | `python3 port-scanner.py <IP> [起始端口] [结束端口]` |
| `ssl-checker.py` | SSL 证书检查 | `python3 ssl-checker.py <域名> [端口]` |
| `http-headers.py` | HTTP 安全头审计 | `python3 http-headers.py <URL>` |

---

## 1. 端口扫描器 `port-scanner.py`

### 功能

- 并发 TCP 端口扫描（100 线程）
- 自动识别常见服务（SSH、HTTP、MySQL 等）
- 支持域名和 IP

### 示例

```bash
# 扫描常见端口
python3 port-scanner.py 192.168.1.1 1 1024

# 扫描特定端口
python3 port-scanner.py 192.168.1.1 80 443

# 扫描自己的服务器
python3 port-scanner.py 154.202.118.123 22 8080
```

### 输出示例

```
🔍 扫描目标: 192.168.1.1
📡 端口范围: 1 - 1024
──────────────────────────────────────────────────
  ✅ 端口    22  开放  (SSH)
  ✅ 端口    80  开放  (HTTP)
  ✅ 端口   443  开放  (HTTPS)
──────────────────────────────────────────────────
⏱  扫描完成，耗时 3.2 秒
📊 共扫描 1024 个端口，3 个开放
```

---

## 2. SSL 证书检查器 `ssl-checker.py`

### 功能

- 检查 TLS 版本和加密套件
- 证书到期时间 + 剩余天数
- 证书链信息（颁发者、SAN 备用域名）
- 到期预警（<7 天 🚨、<30 天 ⚠️）

### 示例

```bash
python3 ssl-checker.py github.com
python3 ssl-checker.py example.com 8443
```

### 输出示例

```
🔒 SSL/TLS 证书信息
──────────────────────────────────────────────────
📍 站点:        github.com:443
🔐 TLS 版本:    TLSv1.3
🔑 加密套件:    TLS_AES_256_GCM_SHA384

📛 颁发给:      *.github.com
🏢 颁发者:      DigiCert Inc

📅 生效时间:    2025-03-15 00:00:00
📅 到期时间:    2027-03-15 23:59:59
⏰ 剩余天数:    ✅ 261 天

🌐 备用域名 (SAN):
    github.com
    *.github.com
    *.githubusercontent.com
```

---

## 3. HTTP 安全头审计器 `http-headers.py`

### 功能

- 检查 9 项关键安全头是否配置
- 按严重性分高/中/低三级
- 安全评分（A+ 到 D）
- 检测信息泄露头（Server、X-Powered-By 等）

### 检查的安全头

| 安全头 | 严重性 | 防护目标 |
|--------|--------|---------|
| `Strict-Transport-Security` | 🔴 高 | HTTPS 强制 |
| `Content-Security-Policy` | 🔴 高 | XSS 防御 |
| `X-Content-Type-Options` | 🟡 中 | MIME 嗅探 |
| `X-Frame-Options` | 🟡 中 | 点击劫持 |
| `X-XSS-Protection` | 🟢 低 | XSS 过滤 |
| `Referrer-Policy` | 🟢 低 | 隐私控制 |
| `Permissions-Policy` | 🟡 中 | API 权限 |
| `Cache-Control` | 🟢 低 | 缓存控制 |
| `X-Permitted-Cross-Domain-Policies` | 🟢 低 | 跨域控制 |

### 示例

```bash
python3 http-headers.py https://github.com
python3 http-headers.py http://154.202.118.123:8080
```

### 输出示例

```
🔍 扫描目标: github.com
📍 完整 URL: https://github.com
───────────────────────────────────────────────────────
✅ Strict-Transport-Security
   max-age=31536000; includeSubdomains; preload
✅ Content-Security-Policy
   default-src 'none'; ...
✅ X-Content-Type-Options
   nosniff
❌ X-Frame-Options  【缺失】
   防止页面被嵌入 iframe
   建议值: DENY 或 SAMEORIGIN
❌ X-XSS-Protection  【缺失】
   启用浏览器内置 XSS 过滤器
   建议值: 1; mode=block
...
───────────────────────────────────────────────────────
📊 HTTP 状态码: 200
📊 安全评分:    🟡 B
📊 通过/总计:   7/9
```

---

## 🛠 快速测试本项目

```bash
# 扫描服务器开放端口
python3 port-scanner.py 154.202.118.123 22 8080

# 检查 HTTP 安全头
python3 http-headers.py http://154.202.118.123:8080
```

---

> ⚠️ **免责声明**：这些脚本仅用于授权的安全自查、运维监控和教育学习。未经授权对他人服务器进行端口扫描属于违法行为。
