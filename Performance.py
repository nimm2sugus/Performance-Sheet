import streamlit as st
import pandas as pd
import altair as alt

# --- Streamlit App ---
st.set_page_config(page_title="Performance PARK 25", layout="wide")
st.title("📊 Performance Analyse")

# --- Datei Upload ---
uploaded_file = st.file_uploader("Bitte Excel-Datei hochladen", type=["xlsx"])

if uploaded_file:
    # Excel einlesen (ohne Header, damit wir Positionen nutzen können)
    df = pd.read_excel(uploaded_file, sheet_name="Performance PARK 25", header=None)

    # Vorgegebene Startzeilen der Datenblöcke (0-basiert)
    section_starts = [1, 18, 35, 52, 69, 86, 103, 120, 137, 154]

    # Abschnittsnamen auslesen (erste Zelle der Startzeile)
    section_labels = [df.iloc[i, 0] for i in section_starts]

    # Funktion: Datenblöcke extrahieren
    def extract_section(df, start_row, drop_sum=False):
        header = df.iloc[start_row]
        end_row = start_row + 13  # 12 Monate + Jahressumme
        section = df.iloc[start_row+1:end_row+1, :]
        section = section.rename(columns=header)
        section = section.dropna(axis=1, how="all")
        section = section.set_index(section.columns[0])
        if drop_sum:
            section = section.drop(index=["Jahressumme"], errors="ignore")
        # Reihenfolge der Monate fixieren (Januar zuerst)
        months_order = [
            "Januar", "Februar", "März", "April", "Mai", "Juni",
            "Juli", "August", "September", "Oktober", "November", "Dezember", "Jahressumme"
        ]
        section = section.reindex([m for m in months_order if m in section.index])
        return section

    # Auswahl des Abschnitts
    section_choice = st.selectbox("Abschnitt auswählen:", section_labels)
    start_row = section_starts[section_labels.index(section_choice)]

    # Option: Jahressumme ausblenden
    drop_sum = st.checkbox("Jahressumme ausblenden", value=True)

    data = extract_section(df, start_row, drop_sum)

    # Standortauswahl
    locations = data.columns
    selected_locations = st.multiselect("Standorte auswählen:", locations, default=[locations[0]])

    # Monatsbereich einstellen
    months_order = [
        "Januar", "Februar", "März", "April", "Mai", "Juni",
        "Juli", "August", "September", "Oktober", "November", "Dezember"
    ]
    available_months = [m for m in months_order if m in data.index]
    start_month, end_month = st.select_slider(
        "Monatsbereich wählen:",
        options=available_months,
        value=(available_months[0], available_months[-1])
    )

    # Daten auf ausgewählten Monatsbereich filtern
    if available_months:
        start_idx = available_months.index(start_month)
        end_idx = available_months.index(end_month)
        month_range = available_months[start_idx:end_idx+1]
        data = data.loc[data.index.isin(month_range)]

    if selected_locations:
        # Daten ins Long-Format für Altair
        chart_data = data[selected_locations].reset_index().melt(id_vars=data.index.name or data.columns[0],
                                                               var_name="Standort",
                                                               value_name="kWh")

        chart = (
            alt.Chart(chart_data)
            .mark_line(point=True)
            .encode(
                x=alt.X(f"{data.index.name or data.columns[0]}:O", title="Monat",
                        sort=months_order),
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
