import html
from scripts.colors import background_color, border_color, text_highlight_color
import streamlit as st

def render_resume_card(summary_text, label, in_tok=None, out_tok=None, price=None):
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
