import locale
import streamlit as st
import feedparser
import re
import requests
import html
from bs4 import BeautifulSoup
from datetime import datetime
from scripts.init_openai import get_openai_client


# Définir la locale en français
locale.setlocale(locale.LC_TIME, 'fr_FR.UTF-8')

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(
    page_title="Articles du jour 📰",
    page_icon="🗞️",
    layout="centered",
)

# Pour le look
background_color = "#08131F"
border_color = "#142B44"
text_highlight_color = "#239CFF"

# --- Création du client OpenAI via le script dans scripts/ ---
client = get_openai_client()

# --- EN-TÊTE ---
st.title("📰 Les 5 articles du jour")
st.write(f"📅 {datetime.now().strftime('%A %d %B %Y')}")
st.divider()

# --- Liste des catégories ---
categories = ["Généraliste", "Politique", "Tech", "Sports", "Environnement"]

# --- Menu déroulant ---
selected_category = st.selectbox("Sélectionne une catégorie :", categories)

nombre_articles = 5

# --- Choisir l'URL en fonction de la catégorie ---
if selected_category == "Généraliste":
    url = "https://www.20minutes.fr/feeds/rss-une.xml"
elif selected_category == "Politique":
    url = "https://www.20minutes.fr/feeds/rss-politique.xml"
elif selected_category == "Tech":
    url = "https://www.01net.com/actualites/feed/"
elif selected_category == "Sports":
    url = "https://dwh.lequipe.fr/api/edito/rss?path=/"
elif selected_category == "Environnement":
    url = "https://www.actu-environnement.com/"
else:
    url = "https://www.20minutes.fr/feeds/rss-une.xml"  # fallback


# Création de la liste d'articles
articles = []

def afficher_si_scraping(n):
    """Scrape les 5 premiers articles du site actu-environnement.com et les affiche dans Streamlit."""
    url = "https://www.actu-environnement.com/"
    try:
        response = requests.get(url)
        # Utilise l'encodage détecté automatiquement (chardet)
        encoding = response.apparent_encoding or 'utf-8'
        html_data = response.content.decode(encoding, errors='replace')
        soup = BeautifulSoup(html_data, "html.parser")
        blocs = soup.find_all("div", class_="news")
        articles = []
        html_content = (
            f'<div style="height:500px; overflow:auto; border:1px solid {border_color}; background-color:{background_color};'
            'padding:10px; border-radius:10px;">'
        )
        for bloc in blocs[:n]:
            # Image
            illu_div = bloc.find("div", class_="illustration")
            img_tag = illu_div.find("img") if illu_div else None
            image_url = img_tag["src"] if img_tag and img_tag.has_attr("src") else ""
            if image_url and image_url.startswith("/"):
                image_url = url.rstrip("/") + image_url
            # Titre et lien
            titre_tag = bloc.find("h2", class_="titre")
            titre_a = titre_tag.find("a") if titre_tag else None
            titre = html.unescape(titre_a.get_text(strip=True)) if titre_a else "Titre non trouvé"
            lien = titre_a["href"] if titre_a and titre_a.has_attr("href") else "#"
            full_link = url.rstrip("/") + lien if lien.startswith("/") else lien
            # Description
            desc_tag = bloc.find("p", class_="chapeau")
            desc_a = desc_tag.find("a") if desc_tag else None
            description = html.unescape(desc_a.get_text(strip=True)) if desc_a else ""
            # Carte HTML
            html_content += (
                '<div style="display:flex; border-bottom:1px solid #ccc; '
                'padding:10px 10px 40px 10px; margin-bottom:15px; '
                'gap:15px; align-items:flex-start;">'
            )
            if image_url:
                html_content += (
                    f'<img src="{image_url}" '
                    'style="width:200px; height:120px; object-fit:cover; border-radius:5px;">'
                )
            html_content += (
                f'<div style="flex:1;">'
                f'<h2 style="font-size:20px; margin:0; padding:0;">{titre}</h2>'
                f'<p style="opacity:0.8; line-height:1.3; margin:10px 0 25px 0;">{description}</p>'
                f'<a href="{full_link}" target="_blank" '
                'style="background-color:#1E90FF; color:white; padding:5px 10px; '
                'text-decoration:none; border-radius:5px;">Lire l\'article</a>'
                '</div>'
                '</div>'
            )
            articles.append({
                'title': titre,
                'link': full_link,
                'description': description,
                'image': image_url,
            })
        html_content += '</div>'
        st.markdown(html_content, unsafe_allow_html=True)
        return articles
    except Exception as e:
        st.error(f"Erreur lors du scraping d'Actu Environnement : {e}")
        return []
    
