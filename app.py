import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import google.generativeai as genai
import feedparser
import urllib.parse

# 1. Configure page layout
st.set_page_config(page_title="MarketPulse Diagnostic", page_icon="📈", layout="wide")

# --- CACHING FUNCTIONS ---
@st.cache_data(show_spinner=False, ttl=3600)
def get_financial_data(ticker):
    stock = yf.Ticker(ticker)
    return stock.info, stock.history(period="6mo")

@st.cache_data(show_spinner=False, ttl=3600)
def get_news_data(company_name, ticker):
    # Use Google News RSS feed for reliable, real-time, rate-limit-free data
    query = urllib.parse.quote(f"{ticker} stock OR {company_name} financial news")
    url = f"https://news.google.com/rss/search?q={query}&hl=en-US&gl=US&ceid=US:en"
    
    feed = feedparser.parse(url)
    news_items = []
    
    # Grab the top 4 most recent articles
    for entry in feed.entries[:4]:
        publisher = entry.source.title if hasattr(entry, 'source') else 'Financial News'
        news_items.append({
            'title': entry.title,
            'link': entry.link,
            'publisher': publisher
        })
        
    return news_items

# 2. Sidebar for Inputs
with st.sidebar:
    st.markdown("### ⚙️ Control Panel")
    ticker_symbol = st.text_input("Primary Ticker (e.g., NVDA):", "NVDA").upper()
    comp_symbol = st.text_input("Competitor Ticker (Optional, e.g., AMD):", "AMD").upper()
    
    st.divider()
    run_btn = st.button("Generate Diagnostic", type="primary", use_container_width=True)
    st.divider()
    st.caption("MarketPulse v9.0 | RSS Intelligence Edition")

# --- INITIALIZE SESSION STATE ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "analyze_triggered" not in st.session_state:
    st.session_state.analyze_triggered = False

if run_btn:
    st.session_state.analyze_triggered = True
    st.session_state.messages = [] 
    if "summary" in st.session_state:
        del st.session_state["summary"]

