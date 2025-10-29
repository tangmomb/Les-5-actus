import locale
import streamlit as st
import feedparser
import re
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from openai import OpenAI  # ✅ nouvelle importation
from newspaper import Article
from dotenv import load_dotenv
import os

# Charger la clé API depuis .env
load_dotenv()
client = OpenAI()  # ✅ le client charge automatiquement la clé OPENAI_API_KEY

# --- LOCALE FR ---
try:
    locale.setlocale(locale.LC_TIME, 'fr_FR.UTF-8')
except:
    pass  # fallback si Windows

# --- CONFIGURATION PAGE ---
st.set_page_config(page_title="Articles du jour 📰", page_icon="🗞️", layout="centered")

st.title("📰 Les 5 articles du jour")
st.write(f"📅 {datetime.now().strftime('%A %d %B %Y')}")
st.divider()

# --- Catégories ---
categories = ["Généraliste", "Politique", "Tech", "Sports", "Environnement"]
selected_category = st.selectbox("Sélectionne une catégorie :", categories)
nombre_articles = 5

# --- Choisir l'URL selon la catégorie ---
if selected_category == "Généraliste":
    url = "https://www.20minutes.fr/feeds/rss-une.xml"
elif selected_category == "Politique":
    url = "https://www.20minutes.fr/feeds/rss-politique.xml"
elif selected_category == "Tech":
    url = "https://www.01net.com/actualites/feed/"
elif selected_category == "Sports":
    url = "https://dwh.lequipe.fr/api/edito/rss?path=/"
elif selected_category == "Environnement":
    url = "https://www.actu-environnement.com/"  # pas de RSS
else:
    url = "https://www.20minutes.fr/feeds/rss-une.xml"

# --- Extraction de texte pour sites sans RSS ---
def extract_articles_from_html(url, n=5):
    """Scrape les titres et liens d’un site sans flux RSS."""
    response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
    soup = BeautifulSoup(response.text, "html.parser")

    articles = []
    # Exemple spécifique : actu-environnement
    for h2 in soup.find_all("h2", class_="titre")[:n]:
        titre = h2.get_text(strip=True)
        lien = h2.a["href"] if h2.a and "href" in h2.a.attrs else "#"
        if not lien.startswith("http"):
            lien = url.rstrip("/") + "/" + lien.lstrip("/")
        articles.append({"title": titre, "link": lien})
    return articles

# --- Récupération du texte d’un article (newspaper3k) ---
def get_full_text(article_url):
    """Télécharge et extrait le texte d’un article complet."""
    try:
        art = Article(article_url)
        art.download()
        art.parse()
        return art.text[:4000]  # limite pour l’API
    except Exception:
        return ""

# --- LLM : génération de contenu assisté ---
def call_llm(prompt, max_tokens=400):
    """Appelle le modèle pour générer du texte."""
    try:
        response = client.chat.completions.create(  # ✅ nouvelle syntaxe
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            temperature=0.6
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Erreur : {e}"

def generate_tweet(title, text, link):
    return call_llm(
        f"Rédige 3 tweets accrocheurs (≤400 caractères chacun) pour résumer cet article :\n\n"
        f"Titre : {title}\n\nTexte : {text[:1000]}\n\n"
        f"Ajoute le lien {link} à la fin de chaque tweet."
    )

def generate_summary(title, text, link):
    return call_llm(
        f"Fais un résumé critique (~200 mots) de cet article :\n\n"
        f"Titre : {title}\n\nContenu : {text[:1500]}\n\n"
        f"Donne les grandes idées, les points de débat et cite 1 ou 2 autres sources potentielles."
    )

def generate_mail(title, text, link):
    return call_llm(
        f"Écris un e-mail court et engageant (objet + corps) pour partager cet article :\n\n"
        f"Titre : {title}\n\nContenu : {text[:1000]}\n\n"
        f"Le mail doit donner envie de cliquer sur {link}."
    )

# --- Affichage des articles RSS ---
def afficher_flux(url, n):
    """Affiche joliment les articles RSS."""
    feed = feedparser.parse(url)

    for entry in feed.entries[:n]:
        image_url = ""
        if "enclosures" in entry and len(entry.enclosures) > 0:
            image_url = entry.enclosures[0].get("url", "")
        description = re.sub(r"<.*?>", "", entry.get("description", ""))

        st.markdown(f"### {entry.title}")
        if image_url:
            st.image(image_url, width=300)
        st.write(description)
        st.markdown(f"[🔗 Lire l'article complet]({entry.link})")

        # Boutons IA
        if st.button(f"🧠 Générer contenu IA pour '{entry.title}'", key=entry.link):
            with st.spinner("Extraction du texte et génération..."):
                texte = get_full_text(entry.link)
                tweet = generate_tweet(entry.title, texte, entry.link)
                resume = generate_summary(entry.title, texte, entry.link)
                mail = generate_mail(entry.title, texte, entry.link)
            st.subheader("💬 Propositions de tweets")
            st.code(tweet)
            st.subheader("🧾 Résumé critique")
            st.write(resume)
            st.subheader("📧 Mail de partage")
            st.write(mail)
        st.divider()

# --- AFFICHAGE selon le type ---
if "actu-environnement" in url:  # cas sans RSS
    st.info("Ce site ne fournit pas de flux RSS. Extraction directe des titres...")
    articles = extract_articles_from_html(url, nombre_articles)
    for art in articles:
        st.markdown(f"### {art['title']}")
        st.markdown(f"[🔗 Lire l'article complet]({art['link']})")

        if st.button(f"🧠 Générer contenu IA pour '{art['title']}'", key=art['link']):
            with st.spinner("Récupération du contenu..."):
                texte = get_full_text(art["link"])
                tweet = generate_tweet(art["title"], texte, art["link"])
                resume = generate_summary(art["title"], texte, art["link"])
                mail = generate_mail(art["title"], texte, art["link"])
            st.subheader("💬 Tweets proposés")
            st.code(tweet)
            st.subheader("🧾 Résumé critique")
            st.write(resume)
            st.subheader("📧 Mail de partage")
            st.write(mail)
        st.divider()
else:
    afficher_flux(url, nombre_articles)
