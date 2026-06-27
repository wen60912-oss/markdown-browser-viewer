# 🎬 影视内容发现工具

查找 Netflix 最新/高分内容和豆瓣 Top 250 的 Python 小工具。

> 📅 最后更新：2026-06-27  
> ⚠️ 仅用于个人学习和内容发现

---

## 📦 脚本清单

| 脚本 | 数据源 | 需要 API Key | 功能 |
|------|--------|:--:|------|
| `netflix-finder.py` | TMDB 免费 API | ✅ | Netflix 最新/高分/按类型/动漫 |
| `douban-top.py` | 豆瓣公开页面 | ❌ | 电影 Top 250 + 热门剧集 + 动画 |

---

## 1. Netflix 内容发现器

### 获取 API Key（1 分钟，免费）

1. 打开 https://www.themoviedb.org/signup 注册
2. 登录后 → 设置 → API → 申请 API Key
3. 复制 key

### 使用

```bash
# 最新上映
python3 netflix-finder.py --api-key YOUR_KEY --mode latest

# 高分推荐（评分最高）
python3 netflix-finder.py --api-key YOUR_KEY --mode top-rated

# 热门内容
python3 netflix-finder.py --api-key YOUR_KEY --mode popular

# 动漫专场
python3 netflix-finder.py --api-key YOUR_KEY --mode anime

# 按类型筛选（28=动作, 35=喜剧, 878=科幻）
python3 netflix-finder.py --api-key YOUR_KEY --mode genre --genre-id 28

# 关键词搜索
python3 netflix-finder.py --api-key YOUR_KEY --search "怪奇物语"
```

### 特点
- ✅ 合法：使用 TMDB 公开 API，不违反 ToS
- ✅ 免费：TMDB API 免费额度足够个人使用
- ✅ 中文支持：返回中文标题和简介

---

## 2. 豆瓣高分爬虫

### 使用

```bash
# 电影 Top 250
python3 douban-top.py

# 热门电视剧
python3 douban-top.py --type tv

# 高分日本动画
python3 douban-top.py --type anime
```

### 特点
- ✅ 无需 API Key
- ✅ 自动延迟请求，避免被封
- ⚠️ 豆瓣有反爬机制，如频繁请求需换 IP

---

## 为什么不用 Selenium 爬 Netflix

| 方案 | 可行性 |
|------|--------|
| Netflix 直接爬 | ❌ 登录墙 + 反爬 + 违法 DMCA |
| TMDB API | ✅ 合法、免费、稳定、支持中文 |
| 豆瓣爬虫 | ✅ 公开页面，无登录，低频可用 |

> TMDB 收录了 Netflix 在全球各地区的完整内容库，比 Netflix 自己的页面更适合程序化查找。
