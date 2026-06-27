#!/usr/bin/env python3
"""豆瓣 Top 250 + 热门影剧爬虫 —— 无需 API Key，开箱即用。

用法:
    python3 douban-top.py              ← 默认：电影 Top 250
    python3 douban-top.py --type tv    ← 电视剧高分榜
    python3 douban-top.py --type anime ← 动画/动漫高分榜
    python3 douban-top.py --type movie --pages 5  ← 爬取前 5 页
"""

import sys
import json
import urllib.request
import urllib.parse
import argparse
import re
import time
from html.parser import HTMLParser


# 豆瓣各榜单 URL
DOUBAN_URLS = {
    "movie": "https://movie.douban.com/top250",
    "tv": "https://movie.douban.com/tv/#!type=tv&tag=热门&sort=recommend&page_limit=20&page_start=0",
    "anime": "https://movie.douban.com/tv/#!type=tv&tag=日本动画&sort=recommend&page_limit=20&page_start=0",
}

# TV 排行榜 API (JSON 接口，更稳定)
DOUBAN_TV_API = (
    "https://movie.douban.com/j/search_subjects"
    "?type=tv&tag={tag}&sort=rank&page_limit=50&page_start=0"
)


class DoubanParser(HTMLParser):
    """解析豆瓣电影 Top 250 页面。"""

    def __init__(self):
        super().__init__()
        self.items = []
        self.current = {}
        self.in_title = False
        self.in_rating = False
        self.in_quote = False
        self.field = ""

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)

        if tag == "span" and "title" in attrs and attrs.get("class") != "other":
            self.current["title"] = attrs["title"]
            self.in_title = True
        elif tag == "span" and attrs.get("class") == "rating_num":
            self.in_rating = True
        elif tag == "span" and attrs.get("class") == "inq":
            self.in_quote = True

    def handle_data(self, data):
        if self.in_title:
            self.current.setdefault("title2", data.strip())
            self.in_title = False
        elif self.in_rating:
            self.current["rating"] = data.strip()
            self.in_rating = False
        elif self.in_quote:
            self.current["quote"] = data.strip()
            self.in_quote = False
            self.items.append(self.current)
            self.current = {}


def fetch_url(url: str, headers: dict = None) -> str:
    """获取 URL 内容，带重试。"""
    if headers is None:
        headers = {}
    headers.setdefault("User-Agent",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

    req = urllib.request.Request(url, headers=headers)
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                return resp.read().decode("utf-8", errors="replace")
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return ""
            if attempt < 2:
                time.sleep(1)
        except Exception:
            if attempt < 2:
                time.sleep(1)
    return ""


def fetch_movie_top250(pages: int = 2) -> list:
    """爬取电影 Top 250。"""
    items = []
    for page in range(pages):
        url = f"https://movie.douban.com/top250?start={page * 25}"
        print(f"  正在爬取第 {page + 1} 页: {url}")

        html = fetch_url(url)
        if not html:
            break

        parser = DoubanParser()
        parser.feed(html)
        items.extend(parser.items)
        time.sleep(1.5)  # 礼貌延迟

    return items


def fetch_tv_top(tag: str = "热门") -> list:
    """通过 JSON 接口获取电视剧/动画排行榜。"""
    items = []
    total = 0
    while True:
        api_url = DOUBAN_TV_API.format(tag=urllib.parse.quote(tag))
        api_url += f"&page_start={total}"
        print(f"  正在获取: {tag} (offset {total})")

        data = fetch_url(api_url)
        if not data:
            break

        try:
            result = json.loads(data)
        except json.JSONDecodeError:
            break

        subjects = result.get("subjects", [])
        if not subjects:
            break

        for s in subjects:
            items.append({
                "title": s.get("title"),
                "rating": s.get("rate"),
                "url": s.get("url"),
                "cover": s.get("cover"),
            })

        total += len(subjects)
        if total >= 100:
            break
        time.sleep(1.5)

    return items


def star_str(rating: str) -> str:
    """评分转星级。"""
    try:
        r = float(rating)
        full = int(r // 2)
        return "★" * full + "☆" * (5 - full)
    except (ValueError, TypeError):
        return "—"


def print_results(items: list, title: str):
    """格式化输出。"""
    print(f"\n{'═' * 65}")
    print(f"  {title}  (共 {len(items)} 部)")
    print(f"{'═' * 65}")

    for i, item in enumerate(items[:50], 1):
        name = item.get("title", "?")
        rating = item.get("rating", "?")
        stars = star_str(rating)
        quote = item.get("quote", "")

        print(f"  {i:2d}. {name}")
        print(f"      评分: {rating}  {stars}")
        if quote:
            print(f"      热评: {quote}")


def main():
    parser = argparse.ArgumentParser(description="豆瓣高分影视爬虫")
    parser.add_argument("--type", "-t", default="movie",
                        choices=["movie", "tv", "anime"],
                        help="类型: movie(电影) / tv(电视剧) / anime(动画)")
    parser.add_argument("--pages", "-p", type=int, default=2,
                        help="爬取页数 (movie 模式, 每页 25 条)")

    args = parser.parse_args()

    print(f"🎬 豆瓣高分影视")
    print(f"{'─' * 65}")

    if args.type == "movie":
        items = fetch_movie_top250(args.pages)
        title = "🍿 豆瓣电影 Top 250"
    elif args.type == "tv":
        items = fetch_tv_top("热门")
        title = "📺 豆瓣热门电视剧"
    elif args.type == "anime":
        items = fetch_tv_top("日本动画")
        title = "🎌 豆瓣高分日本动画"

    if not items:
        print("\n未获取到数据。可能网络不通或豆瓣限制了当前 IP。")
        sys.exit(1)

    print_results(items, title)
    print()


if __name__ == "__main__":
    main()
