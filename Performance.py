import streamlit as st
import pandas as pd
import altair as alt

# --- Streamlit App ---
st.set_page_config(page_title="Performance PARK 25", layout="wide")
st.title("📊 Performance Analyse")

# --- Datei Upload ---
uploaded_file = st.file_uploader("Bitte Excel-Datei hochladen", type=["xlsx"])

if uploaded_file:
    # Excel einlesen
    df = pd.read_excel(uploaded_file, sheet_name="Performance PARK 25", header=None)

    # Abschnitte erkennen (Zeilen mit Text wie "in kWh")
    section_labels = df[df.iloc[:, 0].astype(str).str.contains("in kWh", na=False)].iloc[:, 0].tolist()

    # Funktion: Datenblöcke extrahieren
    def extract_section(df, start_label):
        start_row = df[df.iloc[:, 0] == start_label].index[0]
        # Abschnitt läuft bis zur nächsten Abschnittsbeschriftung oder Ende
        next_labels = df[df.index > start_row][df.iloc[:, 0].astype(str).str.contains("in kWh", na=False)].index
        end_row = next_labels[0] if not next_labels.empty else len(df)
        section = df.iloc[start_row+1:end_row, :]
        section = section.rename(columns=df.iloc[start_row])
        section = section.dropna(axis=1, how="all")
        section = section.set_index(section.columns[0])
        # Jahressumme ggf. behalten
        return section

    # Abschnittsauswahl
    section_choice = st.selectbox("Abschnitt auswählen:", section_labels)
    data = extract_section(df, section_choice)

    # Standortauswahl (inkl. Alle Anlagen)
    locations = data.columns
    selected_locations = st.multiselect("Standorte auswählen:", locations, default=[locations[0]])

    if selected_locations:
        # Daten ins Long-Format für Altair
        chart_data = data[selected_locations].reset_index().melt(id_vars=data.index.name or data.columns[0],
                                                               var_name="Standort",
                                                               value_name="kWh")

        chart = (
            alt.Chart(chart_data)
            .mark_line(point=True)
            .encode(
                x=alt.X(f"{data.index.name or data.columns[0]}:O", title="Monat"),
                y=alt.Y("kWh:Q", title="kWh"),
                color="Standort:N",
                tooltip=[data.index.name or data.columns[0], "Standort", "kWh"]
            )
            .properties(
                title=f"Monatliche Werte: {section_choice}",
                width=800,
                height=400
            )
        )

        st.altair_chart(chart, use_container_width=True)
    else:
        st.info("Bitte mindestens einen Standort auswählen.")
else:
    st.info("⬆️ Bitte eine Excel-Datei hochladen.")
