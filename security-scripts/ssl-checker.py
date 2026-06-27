#!/usr/bin/env python3
"""SSL/TLS 证书检查器 —— 检查 HTTPS 站点的证书信息和到期时间。

用法:
    python3 ssl-checker.py <域名> [端口]
    python3 ssl-checker.py github.com
    python3 ssl-checker.py example.com 8443
"""

import ssl
import socket
import sys
from datetime import datetime, timezone


def get_cert_info(host: str, port: int = 443, timeout: float = 5.0) -> dict:
    """获取 SSL 证书信息。"""
    ctx = ssl.create_default_context()
    # 允许检查自签名证书
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(timeout)

    try:
        with ctx.wrap_socket(sock, server_hostname=host) as ssock:
            ssock.settimeout(timeout)
            cert = ssock.getpeercert()
            cipher = ssock.cipher()
            version = ssock.version()

        return {
            "host": host,
            "port": port,
            "cert": cert,
            "cipher": cipher,
            "tls_version": version,
            "error": None,
        }
    except socket.gaierror:
        return {"error": f"无法解析域名: {host}"}
    except socket.timeout:
        return {"error": f"连接超时 ({timeout}秒)"}
    except ConnectionRefusedError:
        return {"error": f"端口 {port} 连接被拒绝"}
    except ssl.SSLError as e:
        return {"error": f"SSL 错误: {e.reason if hasattr(e, 'reason') else str(e)}"}
    except Exception as e:
        return {"error": str(e)}


def format_date(date_str: str) -> str:
    """格式化日期字符串。"""
    dt = datetime.strptime(date_str, "%b %d %H:%M:%S %Y %Z")
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def days_until(date_str: str) -> int:
    """计算距离到期还有多少天。"""
    dt = datetime.strptime(date_str, "%b %d %H:%M:%S %Y %Z").replace(tzinfo=timezone.utc)
    now = datetime.now(timezone.utc)
    return (dt - now).days


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    host = sys.argv[1]
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 443

    result = get_cert_info(host, port)

    if result.get("error"):
        print(f"❌ {result['error']}")
        sys.exit(1)

    cert = result["cert"]
    subject = dict(x[0] for x in cert.get("subject", []))
    issuer = dict(x[0] for x in cert.get("issuer", []))

    not_before = cert.get("notBefore", "")
    not_after = cert.get("notAfter", "")
    remaining = days_until(not_after)

    print(f"🔒 SSL/TLS 证书信息")
    print(f"{'─' * 50}")
    print(f"📍 站点:        {host}:{port}")
    print(f"🔐 TLS 版本:    {result['tls_version']}")
    print(f"🔑 加密套件:    {result['cipher'][0]}")
    print(f"")
    print(f"📛 颁发给:      {subject.get('commonName', '?')}")
    print(f"🏢 颁发者:      {issuer.get('organizationName', issuer.get('commonName', '?'))}")
    print(f"")
    print(f"📅 生效时间:    {format_date(not_before)}")
    print(f"📅 到期时间:    {format_date(not_after)}")

    # 到期状态
    if remaining < 0:
        print(f"⏰ 剩余天数:    ⚠️  已过期 {abs(remaining)} 天！")
    elif remaining < 7:
        print(f"⏰ 剩余天数:    🚨 {remaining} 天（即将过期！）")
    elif remaining < 30:
        print(f"⏰ 剩余天数:    ⚠️  {remaining} 天（建议尽快续期）")
    else:
        print(f"⏰ 剩余天数:    ✅ {remaining} 天")

    # SAN（备用域名）
    san = cert.get("subjectAltName", [])
    if san:
        print(f"")
        print(f"🌐 备用域名 (SAN):")
        for entry in san:
            print(f"    {entry[1]}")


if __name__ == "__main__":
    main()
