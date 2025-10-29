import locale
import streamlit as st
import html
from scripts.articles import get_articles_scraping, get_articles_rss, render_articles_html
from scripts.colors import background_color, border_color, text_highlight_color
from scripts.resume import generer_resume
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

if selected_category == "Environnement":
    articles = get_articles_scraping(nombre_articles)
    html_content = render_articles_html(articles)
    st.markdown(html_content, unsafe_allow_html=True)
elif url and any(x in url for x in ["lequipe", "01net", "20minutes"]):
    articles = get_articles_rss(url, nombre_articles)
    html_content = render_articles_html(articles)
    st.markdown(html_content, unsafe_allow_html=True)


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


# Affichage des boutons l'un sous l'autre et du résultat
resume_tweet = None
tweet_in_tok = tweet_out_tok = tweet_price = None
resume_linkedin = None
linkedin_in_tok = linkedin_out_tok = linkedin_price = None
if st.button("En faire un tweet (280 caractères)"):
    res = generer_resume(selected_link, client, 280, "Tweet")
    if res and isinstance(res, (list, tuple)) and len(res) == 4:
        resume_tweet, tweet_in_tok, tweet_out_tok, tweet_price = res
    elif res and isinstance(res, str):
        resume_tweet = res
if st.button("En faire un résumé LinkedIn (600 caractères)"):
    res = generer_resume(selected_link, client, 600, "LinkedIn")
    if res and isinstance(res, (list, tuple)) and len(res) == 4:
        resume_linkedin, linkedin_in_tok, linkedin_out_tok, linkedin_price = res
    elif res and isinstance(res, str):
        resume_linkedin = res

def render_resume_card(summary_text, label, in_tok=None, out_tok=None, price=None):
    """Affiche le résumé dans un encart sombre avec un titre et les infos tokens/prix."""
    escaped = html.escape(summary_text)
    html_content = f"""
<div style="background-color:{background_color}; color:#ffffff; padding:15px; border-radius:8px; margin:12px 0; border:1px solid {border_color}; ">
<h3 style="margin:0 0 8px 0; font-size:26px; padding:0; color:{text_highlight_color};">Votre résumé prêt à être publié</h3>
<div style="white-space:pre-wrap; font-size:16px; line-height:1.4; margin: 20px 0;">{escaped}</div>
<p style="margin:0; font-size:13px; line-height:1.4; opacity:0.4;">{label}</p>
<div style='font-size:12px; color:#bbb; margin-top:8px;'>Tokens utilisés : entrée <b>{in_tok if in_tok is not None else '?'} </b> / sortie <b>{out_tok if out_tok is not None else '?'} </b> | Prix estimé : <b>{f'${price:.5f}' if price is not None else '?'}</b></div>
</div>
"""
    st.markdown(html_content, unsafe_allow_html=True)

if resume_tweet:
    render_resume_card(resume_tweet, "Tweet (≤280 caractères)", in_tok=tweet_in_tok, out_tok=tweet_out_tok, price=tweet_price)
if resume_linkedin:
    render_resume_card(resume_linkedin, "LinkedIn (≤600 caractères)", in_tok=linkedin_in_tok, out_tok=linkedin_out_tok, price=linkedin_price)

