# Cloudflare 域名申请与使用完全指南

> 从注册域名到 DNS 配置、SSL 证书、安全加固的全流程指南，含 2025-2026 最新定价与技巧。

---

## 目录

- [1. Cloudflare 是什么](#1-cloudflare-是什么)
- [2. 域名注册流程](#2-域名注册流程)
- [3. 定价（2025-2026）](#3-定价2025-2026)
- [4. 域名转移到 Cloudflare](#4-域名转移到-cloudflare)
- [5. DNS 配置技巧](#5-dns-配置技巧)
- [6. SSL/TLS 证书配置](#6-ssltls-证书配置)
- [7. 安全加固清单](#7-安全加固清单)
- [8. 性能优化](#8-性能优化)
- [9. 常见问题与排错](#9-常见问题与排错)
- [10. Cloudflare vs 其他注册商](#10-cloudflare-vs-其他注册商)
- [11. 什么情况选/不选 Cloudflare](#11-什么情况选不选-cloudflare)

---

## 1. Cloudflare 是什么

Cloudflare 是全球最大的网络服务商之一，提供：
- **域名注册**（零加价，按批发价）
- **DNS 解析**（全球最快的 1.1.1.1）
- **CDN 加速**（全球 330+ 节点）
- **DDoS 防护**（免费套餐也无限量）
- **SSL 证书**（自动签发，免费）

一句话理解：**域名 + DNS + CDN + 安全，一站式搞定。**

---

## 2. 域名注册流程

### 准备工作

- 一个邮箱（用于注册 Cloudflare 账号）
- 信用卡 / PayPal（用于支付域名费用）
- 想好要注册的域名

### 第一步：注册 Cloudflare 账号

打开 https://dash.cloudflare.com/sign-up，用邮箱注册，验证后登录。

### 第二步：进入域名注册页面

登录后 → 左侧菜单点击 **"域名注册"** → **"注册域名"**。

### 第三步：搜索域名

在搜索框输入你想要的域名（如 `myproject.com`），Cloudflare 会显示：
- ✅ 可注册（显示价格）
- ❌ 已被注册（显示 "已注册"）
- 💡 推荐备选（其他可用的相似域名）

### 第四步：加入购物车并结算

```
1. 勾选要注册的域名
2. 选择注册年限（建议 1 年，到期再续）
3. 检查价格（批发价 + $0.20 ICANN 费用）
4. 填写联系信息（WHOIS 自动隐私保护）
5. 支付
```

**支付完成约 60 秒后域名即归你所有。**

### 第五步：初始 DNS 配置

域名注册后，Cloudflare 自动添加基础 DNS 记录。你需要：

```dns
类型    名称    内容                    代理状态
A       @       你的服务器 IP           橙色云朵（已代理）
CNAME   www     你的域名.com            橙色云朵（已代理）
```

如果你像本文档的场景一样有服务器（如 `154.202.118.123`），就填：

```dns
A       @       154.202.118.123        开始先灰色云朵，验证后再开橙色
```

---

## 3. 定价（2025-2026）

Cloudflare 采用**批发价零加价**模式——注册、续费、转入价格完全一致，不会第一年便宜第二年涨价。

| 域名后缀 | 年费（注册/续费/转入） |
|----------|----------------------|
| `.com` | $10.46 |
| `.net` | $11.86 |
| `.org` | $7.52 - $10.13 |
| `.dev` | $10.18 |
| `.io` | $45.00 |
| `.app` | $14.20 |
| `.co` | $8.00 |
| `.xyz` | $12.30 |
| `.ai` | 按批发价（支持） |

> **核心优势**：续费价 = 注册价。没有"首年 $1.99，次年 $49.99"这种套路。

---

## 4. 域名转移到 Cloudflare

如果你已有域名在其他注册商（如 Namecheap、GoDaddy），可以转入 Cloudflare：

### 转移步骤

```
1. 在原注册商解锁域名（关闭 Transfer Lock）
2. 获取转移授权码（EPP Code / Auth Code）
3. 在 Cloudflare 域名注册 → "转移域名"
4. 输入域名和授权码
5. 支付转入费用（一年的续费价格）
6. 等待 5-7 天自动完成
```

### 注意事项

- 域名注册不满 60 天**不能转移**（ICANN 规定）
- 转移后原有剩余时间**不会丢失**（叠加到新有效期）
- 转移过程中网站**不受影响**（前提是 DNS 不变）

---

## 5. DNS 配置技巧

### 5.1 灰色云朵 vs 橙色云朵

Cloudflare DNS 记录有两种模式：

| 模式 | 图标 | 行为 | 何时用 |
|------|------|------|--------|
| **仅 DNS** | 灰色云朵 ☁️ | 直接解析到源站 IP | 调试阶段、非 HTTP 服务 |
| **已代理** | 橙色云朵 🟠 | 流量经过 Cloudflare 中转 | 正式上线后 |

**最佳实践**：先全用灰色云朵验证服务正常，再切橙色。

### 5.2 关键 DNS 配置

```dns
# 根域名（A 记录）
类型   名称   内容              代理    TTL
A      @      154.202.118.123   🟠     自动

# www 子域名（CNAME 记录）
CNAME  www    你的域名.com       🟠     自动

# 邮件（MX 记录）—— 不要代理！
MX     @      mail.你的域名.com  ☁️     自动

# TXT 记录（域名验证、SPF 等）
TXT    @      "v=spf1 ..."      ☁️     自动
```

### 5.3 CNAME 扁平化（CNAME Flattening）

Cloudflare 支持根域名（`@`）使用 CNAME，内部自动解析为 A 记录。这允许你把裸域名指向 CDN 别名，而不必暴露源站 IP。

### 5.4 DNSSEC —— 建议开启

```
Cloudflare 控制台 → DNS → 设置 → DNSSEC → 启用
```

然后把生成的 DS 记录添加到你的域名注册商处，防止 DNS 劫持和缓存投毒攻击。

### 5.5 DNS 迁移注意事项

```
✅ 迁移前截图/备份所有 DNS 记录
✅ 先迁移关键记录（A、CNAME、MX），再迁移次要记录
✅ 修改 Nameserver 后等待 24-48 小时全球生效
✅ dig NS 你的域名.com  # 检查是否已切换到 Cloudflare NS
❌ 不要在迁移期间同时做大量 DNS 改动
```

---

## 6. SSL/TLS 证书配置

### 6.1 加密模式 —— 只用 Full (Strict)

Cloudflare 提供四种 SSL 模式：

| 模式 | 安全？ | 说明 |
|------|--------|------|
| **关闭** | ❌ | 不加密 |
| **Flexible** | ❌ | 浏览器到 CF 加密，CF 到源站**明文** |
| **Full** | ⚠️ | 全程加密但不验证源站证书 |
| **Full (Strict)** | ✅ | 全程加密且验证源站证书 —— **唯一安全的选择** |

> 🚫 **绝对不要用 Flexible 模式**——它会导致重定向死循环，而且源站流量完全未加密。

### 6.2 SSL 必开设置

```
✅ 始终使用 HTTPS          —— 所有 HTTP 请求强制跳转 HTTPS
✅ HSTS                    —— 告诉浏览器"永远用 HTTPS 访问我"
✅ 最低 TLS 版本 → 1.2     —— 拒绝老旧不安全的加密协议
✅ TLS 1.3                 —— 更快握手 + 更强安全
✅ 自动 HTTPS 重写          —— 修复页面中的混合内容警告
✅ 证书透明度监控           —— 有人冒签你的证书时报警
```

### 6.3 证书类型选择

| 类型 | 适用场景 |
|------|---------|
| **Universal SSL** | 免费，自动签发，覆盖根域名 + 一级子域名 |
| **Cloudflare Origin Certificate** | 15 年有效期，支持泛域名，用于源站到 CF 之间的加密 |
| **Advanced Certificate** | 自定义域名覆盖范围，更灵活 |

**关键**：在你的服务器上安装 Cloudflare Origin Certificate，这样 Full (Strict) 模式在免费套餐上也能正常工作。

### 6.4 CAA 记录 —— 签发证书的前提

Cloudflare 签发证书前需要验证 CAA 记录：

```dns
类型   名称   标签        值
CAA    @      0 issue     cloudflare.com
```

如果同时用 Let's Encrypt：

```dns
CAA    @      0 issue     "letsencrypt.org"
CAA    @      0 issue     "cloudflare.com"
```

---

## 7. 安全加固清单

| 设置项 | 建议值 |
|--------|--------|
| **安全级别** | 中（Medium）或更高 |
| **浏览器完整性检查** | 开启 |
| **Privacy Pass** | 开启 |
| **Bot 攻击模式** | 开启（确认不影响 API） |
| **WAF 托管规则** | 开启 OWASP 核心规则集 |
| **速率限制** | 敏感路径至少 15 次请求 / 30 秒 |
| **DDoS 防护** | 始终开启（免费套餐已包含） |
| **Page Shield** | 如果有网页服务则开启 |
| **API Shield** | 如果有 API 则开启 |

### 速率限制策略

```
- 对已通过验证的机器人也做速率限制
- 对敏感路径单独限流（登录页 /login、API /api/*）
- 在 WAF → 工具中放行受信任的 IP/国家/ASN
- ⚠️ 绝对不要在 WAF 规则中使用 "Bypass" 动作 —— 会跳过所有安全防护
```

---

## 8. 性能优化

```
✅ HTTP/2 到源站          —— 如果访客端开了 HTTP/2
✅ HTTP/3 (QUIC)          —— 更快的连接速度
✅ 自动压缩（JS/CSS/HTML） —— 减小文件体积
✅ Brotli 压缩             —— 比 gzip 更高效的压缩算法
✅ 缓存级别 → 缓存所有     —— 对静态资源
✅ Rocket Loader          —— 加速 JS 加载（可能影响部分脚本，需测试）
✅ Page Rules             —— 精细化缓存策略
```

---

## 9. 常见问题与排错

| 错误 | 可能原因 | 解决方法 |
|------|---------|---------|
| **522 Connection Timeout** | 源站未响应 | 在源站防火墙放行 Cloudflare IP 段 |
| **ERR_SSL_VERSION_INTERFERENCE** | 证书冲突 | 源站关闭自动证书管理 |
| **重定向死循环** | 开启了 Flexible SSL | 切换到 Full (Strict) |
| **证书签发卡住** | 缺少 CAA 记录 | 添加 `0 issue cloudflare.com` 的 CAA 记录 |
| **DNS_PROBE_FINISHED_NXDOMAIN** | NS 未生效 | 等待传播（最长 48 小时） |
| **网站打不开但 IP 能直接访问** | 防火墙拦截了 Cloudflare IP | 放行 Cloudflare IP 段 |
| **邮件收发异常** | MX 记录被代理（橙色云朵） | 把 MX 记录改为仅 DNS（灰色云朵） |

---

## 10. Cloudflare vs 其他注册商

| 对比维度 | Cloudflare | Namecheap | Porkbun | GoDaddy |
|----------|-----------|-----------|---------|---------|
| `.com` 价格 | $10.46 | $10.18→$18.68 | $7.00→$11.08 | $11.99→$21.99 |
| 续费加价 | ❌ 无 | ⚠️ 有 | ⚠️ 有 | ⚠️ 严重 |
| WHOIS 隐私 | 免费 | 免费 | 免费 | 免费（部分收费） |
| DNS 独立性 | ❌ 必须用 CF | ✅ 可换 | ✅ 可换 | ✅ 可换 |
| API | ✅ 完整 | ✅ 完整 | 有限 | ✅ 完整 |
| DDoS 防护 | ✅ 无限量免费 | ❌ 无 | ❌ 无 | ❌ 无 |
| 免费 SSL | ✅ 自动 | ❌ | ❌ | ❌ |

---

## 11. 什么情况选/不选 Cloudflare

### ✅ 适合选 Cloudflare

- **开发者**——已经在用或打算用 Cloudflare 的 DNS/CDN/安全产品
- **追求价格透明**——续费不涨价，没有隐藏费用
- **重视安全**——自带 DDoS 防护、WAF、自动 DNSSEC
- **需要 API 管理域名**——2026 年 Registrar API 已公测，可编程注册域名
- **长期持有**——续费不会一年比一年贵

### ❌ 不太适合

- **需要 DNS 与注册商分离**——想把 DNS 放在别处管理
- **域名投资者**——管理大量域名，需要批量操作和灵活的 DNS
- **需要小众后缀**——Cloudflare 支持 300+ TLD，比专业注册商少
- **需要电话客服**——非企业套餐只有工单支持

---

## 快速上手清单

```
□ 1. 注册 Cloudflare 账号
□ 2. 搜索并购买域名
□ 3. 添加 CAA 记录（0 issue cloudflare.com）
□ 4. 扫描/导入现有 DNS 记录
□ 5. 修改注册商 Nameserver 为 Cloudflare
□ 6. 等待 SSL 边缘证书变为 Active
□ 7. SSL 模式设为 Full (Strict)
□ 8. 开启：始终 HTTPS、HSTS、TLS 1.3
□ 9. 关键 A/CNAME 记录切为橙色云朵（已代理）
□ 10. 开启 DNSSEC
□ 11. 配置 WAF 规则 + 速率限制
□ 12. 源站防火墙放行 Cloudflare IP 段
```

---

> 📅 **编写日期**：2026-06-27  
> 🔗 **Cloudflare 控制台**：https://dash.cloudflare.com  
> 📦 **本文档也存在于 GitHub**：https://github.com/wen60912-oss/markdown-browser-viewer

---

## 附：用户原始提问记录

### 本次提问

**原文**：
> cloudflare怎么申请的域名及使用技巧怎么使用，需要注意什么。我可能问的问题与病很多帮我改正语病。写好后的md文件上传github

**语病修正**：
- `cloudflare` → `Cloudflare`（专有名词首字母大写）
- `怎么申请的域名及使用技巧怎么使用` → `怎么申请域名、有哪些使用技巧、需要注意什么`（拆分并列问句，避免粘连）
- `与病很多` → `有很多语病`（"与病"应为"语病"，补"有"字）
- `帮我改正语病` → `请帮我改正语病`（加"请"更礼貌完整）

**修正版**：
> Cloudflare 怎么申请域名、有哪些使用技巧、需要注意什么。我的提问可能有很多语病，请帮我改正。写好后的 Markdown 文件上传到 GitHub。

**英文翻译**：
> How do I register a domain on Cloudflare, what are the usage tips, and what should I pay attention to? My questions may have many language errors — please correct them. Once written, upload the Markdown file to GitHub.
