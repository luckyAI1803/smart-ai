import streamlit as st
import requests
from urllib.parse import quote
from bs4 import BeautifulSoup

# ---------- Zoekfuncties (zonder API's) ----------
# Automatische installatie van beautifulsoup4 indien nodig
import subprocess
import sys

try:
    from bs4 import BeautifulSoup
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "beautifulsoup4"])
    from bs4 import BeautifulSoup

def search_wikipedia(query, lang='nl'):
    try:
        url = f"https://{lang}.wikipedia.org/api/rest_v1/page/summary/{quote(query)}"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            extract = data.get('extract', '')
            if extract and len(extract) > 50:
                return extract
    except:
        return None
    return None

def search_duckduckgo_snippet(query):
    try:
        url = f"https://html.duckduckgo.com/html/?q={quote(query)}"
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            snippet = soup.find('a', class_='result__snippet')
            return snippet.get_text(strip=True) if snippet else None
    except:
        return None
    return None

def extract_direct_answer(content, query):
    if not content:
        return "Geen antwoord gevonden."

    sentences = content.split('.')
    relevant = []
    query_words = query.lower().split()

    for sentence in sentences:
        sentence = sentence.strip()
        if len(sentence) > 20:
            match_score = sum(1 for word in query_words if word in sentence.lower())
            if match_score > 0:
                relevant.append(sentence)
        if len(relevant) >= 2:
            break

    answer = '. '.join(relevant)
    return answer[:300] + "..." if len(answer) > 300 else answer

def get_direct_answer(query):
    sources = [
        lambda q: search_wikipedia(q, 'nl'),
        lambda q: search_wikipedia(q, 'en'),
        search_duckduckgo_snippet
    ]
    for source in sources:
        result = source(query)
        if result:
            return extract_direct_answer(result, query)
    return "❌ Geen duidelijk antwoord gevonden. Probeer een andere vraag."

# ---------- Streamlit UI ----------

st.set_page_config(page_title="🤖 Smart AI", layout="wide")

# Dark theme
st.markdown("""
    <style>
        body { background-color: #1a1a1a; color: white; }
        .stTextInput>div>div>input {
            background-color: #2d2d2d;
            color: white;
            border: 1px solid #4a9eff;
        }
        .stButton>button {
            background-color: #4a9eff;
            color: white;
            font-weight: bold;
        }
        .stMarkdown, .stTextArea, .stTextInput, .stCaption {
            color: white;
        }
    </style>
""", unsafe_allow_html=True)

# Header
st.markdown("## 🤖 Smart AI")
st.markdown("### Directe antwoorden op je vragen – zonder gedoe")

# Input veld
query = st.text_input("💬 Stel je vraag:", "", key="vraag")

if query:
    with st.spinner("Zoeken naar antwoord..."):
        antwoord = get_direct_answer(query)
        st.markdown("#### ❓ Je vraag:")
        st.markdown(f"**{query}**")

        st.markdown("#### 💡 Antwoord:")
        st.success(antwoord)
else:
    st.markdown("""
    #### 🚀 Welkom bij Smart AI

    Stel een vraag en krijg direct een kort antwoord!

    **Voorbeelden**:
    - "Wat is de hoofdstad van België?"
    - "Hoe werkt fotosynthese?"
    - "Wie was Albert Einstein?"

    👆 Typ hierboven en druk op Enter.
    """)

st.markdown("---")
st.caption("✨ Smart AI • Gemaakt zonder API • Snel & Slim")

