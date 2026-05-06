Commentary Score Analyzer is a Python tool that takes raw cricket match commentary 

Input:
either typed directly or uploaded as a .txt or .pdf file 

How it works:
 -uses GPT-4o-mini to parse and return a structured JSON representation of each over. 
 
 -extracts delivery-by-delivery outcomes, handles extras (wides and no balls), assigns confidence scores to each ball,
 
 -estimates the cost of each API call in both USD and INR.



Setup & Installation
Prerequisites

•	Python 3.9 or higher

•	An OpenAI API key with access to gpt-4o-mini

1. Clone the repository
git clone https://github.com/nirali-brahmbhatt/Commentary-Score-Analyzer.git
cd Commentary-Score-Analyzer
2. Install dependencies
pip install openai streamlit pypdf
3. Set your API key
export api_key=your-openai-api-key-here
Note: the project reads the key from the environment variable named api_key (not OPENAI_API_KEY).
4. Run the app
streamlit run st.py
