import streamlit as st
from openai import OpenAI

def get_openai_client():
    """
    Gère la saisie et le stockage de la clé API OpenAI dans la session Streamlit.
    Retourne un client OpenAI prêt à l'emploi.
    """

    # --- Stockage de la clé API dans la session ---
    if "api_key" not in st.session_state:
        st.session_state.api_key = ""

    # --- Si la clé n'est pas encore définie, on affiche le champ ---
    if not st.session_state.api_key:
        api_key_input = st.text_input(
            "🔐 Entre ta clé OpenAI :", 
            type="password", 
            help="Ta clé sera gardée uniquement pendant ta session Streamlit."
        )
        
        # Si l’utilisateur entre une clé → on la sauvegarde
        if api_key_input:
            st.session_state.api_key = api_key_input
            st.rerun()
        else:
            st.warning("👉 Entre ta clé OpenAI pour continuer.")
            st.stop()

    # --- Affichage partiel de la clé ---
    masked_key = st.session_state.api_key[:7] + "..." + st.session_state.api_key[-4:]
    st.info(f"✅ Votre clé OpenAI est : `{masked_key}` (stockée uniquement pour cette session)")

    # --- Création du client OpenAI ---
    client = OpenAI(api_key=st.session_state.api_key)

    return client
