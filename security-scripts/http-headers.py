#!/usr/bin/env python3
"""HTTP 安全头检查器 —— 审计网站的 HTTP 安全响应头配置。

用法:
    python3 http-headers.py <URL>
    python3 http-headers.py https://example.com
    python3 http-headers.py http://154.202.118.123:8080
"""

import sys
import urllib.request
import ssl
from urllib.parse import urlparse

# 安全头检查规则: {header_name: (description, recommended_value, severity)}
SECURITY_HEADERS = {
    "Strict-Transport-Security": (
        "强制 HTTPS 连接，防止降级攻击",
        "max-age=31536000; includeSubDomains",
        "high",
    ),
    "Content-Security-Policy": (
        "限制页面可加载的资源来源，防止 XSS 和数据注入",
        "应包含 default-src 'self' 等指令",
        "high",
    ),
    "X-Content-Type-Options": (
        "防止浏览器 MIME 类型嗅探",
        "nosniff",
        "medium",
    ),
    "X-Frame-Options": (
        "防止页面被嵌入 iframe，抵御点击劫持",
        "DENY 或 SAMEORIGIN",
        "medium",
    ),
    "X-XSS-Protection": (
        "启用浏览器内置 XSS 过滤器（已过时但仍有防护作用）",
        "1; mode=block",
        "low",
    ),
    "Referrer-Policy": (
        "控制 Referer 请求头中发送的信息量",
        "strict-origin-when-cross-origin",
        "low",
    ),
    "Permissions-Policy": (
        "控制浏览器 API 的使用权限（摄像头、麦克风等）",
        "应限制不必要的 API",
        "medium",
    ),
    "Cache-Control": (
        "控制浏览器缓存行为",
        "no-store（敏感页面）",
        "low",
    ),
    "X-Permitted-Cross-Domain-Policies": (
        "控制跨域策略文件加载",
        "none",
        "low",
    ),
}

# 缺失时应显示的额外信息头
INFO_HEADERS = {
    "Server": "泄露服务器软件版本信息",
    "X-Powered-By": "泄露后端技术栈信息",
    "X-AspNet-Version": "泄露 ASP.NET 版本信息",
}


def check_headers(url: str) -> dict:
    """发送请求并提取响应头。"""
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    req = urllib.request.Request(url, method="HEAD")
    req.add_header("User-Agent", "SecurityHeaderChecker/1.0")

    try:
        resp = urllib.request.urlopen(req, context=ctx, timeout=10)
        return {
            "url": url,
            "status": resp.status,
            "headers": dict(resp.headers),
            "error": None,
        }
    except urllib.error.HTTPError as e:
        return {"url": url, "status": e.code, "headers": dict(e.headers), "error": None}
    except urllib.error.URLError as e:
        return {"url": url, "status": 0, "headers": {}, "error": str(e.reason)}
    except Exception as e:
        return {"url": url, "status": 0, "headers": {}, "error": str(e)}


def score(issues: list) -> str:
    """根据问题严重性打分。"""
    highs = sum(1 for i in issues if i["severity"] == "high")
    mediums = sum(1 for i in issues if i["severity"] == "medium")
    if highs == 0 and mediums == 0:
        return "🟢 A+"
    if highs == 0:
        return "🟡 B"
    if highs <= 2:
        return "🟠 C"
    return "🔴 D"


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    url = sys.argv[1]
    if not url.startswith("http"):
        url = "https://" + url

    parsed = urlparse(url)
    print(f"🔍 扫描目标: {parsed.netloc or parsed.path}")
    print(f"📍 完整 URL: {url}")
    print(f"{'─' * 55}")

    result = check_headers(url)

    if result.get("error"):
        print(f"❌ 请求失败: {result['error']}")
        sys.exit(1)

    headers = result["headers"]
    issues = []

    # 检查安全头
    for header, (desc, recommended, severity) in SECURITY_HEADERS.items():
        if header in headers:
            value = headers[header]
            print(f"✅ {header}")
            print(f"   {value[:80]}")
        else:
            print(f"❌ {header}  【缺失】")
            print(f"   {desc}")
            print(f"   建议值: {recommended}")
            issues.append({
                "header": header,
                "severity": severity,
                "desc": desc,
                "recommended": recommended,
            })

    # 检查信息泄露头
    leaks = []
    for header, desc in INFO_HEADERS.items():
        if header in headers:
            leaks.append((header, headers[header], desc))

    print(f"\n{'─' * 55}")
    print(f"📊 HTTP 状态码: {result['status']}")
    print(f"📊 安全评分:    {score(issues)}")
    total = len(SECURITY_HEADERS)
    passed = total - len(issues)
    print(f"📊 通过/总计:   {passed}/{total}")

    if issues:
        print(f"\n⚠️  待修复 ({len(issues)} 项):")
        for i in issues:
            tag = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(i["severity"], "")
            print(f"  {tag} {i['header']}: {i['desc']}")

    if leaks:
        print(f"\n📢 信息泄露:")
        for name, value, desc in leaks:
            print(f"  ⚠️  {name}: {value} ({desc})")


if __name__ == "__main__":
    main()