def afficher_si_rss(url, n):
    """Affiche les articles d’un flux RSS dans Streamlit."""
    feed = feedparser.parse(url)
    articles = []
    html_content = (
        f'<div style="height:500px; overflow:auto; border:1px solid {border_color}; background-color:{background_color};'
        'padding:10px; border-radius:10px;">'
    )
    for entry in feed.entries[:n]:
        image_url = ""
        if 'enclosures' in entry and len(entry.enclosures) > 0:
            image_url = entry.enclosures[0].get('url', '')
        if "01net" in url or "lequipe" in url:
            description = re.sub(r'<img[^>]*>', '', entry.description)
        else:
            description = entry.description
        html_content += (
            '<div style="display:flex; border-bottom:1px solid #ccc; '
            'padding:10px 10px 40px 10px; margin-bottom:15px; '
            'gap:15px; align-items:flex-start;">'
        )
        if image_url:
            html_content += (
                f'<img src="{image_url}" '
                'style="width:200px; height:120px; object-fit:cover; border-radius:5px;">'
            )
        html_content += (
            f'<div style="flex:1;">'
            f'<h2 style="font-size:20px; margin:0; padding:0;">{entry.title}</h2>'
            f'<p style="opacity:0.8; line-height:1.3; margin:10px 0 25px 0;">{description}</p>'
            f'<a href="{entry.link}" target="_blank" '
            'style="background-color:#1E90FF; color:white; padding:5px 10px; '
            'text-decoration:none; border-radius:5px;">Lire l\'article</a>'
            '</div>'
            '</div>'
        )
        articles.append({
            'title': entry.title,
            'link': entry.link,
            'description': description,
            'image': image_url,
        })
    html_content += '</div>'
    st.markdown(html_content, unsafe_allow_html=True)
    return articles


if selected_category == "Environnement":
    articles = afficher_si_scraping(nombre_articles)
elif url and any(x in url for x in ["lequipe", "01net", "20minutes"]):
    articles = afficher_si_rss(url, nombre_articles)


# Sélection d'un article et stockage du titre et du lien
st.divider()
if articles:
    titles = [a.get('title', 'Titre non disponible') for a in articles]
    # Afficher les titres sous forme de boutons radio (titre uniquement)
    selected_title = st.radio("Sélectionne un article :", titles)

    # retrouver l'article correspondant (première occurrence)
    selected_article = next((a for a in articles if a.get('title') == selected_title), None)
    selected_link = selected_article.get('link') if selected_article else None



