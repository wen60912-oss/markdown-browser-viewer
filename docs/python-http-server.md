# Python HTTP 服务器搭建 —— 让手机浏览器访问你电脑上的网页

> 用一行命令把任何目录变成网站，手机、平板、其他电脑都能访问。

---

## 1. 我做了什么

### 第一步：进入文件所在目录

```bash
cd /root
```

### 第二步：一行命令启动服务器

```bash
python3 -m http.server 8080
```

**就这么简单。** 服务器立即启动。

### 第三步：后台运行（可选）

如果想让服务器在后台一直运行，不占用终端：

```bash
python3 -m http.server 8080 &
```

或者用 `nohup` 保证关掉终端也不会停：

```bash
nohup python3 -m http.server 8080 > /dev/null 2>&1 &
```

---

## 2. 命令拆解

```
python3 -m http.server 8080
  │      │      │        │
  │      │      │        └── 端口号（可以改成任意数字，如 8000、9000）
  │      │      └─────────── 模块名：HTTP 服务器
  │      └────────────────── -m 表示"运行一个模块"
  └───────────────────────── Python 3 解释器
```

| 参数 | 含义 |
|------|------|
| `python3` | 调用 Python 3（Linux/Mac 系统自带） |
| `-m` | 运行 Python 内置模块 |
| `http.server` | Python 内置的 HTTP 服务器模块 |
| `8080` | 监听端口号（1024-65535 之间随便选） |

---

## 3. 如何访问

### 本机访问

```
http://localhost:8080
http://127.0.0.1:8080
```

### 局域网访问（手机和电脑同 WiFi）

先查电脑 IP：

```bash
hostname -I | awk '{print $1}'
# 例如输出：10.0.72.3
```

手机浏览器打开：

```
http://10.0.72.3:8080/markdown-viewer.html
```

### 公网访问（任何网络都能访问）

先查公网 IP：

```bash
curl -s ifconfig.me
# 例如输出：154.202.118.123
```

手机用流量也能打开：

```
http://154.202.118.123:8080/markdown-viewer.html
```

> ⚠️ 云服务器需要去控制台放行端口（安全组添加 TCP 8080 入站规则）

---

## 4. 防火墙检查（公网访问必须）

```bash
# 检查系统防火墙
ufw status

# 检查端口是否在监听
ss -tlnp | grep 8080
```

期望看到：

```
LISTEN  0  5  0.0.0.0:8080  0.0.0.0:*
```

其中 `0.0.0.0:8080` 表示**所有网络接口**都能访问，是正确状态。

如果是 `127.0.0.1:8080`，则只能本机访问，外人打不开。

---

## 5. 它怎么工作的

```
┌────────────────────────────────────────────────┐
│              你的电脑（服务器）                  │
│                                                │
│  /root/                                        │
│  ├── markdown-viewer.html                      │
│  ├── markdown-browser-viewer-development-log.md │
│  └── ...                                       │
│                                                │
│  python3 -m http.server 8080                   │
│         │                                      │
│         ▼                                      │
│  ┌──────────────┐                              │
│  │ HTTP 服务器   │  监听 0.0.0.0:8080          │
│  │ (端口 8080)  │                              │
│  └──────┬───────┘                              │
└─────────┼──────────────────────────────────────┘
          │
    ──────┼─────── 网络（WiFi / 互联网）────────
          │
┌─────────┴──────────────────────────────────────┐
│           手机浏览器                             │
│                                                 │
│  输入：http://154.202.118.123:8080/             │
│               markdown-viewer.html              │
│                                                 │
│  服务器收到请求 → 找到文件 → 返回文件内容       │
│  浏览器收到内容 → 渲染成网页                     │
└─────────────────────────────────────────────────┘
```

**流程**：

1. 手机浏览器发送 HTTP 请求：`GET /markdown-viewer.html`
2. 服务器在 `/root/` 目录下找到 `markdown-viewer.html`
3. 读取文件内容，返回给手机
4. 手机浏览器收到 HTML，执行里面的 JS（marked.js 渲染 Markdown）
5. 用户看到渲染后的网页

---

## 6. 常用操作

### 查看服务器是否在运行

```bash
ss -tlnp | grep 8080
```

有输出 = 在运行，无输出 = 已停止。

### 停止服务器

```bash
# 方法一：找到进程 ID 然后杀掉
ss -tlnp | grep 8080
# 输出示例：... pid=645591 ...
kill 645591

# 方法二：直接杀所有 python http.server
pkill -f "http.server"
```

### 换一个端口

```bash
python3 -m http.server 9000
```

### 指定绑定地址（只允许本机访问）

```bash
python3 -m http.server 8080 --bind 127.0.0.1
```

---

## 7. 为什么用 Python 而不是 Nginx/Apache

| 方案 | 优点 | 缺点 |
|------|------|------|
| `python3 -m http.server` | 系统自带，一行命令，无需配置 | 性能低，不适合生产环境 |
| Nginx | 高性能，功能强大 | 需要安装和配置 |
| Node.js http-server | 功能丰富 | 需要 npm install |

对于**临时分享一个 HTML 文件给手机看**这种场景，Python 内置服务器是最快的选择——零安装、零配置、用完即停。

---

## 8. 当前服务器状态

| 项目 | 值 |
|------|-----|
| 运行目录 | `/root/` |
| 端口 | `8080` |
| 进程 | Python SimpleHTTP/0.6 |
| 局域网 IP | `10.0.72.3` |
| 公网 IP | `154.202.118.123` |

**可访问的文件**：

| URL | 内容 |
|-----|------|
| `/markdown-viewer.html` | 浏览器 Markdown 查看器 |
| `/markdown-viewer.html?file=markdown-viewer/markdown-browser-viewer-development-log.md` | 查看器加载开发记录 |
| `/markdown-viewer.html?file=markdown-viewer/github-setup-guide.md` | 查看器加载 GitHub 指南 |
| `/markdown-viewer.html?file=markdown-viewer/2026-06-27-0640-session-action-log.md` | 查看器加载操作日志 |

---

> 📅 **创建时间**：2026-06-27  
> 🐍 **Python 版本**：3.10.12  
> 🖥 **服务器**：Python http.server（SimpleHTTP/0.6）
