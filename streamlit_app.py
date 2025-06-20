
import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import re

st.title("South African Racecourse Prediction App")

@st.cache_data
def fetch_racecard_links():
    url = "https://www.goldcircle.co.za/"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    links = soup.find_all("a", href=True)
    racecard_links = [a["href"] for a in links if "racecard" in a["href"] and a["href"].endswith(".pdf")]
    return racecard_links

def extract_racecard_text(pdf_url):
    import fitz  # PyMuPDF
    response = requests.get(pdf_url)
    with open("temp_racecard.pdf", "wb") as f:
        f.write(response.content)
    doc = fitz.open("temp_racecard.pdf")
    text = ""
    for page in doc:
        text += page.get_text()
    return text

def parse_racecard(text):
    races = {}
    current_race = None
    for line in text.splitlines():
        if re.match(r"Race \d+", line):
            current_race = line.strip()
            races[current_race] = []
        elif current_race and re.search(r"\(\d+\)", line):
            races[current_race].append(line.strip())
    return races

def generate_predictions(race_data):
    predictions = {}
    for race, horses in race_data.items():
        if len(horses) >= 4:
            predictions[race] = {
                "Top 3 Picks": horses[:3],
                "Outsider": horses[-1]
            }
    return predictions

st.subheader("Fetching latest racecards...")
racecard_links = fetch_racecard_links()

if racecard_links:
    selected_pdf = st.selectbox("Select a racecard PDF", racecard_links)
    if st.button("Generate Predictions"):
        text = extract_racecard_text(selected_pdf)
        race_data = parse_racecard(text)
        predictions = generate_predictions(race_data)
        for race, picks in predictions.items():
            st.markdown(f"### {race}")
            st.write("**Top 3 Picks:**")
            for pick in picks["Top 3 Picks"]:
                st.write(f"- {pick}")
            st.write("**Outsider Pick:**")
            st.write(f"- {picks['Outsider']}")
else:
    st.warning("No racecards found.")