# Deux boutons l'un sous l'autre pour résumer l'article en 280 ou 600 caractères
def generer_resume(max_length, label):
    if not selected_link:
        st.warning("Aucun lien d'article disponible pour le résumé.")
        return None
    with st.spinner(f"Récupération de l'article et génération du résumé {label}..."):
        article_text = ""
        try:
            resp = requests.get(selected_link, timeout=10)
            resp.encoding = resp.encoding or 'utf-8'
            soup = BeautifulSoup(resp.text, "html.parser")
            paragraphs = [p.get_text(separator=' ', strip=True) for p in soup.find_all('p')]
            article_text = "\n\n".join(paragraphs).strip()
        except Exception as e:
            article_text = ""
            st.error(f"Impossible de récupérer l'article : {e}")

        if not article_text:
            prompt = (
                f"Voici un lien vers un article : {selected_link}\n"
                f"Tâche : propose un résumé en français de l'article en maximum {max_length} caractères, adapté pour {label}."
            )
        else:
            max_chars = 15000
            if len(article_text) > max_chars:
                article_text = article_text[:max_chars] + "\n\n...[truncated]"
            prompt = (
                f"Tu es un assistant utile. Résume en français l'article fourni en maximum {max_length} caractères, "
                f"pour un post {label}. Sois percutant, synthétique, et respecte la limite de caractères.\n\n"
                f"Contenu de l'article :\n{article_text}"
            )

        try:
            response = client.responses.create(
                model="gpt-3.5-turbo",
                input=prompt,
            )
            summary = None
            if hasattr(response, 'output_text') and response.output_text:
                summary = response.output_text
            else:
                try:
                    parts = []
                    for item in getattr(response, 'output', []):
                        if isinstance(item, dict) and 'content' in item:
                            for c in item['content']:
                                if isinstance(c, dict) and c.get('type') == 'output_text':
                                    parts.append(c.get('text', ''))
                                elif isinstance(c, str):
                                    parts.append(c)
                    summary = "".join(parts).strip() if parts else None
                except Exception:
                    summary = None
            if not summary:
                try:
                    choices = getattr(response, 'choices', None)
                    if choices:
                        summary = choices[0].message['content'] if isinstance(choices[0].message, dict) else str(choices[0].message)
                except Exception:
                    summary = None
            if summary:
                return summary
            else:
                st.error("Impossible d'extraire le résumé depuis la réponse OpenAI.")
                return None
        except Exception as e:
            st.error(f"Erreur lors de l'appel à l'API OpenAI : {e}")
            return None

# Affichage des boutons l'un sous l'autre et du résultat
resume_tweet = None
resume_linkedin = None
if st.button("En faire un tweet (280 caractères)"):
    resume_tweet = generer_resume(280, "Tweet")
if st.button("En faire un résumé LinkedIn (600 caractères)"):
    resume_linkedin = generer_resume(600, "LinkedIn")

def render_resume_card(summary_text, label):
    """Affiche le résumé dans un encart sombre avec un titre.

    summary_text est échappé pour éviter l'injection HTML et affiché en
    respectant les retours à la ligne (white-space: pre-wrap).
    """
    escaped = html.escape(summary_text)
    html_content = f"""
<div style="background-color:{background_color}; color:#ffffff; padding:15px; border-radius:8px; margin:12px 0; border:1px solid {border_color}; ">
<h3 style="margin:0 0 8px 0; font-size:26px; padding:0; color:{text_highlight_color};">Votre résumé prêt à être publié</h3>
<div style="white-space:pre-wrap; font-size:16px; line-height:1.4; margin: 20px 0;">{escaped}</div>
<p style="margin:0; font-size:13px; line-height:1.4; opacity:0.4;">{label}</p>
</div>
"""
    st.markdown(html_content, unsafe_allow_html=True)

if resume_tweet:
    render_resume_card(resume_tweet, "Tweet (≤280 caractères)")
if resume_linkedin:
    render_resume_card(resume_linkedin, "LinkedIn (≤600 caractères)")




# URL du site
url = "https://www.actu-environnement.com/"

# Récupérer le HTML
response = requests.get(url)
response.encoding = 'utf-8'  # s'assurer du bon encodage

# Parser le contenu avec BeautifulSoup
soup = BeautifulSoup(response.text, "html.parser")

# Trouver tous les titres dans des balises <h2 class="titre">
titres = soup.find_all("h2", class_="titre")

# Extraire les 5 premiers titres
for i, h2 in enumerate(titres[:nombre_articles], start=1):
    titre = h2.a.get_text(strip=True) if h2.a else "Titre non trouvé"
    lien = h2.a["href"] if h2.a and "href" in h2.a.attrs else "#"
    print(f"{i}. {titre}")
    print(f"   🔗 Lien : {url.rstrip('/')}{lien}\n")

