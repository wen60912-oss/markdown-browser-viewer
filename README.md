# Markdown Browser Viewer

自包含的单文件 HTML Markdown 实时预览器。支持手机浏览器编辑、预览、下载，通过公网 IP 或 GitHub Pages 访问。

## 🚀 快速开始

```
python3 -m http.server 8080
# 浏览器打开 http://你的IP:8080/index.html
```

或加载外部 .md 文件：

```
http://你的IP:8080/index.html?file=docs/development-log.md
```

## ✨ 功能

- 📝 GitHub Flavored Markdown 渲染
- 🌓 自动亮/暗主题（跟随系统）
- ✏️ 实时编辑 + 即时预览
- ⬇ 下载为 .md 文件
- 📂 URL 参数加载外部 .md 文件
- 📑 自动生成目录导航

## 📚 文档

| 文档 | 说明 |
|------|------|
| [开发全记录](docs/development-log.md) | 从零到完成的所有过程、问题、决策 |
| [会话操作日志](docs/session-log.md) | 每次操作的详细记录 |
| [GitHub 搭建指南](docs/github-setup.md) | gh CLI 从安装到推送 |
| [Python 服务器搭建](docs/python-http-server.md) | 一行命令搭 HTTP 服务器 |
| [Cloudflare 域名指南](docs/cloudflare-domain.md) | 域名申请、DNS、SSL、安全 |

## 📂 项目结构

```
├── index.html              ← 核心程序
├── docs/
│   ├── development-log.md
│   ├── session-log.md
│   ├── github-setup.md
│   ├── python-http-server.md
│   └── cloudflare-domain.md
└── README.md
```
