import requests
from bs4 import BeautifulSoup
import html

def get_token_usage_info(response):
    """Extrait le nombre de tokens input/output et le prix depuis la réponse OpenAI."""
    usage = getattr(response, 'usage', None)
    input_tokens = None
    output_tokens = None
    price = None
    # Pour OpenAI SDK v1, usage est un objet ResponseUsage(input_tokens=..., output_tokens=...)
    if usage:
        input_tokens = getattr(usage, 'input_tokens', None)
        output_tokens = getattr(usage, 'output_tokens', None)
        # fallback pour d'autres noms
        if input_tokens is None:
            input_tokens = getattr(usage, 'prompt_tokens', None)
        if output_tokens is None:
            output_tokens = getattr(usage, 'completion_tokens', None)
    # Si pas dans usage, tente d'autres chemins (OpenAI API standard)
    if input_tokens is None or output_tokens is None:
        input_tokens = getattr(response, 'input_tokens', None)
        output_tokens = getattr(response, 'output_tokens', None)
        if input_tokens is None:
            input_tokens = getattr(response, 'prompt_tokens', None)
        if output_tokens is None:
            output_tokens = getattr(response, 'completion_tokens', None)
    # Calcul du prix
    if input_tokens is not None and output_tokens is not None:
        price = (input_tokens / 1_000_000 * 0.5) + (output_tokens / 1_000_000 * 1.5)
    return input_tokens, output_tokens, price


def generer_resume(selected_link, client, max_length, label):
    import streamlit as st
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
            print("[DEBUG OPENAI RESPONSE]", response)
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
                # Si besoin, retourne aussi les tokens/prix
                input_tokens, output_tokens, price = get_token_usage_info(response)
                print(f"[TOKENS] input: {input_tokens}, output: {output_tokens}, price: {price}")
                return summary, input_tokens, output_tokens, price
            else:
                st.error("Impossible d'extraire le résumé depuis la réponse OpenAI.")
                return None, None, None, None
        except Exception as e:
            st.error(f"Erreur lors de l'appel à l'API OpenAI : {e}")
            return None, None, None, None
