# 浏览器端 Markdown 实时预览器 —— 开发全记录

> **项目概述**：从零开始构建一个可在手机浏览器上实时编辑与预览 Markdown 的自包含 HTML 页面，并通过公网 IP 直接访问。

---

## 目录

- [1. 需求起源](#1-需求起源)
- [2. 方案选型](#2-方案选型)
- [3. 第一版：静态渲染页面](#3-第一版静态渲染页面)
- [4. 本地服务器与局域网访问](#4-本地服务器与局域网访问)
- [5. 公网访问](#5-公网访问)
- [6. 第二版：源码查看与下载](#6-第二版源码查看与下载)
- [7. 第三版：可编辑源码 + 实时重新渲染](#7-第三版可编辑源码--实时重新渲染)
- [8. 最终文件结构](#8-最终文件结构)
- [9. 技术要点总结](#9-技术要点总结)

---

## 1. 需求起源

### 用户原始提问

> 什么方法可以让我在浏览器中看 Markdown 文档？

### 语病修正版

> 有什么方法可以让我在浏览器中预览 Markdown 文档？

**修正说明**：
- `markdown` → `Markdown`（专有名词首字母大写）
- `看` → `预览`（书面语更准确）
- 添加 `有什么` 使句式更完整

### 英文翻译

> What methods can I use to preview Markdown documents in a browser?

### 思考过程

这是一个通用知识问题。需要列举从简单到专业的多种方案，让用户根据自身场景（偶尔查看 vs 经常预览 vs 需要分享）选择合适的方案。回答应该覆盖浏览器扩展、在线工具、编辑器预览、命令行工具、代码托管平台五个维度。

---

## 2. 方案选型

针对"在浏览器中预览 Markdown"这一需求，存在以下几种可行方案：

| 方案 | 适用场景 | 优点 | 缺点 |
|------|---------|------|------|
| 浏览器扩展（Markdown Viewer） | 偶尔查看本地 .md 文件 | 安装即用 | 每个浏览器需单独安装 |
| 在线编辑器（Dillinger.io 等） | 临时粘贴预览 | 无需安装 | 隐私风险，需联网 |
| VS Code 内置预览（Ctrl+Shift+V） | 开发编辑场景 | 实时并排预览 | 需要安装 VS Code |
| 命令行工具（grip / http.server） | 本地服务 | 灵活可控 | 需一定技术基础 |
| GitHub / GitLab | 共享文档 | 天然支持渲染 | 需推送到仓库 |

### 用户进一步明确需求

> 我是想让你创建一个 Markdown 文件，让我可以在手机浏览器上看到渲染后的效果。

**修正版**：我想让你创建一个 Markdown 文件，让我可以在手机浏览器上看到渲染后的效果。

**修正说明**：
- `你创` → `让你创建`（补充被省略的"让"字）
- `mdakdown` → `Markdown`（拼写错误修正）

**英文翻译**：I want you to create a Markdown file so I can view the rendered result in my mobile browser.

### 思考过程

手机浏览器不能直接渲染 `.md` 文件。最实用的方案是创建一个**自包含的 HTML 文件**，内嵌 Markdown 渲染器（通过 CDN 加载 marked.js），将 Markdown 内容也嵌入其中。只需一个 HTTP 服务器即可在手机浏览器中访问。

---

## 3. 第一版：静态渲染页面

### 技术选型

- **渲染引擎**：marked.js（通过 jsDelivr CDN 加载，GitHub Flavored Markdown 兼容）
- **部署方式**：单文件 HTML，零依赖，拿去哪都能用
- **移动端适配**：响应式设计，viewport 元标签 + 弹性布局
- **暗色模式**：`prefers-color-scheme: dark` 自动跟随系统

### 核心功能（第一版）

| 功能 | 实现方式 |
|------|---------|
| Markdown 渲染 | marked.js CDN |
| 自动暗色模式 | CSS `@media (prefers-color-scheme: dark)` |
| 响应式布局 | `max-width: 720px` + viewport |
| 自动目录 | JS 遍历 `<h1>-<h3>` 生成锚点导航 |
| 回到顶部 | 固定定位按钮，滚动超过 300px 显示 |
| 代码块 | 等宽字体 + 独立背景 + 横向滚动 |

### 创建的文件

**文件路径**：`/root/markdown-viewer.html`

### 关键代码结构

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Markdown 预览</title>
  <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
  <style>
    /* CSS 变量定义亮/暗主题 */
    :root { --bg: #fff; --text: #1a1a2e; /* ... */ }
    @media (prefers-color-scheme: dark) {
      :root { --bg: #0f172a; --text: #e2e8f0; /* ... */ }
    }
    /* 响应式布局、代码块、引用块、表格等样式 */
  </style>
</head>
<body>
  <div id="content"></div>
  <script>
    const MARKDOWN = `...`;  // 内嵌 Markdown 内容
    marked.setOptions({ breaks: true, gfm: true });
    document.getElementById('content').innerHTML = marked.parse(MARKDOWN);
    // 自动生成目录、回到顶部等交互逻辑
  </script>
</body>
</html>
```

---

## 4. 本地服务器与局域网访问

### 获取本机 IP

```bash
hostname -I | awk '{print $1}'
```

**输出**：`10.0.72.3`

### 启动 HTTP 服务器

```bash
python3 -m http.server 8080
```

在后台运行，监听 `0.0.0.0:8080`。

### 手机访问方式

确保手机与电脑连接同一 WiFi，浏览器打开：

```
http://10.0.72.3:8080/markdown-viewer.html
```

---

## 5. 公网访问

### 用户需求

> 公网地址

**修正版**：用公网地址访问。

**英文翻译**：Access it via a public IP address.

### 检查公网环境

#### 检查可用工具和公网 IP

```bash
which ngrok cloudflared localtunnel ssh npx 2>/dev/null
curl -s ifconfig.me 2>/dev/null
```

**结果**：
- 可用工具：`cloudflared`、`ssh`、`npx`
- 公网 IP：`154.202.118.123`

#### 尝试 localtunnel（被用户拒绝）

```bash
npx localtunnel --port 8080
```

用户回复：**"不要域名"**——要求直接使用裸 IP，不通过隧道服务生成的域名。

### 用户需求澄清

> 不要域名

**修正版**：不需要域名，直接用 IP 访问即可。

**英文翻译**：No domain names — just use the raw IP.

### 检查防火墙和端口可达性

```bash
ufw status          # 检查系统防火墙
iptables -L INPUT -n # 检查 iptables 规则
ss -tlnp | grep 8080 # 检查端口监听状态
```

**结果**：
- `ufw`：`inactive`（防火墙未启用）
- `iptables` INPUT 策略：`ACCEPT`，仅有 fail2ban SSH 规则
- 端口 8080：`LISTEN` 在 `0.0.0.0:8080`（所有网络接口可访问）

### 验证服务正常

```bash
curl -sI http://localhost:8080/markdown-viewer.html | head -5
```

**输出**：

```
HTTP/1.0 200 OK
Server: SimpleHTTP/0.6 Python/3.10.12
Content-type: text/html
Content-Length: 7978
```

### 最终公网地址

```
http://154.202.118.123:8080/markdown-viewer.html
```

> ⚠️ **注意**：如果使用云服务器（阿里云、腾讯云、AWS 等），还需在云控制台的**安全组**中放行 TCP `8080` 端口。系统层面的防火墙已确认关闭，但云平台通常还有一层独立的安全组规则。

---

## 6. 第二版：源码查看与下载

### 用户需求

> 文档最上面添加查看 Markdown 源码的功能，包含下载 Markdown 源码。

**修正版**：在文档顶部添加查看 Markdown 源码的功能，并支持下载为 .md 文件。

**修正说明**：
- 补充 `在……顶部` 的方位描述
- `markdown` → `Markdown`
- 添加 `支持` 使语义更连贯

**英文翻译**：Add a feature at the top of the document to view the Markdown source code, with the ability to download it as a .md file.

### 技术设计

新增**固定工具栏**（sticky 定位），包含：
- 左侧标签切换：`预览` / `源码`
- 右侧操作按钮：`下载 .md`

| 组件 | 实现 |
|------|------|
| 工具栏 | `position: sticky; top: 8px` + `backdrop-filter: blur(8px)` |
| 预览/源码切换 | CSS class 切换 `#content.hidden` / `#source-view.visible` |
| 下载按钮 | `Blob` → `URL.createObjectURL` → 临时 `<a>` 触发下载 |

### 遇到的问题：Edit 工具匹配失败

在使用 `Edit` 工具修改 CSS 部分时，连续两次报错：

```
String to replace not found in file.
```

**原因分析**：`Edit` 工具对 `old_string` 的匹配非常严格，缩进字符（空格 vs Tab）和空白符的细微差异都会导致匹配失败。虽然肉眼看上去一致，但文件中实际使用的是空格缩进，而编辑时粘贴的字符串可能混入了 Tab。

**解决方案**：改用 `Write` 工具**整体重写文件**。在变更范围较大时，整体重写比多次 `Edit` 更可靠。`Write` 不存在匹配问题，可以一次性完成所有修改。

### 新增代码

**工具栏 HTML**：

```html
<div id="toolbar">
  <div class="tabs">
    <button id="btn-preview" class="active">👁 预览</button>
    <button id="btn-source">📄 源码</button>
  </div>
  <button id="btn-download">⬇ 下载 .md</button>
</div>
<pre id="source-view"></pre>  <!-- 源码展示区 -->
```

**工具栏 CSS**：

```css
#toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  position: sticky; top: 8px; z-index: 100;
  backdrop-filter: blur(8px);
  /* ... */
}
```

**下载逻辑（JS）**：

```javascript
btnDownload.addEventListener('click', function() {
  const blob = new Blob([MARKDOWN], { type: 'text/markdown;charset=utf-8' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = 'document.md';
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
});
```

### 验证

```bash
curl -sI http://localhost:8080/markdown-viewer.html | head -5
```

文件从 7.9KB 增长到 11.5KB，服务正常返回 200。

---

## 7. 第三版：可编辑源码 + 实时重新渲染

### 用户需求

> 查看 Markdown 源码后，里面的源码可以修改和添加。

**修正版**：查看 Markdown 源码后，可以编辑里面的内容，切回预览时能实时看到修改效果。

**修正说明**：
- `修改和添加` → `编辑内容`（更简洁的表述）
- 补充预期行为：`切回预览时能实时看到修改效果`

**英文翻译**：After viewing the Markdown source, the content should be editable, and switching back to preview should show the updated rendering in real time.

### 技术变更

| 项目 | 第二版 | 第三版 |
|------|--------|--------|
| 源码区元素 | `<pre>`（只读） | `<textarea>`（可编辑） |
| 按钮文案 | 📄 源码 | ✏️ 编辑 |
| 切换行为 | 仅切换视图 | 切换时重新渲染 |
| 下载数据源 | `MARKDOWN` 常量 | `textarea.value`（最新编辑内容） |
| 状态反馈 | 无 | 行数 / 字符数实时显示 |

### 关键代码变更

**HTML**：

```html
<!-- 之前：只读展示 -->
<pre id="source-view"></pre>

<!-- 之后：可编辑文本框 -->
<textarea id="source-view" spellcheck="false"></textarea>
<div id="source-status"></div>  <!-- 新增状态栏 -->
```

**CSS 新增**：

```css
#source-view {
  width: 100%;
  min-height: 70vh;
  resize: vertical;
  outline: none;
  -webkit-appearance: none;
}
#source-view:focus {
  border-color: var(--link);
  box-shadow: 0 0 0 2px rgba(37,99,235,0.15);
}
```

**JS 核心逻辑 —— 提取重新渲染函数**：

```javascript
// 将渲染逻辑提取为可复用函数
function renderPreview(mdText) {
  try {
    const html = marked.parse(mdText);
    // 生成目录 + 注入内容
    content.innerHTML = tocHTML + temp.innerHTML;
  } catch (e) {
    content.innerHTML = '<p style="color:#ef4444;">❌ 渲染失败：' + e.message + '</p>';
  }
}

// 切换到预览时，用编辑区最新内容重新渲染
btnPreview.addEventListener('click', function() {
  renderPreview(sourceView.value);  // 关键：用 textarea 当前值
  // ...
});

// 下载也使用最新内容
btnDownload.addEventListener('click', function() {
  var md = sourceView.value;  // 从 textarea 取值，而非 MARKDOWN 常量
  // ...
});
```

**行数/字符数实时统计**：

```javascript
sourceView.addEventListener('input', function() {
  const lines = sourceView.value.split('\n').length;
  const chars = sourceView.value.length;
  sourceStatus.textContent = lines + ' 行 | ' + chars + ' 字符';
});
```

### 验证

```bash
curl -sI http://localhost:8080/markdown-viewer.html | head -5
```

文件增长到 12.6KB，服务正常。

---

## 8. 最终文件结构

```
/root/markdown-viewer.html    （12.6KB，单文件自包含）
```

### 文件内部结构

```
markdown-viewer.html
├── <head>
│   ├── <meta> viewport 移动端适配
│   ├── <script> marked.js CDN
│   └── <style>
│       ├── CSS 变量（亮/暗主题）
│       ├── 基础排版样式（标题、段落、链接、代码）
│       ├── 特殊元素样式（引用块、表格、图片）
│       ├── #toc 目录样式
│       ├── #back-to-top 回到顶部按钮
│       ├── #toolbar 固定工具栏
│       ├── #source-view 可编辑源码区
│       └── #source-status 状态栏
├── <body>
│   ├── #toolbar（👁预览 | ✏️编辑 | ⬇下载）
│   ├── #content（渲染后的 Markdown）
│   ├── #source-view（<textarea> 可编辑源码）
│   ├── #source-status（行数/字符数）
│   └── #back-to-top（回到顶部按钮）
└── <script>
    ├── MARKDOWN 常量（默认内容）
    ├── renderPreview() 渲染函数
    ├── 预览/编辑切换逻辑
    ├── 下载逻辑（Blob + createObjectURL）
    ├── 行数/字符数实时统计
    └── 回到顶部交互
```

### 功能清单

| 功能 | 状态 |
|------|------|
| GitHub Flavored Markdown 渲染 | ✅ |
| 自动亮/暗主题 | ✅ |
| 响应式移动端布局 | ✅ |
| 自动目录（H1-H3 锚点导航） | ✅ |
| 固定工具栏（sticky 吸顶） | ✅ |
| 预览 / 编辑模式切换 | ✅ |
| 可编辑源码区（`<textarea>`） | ✅ |
| 行数 / 字符数实时统计 | ✅ |
| 下载为 .md 文件 | ✅ |
| 回到顶部按钮 | ✅ |
| 渲染异常捕获与友好提示 | ✅ |
| 代码块横向滚动 | ✅ |

---

## 9. 技术要点总结

### 用到的命令一览

| 命令 | 用途 |
|------|------|
| `python3 -m http.server 8080` | 启动 HTTP 静态文件服务器 |
| `hostname -I \| awk '{print $1}'` | 获取本机局域网 IP |
| `curl -s ifconfig.me` | 获取公网 IP |
| `ufw status` | 检查系统防火墙状态 |
| `iptables -L INPUT -n` | 检查 iptables 规则 |
| `ss -tlnp \| grep 8080` | 检查端口监听状态 |
| `curl -sI http://localhost:8080/markdown-viewer.html` | 验证 HTTP 服务可用性 |
| `sed -n '151,158p' file \| cat -A` | 查看文件中不可见字符（调试 Edit 匹配失败） |

### 遇到的问题与解决方法

| 问题 | 原因 | 解决方法 |
|------|------|---------|
| `Edit` 工具匹配 `old_string` 失败 | 缩进字符差异（空格 vs Tab），肉眼不可见 | 改用 `Write` 整体重写文件 |
| 云服务器公网 IP 无法访问 | 云平台安全组可能拦截非标准端口 | 提示用户在云控制台放行 TCP 8080 |
| 手机浏览器显示效果不佳 | 默认 viewport 缩放问题 | 添加 `<meta name="viewport" content="width=device-width, initial-scale=1.0">` |

### 设计决策

1. **为什么用单文件 HTML 而不是分离的 .md + .html？**  
   → 手机场景简化部署，只需一个 HTTP 服务器承载一个文件，降低复杂度。

2. **为什么用 `<textarea>` 而不是 contenteditable？**  
   → Markdown 本质是纯文本，`<textarea>` 天然支持等宽字体、无格式粘贴、不会意外混入富文本格式。

3. **为什么下载按钮取 textarea 值而不是 MARKDOWN 常量？**  
   → 用户编辑后的内容才是真正要保存的，MARKDOWN 只是初始默认值。

4. **为什么工具栏用 sticky 而不是 fixed？**  
   → `sticky` 在文档流内占位，不会遮挡内容，向下滚动时才吸附顶部。

---

> 📅 **开发日期**：2026-06-27  
> 🖥 **服务器**：Python SimpleHTTP/0.6  
> 📡 **公网地址**：`http://154.202.118.123:8080/markdown-viewer.html`
