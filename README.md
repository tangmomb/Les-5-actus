<div align="center">
    <h1>📰 <span style="color:#2d7dd2;">Les 5 Articles du Jour</span> – Web App Streamlit</h1>
    <img src="https://img.shields.io/badge/Python-3.10+-blue?logo=python" alt="python" />
    <img src="https://img.shields.io/badge/Streamlit-%E2%9C%A8-red?logo=streamlit" alt="streamlit" />
    <img src="https://img.shields.io/badge/OpenAI-API-green?logo=openai" alt="openai" />
</div>

---

## 🎯 **Objectif du projet**

L’objectif de ce projet est de concevoir une application web interactive permettant d’afficher les articles d’actualité récents issus de différentes sources d’information, et de proposer une synthèse automatique grâce à l’intelligence artificielle.

L’application a été développée avec Streamlit, un framework Python simple et rapide pour créer des interfaces web.

Elle s’appuie également sur l’API OpenAI pour générer automatiquement des résumés adaptés à différents formats de publication (comme Twitter ou LinkedIn).

---

## ⚙️ **Fonctionnement général**

### 🏠 <u>Affichage de la page principale</u>

L’application affiche la date du jour et un titre clair : Les 5 articles du jour.

### 🗂️ <u>Choix de la catégorie</u>

L’utilisateur choisit une catégorie d’actualité parmi plusieurs options : - Généraliste - Politique - Tech - Sports - Environnement

### 🔄 <u>Récupération automatique des articles</u>

En fonction de la catégorie sélectionnée :

- Les articles sont récupérés à partir de flux RSS (20 Minutes, 01net, L’Équipe, etc.),
  ou, pour la catégorie Environnement, via un scraping d’un site spécialisé.

### 📋 <u>Affichage des articles</u>

Les cinq articles les plus récents sont affichés dans une interface claire et lisible, avec leur titre et leur lien.

### 🖱️ <u>Sélection d’un article</u>

L’utilisateur choisit l’article qui l’intéresse parmi la liste.

### 🤖 <u>Génération automatique d’un résumé</u>

Deux boutons permettent de générer un résumé :

- Tweet (280 caractères) → résumé court et percutant, idéal pour X/Twitter.
- LinkedIn (600 caractères) → résumé plus détaillé, adapté à une publication professionnelle.

Un résumé de la taille correspondante est généré via l’API OpenAI.

### 📝 <u>Affichage du résumé</u>

Le résumé s’affiche dans une carte colorée et bien présentée, avec :

- le texte prêt à être copié,
- le type de résumé (Tweet ou LinkedIn),
- Des informations techniques : tokens utilisés et coût estimé.

---

## 🛠️ **Technologies utilisées**

- Python 3
- Streamlit — pour l’interface web
- OpenAI API — pour la génération des résumés
- RSS et Web Scraping — pour récupérer les articles
- HTML / CSS (intégré dans Streamlit) — pour la mise en forme

---

## 🗃️ Organisation du projet

<details>
<summary>Cliquez pour voir la structure des fichiers</summary>

<pre>
├── app.py                        # Fichier principal de l'application
├── scripts/
│   ├── articles.py               # Fonctions de récupération et d’affichage des articles
│   ├── colors.py                 # Palette de couleurs pour le design
│   ├── resume.py                 # Fonction pour générer les résumés OpenAI
│   ├── render_card.py            # Affichage graphique des cartes de résumé
│   ├── init_openai.py            # Initialisation du client OpenAI
├── requirements.txt              # Liste des dépendances Python
</pre>
</details>

---

## 🚀 **Pour exécuter le projet**

### 📦 <u>Installer les dépendances</u>

pip install -r requirements.txt

### ▶️ <u>Lancer l’application</u>

streamlit run app.py

### 🌐 <u>Ouvrir dans le navigateur</u>

Streamlit lance automatiquement l'app

---

## 💡 **Améliorations possibles**

- Ajouter d’autres catégories d’articles ou d’autres sources d’information.
- Permettre le partage automatique des résumés sur les réseaux sociaux.
- Afficher un historique des résumés générés.
- Personnaliser la longueur du résumé selon les préférences de l’utilisateur.

---

## 👥 **Équipe projet**

- Alexandre JANNIC
- Tanguy MOMBERT
