import requests
from bs4 import BeautifulSoup
import streamlit as st
import groq
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Ensure the API key is set
if not GROQ_API_KEY:
    st.error("❌ Error: GROQ_API_KEY is missing. Add it to your .env file.")

# Initialize Groq Client
client = groq.Client(api_key=GROQ_API_KEY)

visited_urls = set()

def extract_text(url):
    """Extracts and cleans text from a webpage."""
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")

        # Extract relevant text from p, h1, h2, and li tags
        paragraphs = [p.get_text() for p in soup.find_all(["p", "h1", "h2", "li"])]
        text = "\n".join(paragraphs).strip()

        return text if text else "No readable content found."

    except requests.exceptions.RequestException:
        return "Error: Unable to fetch content."

def get_links(url):
    """Extract internal links from the given URL."""
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
    """Recursively crawl website and extract text"""
    if depth == 0 or url in visited_urls:
        return ""

    print(f"Crawling: {url}")
    visited_urls.add(url)

    extracted_text = extract_text(url)
    links = get_links(url)

    for link in links:
        extracted_text += "\n" + crawl(link, depth - 1)

    return extracted_text

def summarize_text(text):
    """Summarize extracted content using AI."""
    response = client.chat.completions.create(
        model="llama3-8b-8192",  # Updated model
        messages=[
            {"role": "system", "content": "Summarize this website content."},
            {"role": "user", "content": f"Summarize: {text}"}
        ],
        temperature=0.5,
        max_tokens=200
    )
    return response.choices[0].message.content

def ask_ai(question, context):
    """Answer user queries based on extracted website content."""
    response = client.chat.completions.create(
        model="llama3-8b-8192",  # Updated model
        messages=[
            {"role": "system", "content": "Answer questions about website content."},
            {"role": "user", "content": f"Based on this data: {context}, answer: {question}"}
        ],
        temperature=0.5,
        max_tokens=200
    )
    return response.choices[0].message.content

# Streamlit UI
st.title("🌐 AI-Powered Web Crawler & Summarizer")
url = st.text_input("Enter Website URL", "https://www.uvtechsoft.com")

if st.button("Start Crawling"):
    st.write("🚀 Crawling started... Please wait.")
    
    extracted_text = crawl(url)
    
    if extracted_text.startswith("Error"):
        st.error(extracted_text)
    else:
        st.success("✅ Crawling completed!")
        st.subheader("Extracted Content")
        st.write(extracted_text[:2000])  # Show first 2000 characters

        # Generate Summary
        summary = summarize_text(extracted_text)
        st.subheader("📌 Summarized Content")
        st.write(summary)

# Ask AI about website content
user_question = st.text_input("❓ Ask AI about the website:")
if user_question:
    answer = ask_ai(user_question, extracted_text)
    st.subheader("🤖 AI Answer")
    st.write(answer)

