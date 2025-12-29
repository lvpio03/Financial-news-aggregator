"""
Terminal Financeiro v1.1
Agregador de notícias financeiras com layout estilo terminal profissional.
"""

import streamlit as st
import feedparser
from datetime import datetime
from typing import Optional, List
import html
import re

# Configuração da página
st.set_page_config(
    page_title="Terminal Financeiro v1.1",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Fontes RSS
RSS_FEEDS = {
    "InfoMoney": {
        "url": "https://www.infomoney.com.br/feed/",
        "icon": "📰"
    },
    "Money Times": {
        "url": "https://www.moneytimes.com.br/feed/",
        "icon": "💰"
    },
    "Valor - Empresas": {
        "url": "https://pox.globo.com/rss/valor/empresas/",
        "icon": "🏢"
    },
    "Valor - Finanças": {
        "url": "https://pox.globo.com/rss/valor/financas/",
        "icon": "💳"
    },
    "Valor - Política": {
        "url": "https://pox.globo.com/rss/valor/politica/",
        "icon": "🏛️"
    },
    "UOL Economia": {
        "url": "https://rss.uol.com.br/feed/economia.xml",
        "icon": "🟡"
    },
    "Brazil Journal": {
        "url": "https://braziljournal.com/feed/",
        "icon": "📓"
    },
    "Exame": {
        "url": "https://exame.com/feed/",
        "icon": "💼"
    },
    "InvestNews": {
        "url": "https://investnews.com.br/feed/",
        "icon": "📈"
    },
    "TheAgriBiz": {
        "url": "https://www.theagribiz.com/feed/",
        "icon": "🌾"
    },
    "Google: Economia Brasil": {
        "url": "https://news.google.com/rss/search?q=economia+brasil&hl=pt-BR&gl=BR&ceid=BR:pt-419",
        "icon": "🔍"
    },
    "Google: Bolsa de Valores": {
        "url": "https://news.google.com/rss/search?q=bolsa+de+valores+ibovespa&hl=pt-BR&gl=BR&ceid=BR:pt-419",
        "icon": "🔍"
    },
    "Google: Agronegócio": {
        "url": "https://news.google.com/rss/search?q=agroneg%C3%B3cio+brasil&hl=pt-BR&gl=BR&ceid=BR:pt-419",
        "icon": "🔍"
    }
}

# CSS do layout
TERMINAL_CSS = """
<style>
    .stApp {
        background-color: #1a1a2e;
        color: #eaeaea;
    }
    
    .ticker-bar {
        background: linear-gradient(90deg, #1a365d 0%, #2c5282 100%);
        color: white;
        padding: 10px 20px;
        font-family: 'Segoe UI', Arial, sans-serif;
        font-size: 14px;
        border-radius: 8px;
        margin-bottom: 20px;
        text-align: center;
    }
    
    .ticker-positive {
        color: #68d391;
    }
    
    .ticker-negative {
        color: #fc8181;
    }
    
    [data-testid="stSidebar"] {
        background-color: #1a365d;
    }
    
    [data-testid="stSidebar"] * {
        color: white !important;
    }
    
    .main-title {
        font-family: 'Segoe UI', Arial, sans-serif;
        font-size: 28px;
        font-weight: 300;
        color: #eaeaea;
        margin-bottom: 20px;
    }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    a {
        color: #58a6ff !important;
        text-decoration: none;
    }
    
    a:hover {
        text-decoration: underline;
    }
</style>
"""


@st.cache_data(ttl=300)
def fetch_feed(feed_name: str, feed_url: str) -> tuple:
    """Busca um feed RSS."""
    try:
        feed = feedparser.parse(feed_url)
        if feed.entries:
            return feed_name, feed.entries, None
        else:
            return feed_name, [], f"Não foi possível carregar as notícias de {feed_name} no momento."
    except Exception as e:
        return feed_name, [], f"Erro ao carregar {feed_name}: {str(e)}"


def clean_html(text: str) -> str:
    """Remove tags HTML."""
    if not text:
        return ""
    text = html.unescape(text)
    clean = re.compile('<.*?>')
    return re.sub(clean, '', text)


def get_relative_time(date_parsed: Optional[tuple]) -> str:
    """Converte data para formato relativo."""
    if not date_parsed:
        return "—"
    
    try:
        article_time = datetime(*date_parsed[:6])
        now = datetime.now()
        diff = now - article_time
        
        minutes = int(diff.total_seconds() / 60)
        hours = int(diff.total_seconds() / 3600)
        days = int(diff.total_seconds() / 86400)
        
        if minutes < 0:
            return "Agora"
        elif minutes < 60:
            return f"{minutes}min atrás"
        elif hours < 24:
            return f"{hours}h atrás"
        elif days == 1:
            return "Ontem"
        elif days < 7:
            return f"{days} dias atrás"
        else:
            return article_time.strftime("%d/%m")
    except:
        return "—"


def main():
    """Função principal."""
    
    # CSS
    st.markdown(TERMINAL_CSS, unsafe_allow_html=True)
    
    # Ticker bar
    st.markdown("""
    <div class="ticker-bar">
        <strong>Ibovespa:</strong> 128.000 <span class="ticker-positive">(+1.5%)</span> | 
        <strong>S&P 500:</strong> 4.800 <span class="ticker-positive">(+0.8%)</span> | 
        <strong>Dólar:</strong> R$ 4,92 <span class="ticker-negative">(-0.3%)</span> | 
        <strong>Euro:</strong> R$ 5,35 <span class="ticker-positive">(+0.2%)</span>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.markdown("### 📊 Fontes")
        st.markdown("---")
        
        # Função para atualizar todas as fontes quando toggle muda
        def toggle_todas():
            valor = st.session_state.toggle_todas
            for nome in RSS_FEEDS.keys():
                st.session_state[f"cb_{nome}"] = valor
        
        # Inicializar toggle se não existir
        if "toggle_todas" not in st.session_state:
            st.session_state.toggle_todas = True
        
        # Toggle on/off
        st.toggle("Selecionar todas", key="toggle_todas", on_change=toggle_todas)
        
        st.markdown("---")
        
        selected_sources = []
        for source_name, source_info in RSS_FEEDS.items():
            icon = source_info["icon"]
            # Inicializar se não existir
            if f"cb_{source_name}" not in st.session_state:
                st.session_state[f"cb_{source_name}"] = True
            
            checked = st.checkbox(
                f"{icon} {source_name}", 
                key=f"cb_{source_name}"
            )
            if checked:
                selected_sources.append(source_name)
        
        st.markdown("---")
        
        if st.button("🔄 Atualizar", use_container_width=True):
            st.cache_data.clear()
            st.rerun()
        
        st.markdown("---")
        st.caption("Atualização automática a cada 5 minutos")
    
    # Título
    st.markdown('<div class="main-title">Terminal Financeiro v1.1</div>', unsafe_allow_html=True)
    
    # Buscar e exibir notícias por fonte
    if selected_sources:
        for source_name in selected_sources:
            feed_info = RSS_FEEDS[source_name]
            
            with st.spinner(f"⏳ Carregando {source_name}..."):
                name, entries, error = fetch_feed(source_name, feed_info["url"])
            
            # Cabeçalho da fonte
            st.markdown(f"### {feed_info['icon']} {source_name}")
            
            if error:
                st.warning(error)
            else:
                # Ordenar por data (mais recentes primeiro)
                def sort_key(article):
                    if article.get("published_parsed"):
                        try:
                            return datetime(*article["published_parsed"][:6])
                        except:
                            return datetime.min
                    return datetime.min
                
                sorted_entries = sorted(entries, key=sort_key, reverse=True)
                
                # Cabeçalho da tabela
                col1, col2 = st.columns([8, 2])
                with col1:
                    st.markdown("**Manchete**")
                with col2:
                    st.markdown("**Hora**")
                
                st.divider()
                
                # Exibir até 50 notícias desta fonte
                for article in sorted_entries[:50]:
                    title = clean_html(article.get("title", "Sem título"))
                    link = article.get("link", "#")
                    time_display = get_relative_time(article.get("published_parsed"))
                    
                    col1, col2 = st.columns([8, 2])
                    
                    with col1:
                        st.markdown(f"🔗 [{title}]({link})")
                    with col2:
                        st.caption(time_display)
                
                st.caption(f"Exibindo {min(len(sorted_entries), 50)} notícias")
            
            st.markdown("---")
    
    else:
        st.info("👈 Selecione pelo menos uma fonte na barra lateral.")


if __name__ == "__main__":
    main()
