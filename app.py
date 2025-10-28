import locale
import streamlit as st
import feedparser
import re
import requests
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

# --- Création du client OpenAI via le script dans scripts/ ---
client = get_openai_client()

# --- EN-TÊTE ---
st.title("📰 Les 5 articles du jour")
st.write(f"📅 {datetime.now().strftime('%A %d %B %Y')}")
st.divider()

# --- Liste des catégories ---
categories = ["Généraliste", "Politique", "Tech", "Sports", "Envirronnement"]

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


def afficher_flux(url, n):
    """Affiche joliment les articles d’un flux RSS dans Streamlit."""
    
    feed = feedparser.parse(url)

    # Construire la liste d'articles et le conteneur HTML
    articles = []
    html_content = (
        '<div style="height:500px; overflow:auto; border:1px solid #ddd; '
        'padding:10px; border-radius:10px;">'
    )

    for entry in feed.entries[:n]:
        # Image si elle existe
        image_url = ""
        if 'enclosures' in entry and len(entry.enclosures) > 0:
            image_url = entry.enclosures[0].get('url', '')

        # Nettoyer la description selon le site
        if "01net" in url or "lequipe" in url:
            description = re.sub(r'<img[^>]*>', '', entry.description)
        else:
            description = entry.description

        # Ajouter la carte HTML (sans indentation ni triples guillemets multilignes)
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

        # Ajouter aux articles retournés
        articles.append({
            'title': entry.title,
            'link': entry.link,
            'description': description,
            'image': image_url,
        })

    html_content += '</div>'

    # ✅ Afficher le HTML dans Streamlit
    st.markdown(html_content, unsafe_allow_html=True)

    # Retourner la liste d'articles pour permettre la sélection
    return articles


articles = []

if url:
    articles = afficher_flux(url, nombre_articles)

# Sélection d'un article et stockage du titre et du lien
st.divider()
if articles:
    titles = [a.get('title', 'Titre non disponible') for a in articles]
    # Afficher les titres sous forme de boutons radio (titre uniquement)
    selected_title = st.radio("Sélectionne un article :", titles)

    # retrouver l'article correspondant (première occurrence)
    selected_article = next((a for a in articles if a.get('title') == selected_title), None)
    selected_link = selected_article.get('link') if selected_article else None

# Bouton pour demander un résumé via OpenAI
if st.button("Résumer l'article"):
    if not selected_link:
        st.warning("Aucun lien d'article disponible pour le résumé.")
    else:
        with st.spinner("Récupération de l'article et génération du résumé..."):
            article_text = ""
            try:
                resp = requests.get(selected_link, timeout=10)
                resp.encoding = resp.encoding or 'utf-8'
                soup = BeautifulSoup(resp.text, "html.parser")

                # Extraire le texte principal en concaténant les <p>
                paragraphs = [p.get_text(separator=' ', strip=True) for p in soup.find_all('p')]
                article_text = "\n\n".join(paragraphs).strip()
            except Exception as e:
                article_text = ""
                st.error(f"Impossible de récupérer l'article : {e}")

            # Si on n'a pas pu extraire le texte, enverra au moins le titre + lien
            if not article_text:
                prompt = (
                    f"Voici un lien vers un article : {selected_link}\n"
                    f"Tâche : propose un court résumé en français (3-5 phrases) en te basant sur le lien."
                )
            else:
                # Limiter la taille du texte envoyé pour éviter d'excéder les tokens
                max_chars = 15000
                if len(article_text) > max_chars:
                    article_text = article_text[:max_chars] + "\n\n...[truncated]"

                prompt = (
                    "Tu es un assistant utile. Résume en français l'article fourni. "
                    "Donne un résumé concis en 3-5 phrases.\n\n"
                    f"Contenu de l'article :\n{article_text}"
                )

            # Appel à l'API OpenAI via le client retourné par scripts.init_openai.get_openai_client()
            try:
                # Utiliser Responses API si disponible
                response = client.responses.create(
                    model="gpt-3.5-turbo",  # fallback simple model
                    input=prompt,
                )

                # Récupérer le texte de sortie selon la forme renvoyée par le SDK
                summary = None
                if hasattr(response, 'output_text') and response.output_text:
                    summary = response.output_text
                else:
                    # essayer d'extraire depuis response.output...
                    try:
                        # new SDK: response.output is a list of items with 'content'
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
                    # dernier recours: regarder choices (ancienne API)
                    try:
                        choices = getattr(response, 'choices', None)
                        if choices:
                            summary = choices[0].message['content'] if isinstance(choices[0].message, dict) else str(choices[0].message)
                    except Exception:
                        summary = None

                if summary:
                    st.subheader("Résumé")
                    st.write(summary)
                else:
                    st.error("Impossible d'extraire le résumé depuis la réponse OpenAI.")
            except Exception as e:
                st.error(f"Erreur lors de l'appel à l'API OpenAI : {e}")



# # URL du site
# url = "https://www.actu-environnement.com/"

# # Récupérer le HTML
# response = requests.get(url)
# response.encoding = 'utf-8'  # s'assurer du bon encodage

# # Parser le contenu avec BeautifulSoup
# soup = BeautifulSoup(response.text, "html.parser")

# # Trouver tous les titres dans des balises <h2 class="titre">
# titres = soup.find_all("h2", class_="titre")

# # Extraire les 5 premiers titres
# for i, h2 in enumerate(titres[:nombre_articles], start=1):
#     titre = h2.a.get_text(strip=True) if h2.a else "Titre non trouvé"
#     lien = h2.a["href"] if h2.a and "href" in h2.a.attrs else "#"
#     print(f"{i}. {titre}")
#     print(f"   🔗 Lien : {url.rstrip('/')}{lien}\n")

