# 📈 MarketPulse: AI-Native Financial Diagnostic Platform

MarketPulse is a consumer-grade, fault-tolerant SaaS dashboard designed to solve investor "information overload." It synthesizes live market data, competitor benchmarks, and unstructured news feeds into AI-driven strategic summaries and features a context-aware AI Copilot for deep-dive financial analysis.

## 🚀 Core Features

* **Executive Financial Summaries:** Real-time tracking of critical valuation metrics (Market Cap, P/E Ratio, Gross Margins) utilizing the `yfinance` API.
* **Competitor Benchmarking:** Interactive, gradient-filled Plotly spline charts to benchmark 6-month normalized returns against industry rivals.
* **Fault-Tolerant News Pipeline:** A robust, rate-limit-free Google News RSS integration that guarantees 100% uptime for real-time market context.
* **Automated Strategic Synthesis:** Integration with the **Gemini 2.5 Flash LLM** to automatically distill unstructured news into Immediate Headwinds, Strategic Pivots, and Market Sentiment.
* **Context-Aware AI Copilot:** A conversational interface that allows users to interrogate the live news feed and extract hidden market risks.
* **Consumer-Grade UI:** Custom CSS implementation featuring glassmorphism metric cards, cascading entrance animations, and a sleek dark-mode aesthetic.

## 🛠️ System Architecture & Tech Stack

* **Frontend:** Python, Streamlit, Custom CSS
* **Data Visualization:** Plotly Graph Objects
* **Market Data Pipeline:** `yfinance` API
* **News Aggregation:** `feedparser` (Google News RSS)
* **Generative AI:** Google Gemini 2.5 Flash LLM

## 🛠 How to Use

1. Clone the repository:
   ```bash
   git clone [https://github.com/YOUR_GITHUB_USERNAME/marketpulse.git](https://github.com/YOUR_GITHUB_USERNAME/marketpulse.git)
   ```

2. Navigate into the project directory:
   ```bash
   cd marketpulse
   ```

3. Create and activate a virtual environment (Recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use: .\venv\Scripts\activate
   ```

4. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

5. Configure your API Key (Create a `.streamlit/secrets.toml` file):
   ```toml
   GEMINI_API_KEY = "your_actual_api_key_here"
   ```

6. Launch the dashboard:
   ```bash
   streamlit run app.py
   ```

## 🧠 Design Philosophy
MarketPulse was architected with a strict separation of concerns, decoupling the backend logic (`app.py`) from the frontend styling (`style.css`). Brittle web-scraping dependencies were intentionally bypassed in favor of native APIs and RSS feeds to prioritize system resilience and ensure deployment stability.