# --- INITIALIZE GEMINI AI ---
api_key = st.secrets.get("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.5-flash')

# 3. Main Dashboard Area
if st.session_state.analyze_triggered:
    with st.spinner("Aggregating intelligence..."):
        try:
            # --- Fetch Primary Data ---
            info, hist = get_financial_data(ticker_symbol)
            company_name = info.get('shortName', ticker_symbol)
            
            st.markdown(f"## 🏢 Strategic Diagnostic: {company_name}")
            st.divider()
            
            # --- Top Row: Financial Metric Cards ---
            st.subheader("Executive Financial Summary")
            col1, col2, col3, col4, col5 = st.columns(5)
            
            current_price = info.get('currentPrice', info.get('regularMarketPrice', 0.0))
            previous_close = info.get('previousClose', current_price)
            price_change = current_price - previous_close
            pct_change = (price_change / previous_close) * 100 if previous_close else 0.0
            
            col1.metric("Current Price", f"${current_price:,.2f}", f"{price_change:,.2f} ({pct_change:.2f}%)")
            market_cap = info.get('marketCap', 0)
            col2.metric("Market Capitalization", f"${market_cap / 1e9:.2f}B" if market_cap else "N/A")
            col3.metric("P/E Ratio (Trailing)", round(info.get('trailingPE', 0), 2) if info.get('trailingPE') else 'N/A')
            col4.metric("52-Week High", f"${info.get('fiftyTwoWeekHigh', 'N/A')}")
            col5.metric("Gross Margins", f"{info.get('grossMargins', 0) * 100:.1f}%" if info.get('grossMargins') else "N/A")
            
            # --- Middle Row: Charting ---
            st.write("") 
            if comp_symbol:
                comp_info, comp_hist = get_financial_data(comp_symbol)
                if not hist.empty and not comp_hist.empty:
                    hist['PctReturn'] = (hist['Close'] / hist['Close'].iloc[0] - 1) * 100
                    comp_hist['PctReturn'] = (comp_hist['Close'] / comp_hist['Close'].iloc[0] - 1) * 100
                    
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(x=hist.index, y=hist['PctReturn'], mode='lines', name=ticker_symbol, line=dict(color='#0033A1', width=3)))
                    fig.add_trace(go.Scatter(x=comp_hist.index, y=comp_hist['PctReturn'], mode='lines', name=comp_symbol, line=dict(color='#FF8300', width=3)))
                    
                    fig.update_layout(title=f"6-Month Performance Benchmark: {ticker_symbol} vs {comp_symbol}", yaxis_title="Normalized Return (%)", margin=dict(l=0, r=0, t=40, b=0), height=400)
                    st.plotly_chart(fig, use_container_width=True)
                    
                    comp_mcap = comp_info.get('marketCap', 0)
                    if market_cap and comp_mcap:
                        gap = abs(market_cap - comp_mcap)
                        leader = ticker_symbol if market_cap > comp_mcap else comp_symbol
                        st.caption(f"**Valuation Gap:** {leader} leads by ${gap / 1e9:.2f} Billion in Market Cap.")
            else:
                if not hist.empty:
                    fig = go.Figure(data=[go.Candlestick(x=hist.index, open=hist['Open'], high=hist['High'], low=hist['Low'], close=hist['Close'])])
                    fig.update_layout(title="6-Month Price Action & Volatility", yaxis_title="Price (USD)", margin=dict(l=0, r=0, t=40, b=0), height=400, xaxis_rangeslider_visible=False)
                    st.plotly_chart(fig, use_container_width=True)
            
            # --- Bottom Row: News & Synthesis ---
            st.divider()
            col_news, col_genai = st.columns([1, 1.2]) 
            news_context = "" 
            
            with col_news:
                st.subheader("📰 Live Market Context")
                
                # Fetch RSS News
                live_news = get_news_data(company_name, ticker_symbol)
                
                if live_news:
                    for article in live_news:
                        with st.expander(f"**{article['title']}**", expanded=False):
                            st.caption(f"Source: {article['publisher']}")
                            st.markdown(f"[Read full article here]({article['link']})")
                            
                        news_context += f"Headline: {article['title']}\nSource: {article['publisher']}\n\n"
                else:
                    st.warning("No recent news found for this ticker.")
            
            with col_genai:
                st.subheader("🧠 Automated Strategic Synthesis")
                
                if not api_key:
                    st.error("API Key not found. Please add GEMINI_API_KEY to secrets.toml.")
                elif news_context:
                    if "summary" not in st.session_state:
                        prompt = f"""
                        Based strictly on the following recent news headlines about {company_name}, provide a concise, 3-bullet-point strategic diagnostic. Format exactly like this:
                        * ⚠️ **Immediate Headwinds:** [1 sentence]
                        * 🔄 **Strategic Pivots:** [1 sentence]
                        * 📊 **Market Sentiment:** [1 sentence]
                        
                        News Context: {news_context}
                        """
                        response = model.generate_content(prompt)
                        st.session_state.summary = response.text
                    
                    st.markdown(st.session_state.summary)
                else:
                    st.info("Awaiting live news context to generate strategic synthesis.")

            # --- AI COPILOT CHAT ---
            st.divider()
            st.subheader("💬 Ask the Copilot")
            st.caption(f"Powered by Gemini 2.5 Flash. Ask questions specifically about {company_name}'s recent news and strategy.")
            
            for message in st.session_state.messages:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])

            if prompt := st.chat_input(f"E.g., What are the main risks mentioned for {company_name}?"):
                st.session_state.messages.append({"role": "user", "content": prompt})
                with st.chat_message("user"):
                    st.markdown(prompt)

                with st.chat_message("assistant"):
                    if api_key:
                        conversation_block = f"You are an expert strategic analyst. Answer this question directly and professionally, based ONLY on the following news headlines. Do not introduce yourself.\n\nContext: {news_context}\n\n"
                        
                        for msg in st.session_state.messages:
                            speaker = "Analyst" if msg["role"] == "assistant" else "User"
                            conversation_block += f"{speaker}: {msg['content']}\n"
                        
                        conversation_block += "Analyst:"
                        
                        response = model.generate_content(conversation_block)
                        msg_content = response.text
                        
                        st.markdown(msg_content)
                        st.session_state.messages.append({"role": "assistant", "content": msg_content})

        except Exception as e:
            st.error(f"An error occurred. Details: {e}")
else:
    st.title("📈 MarketPulse")
    st.markdown("Please enter a stock ticker in the sidebar, then click **Generate Diagnostic**.")
