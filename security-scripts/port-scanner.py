#!/usr/bin/env python3
"""简易 TCP 端口扫描器 —— 检测目标主机的开放端口。

用法:
    python3 port-scanner.py <目标IP> [起始端口] [结束端口]
    python3 port-scanner.py 192.168.1.1
    python3 port-scanner.py 192.168.1.1 1 1024
    python3 port-scanner.py 192.168.1.1 80 443
"""

import socket
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

# 常见端口及其服务名
COMMON_SERVICES = {
    20: "FTP-DATA", 21: "FTP", 22: "SSH", 23: "Telnet",
    25: "SMTP", 53: "DNS", 80: "HTTP", 110: "POP3",
    143: "IMAP", 443: "HTTPS", 445: "SMB", 993: "IMAPS",
    995: "POP3S", 3306: "MySQL", 3389: "RDP", 5432: "PostgreSQL",
    6379: "Redis", 8080: "HTTP-Alt", 8443: "HTTPS-Alt",
    27017: "MongoDB", 5000: "Flask", 3000: "Node/React",
}


def scan_port(target: str, port: int, timeout: float = 1.0) -> tuple[int, bool, str]:
    """扫描单个端口，返回 (端口号, 是否开放, 错误信息)。"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((target, port))
        sock.close()
        if result == 0:
            return (port, True, "")
        return (port, False, "")
    except socket.gaierror:
        return (port, False, "域名解析失败")
    except socket.timeout:
        return (port, False, "超时")
    except Exception as e:
        return (port, False, str(e))


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    target = sys.argv[1]
    start_port = int(sys.argv[2]) if len(sys.argv) > 2 else 1
    end_port = int(sys.argv[3]) if len(sys.argv) > 3 else 1024

    # 解析域名
    try:
        ip = socket.gethostbyname(target)
    except socket.gaierror:
        print(f"❌ 无法解析目标: {target}")
        sys.exit(1)

    print(f"🔍 扫描目标: {target} ({ip})")
    print(f"📡 端口范围: {start_port} - {end_port}")
    print(f"{'─' * 50}")

    start_time = time.time()
    open_ports = []

    # 并发扫描（最大 100 线程）
    with ThreadPoolExecutor(max_workers=100) as executor:
        futures = {
            executor.submit(scan_port, target, port): port
            for port in range(start_port, end_port + 1)
        }
        for future in as_completed(futures):
            port, is_open, error = future.result()
            if is_open:
                service = COMMON_SERVICES.get(port, "?")
                print(f"  ✅ 端口 {port:5d}  开放  ({service})")
                open_ports.append(port)

    elapsed = time.time() - start_time

    print(f"{'─' * 50}")
    print(f"⏱  扫描完成，耗时 {elapsed:.1f} 秒")
    print(f"📊 共扫描 {end_port - start_port + 1} 个端口，{len(open_ports)} 个开放")

    if open_ports:
        print(f"\n⚠️  开放端口列表:")
        for p in open_ports:
            svc = COMMON_SERVICES.get(p, "未知服务")
            print(f"    {p}/tcp ({svc})")


if __name__ == "__main__":
    main()
