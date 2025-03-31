import requests
from bs4 import BeautifulSoup
import openai
import streamlit as st
import groq

# Configure API Key
GROQ_API_KEY = "your-groq-api-key"
client = groq.Client(api_key=GROQ_API_KEY)

visited_urls = set()

def get_links(url):
    """Extract internal links"""
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        links = set()
        base_url = "https://www.uvtechsoft.com"
        
        for a_tag in soup.find_all("a", href=True):
            link = a_tag["href"]
            if link.startswith("/") or base_url in link:
                full_link = link if base_url in link else base_url + link
                links.add(full_link)
        return links

    except requests.exceptions.RequestException:
        return set()

def crawl(url, depth=2):
    """Recursively crawl website"""
    if depth == 0 or url in visited_urls:
        return

    print(f"Crawling: {url}")
    visited_urls.add(url)

    links = get_links(url)
    for link in links:
        crawl(link, depth - 1)

def summarize_text(text):
    """Summarize content with AI"""
    response = client.chat.completions.create(
        model="mixtral-8x7b-32768",
        messages=[
            {"role": "system", "content": "Summarize this website content."},
            {"role": "user", "content": f"Summarize: {text}"}
        ],
        temperature=0.5,
        max_tokens=200
    )
    return response.choices[0].message.content

def ask_ai(question, context):
    """Answer user queries"""
    response = client.chat.completions.create(
        model="mixtral-8x7b-32768",
        messages=[
            {"role": "system", "content": "Answer questions about website content."},
            {"role": "user", "content": f"Based on this data: {context}, answer: {question}"}
        ],
        temperature=0.5,
        max_tokens=200
    )
    return response.choices[0].message.content

st.title("Web Crawler & AI Summarizer")
url = st.text_input("Enter Website URL", "https://www.uvtechsoft.com")

if st.button("Start Crawling"):
    st.write("Crawling started... Please wait.")
    crawl(url)
    st.success("Crawling completed!")

extracted_text = "Sample extracted text from website..."
summary = summarize_text(extracted_text)
st.subheader("Summarized Content")
st.write(summary)

user_question = st.text_input("Ask AI about the website:")
if user_question:
    answer = ask_ai(user_question, extracted_text)
    st.subheader("AI Answer")
    st.write(answer)

st.markdown("---")
st.markdown("🚀 Developed by Sakshi Ambavade")
