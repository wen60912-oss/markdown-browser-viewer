# Markdown Browser Viewer

自包含的单文件 HTML Markdown 实时预览器。支持手机/电脑浏览器编辑、预览、上传、下载，通过公网 IP 或 GitHub Pages 访问。

> 📅 最后更新：2026-06-27

---

## 🚀 快速开始

### 1. 启动服务器

```bash
cd /root/markdown-viewer
python3 -m http.server 8080
```

### 2. 浏览器打开

```
本机：  http://localhost:8080
局域网：http://你的局域网IP:8080
公网：  http://你的公网IP:8080
```

### 3. 访问查看器

```
http://你的IP:8080/index.html
```

---

## 📖 使用说明

### 工具栏按钮

| 按钮 | 功能 | 说明 |
|------|------|------|
| 👁 **预览** | 查看渲染效果 | Markdown → 格式化网页 |
| ✏️ **编辑** | 修改源码 | 直接编辑 Markdown 文本，切回预览即时生效 |
| 📂 **打开** | 打开本地文件 | 从手机/电脑选择 .md 文件，自动渲染 |
| ⬇ **下载** | 保存为文件 | 将当前内容下载为 .md 文件 |

### 加载外部文件

URL 加 `?file=` 参数，查看器会自动加载同目录下的 .md 文件：

```
http://你的IP:8080/index.html?file=docs/development-log.md
```

### 典型使用流程

```
手机上打开网址 → 点 📂 打开 → 选手机里的 .md 文件 → 自动渲染预览
                → 点 ✏️ 编辑 → 修改内容 → 点 👁 预览 → 看效果
                → 点 ⬇ 下载 → 保存到手机
```

---

## ✨ 功能清单

- 📝 GitHub Flavored Markdown 渲染（marked.js）
- 🌓 自动亮/暗主题（跟随系统设置）
- ✏️ 实时编辑 + 即时预览
- 📂 打开本地 .md 文件（FileReader API）
- ⬇ 下载为 .md 文件（Blob + createObjectURL）
- 📂 URL 参数加载服务器文件（?file=xxx.md）
- 📑 自动生成目录导航（H1-H3 锚点）
- ⬆️ 回到顶部按钮
- 📱 移动端响应式布局
- 🎨 代码块等宽字体 + 横向滚动

---

## 📚 文档

| 文档 | 说明 |
|------|------|
| [开发全记录](docs/development-log.md) | 从零到完成的所有过程、问题、决策 |
| [会话操作日志](docs/session-log.md) | 每次操作的详细记录 |
| [浏览器上传下载指南](docs/browser-upload-download.md) | File API、Blob、FileReader 完整实现 |
| [GitHub 搭建指南](docs/github-setup.md) | gh CLI 从安装到推送 |
| [Python 服务器搭建](docs/python-http-server.md) | 一行命令搭 HTTP 服务器 |
| [Cloudflare 域名指南](docs/cloudflare-domain.md) | 域名申请、DNS、SSL、安全 |

---

## 📂 项目结构

```
├── index.html                       ← 核心程序
├── docs/
│   ├── development-log.md            ← 开发全记录
│   ├── session-log.md                ← 会话操作日志
│   ├── browser-upload-download.md    ← 浏览器上传下载指南
│   ├── github-setup.md               ← GitHub 搭建指南
│   ├── python-http-server.md         ← Python 服务器搭建
│   └── cloudflare-domain.md          ← Cloudflare 域名指南
└── README.md
```

---

## 🛠 技术栈

| 技术 | 用途 |
|------|------|
| [marked.js](https://marked.js.org) | Markdown 渲染引擎 |
| CSS `prefers-color-scheme` | 自动暗色模式 |
| FileReader API | 读取本地文件 |
| Blob + createObjectURL | 动态文件下载 |
| Python `http.server` | 零配置静态文件服务 |

---

> 📅 **创建日期**：2026-06-27  
> 📅 **最后更新**：2026-06-27  
> 👤 **GitHub**：[wen60912-oss/markdown-browser-viewer](https://github.com/wen60912-oss/markdown-browser-viewer)
