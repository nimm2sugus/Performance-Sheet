import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# --- Streamlit App ---
st.set_page_config(page_title="Performance PARK 25", layout="wide")
st.title("📊 Performance Analyse")

# --- Datei Upload ---
uploaded_file = st.file_uploader("Bitte Excel-Datei hochladen", type=["xlsx"])

if uploaded_file:
    # Excel einlesen
    df = pd.read_excel(uploaded_file, sheet_name="Performance PARK 25", header=None)

    # Abschnitte erkennen (Zeilen mit Text wie "Soll in kWh (monatlich)")
    section_labels = df[df.iloc[:, 0].astype(str).str.contains("in kWh", na=False)].iloc[:, 0].tolist()

    # Funktion: Datenblöcke extrahieren
    def extract_section(df, start_label):
        start_row = df[df.iloc[:, 0] == start_label].index[0]
        end_row = start_row + 13  # 12 Monate + Summe
        section = df.iloc[start_row+1:end_row, :]
        section = section.rename(columns=df.iloc[start_row])
        section = section.dropna(axis=1, how="all")
        section = section.set_index(section.columns[0])
        section = section.drop(index=["Jahressumme"], errors="ignore")
        return section

    # Auswahl des Abschnitts
    section_choice = st.selectbox("Abschnitt auswählen:", section_labels)
    data = extract_section(df, section_choice)

    # Standortauswahl (inkl. Alle Anlagen)
    locations = data.columns
    selected_locations = st.multiselect("Standorte auswählen:", locations, default=[locations[0]])

    # Plot
    if selected_locations:
        fig, ax = plt.subplots(figsize=(10, 5))
        for loc in selected_locations:
            ax.plot(data.index, data[loc], marker="o", label=loc)
        ax.set_title(f"Monatliche Werte: {section_choice}")
        ax.set_xlabel("Monat")
        ax.set_ylabel("kWh")
        ax.legend()
        plt.xticks(rotation=45)
        st.pyplot(fig)
    else:
        st.info("Bitte mindestens einen Standort auswählen.")
else:
    st.info("⬆️ Bitte eine Excel-Datei hochladen.")
