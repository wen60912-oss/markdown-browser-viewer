#!/usr/bin/env python3
"""Netflix 内容发现器 —— 用 TMDB 免费 API 查找 Netflix 最新/高分内容。

首次使用前：去 https://www.themoviedb.org/settings/api 免费注册获取 API Key。

用法:
    python3 netflix-finder.py --api-key YOUR_KEY --mode latest
    python3 netflix-finder.py --api-key YOUR_KEY --mode top-rated
    python3 netflix-finder.py --api-key YOUR_KEY --mode anime
    python3 netflix-finder.py --api-key YOUR_KEY --mode genre --genre-id 28  (动作片)
"""

import sys
import json
import urllib.request
import urllib.parse
import urllib.error
import argparse

# Netflix 在 TMDB 中的 provider ID
NETFLIX_PROVIDER_ID = 8

# 常见类型 ID: 28=动作 35=喜剧 18=剧情 27=恐怖 878=科幻 16=动画 10749=爱情
GENRE_MAP = {
    "28": "动作", "12": "冒险", "16": "动画", "35": "喜剧",
    "80": "犯罪", "99": "纪录", "18": "剧情", "10751": "家庭",
    "14": "奇幻", "36": "历史", "27": "恐怖", "10402": "音乐",
    "9648": "悬疑", "10749": "爱情", "878": "科幻", "53": "惊悚",
    "10752": "战争", "37": "西部", "10759": "动作冒险(剧)", "10765": "科幻(剧)",
}

BASE_URL = "https://api.themoviedb.org/3"


