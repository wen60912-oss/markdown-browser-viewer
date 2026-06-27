# GitHub 命令行（gh CLI）从零到推送 —— 实操全记录

> **场景**：在 Ubuntu 22.04 服务器上，从没有 GitHub CLI 开始，完成安装、认证、初始化仓库、提交文件、推送到 GitHub 的全过程。

---

## 目录

- [1. 环境检查](#1-环境检查)
- [2. 安装 GitHub CLI](#2-安装-github-cli)
- [3. 登录认证](#3-登录认证)
- [4. 初始化本地 Git 仓库](#4-初始化本地-git-仓库)
- [5. 提交文件](#5-提交文件)
- [6. 创建远程仓库并推送](#6-创建远程仓库并推送)
- [7. 验证结果](#7-验证结果)
- [8. 命令速查表](#8-命令速查表)

---

## 1. 环境检查

### 系统版本

```bash
cat /etc/os-release | head -4
```

**输出**：

```
PRETTY_NAME="Ubuntu 22.04 LTS"
NAME="Ubuntu"
VERSION_ID="22.04"
VERSION="22.04 LTS (Jammy Jellyfish)"
```

### 检查 gh 是否已安装

```bash
gh auth status
```

**输出**：

```
/bin/bash: line 1: gh: command not found
```

> ❌ `gh` 未安装，需要先安装。

---

## 2. 安装 GitHub CLI

### 添加 GitHub 官方软件源

```bash
curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg \
  | dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg

echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" \
  > /etc/apt/sources.list.d/github-cli.list
```

**说明**：
- 第一行：下载 GitHub 的 GPG 签名密钥，用于验证软件包来源可信
- 第二行：添加 GitHub CLI 的 APT 软件源地址

### 更新软件索引并安装

```bash
apt-get update
apt-get install -y gh
```

### 验证安装

```bash
gh --version
```

安装成功后 `gh` 命令即可使用。

---

## 3. 登录认证

### 已安装但未登录

```bash
gh auth status
```

**输出**：

```
You are not logged into any GitHub hosts. To log in, run: gh auth login
```

### 启动设备码认证

```bash
gh auth login --hostname github.com --web
```

**输出**：

```
! First copy your one-time code: FB58-2B5C
Open this URL to continue in your web browser: https://github.com/login/device
```

### 用户在浏览器中完成授权

1. 打开 `https://github.com/login/device`
2. 输入一次性验证码 `FB58-2B5C`
3. 确认授权

### 验证登录成功

```bash
gh auth status
```

**输出**：

```
github.com
  ✓ Logged in to github.com account wen60912-oss
  - Active account: true
  - Git operations protocol: https
  - Token scopes: 'gist', 'read:org', 'repo'
```

> ✅ 登录成功！账号：`wen60912-oss`，token 权限包含 `repo`（可以操作仓库）。

### 备选认证方式：Personal Access Token

如果无法使用浏览器认证，也可以通过 Token 登录：

```bash
gh auth login --with-token
```

然后粘贴 GitHub 上生成的 Personal Access Token（需勾选 `repo` 权限）。

---

## 4. 初始化本地 Git 仓库

### 创建项目目录

```bash
mkdir -p /root/markdown-viewer
cp /root/markdown-viewer.html /root/markdown-browser-viewer-development-log.md /root/markdown-viewer/
cd /root/markdown-viewer
```

### 初始化 Git 仓库

```bash
git init
```

**输出**：

```
Initialized empty Git repository in /root/markdown-viewer/.git/
```

### 配置用户信息

```bash
git config user.email "wen60912@users.noreply.github.com"
git config user.name "wen60912-oss"
```

**说明**：每次 `git commit` 都需要记录作者信息，这两行设置了用户名和邮箱。

---

## 5. 提交文件

### 查看文件状态

```bash
git status
```

会列出所有未跟踪的文件。

### 添加所有文件到暂存区

```bash
git add -A
```

**说明**：
- `git add` 把文件加入"暂存区"（staging area），相当于标记"这些文件我要存档"
- `-A` 表示所有文件（新增 + 修改 + 删除）

### 提交（创建存档点）

```bash
git commit -m "feat: Markdown browser viewer with live edit & preview"
```

**输出**：

```
[master (root-commit) 97d17c2] feat: Markdown browser viewer with live edit & preview
 3 files changed, 1039 insertions(+)
 create mode 100644 README.md
 create mode 100644 markdown-browser-viewer-development-log.md
 create mode 100644 markdown-viewer.html
```

**说明**：
- `commit` 创建一个永久存档点
- `-m` 后面是提交信息，描述这次改了什么
- `97d17c2` 是这个存档点的唯一编号（commit hash）
- `root-commit` 表示这是仓库的第一个提交

---

## 6. 创建远程仓库并推送

### 一条命令完成：创建 + 推送

```bash
gh repo create markdown-browser-viewer --source . --public --push
```

**参数说明**：

| 参数 | 含义 |
|------|------|
| `markdown-browser-viewer` | GitHub 仓库名称 |
| `--source .` | 用当前目录作为源代码 |
| `--public` | 公开仓库（任何人都能看） |
| `--push` | 创建后立即推送本地代码 |

### 执行结果

```
https://github.com/wen60912-oss/markdown-browser-viewer
To https://github.com/wen60912-oss/markdown-browser-viewer.git
 * [new branch]      HEAD -> master
Branch 'master' set up to track remote branch 'master' from 'origin'.
```

**说明**：
- 第一行：GitHub 仓库的网页地址
- 第二行开始：本地代码已推送到 GitHub
- `HEAD -> master`：本地 `master` 分支推到了远程 `master` 分支
- 最后一行：本地分支已关联远程分支，以后直接 `git push` 就行

---

## 7. 验证结果

### 浏览器打开仓库

```
https://github.com/wen60912-oss/markdown-browser-viewer
```

可以看到：

```
📁 markdown-browser-viewer
├── README.md
├── markdown-browser-viewer-development-log.md
└── markdown-viewer.html
```

### # GitHub 自动渲染 .md 文件

点击任意 `.md` 文件，GitHub 会自动将其渲染为格式化的网页，无需任何额外配置。

### 查看提交历史

```bash
git log --oneline
```

**输出**：

```
97d17c2 feat: Markdown browser viewer with live edit & preview
```

---

## 8. 命令速查表

### 流程图

```
安装 gh CLI
    │
    ▼
gh auth login ────── 浏览器授权
    │
    ▼
git init ─────────── 初始化本地仓库
    │
    ▼
git add -A ───────── 暂存所有文件
    │
    ▼
git commit -m "..." ─ 创建存档点
    │
    ▼
gh repo create ... ── 创建远程仓库 + 推送
    │
    ▼
GitHub 上可见 ✅
```

### 常用命令一览

| 命令 | 作用 |
|------|------|
| `gh auth status` | 查看登录状态 |
| `gh auth login` | 登录 GitHub 账号 |
| `git init` | 初始化本地 Git 仓库 |
| `git config user.email "..."` | 设置提交者邮箱 |
| `git config user.name "..."` | 设置提交者名字 |
| `git status` | 查看文件变动状态 |
| `git add -A` | 暂存所有文件 |
| `git add 文件名` | 暂存指定文件 |
| `git commit -m "说明"` | 提交（创建存档点） |
| `git log --oneline` | 查看提交历史 |
| `gh repo create 名称 --public --push` | 创建 GitHub 仓库并推送 |
| `git push` | 推送后续修改（首次之后） |
| `git pull` | 拉取远程更新 |

### 后续更新流程

第一次推送后，如果有新改动：

```bash
git add -A
git commit -m "描述你的改动"
git push
```

三行命令，搞定。

---

> 📅 **操作日期**：2026-06-27  
> 👤 **GitHub 账号**：wen60912-oss  
> 📦 **仓库地址**：https://github.com/wen60912-oss/markdown-browser-viewer
