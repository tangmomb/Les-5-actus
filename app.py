import locale
import streamlit as st
import feedparser
import re
import requests
from bs4 import BeautifulSoup
from datetime import datetime

# Définir la locale en français
locale.setlocale(locale.LC_TIME, 'fr_FR.UTF-8')

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(
    page_title="Articles du jour 📰",
    page_icon="🗞️",
    layout="centered",
)

# --- EN-TÊTE ---
st.title("📰 Les 5 articles du jour")
st.write(f"📅 {datetime.now().strftime('%A %d %B %Y')}")
st.divider()

# --- Liste des catégories ---
categories = ["Généraliste", "Politique", "Tech", "Sports", "Envirronnement"]

# --- Menu déroulant ---
selected_category = st.selectbox("Sélectionne une catégorie :", categories)


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


# Nombre d'articles à afficher
n = 5

# Parser le flux RSS
feed = feedparser.parse(url)

# Début du conteneur scrollable
html_content = '<div style="height:500px; overflow:auto; border:1px solid #ddd; padding:10px; border-radius:10px;">'

for entry in feed.entries[:n]:
    # Image si elle existe
    image_url = ""
    if 'enclosures' in entry and len(entry.enclosures) > 0:
        image_url = entry.enclosures[0].get('url', '')

    # Description : enlever les <img> uniquement pour certains flux
    if "01net" or "lequipe" in url:
        description = re.sub(r'<img[^>]*>', '', entry.description)
    else:
        description = entry.description

    # Carte avec flexbox
    html_content += '''
    <div style="display:flex; border-bottom:1px solid #ccc; padding:10px 10px 40px 10px; margin-bottom:15px; gap:15px; align-items:flex-start;">
    '''

    # Image à gauche
    if image_url:
        html_content += f'<img src="{image_url}" style="width:200px; height:120px; object-fit:cover; border-radius:5px;">'

    # Texte à droite
    html_content += f'''
    <div style="flex:1;">
        <h2 style="font-size:20px; margin:0; padding:0;">{entry.title}</h2>
        <p style="opacity:0.8; line-height:1.3; margin: 10px 0 25px 0;">{description}</p>
        <a href="{entry.link}" target="_blank" style="background-color:#1E90FF; color:white; padding:5px 10px; text-decoration:none; border-radius:5px;">Lire l'article</a>
    </div>
    '''
    
    html_content += '</div>'

html_content += '</div>'

st.markdown(html_content, unsafe_allow_html=True)



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
for i, h2 in enumerate(titres[:n], start=1):
    titre = h2.a.get_text(strip=True) if h2.a else "Titre non trouvé"
    lien = h2.a["href"] if h2.a and "href" in h2.a.attrs else "#"
    print(f"{i}. {titre}")
    print(f"   🔗 Lien : {url.rstrip('/')}{lien}\n")

