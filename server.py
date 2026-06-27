#!/usr/bin/env python3
"""Markdown 浏览器查看器后端服务 —— 纯标准库实现。

功能:
    GET  /                    → 返回查看器页面
    GET  /api/files           → 列出所有 .md 文件
    POST /api/files           → 保存 .md 文件
    GET  /api/files/<name>    → 读取单个 .md 文件
    DELETE /api/files/<name>  → 删除 .md 文件
    GET  /<path>              → 静态文件服务

用法:
    python3 server.py                  # 默认 8080 端口
    python3 server.py --port 9000      # 指定端口
    python3 server.py --dir ./my_docs  # 指定文件存储目录
"""

import os
import sys
import json
import time
import hashlib
import argparse
import cgi
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler

# 默认配置
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "markdown-files")
STATIC_DIR = os.path.dirname(os.path.abspath(__file__))


def ensure_dir(path: str):
    """确保目录存在。"""
    if not os.path.isdir(path):
        os.makedirs(path)


def list_md_files(directory: str) -> list:
    """列出目录下的 .md 文件。"""
    files = []
    if not os.path.isdir(directory):
        return files
    for name in sorted(os.listdir(directory)):
        if name.endswith(".md") and os.path.isfile(os.path.join(directory, name)):
            stat = os.stat(os.path.join(directory, name))
            files.append({
                "name": name,
                "size": stat.st_size,
                "modified": time.strftime("%Y-%m-%d %H:%M:%S",
                                          time.localtime(stat.st_mtime)),
            })
    return files


def json_response(handler, data, status=200):
    """发送 JSON 响应。"""
    body = json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Content-Length", len(body))
    handler.send_header("Access-Control-Allow-Origin", "*")
    handler.end_headers()
    handler.wfile.write(body)


def error_response(handler, status, message):
    """发送错误响应。"""
    json_response(handler, {"error": message}, status)


