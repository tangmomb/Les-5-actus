import feedparser
import re
import requests
import html
from bs4 import BeautifulSoup
from .colors import background_color, border_color

def get_articles_scraping(n):
    """Scrape les n premiers articles du site actu-environnement.com."""
    url = "https://www.actu-environnement.com/"
    try:
        response = requests.get(url)
        encoding = response.apparent_encoding or 'utf-8'
        html_data = response.content.decode(encoding, errors='replace')
        soup = BeautifulSoup(html_data, "html.parser")
        blocs = soup.find_all("div", class_="news")
        articles = []
        for bloc in blocs[:n]:
            illu_div = bloc.find("div", class_="illustration")
            img_tag = illu_div.find("img") if illu_div else None
            image_url = img_tag["src"] if img_tag and img_tag.has_attr("src") else ""
            if image_url and image_url.startswith("/"):
                image_url = url.rstrip("/") + image_url
            titre_tag = bloc.find("h2", class_="titre")
            titre_a = titre_tag.find("a") if titre_tag else None
            titre = html.unescape(titre_a.get_text(strip=True)) if titre_a else "Titre non trouvé"
            lien = titre_a["href"] if titre_a and titre_a.has_attr("href") else "#"
            full_link = url.rstrip("/") + lien if lien.startswith("/") else lien
            desc_tag = bloc.find("p", class_="chapeau")
            desc_a = desc_tag.find("a") if desc_tag else None
            description = html.unescape(desc_a.get_text(strip=True)) if desc_a else ""
            articles.append({
                'title': titre,
                'link': full_link,
                'description': description,
                'image': image_url,
            })
        return articles
    except Exception as e:
        return []

def get_articles_rss(url, n):
    """Récupère les articles d’un flux RSS."""
    feed = feedparser.parse(url)
    articles = []
    for entry in feed.entries[:n]:
        image_url = ""
        if 'enclosures' in entry and len(entry.enclosures) > 0:
            image_url = entry.enclosures[0].get('url', '')
        if "01net" in url or "lequipe" in url:
            description = re.sub(r'<img[^>]*>', '', entry.description)
        else:
            description = entry.description
        articles.append({
            'title': entry.title,
            'link': entry.link,
            'description': description,
            'image': image_url,
        })
    return articles

def render_articles_html(articles):
    html_content = (
        f'<div style="height:500px; overflow:auto; border:1px solid {border_color}; background-color:{background_color};'
        'padding:10px; border-radius:10px;">'
    )
    for article in articles:
        html_content += (
            '<div style="display:flex; border-bottom:1px solid #ccc; '
            'padding:10px 10px 40px 10px; margin-bottom:15px; '
            'gap:15px; align-items:flex-start;">'
        )
        if article['image']:
            html_content += (
                f'<img src="{article["image"]}" '
                'style="width:200px; height:120px; object-fit:cover; border-radius:5px;">'
            )
        html_content += (
            f'<div style="flex:1;">'
            f'<h2 style="font-size:20px; margin:0; padding:0;">{article["title"]}</h2>'
            f'<p style="opacity:0.8; line-height:1.3; margin:10px 0 25px 0;">{article["description"]}</p>'
            f'<a href="{article["link"]}" target="_blank" '
            'style="background-color:#1E90FF; color:white; padding:5px 10px; '
            'text-decoration:none; border-radius:5px;">Lire l\'article</a>'
            '</div>'
            '</div>'
        )
    html_content += '</div>'
    return html_content
