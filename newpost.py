#!/usr/bin/env python3
"""
小子博客 - 新增文章工具
用法：
  python3 newpost.py "文章标题" "YYYY-MM-DD" "分类" "标签1,标签2" "tag3,tag4"
  
示例：
  python3 newpost.py "我的新文章" "2026-07-15" "心情随笔" "生活,感悟" "随想"
"""

import json, os, re, sys
from datetime import date

def slugify(text):
    """将中文标题转为拼音式文件名"""
    import unicodedata
    # 保留中文和字母数字，其余转-
    s = text.strip().lower()
    s = re.sub(r'[^\w\u4e00-\u9fff]+', '-', s)
    s = s.strip('-')
    return s

def make_html(title, date_str, category, tags_list, content_lines):
    """生成文章HTML"""
    # 摘要 = 第一段
    excerpt = content_lines[0] if content_lines else title
    
    tags_html = ''.join(f'<span class="tag">{t}</span>' for t in tags_list)
    
    # 内容段落
    paragraphs = '\n        '.join(f'<p>{line}</p>' for line in content_lines if line.strip())
    
    filename = slugify(title) + '.html'
    
    html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="{excerpt}">
    <title>{title} · 小子博客</title>
    <link rel="stylesheet" href="style.css">
    <link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>✍</text></svg>">
</head>
<body>
    <header class="site-header">
        <div class="header-bg"></div>
        <div class="header-content container">
            <div class="header-avatar">
                <img src="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><rect width='100' height='100' rx='50' fill='%23df846c'/><text x='50' y='68' text-anchor='middle' font-size='48' fill='white' font-family='serif'>小</text></svg>" alt="头像" class="avatar-img">
            </div>
            <h1 class="site-title"><a href="/">小子</a></h1>
            <p class="site-desc">记录思考，分享创造</p>
            <nav class="header-nav">
                <a href="/#about">关于</a>
                <a href="/#blog">随笔</a>
                <a href="/#contact">联系</a>
            </nav>
        </div>
    </header>

    <div class="container main-wrap">
        <article class="post-card">
            <time class="post-date">{date_str}</time>
            <h1 class="post-title">{title}</h1>
            <div class="entry-content">
        {paragraphs}
            </div>
            <div class="post-meta">
                <span class="post-cat">{category}</span>
                {tags_html}
            </div>
        </article>
        <nav class="post-nav">
            <a href="/" class="back-home">← 返回首页</a>
        </nav>
    </div>

    <footer class="site-footer">
        <div class="container">
            <p>&copy; 2025 小子 · Powered by Cloudflare Pages</p>
        </div>
    </footer>

    <div id="scrolltop" title="回到顶部">↑</div>
    <script src="script.js"></script>
</body>
</html>'''
    return filename, html, excerpt

def update_articles_json(filename, title, date_str, category, tags_list, excerpt):
    """更新articles.json"""
    json_path = 'articles.json'
    if os.path.exists(json_path):
        with open(json_path, 'r', encoding='utf-8') as f:
            articles = json.load(f)
    else:
        articles = []
    
    # 检查是否已存在
    for a in articles:
        if a['file'] == filename:
            print(f"⚠️ 文章 {filename} 已存在，跳过articles.json更新")
            return
    
    articles.append({
        "file": filename,
        "title": title,
        "date": date_str,
        "category": category,
        "tags": tags_list,
        "excerpt": excerpt[:200]
    })
    
    # 按日期降序排序
    articles.sort(key=lambda x: x.get('date', ''), reverse=True)
    
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(articles, f, ensure_ascii=False, indent=2)
    print(f"✅ articles.json 已更新 (共{len(articles)}篇)")

def update_index_html(filename, title, date_str, category, excerpt):
    """在index.html的随笔区插入新文章"""
    index_path = 'index.html'
    with open(index_path, 'r', encoding='utf-8') as f:
        html = f.read()
    
    # 寻找第一个 post-item 插入
    new_item = f'''                <article class="post-item">
                    <time class="post-date">{date_str}</time>
                    <h3><a href="{filename}">{title}</a></h3>
                    <p>{excerpt[:150]}</p>
                    <span class="post-cat">{category}</span>
                </article>
                <article class="post-item">'''
    
    # 在第一个 post-item 之后插入
    if '<article class="post-item">' in html:
        html = html.replace('<article class="post-item">', new_item, 1)
        with open(index_path, 'w', encoding='utf-8') as f:
            f.write(html)
        print(f"✅ index.html 已更新")
    else:
        print("⚠️ 未找到 post-item 标记，请手动更新 index.html")

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("""
使用方法:
  python3 newpost.py "文章标题" "YYYY-MM-DD" "分类" "标签1,标签2"
  
示例:
  python3 newpost.py "我的新博客" "2026-07-15" "心情随笔" "生活,感悟"
  python3 newpost.py "一首好歌" "2026-07-14" "音乐分享" "音乐,民谣"
  
交互模式:
  直接运行 python3 newpost.py 会提示你输入
""")
        # 交互模式
        title = input("文章标题: ").strip()
        date_str = input("日期 (YYYY-MM-DD, 回车默认今天): ").strip()
        if not date_str:
            date_str = str(date.today())
        category = input("分类 (心情随笔/音乐分享): ").strip()
        if not category:
            category = "心情随笔"
        tags_input = input("标签 (逗号分隔): ").strip()
        tags_list = [t.strip() for t in tags_input.split(',') if t.strip()]
        print("请输入文章正文 (空行结束):")
        content_lines = []
        while True:
            line = input()
            if line == '':
                break
            content_lines.append(line)
        if not content_lines:
            content_lines = ["新文章内容待补充。"]
    else:
        title = sys.argv[1]
        date_str = sys.argv[2] if len(sys.argv) > 2 else str(date.today())
        category = sys.argv[3] if len(sys.argv) > 3 else "心情随笔"
        tags_list = []
        if len(sys.argv) > 4:
            for t in sys.argv[4:]:
                tags_list.extend([x.strip() for x in t.split(',')])
        print("请输入文章正文 (空行结束):")
        content_lines = []
        while True:
            try:
                line = input()
                if line == '':
                    break
                content_lines.append(line)
            except EOFError:
                break
        if not content_lines:
            content_lines = ["新文章内容待补充。"]
    
    filename, html, excerpt = make_html(title, date_str, category, tags_list, content_lines)
    
    # 写入HTML
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"✅ 已创建 {filename}")
    
    # 更新JSON
    update_articles_json(filename, title, date_str, category, tags_list, excerpt)
    
    # 更新首页
    update_index_html(filename, title, date_str, category, excerpt)
    
    print(f"\n🎉 文章发布成功！")
    print(f"   链接: https://caogenfunan.me/{filename}")
    print(f"   记得把文件推送到 GitHub 部署！")