class MarkdownServer(BaseHTTPRequestHandler):
    """HTTP 请求处理器。"""

    data_dir = DATA_DIR
    static_dir = STATIC_DIR

    # ===== 路由分发 =====

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        # API 路由
        if path == "/api/files":
            return self.api_list_files()
        if path.startswith("/api/files/"):
            name = urllib.parse.unquote(path[len("/api/files/"):])
            return self.api_get_file(name)

        # 静态文件
        return self.serve_static(path)

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        if path == "/api/files":
            return self.api_save_file()

        error_response(self, 404, "接口不存在")

    def do_DELETE(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        if path.startswith("/api/files/"):
            name = urllib.parse.unquote(path[len("/api/files/"):])
            return self.api_delete_file(name)

        error_response(self, 404, "接口不存在")

    def do_OPTIONS(self):
        """CORS 预检请求。"""
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    # ===== API 实现 =====

    def api_list_files(self):
        """列出所有 .md 文件。"""
        files = list_md_files(self.data_dir)
        json_response(self, {"files": files, "total": len(files)})

    def api_get_file(self, name: str):
        """读取单个 .md 文件。"""
        filepath = os.path.join(self.data_dir, name)
        # 安全检查：禁止路径穿越
        real = os.path.realpath(filepath)
        if not real.startswith(os.path.realpath(self.data_dir)):
            return error_response(self, 403, "禁止访问")

        if not os.path.isfile(filepath):
            return error_response(self, 404, f"文件不存在: {name}")

        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
            json_response(self, {"name": name, "content": content})
        except Exception as e:
            error_response(self, 500, f"读取失败: {e}")

    def api_save_file(self):
        """保存 .md 文件（从 POST body 或 multipart 表单）。"""
        content_type = self.headers.get("Content-Type", "")

        name = None
        content = None

        if "multipart/form-data" in content_type:
            # 处理文件上传
            form = cgi.FieldStorage(
                fp=self.rfile,
                headers=self.headers,
                environ={"REQUEST_METHOD": "POST"}
            )
            if "file" in form:
                item = form["file"]
                name = item.filename
                content = item.file.read().decode("utf-8", errors="replace")
            elif "content" in form:
                content = form.getvalue("content", "")
                name = form.getvalue("name", "untitled.md")
        elif "application/json" in content_type:
            # JSON body
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length)
            try:
                data = json.loads(body)
                name = data.get("name", "untitled.md")
                content = data.get("content", "")
            except json.JSONDecodeError:
                return error_response(self, 400, "JSON 格式错误")
        else:
            return error_response(self, 400, "不支持的 Content-Type")

        if not name or content is None:
            return error_response(self, 400, "缺少 name 或 content")

        # 安全检查
        if not name.endswith(".md"):
            name += ".md"
        # 防止路径穿越
        safe_name = os.path.basename(name)
        if not safe_name or safe_name in (".", ".."):
            return error_response(self, 400, "无效的文件名")

        ensure_dir(self.data_dir)
        filepath = os.path.join(self.data_dir, safe_name)

        try:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)
            json_response(self, {
                "ok": True,
                "name": safe_name,
                "path": filepath,
                "size": len(content.encode("utf-8")),
            })
        except Exception as e:
            error_response(self, 500, f"保存失败: {e}")

    def api_delete_file(self, name: str):
        """删除 .md 文件。"""
        filepath = os.path.join(self.data_dir, name)
        real = os.path.realpath(filepath)
        if not real.startswith(os.path.realpath(self.data_dir)):
            return error_response(self, 403, "禁止访问")

        if not os.path.isfile(filepath):
            return error_response(self, 404, f"文件不存在: {name}")

        try:
            os.remove(filepath)
            json_response(self, {"ok": True, "deleted": name})
        except Exception as e:
            error_response(self, 500, f"删除失败: {e}")

    # ===== 静态文件 =====

    def serve_static(self, path: str):
        """提供静态文件服务。"""
        if path == "/":
            path = "/index.html"

        # 去掉开头的 /
        rel = path.lstrip("/")
        filepath = os.path.join(self.static_dir, rel)

        # 安全检查
        real = os.path.realpath(filepath)
        if not real.startswith(os.path.realpath(self.static_dir)):
            self.send_error(403)
            return

        if not os.path.isfile(filepath):
            self.send_error(404)
            return

        # MIME 类型
        ext = os.path.splitext(filepath)[1].lower()
        mime_types = {
            ".html": "text/html; charset=utf-8",
            ".css": "text/css",
            ".js": "application/javascript",
            ".json": "application/json",
            ".md": "text/markdown; charset=utf-8",
            ".txt": "text/plain; charset=utf-8",
            ".png": "image/png",
            ".jpg": "image/jpeg",
            ".svg": "image/svg+xml",
        }
        content_type = mime_types.get(ext, "application/octet-stream")

        try:
            with open(filepath, "rb") as f:
                data = f.read()
            self.send_response(200)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", len(data))
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(data)
        except Exception:
            self.send_error(500)

    def log_message(self, format, *args):
        """自定义日志格式。"""
        print(f"[{time.strftime('%H:%M:%S')}] {args[0]}")


def main():
    parser = argparse.ArgumentParser(description="Markdown 查看器后端服务")
    parser.add_argument("--port", "-p", type=int, default=8080, help="监听端口 (默认 8080)")
    parser.add_argument("--dir", "-d", default=None, help="Markdown 文件存储目录")
    args = parser.parse_args()

    # 配置
    data_dir = args.dir or os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "markdown-files"
    )
    ensure_dir(data_dir)

    MarkdownServer.data_dir = data_dir
    MarkdownServer.static_dir = os.path.dirname(os.path.abspath(__file__))

    server = HTTPServer(("0.0.0.0", args.port), MarkdownServer)

    print(f"🚀 Markdown 查看器后端服务")
    print(f"{'─' * 50}")
    print(f"📍 地址:        http://0.0.0.0:{args.port}")
    print(f"📂 文件目录:    {data_dir}")
    print(f"📂 静态文件:    {MarkdownServer.static_dir}")
    print(f"")
    print(f"📡 API 端点:")
    print(f"   GET  /api/files            列出所有 .md 文件")
    print(f"   GET  /api/files/<name>     读取文件内容")
    print(f"   POST /api/files            保存/上传文件")
    print(f"   DELETE /api/files/<name>   删除文件")
    print(f"{'─' * 50}")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n⏹  服务已停止")
        server.server_close()


if __name__ == "__main__":
    main()