def api_request(endpoint: str, api_key: str, params: dict = None) -> dict:
    """调用 TMDB API。"""
    if params is None:
        params = {}
    params["api_key"] = api_key
    params["language"] = "zh-CN"
    params["region"] = "US"
    url = f"{BASE_URL}{endpoint}?{urllib.parse.urlencode(params)}"

    req = urllib.request.Request(url)
    req.add_header("Accept", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        try:
            msg = json.loads(body).get("status_message", body)
        except Exception:
            msg = body
        print(f"❌ API 错误 {e.code}: {msg}")
        sys.exit(1)


def star_rating(vote: float) -> str:
    """把 0-10 评分转为星级。"""
    stars = int(round(vote / 2))
    return "★" * stars + "☆" * (5 - stars)


def print_results(items: list, title: str):
    """格式化输出结果。"""
    print(f"\n{'═' * 65}")
    print(f"  {title}")
    print(f"{'═' * 65}")

    for i, item in enumerate(items[:30], 1):
        name = item.get("name") or item.get("title") or "?"
        date = (item.get("first_air_date") or item.get("release_date") or "?")[:4]
        vote = item.get("vote_average", 0)
        stars = star_rating(vote)
        overview = (item.get("overview") or "暂无简介")[:60]

        media_type = "🎬" if item.get("title") else "📺"
        print(f"  {i:2d}. {media_type} {name} ({date})")
        print(f"      评分: {vote:.1f} {stars}")
        print(f"      简介: {overview}...")


def fetch_netflix_content(api_key: str, mode: str, genre_id: str = None,
                          min_votes: int = 100) -> list:
    """获取 Netflix 内容。"""
    all_items = []

    # 尝试多个 provider 区域的 Netflix ID
    for region in ["US", "HK", "JP", "KR"]:
        if len(all_items) > 0:
            break
        params = {
            "with_watch_providers": str(NETFLIX_PROVIDER_ID),
            "watch_region": region,
            "sort_by": {
                "latest": "primary_release_date.desc",
                "top-rated": "vote_average.desc",
                "popular": "popularity.desc",
            }.get(mode, "popularity.desc"),
            "vote_count.gte": str(min_votes),
            "page": 1,
        }
        if genre_id:
            params["with_genres"] = genre_id

        # 查电影
        data = api_request("/discover/movie", api_key, params)
        all_items.extend(data.get("results", []))

        # 查电视剧
        tv_data = api_request("/discover/tv", api_key, params)
        all_items.extend(tv_data.get("results", []))

    # 去重
    seen = set()
    unique = []
    for item in sorted(all_items, key=lambda x: x.get("popularity", 0), reverse=True):
        key = item.get("id")
        if key not in seen:
            seen.add(key)
            unique.append(item)
    return unique


def mode_anime(api_key: str):
    """专门查找 Netflix 动画/动漫。"""
    all_items = []
    anime_genres = ["16"]  # 动画
    anime_keywords = ["anime", "动漫"]

    for region in ["JP", "US"]:
        for genre in anime_genres:
            params = {
                "with_watch_providers": str(NETFLIX_PROVIDER_ID),
                "watch_region": region,
                "with_genres": genre,
                "sort_by": "popularity.desc",
                "vote_count.gte": "50",
                "page": 1,
            }
            data = api_request("/discover/tv", api_key, params)
            all_items.extend(data.get("results", []))

    seen = set()
    unique = []
    for item in sorted(all_items, key=lambda x: x.get("popularity", 0), reverse=True):
        if item["id"] not in seen:
            seen.add(item["id"])
            unique.append(item)
    return unique


def mode_search(api_key: str, query: str):
    """按关键词搜索。"""
    movie_data = api_request("/search/movie", api_key, {"query": query})
    tv_data = api_request("/search/tv", api_key, {"query": query})
    return movie_data.get("results", []) + tv_data.get("results", [])


def main():
    parser = argparse.ArgumentParser(description="Netflix 内容发现器 (TMDB API)")
    parser.add_argument("--api-key", "-k", help="TMDB API Key (免费注册: themoviedb.org/settings/api)")
    parser.add_argument("--mode", "-m", default="popular",
                        choices=["latest", "top-rated", "popular", "anime", "genre"],
                        help="查找模式")
    parser.add_argument("--genre-id", "-g", help="类型 ID (查 --mode genre 时使用)")
    parser.add_argument("--search", "-s", help="按关键词搜索")
    parser.add_argument("--min-votes", type=int, default=100,
                        help="最低评分人数 (默认 100)")

    args = parser.parse_args()

    if not args.api_key:
        print("请提供 TMDB API Key。")
        print("免费注册: https://www.themoviedb.org/settings/api")
        print(f"\n用法: python3 {sys.argv[0]} --api-key YOUR_KEY --mode latest")
        sys.exit(1)

    print(f"🎬 Netflix 内容发现器")
    print(f"{'─' * 65}")

    if args.search:
        items = mode_search(args.api_key, args.search)
        title = f"🔍 搜索: {args.search}"
    elif args.mode == "anime":
        items = mode_anime(args.api_key)
        title = "🎌 Netflix 动漫/动画 (按热度排序)"
    elif args.mode == "genre":
        if not args.genre_id:
            print("请用 --genre-id 指定类型 ID:")
            for gid, gname in sorted(GENRE_MAP.items()):
                print(f"  {gid}: {gname}")
            sys.exit(1)
        gname = GENRE_MAP.get(args.genre_id, args.genre_id)
        items = fetch_netflix_content(args.api_key, "popular", args.genre_id, args.min_votes)
        title = f"📺 Netflix {gname}类 (按热度排序)"
    else:
        mode_names = {"latest": "最新上映", "top-rated": "高分推荐", "popular": "热门内容"}
        items = fetch_netflix_content(args.api_key, args.mode, min_votes=args.min_votes)
        title = f"📺 Netflix {mode_names.get(args.mode, args.mode)}"

    if not items:
        print("\n没有找到结果。可能 Netflix 在该地区未上线此内容。")
        return

    print_results(items, title)

    # 类型速查
    print(f"\n{'─' * 65}")
    print("💡 类型 ID 速查 (--genre-id):")
    for gid, gname in sorted(GENRE_MAP.items()):
        print(f"  {gid}: {gname}", end="")
        if int(gid) % 4 == 0:
            print()
    print()


if __name__ == "__main__":
    main()
