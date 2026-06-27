# 浏览器文件上传与下载 —— 完全指南

> 从 File API 到 Blob 下载，前端文件操作的完整实现方案。

---

## 目录

- [1. 文件下载](#1-文件下载)
- [2. 文件上传](#2-文件上传)
- [3. 完整示例：Markdown 查看器的上传功能](#3-完整示例markdown-查看器的上传功能)
- [4. 进阶技巧](#4-进阶技巧)
- [5. 浏览器兼容性](#5-浏览器兼容性)

---

## 1. 文件下载

浏览器下载文件的本质是**触发浏览器的"保存文件"对话框**。

### 1.1 最简单的方法：`<a>` 标签 + `download` 属性

```html
<a href="document.md" download>下载 Markdown 文件</a>
<a href="document.md" download="我的文档.md">自定义文件名下载</a>
```

**限制**：只能下载服务器上已有的文件，不能下载动态生成的内容。

### 1.2 动态内容下载：Blob + createObjectURL

当文件内容是 JS 动态生成的（比如用户在 textarea 中编辑的文本），用这个方法：

```javascript
function downloadFile(content, filename) {
  // 1. 创建 Blob 对象（二进制数据容器）
  const blob = new Blob([content], { type: 'text/markdown;charset=utf-8' });

  // 2. 创建临时 URL
  const url = URL.createObjectURL(blob);

  // 3. 创建隐藏的 <a> 标签触发下载
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;  // 指定下载后的文件名
  document.body.appendChild(a);
  a.click();

  // 4. 清理：移除元素 + 释放 URL
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}

// 使用
downloadFile('# 你好\n\n这是动态生成的 Markdown', 'hello.md');
```

**流程解析**：

```
用户点击下载按钮
    │
    ▼
获取文本内容（如 textarea.value）
    │
    ▼
new Blob([内容], { type: '文件类型' })     ← 把文本变成二进制
    │
    ▼
URL.createObjectURL(blob)                  ← 生成临时链接
    │
    ▼
<a href="临时链接" download="文件名.md">    ← 模拟点击
    │
    ▼
浏览器弹出"保存文件"对话框
    │
    ▼
URL.revokeObjectURL(url)                   ← 释放内存
```

### 1.3 常见 MIME 类型

| 文件类型 | MIME Type |
|----------|-----------|
| Markdown | `text/markdown` |
| 纯文本 | `text/plain` |
| JSON | `application/json` |
| CSV | `text/csv` |
| HTML | `text/html` |
| PDF | `application/pdf` |
| 图片 | `image/png`, `image/jpeg` |

---

## 2. 文件上传

浏览器上传文件的本质是**让用户选择本地文件，然后通过 JS 读取内容**。

### 2.1 最简单的方法：`<input type="file">`

```html
<input type="file" id="fileInput" accept=".md,.txt,.markdown">
```

```javascript
document.getElementById('fileInput').addEventListener('change', function(event) {
  const file = event.target.files[0];  // 获取用户选择的文件
  if (!file) return;

  console.log('文件名:', file.name);
  console.log('文件大小:', file.size, 'bytes');
  console.log('文件类型:', file.type);
});
```

### 2.2 读取文件内容：FileReader API

```javascript
function readFileContent(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();

    reader.onload = function(e) {
      resolve(e.target.result);  // 文件内容
    };

    reader.onerror = function() {
      reject(new Error('文件读取失败'));
    };

    reader.readAsText(file, 'UTF-8');  // 以文本方式读取
  });
}

// 使用
document.getElementById('fileInput').addEventListener('change', async function(event) {
  const file = event.target.files[0];
  if (!file) return;

  try {
    const content = await readFileContent(file);
    console.log('文件内容:', content);
    // 现在可以把 content 显示到 textarea 或做其他处理
  } catch (err) {
    alert('读取失败: ' + err.message);
  }
});
```

**流程解析**：

```
用户点击"选择文件"
    │
    ▼
系统文件选择对话框弹出
    │
    ▼
用户选择一个 .md 文件
    │
    ▼
<input type="file"> 的 change 事件触发
    │
    ▼
event.target.files[0] 获取文件对象
    │
    ▼
new FileReader().readAsText(file)
    │
    ▼
reader.onload 中拿到文件文本内容
    │
    ▼
把内容显示到 textarea / 传给渲染器
```

### 2.3 隐藏的 file input + 按钮触发（更美观）

默认的 `<input type="file">` 样式很难定制，通常的做法是用一个隐藏的 input，用普通按钮触发它：

```html
<button id="uploadBtn">📂 打开本地 .md 文件</button>
<input type="file" id="fileInput" accept=".md,.txt,.markdown" style="display: none;">
```

```javascript
// 点击按钮 = 点击隐藏的 file input
document.getElementById('uploadBtn').addEventListener('click', function() {
  document.getElementById('fileInput').click();
});

// 用户选择文件后处理
document.getElementById('fileInput').addEventListener('change', async function(event) {
  const file = event.target.files[0];
  if (!file) return;

  const content = await readFileContent(file);
  // 将内容放入 textarea 或直接渲染
  document.getElementById('source-view').value = content;
  renderPreview(content);  // 渲染 Markdown
});
```

### 2.4 拖拽上传

```javascript
const dropZone = document.getElementById('drop-zone');

dropZone.addEventListener('dragover', function(e) {
  e.preventDefault();  // 必须阻止默认行为才能触发 drop
  dropZone.classList.add('drag-over');
});

dropZone.addEventListener('dragleave', function() {
  dropZone.classList.remove('drag-over');
});

dropZone.addEventListener('drop', async function(e) {
  e.preventDefault();
  dropZone.classList.remove('drag-over');

  const file = e.dataTransfer.files[0];
  if (!file) return;

  const content = await readFileContent(file);
  // 处理文件内容...
});
```

---

## 3. 完整示例：Markdown 查看器的上传功能

以下是给现有的 Markdown 查看器添加"打开本地文件"功能的关键代码：

### HTML 部分

```html
<div id="toolbar">
  <div class="tabs">
    <button id="btn-preview" class="active">👁 预览</button>
    <button id="btn-source">✏️ 编辑</button>
  </div>
  <div class="actions">
    <button id="btn-upload">📂 打开</button>
    <button id="btn-download">⬇ 下载</button>
  </div>
</div>
<input type="file" id="file-input" accept=".md,.txt,.markdown" style="display:none">
```

### JS 部分

```javascript
const btnUpload = document.getElementById('btn-upload');
const fileInput = document.getElementById('file-input');

// 按钮触发文件选择
btnUpload.addEventListener('click', () => fileInput.click());

// 选择文件后读取并渲染
fileInput.addEventListener('change', async function(event) {
  const file = event.target.files[0];
  if (!file) return;

  try {
    const content = await readFileAsText(file);
    sourceView.value = content;
    updateSourceStatus();
    renderPreview(content);
    // 自动切换到预览模式
    btnPreview.click();
    // 更新页面标题
    document.title = file.name + ' — Markdown 预览';
  } catch (err) {
    alert('读取文件失败：' + err.message);
  }
  // 清除选择，允许重复打开同一个文件
  fileInput.value = '';
});

function readFileAsText(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = e => resolve(e.target.result);
    reader.onerror = () => reject(new Error('读取失败'));
    reader.readAsText(file, 'UTF-8');
  });
}
```

---

## 4. 进阶技巧

### 4.1 多文件上传

```javascript
input.addEventListener('change', async function(event) {
  const files = Array.from(event.target.files);  // 转为数组
  for (const file of files) {
    const content = await readFileAsText(file);
    console.log(file.name, content.length, '字符');
  }
});
```

### 4.2 读取为 Data URL（图片预览）

```javascript
function readFileAsDataURL(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = e => resolve(e.target.result);
    reader.onerror = () => reject(new Error('读取失败'));
    reader.readAsDataURL(file);  // 返回 base64 data URL
  });
}

// 图片预览
const dataUrl = await readFileAsDataURL(imageFile);
document.getElementById('preview').src = dataUrl;
```

### 4.3 大文件分块读取

```javascript
function readLargeFile(file, callback) {
  const chunkSize = 1024 * 1024;  // 1MB
  let offset = 0;

  function readNextChunk() {
    const slice = file.slice(offset, offset + chunkSize);
    const reader = new FileReader();
    reader.onload = function(e) {
      callback(e.target.result);
      offset += chunkSize;
      if (offset < file.size) {
        readNextChunk();  // 继续读下一块
      }
    };
    reader.readAsText(slice);
  }

  readNextChunk();
}
```

### 4.4 文件大小格式化

```javascript
function formatFileSize(bytes) {
  if (bytes < 1024) return bytes + ' B';
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
}
```

---

## 5. 浏览器兼容性

| API | Chrome | Firefox | Safari | Edge |
|-----|--------|---------|--------|------|
| `<a download>` | ✅ | ✅ | ✅ | ✅ |
| `Blob` | ✅ | ✅ | ✅ | ✅ |
| `URL.createObjectURL` | ✅ | ✅ | ✅ | ✅ |
| `FileReader` | ✅ | ✅ | ✅ | ✅ |
| `File API` | ✅ | ✅ | ✅ | ✅ |
| 拖拽上传 | ✅ | ✅ | ✅ | ✅ |

> 以上所有 API 均为 Web 标准，主流浏览器（含移动端）全部支持，无需 polyfill。

---

## 附：用户原始提问记录

### 本次提问

**原文**：
> 如何实现在浏览器上上传和下载文件

**语病修正**：
- 语法基本正确，微调为更自然的表达
- `在浏览器上` → `在浏览器中`（"中" 更常用于功能/软件语境）
- 补充 `功能` 使语义更完整

**修正版**：
> 如何在浏览器中实现文件的上传和下载功能？

**英文翻译**：
> How to implement file upload and download functionality in a browser?

---

> 📅 **编写日期**：2026-06-27
