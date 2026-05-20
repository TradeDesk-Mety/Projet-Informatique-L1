import streamlit as st
import os

def set_global_ui():
    # Application du CSS pour cacher les flèches, unifier les couleurs et améliorer le design
    st.markdown("""
    <style>
      @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

      *, *::before, *::after { box-sizing: border-box; }

      html, body, [data-testid="stAppViewContainer"] {
        font-family: 'Inter', sans-serif !important;
        background: #0B132B !important; /* Deep Navy Blue */
        color: #C0C0C0 !important; /* Silver/Grey */
      }

      /* Sidebar */
      [data-testid="stSidebar"] {
        background: #090F22 !important; /* Slightly darker Navy */
        border-right: 1px solid #1C2541 !important;
      }
      [data-testid="stSidebar"] * { font-family: 'Inter', sans-serif !important; }

      /* Cacher les flèches de défilement des onglets et la flèche de fermeture de sidebar */
      [data-testid="stTabs"] [data-testid="stIconMaterial"] { display: none !important; }
      [data-testid="collapsedControl"] { display: none !important; }

      /* Titres */
      h1, h2, h3, h4 { color: #FFFFFF !important; font-weight: 700 !important; }

      /* Inputs */
      input[type="text"], input[type="password"], input[type="email"],
      [data-testid="stTextInput"] input, [data-testid="stSelectbox"] > div {
        background: #111A35 !important;
        border: 1px solid #1C2541 !important;
        border-radius: 10px !important;
        color: #C0C0C0 !important;
        font-family: 'Inter', sans-serif !important;
        transition: border-color 0.2s;
      }
      [data-testid="stTextInput"] input:focus, [data-testid="stSelectbox"] > div:focus-within {
        border-color: #00A8E8 !important; /* Cyan accent */
        box-shadow: 0 0 0 3px rgba(0, 168, 232, 0.15) !important;
      }

      /* Buttons primary */
      .stButton > button[kind="primary"],
      .stButton > button {
        background: linear-gradient(135deg, #00A8E8 0%, #007EA7 100%) !important; /* Cyan Gradient */
        border: none !important;
        border-radius: 10px !important;
        color: #fff !important;
        font-family: 'Inter', sans-serif !important;
        font-weight: 600 !important;
        letter-spacing: 0.02em !important;
        transition: opacity 0.2s, transform 0.1s !important;
        padding: 0.55rem 1.2rem !important;
      }
      .stButton > button:hover { opacity: 0.88 !important; transform: translateY(-1px) !important; }
      .stButton > button:active { transform: translateY(0) !important; }

      /* Cards / metrics */
      .stMetric {
        background: #111A35 !important;
        border: 1px solid #1C2541 !important;
        border-radius: 14px !important;
        padding: 18px 20px !important;
      }
      [data-testid="metric-container"] {
        background: #111A35 !important;
        border: 1px solid #1C2541 !important;
        border-radius: 14px !important;
        padding: 16px !important;
      }

      /* Tabs */
      [data-testid="stTabs"] button {
        font-family: 'Inter', sans-serif !important;
        font-weight: 600 !important;
        color: #8A94A6 !important;
      }
      [data-testid="stTabs"] button[aria-selected="true"] {
        color: #00A8E8 !important;
        border-bottom: 2px solid #00A8E8 !important;
      }

      /* Divider */
      hr { border-color: #1C2541 !important; }

      /* Slider */
      [data-testid="stSlider"] .st-emotion-cache-1gv3huu,
      [data-testid="stSlider"] [data-testid="stThumbValue"] {
        color: #00A8E8 !important;
      }

      /* Success / error banners */
      [data-testid="stAlert"] { border-radius: 10px !important; }
      
      /* Footer Policies */
      .footer {
        position: fixed;
        bottom: 0;
        right: 0;
        width: 100%;
        background: #090F22;
        border-top: 1px solid #1C2541;
        text-align: center;
        padding: 10px 0;
        font-size: 0.8rem;
        color: #8A94A6;
        z-index: 100;
      }
      .footer a {
        color: #00A8E8;
        text-decoration: none;
        margin: 0 10px;
      }
      .footer a:hover {
        text-decoration: underline;
      }
    </style>
    """, unsafe_allow_html=True)
    
    # Affichage du footer global
    st.markdown("""
        <div class="footer">
            © 2026 TradeDesk | 
            <a href="#">Politique de Confidentialité</a> | 
            <a href="#">Conditions d'Utilisation</a> | 
            <a href="#">Mentions Légales</a>
        </div>
    """, unsafe_allow_html=True)

    # Affichage du logo en haut de la barre latérale s'il existe
    logo_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "assets", "logo.png"))
    if os.path.exists(logo_path):
        st.sidebar.image(logo_path, use_column_width=True)
