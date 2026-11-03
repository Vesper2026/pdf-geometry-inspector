"""Build this repository's bilingual, dependency-free static site."""
from pathlib import Path
from html import escape
import json
import shutil

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
OUT = ROOT / "docs"


def json_ld(data):
    payload = json.dumps(data, ensure_ascii=False).replace("<", "\\u003c")
    return f'<script type="application/ld+json">{payload}</script>'


def build():
    config = json.loads((SITE / "content.json").read_text(encoding="utf-8"))
    base = "https://" + config["hostname"]
    OUT.mkdir(exist_ok=True)
    shutil.copyfile(SITE / "style.css", OUT / "style.css")
    (OUT / ".nojekyll").write_text("", encoding="utf-8")
    (OUT / "CNAME").write_text(config["hostname"] + "\n", encoding="utf-8")
    repository = "https://github.com/Vesper2026/" + config["repo"]
    urls = []
    articles = config["articles"]
    article_by_slug = {article["slug"]: article for article in articles}
    for lang in ("en", "zh-Hant"):
        localized = config[lang]
        zh = lang == "zh-Hant"
        about = "維護關係" if zh else "About & affiliation"
        home = "首頁" if zh else "Home"
        back = "閱讀文章" if zh else "Read the fieldnotes"
        cards = "".join(f'<li><span class="article-no">{index:02d}</span><div><p class="eyebrow">{escape(article[lang]["category"])}</p><h2><a href="/{lang}/{article["slug"]}/">{escape(article[lang]["title"])}</a></h2><p>{escape(article[lang]["description"])}</p></div><span aria-hidden="true" class="arrow">↗</span></li>' for index, article in enumerate(articles, 1))
        resources = "".join(f'<li><a href="{escape(link["url"], quote=True)}">{escape(link[lang])}</a></li>' for link in config["resources"])
        home_context = localized.get("home_context_html", "")
        pages = [{"slug": "", "kind": "home", "title": localized["headline"], "seo_title": localized["seo_title"], "description": localized["description"],
                  "body": f'<section class="intro"><p class="eyebrow">{escape(localized["kicker"])}</p><h1>{escape(localized["headline"])}</h1><p class="lede">{escape(localized["description"])}</p>{home_context}<a class="button" href="#fieldnotes">{back} ↓</a></section><section id="fieldnotes" aria-label="{back}"><ol class="article-list">{cards}</ol></section><aside class="resource-box"><h2>{"實際工具與相關資源" if zh else "Tools & related resources"}</h2><ul>{resources}<li><a href="{repository}">GitHub · {escape(config["repo"])}</a></li></ul><p>{escape(localized["boundary"])}</p></aside>', "date_modified": config["site_modified"]},
                 {"slug": "about", "kind": "about", "title": about, "description": localized["about_description"], "body": localized["about"], "date_modified": config["site_modified"]}]
        pages += [{"slug": article["slug"], "kind": "article", "date_published": article["date_published"], "date_modified": article["date_modified"], "related": article["related"], **article[lang]} for article in articles]
        for page in pages:
            suffix = page["slug"] + "/" if page["slug"] else ""
            path = f"/{lang}/{suffix}"
            canonical = base + path
            en_url = base + "/en/" + suffix
            zh_url = base + "/zh-Hant/" + suffix
            other_lang = "en" if zh else "zh-Hant"
            other_label = "English" if zh else "繁體中文"
            is_home = page["kind"] == "home"
            is_article = page["kind"] == "article"
            breadcrumb = ""
            schemas = []
            if not is_home:
                breadcrumb_label = "麵包屑導覽" if zh else "Breadcrumb"
                breadcrumb = f'<nav class="breadcrumbs" aria-label="{breadcrumb_label}"><ol><li><a href="/{lang}/">{home}</a></li><li><span aria-current="page">{escape(page["title"])}</span></li></ol></nav>'
                schemas.append({"@context": "https://schema.org", "@type": "BreadcrumbList", "@id": canonical + "#breadcrumb", "itemListElement": [{"@type": "ListItem", "position": 1, "name": home, "item": base + f"/{lang}/"}, {"@type": "ListItem", "position": 2, "name": page["title"], "item": canonical}]})
            article_header = "" if is_home else f'<header class="article-header"><p class="eyebrow">{escape(page.get("category", "Sourcefold / 2026"))}</p><h1 id="article-title">{escape(page["title"])}</h1><p class="lede">{escape(page["description"])}</p>'
            content = page["body"]
            if is_article:
                author_name = localized["author_name"]
                author_url = config["author_url"]
                author = {"@type": "Organization", "name": author_name, "url": author_url}
                by = "維護署名" if zh else "By"
                published = "首發" if zh else "Published"
                modified = "更新" if zh else "Updated"
                article_header += f'<p class="byline">{by} <a rel="author" href="{escape(author_url, quote=True)}">{escape(author_name)}</a><span>{published} <time datetime="{page["date_published"]}">{page["date_published"]}</time></span><span>{modified} <time datetime="{page["date_modified"]}">{page["date_modified"]}</time></span></p></header>'
                schemas.append({"@context": "https://schema.org", "@type": "BlogPosting" if config["repo"] == "sourcefold-notes" else "Article", "@id": canonical + "#article", "url": canonical, "headline": page["title"], "description": page["description"], "inLanguage": lang, "datePublished": page["date_published"], "dateModified": page["date_modified"], "author": author, "publisher": author, "mainEntityOfPage": {"@type": "WebPage", "@id": canonical}, "isPartOf": {"@type": "WebSite", "name": localized["brand"], "url": base + f"/{lang}/"}})
                related_title = "延伸閱讀" if zh else "Related reading"
                related_links = "".join(f'<li><a href="/{lang}/{slug}/">{escape(article_by_slug[slug][lang]["title"])}</a></li>' for slug in page["related"])
                related = f'<nav class="related-reading" aria-label="{related_title}"><h2>{related_title}</h2><ul>{related_links}</ul></nav>'
                content = f'<article aria-labelledby="article-title">{article_header}{content}</article>{related}'
            elif not is_home:
                content = article_header + "</header>" + content
            structured_data = "".join(json_ld(schema) for schema in schemas)
            title = page.get("seo_title", page["title"]) + " · " + localized["brand"]
            locale, alternate_locale = ("zh_TW", "en_US") if zh else ("en_US", "zh_TW")
            article_meta = f'<meta property="article:published_time" content="{page["date_published"]}"><meta property="article:modified_time" content="{page["date_modified"]}">' if is_article else ""
            html = f'''<!doctype html>
<html lang="{lang}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{escape(title)}</title><meta name="description" content="{escape(page['description'], quote=True)}"><link rel="canonical" href="{canonical}"><link rel="alternate" hreflang="en" href="{en_url}"><link rel="alternate" hreflang="zh-Hant" href="{zh_url}"><link rel="alternate" hreflang="x-default" href="{en_url}"><meta property="og:title" content="{escape(title, quote=True)}"><meta property="og:description" content="{escape(page['description'], quote=True)}"><meta property="og:url" content="{canonical}"><meta property="og:type" content="{'article' if is_article else 'website'}"><meta property="og:site_name" content="{escape(localized['brand'], quote=True)}"><meta property="og:locale" content="{locale}"><meta property="og:locale:alternate" content="{alternate_locale}"><meta name="twitter:card" content="summary"><meta name="twitter:title" content="{escape(title, quote=True)}"><meta name="twitter:description" content="{escape(page['description'], quote=True)}">{article_meta}<link rel="stylesheet" href="/style.css">{structured_data}</head>
<body class="{config['theme']}"><a class="skip" href="#main">{'跳至內容' if zh else 'Skip to content'}</a><div class="page-shell"><header class="masthead"><a class="brand" href="/{lang}/"><span class="brand-mark" aria-hidden="true">{escape(config['mark'])}</span>{escape(localized['brand'])}</a><nav aria-label="{'主要導覽' if zh else 'Main navigation'}"><a href="/{lang}/">{home}</a><a href="/{lang}/about/">{about}</a><a href="/{other_lang}/{suffix}" lang="{other_lang}" hreflang="{other_lang}">{other_label}</a></nav></header><main id="main" class="{'home-content' if is_home else 'article-content'}">{breadcrumb}{content}</main><footer><p>{escape(localized['footer'])}</p><a href="{repository}">GitHub</a><a href="/sitemap.xml">Sitemap</a><a href="/{lang}/about/">{about}</a></footer></div></body></html>'''
            destination = OUT / lang / page["slug"] / "index.html"
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_text(html, encoding="utf-8")
            urls.append((canonical, en_url, zh_url, page["date_modified"]))
    # Remains a fallback for GitHub Pages; Vercel's exact / route uses a permanent redirect.
    (OUT / "index.html").write_text(f'<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta http-equiv="refresh" content="0; url=/en/"><title>{escape(config["en"]["seo_title"])} · {escape(config["en"]["brand"])}</title><link rel="canonical" href="{base}/en/"></head><body><a href="/en/">English</a> · <a href="/zh-Hant/">繁體中文</a></body></html>', encoding="utf-8")
    entries = []
    for url, en, zh, modified in urls:
        entries.append(f'<url><loc>{url}</loc><lastmod>{modified}</lastmod><xhtml:link rel="alternate" hreflang="en" href="{en}"/><xhtml:link rel="alternate" hreflang="zh-Hant" href="{zh}"/><xhtml:link rel="alternate" hreflang="x-default" href="{en}"/></url>')
    (OUT / "sitemap.xml").write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">' + "".join(entries) + '</urlset>\n', encoding="utf-8")
    (OUT / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {base}/sitemap.xml\n", encoding="utf-8")
    examples = ROOT / "examples"
    if examples.exists():
        shutil.copytree(examples, OUT / "downloads", dirs_exist_ok=True, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    print(f"{config['repo']}: {len(urls)} bilingual content pages + root gateway -> {OUT}")


if __name__ == "__main__":
    build()
