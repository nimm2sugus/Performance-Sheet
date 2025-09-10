import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# --- Streamlit App ---
st.set_page_config(page_title="Performance PARK 25", layout="wide")
st.title("📊 Performance Analyse")


# --- Cached Data Loading Functions ---

@st.cache_data
def load_data(uploaded_file):
    """Reads the uploaded Excel file and returns a DataFrame. Cached for performance."""
    df = pd.read_excel(uploaded_file, sheet_name="Performance PARK 25", header=None)
    return df


@st.cache_data
def extract_section(_df, start_row, drop_sum=False):
    """Extracts a specific data block from the main DataFrame. Cached for performance."""
    header = _df.iloc[start_row]
    end_row = start_row + 13  # 12 Monate + Jahressumme
    section = _df.iloc[start_row + 1:end_row + 1, :]
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


# --- Datei Upload ---
uploaded_file = st.file_uploader("Bitte Excel-Datei hochladen", type=["xlsx"])

if uploaded_file:
    # Lade die Daten über die zwischengespeicherte Funktion
    df = load_data(uploaded_file)

    # Vorgegebene Startzeilen der Datenblöcke (0-basiert)
    section_starts = [1, 18, 35, 52, 69, 86, 103, 120, 137, 154]

    # Abschnittsnamen auslesen (erste Zelle der Startzeile)
    section_labels = [df.iloc[i, 0] for i in section_starts]

    # Auswahl des Abschnitts
    section_choice = st.selectbox("Abschnitt auswählen:", section_labels)
    start_row = section_starts[section_labels.index(section_choice)]

    # Option: Jahressumme ausblenden
    drop_sum = st.checkbox("Jahressumme ausblenden", value=True)

    # Extrahiere Daten über die zwischengespeicherte Funktion
    data = extract_section(df, start_row, drop_sum)

    # Prüfen, ob es sich um Prozentwerte handelt
    is_percent = "%" in section_choice

    # Standortauswahl
    locations = data.columns
    selected_locations = st.multiselect("Standorte auswählen:", locations, default=list(locations[:1]))

    # Monatsbereich einstellen
    months_order = [
        "Januar", "Februar", "März", "April", "Mai", "Juni",
        "Juli", "August", "September", "Oktober", "November", "Dezember"
    ]
    available_months = [m for m in months_order if m in data.index]

    if available_months:
        start_month, end_month = st.select_slider(
            "Monatsbereich wählen:",
            options=available_months,
            value=(available_months[0], available_months[-1])
        )

        # Daten auf ausgewählten Monatsbereich filtern (dieser Schritt ist schnell und braucht keinen Cache)
        start_idx = available_months.index(start_month)
        end_idx = available_months.index(end_month)
        month_range = available_months[start_idx:end_idx + 1]
        filtered_data = data.loc[data.index.isin(month_range)]

    if selected_locations and not filtered_data.empty:
        # Erstellen einer leeren Figur mit Plotly Graph Objects
        fig = go.Figure()

        # Standorte nach Durchschnittswert im Zeitraum sortieren für die Hover-Anzeige
        mean_values = filtered_data[selected_locations].mean().sort_values(ascending=False)
        sorted_locations = mean_values.index

        # Hinzufügen einer Linie (Trace) für jeden ausgewählten Standort in sortierter Reihenfolge
        for location in sorted_locations:
            # Hover-Template je nach Datentyp anpassen
            if is_percent:
                # Formatierung für Prozente ohne Rundung
                hover_template = '<b>%{customdata[0]}</b><br>%{x}<br>%{y}%<extra></extra>'
                custom_data = [[location]] * len(filtered_data.index)
            else:
                # Formatierung für kWh mit Tausendertrennzeichen ohne Rundung
                hover_template = '<b>%{customdata[0]}</b><br>%{x}<br>%{y:,} kWh<extra></extra>'
                custom_data = [[location]] * len(filtered_data.index)

            fig.add_trace(go.Scatter(
                x=filtered_data.index,
                y=filtered_data[location],
                name=location,
                mode='lines+markers',  # Linien mit Punkten
                hovertemplate=hover_template,
                customdata=custom_data
            ))

        # Layout der Grafik anpassen
        yaxis_title = "Anteil in %" if is_percent else "kWh"

        fig.update_layout(
            title=f"Monatliche Werte: {section_choice}",
            xaxis_title="Monat",
            yaxis_title=yaxis_title,
            legend_title="Standort",
            hovermode="x unified"  # Verbessert das Hover-Verhalten
        )

        # Y-Achsen-Formatierung für Prozentwerte
        if is_percent:
            fig.update_yaxes(ticksuffix="%")

        # X-Achsen-Reihenfolge festlegen, um die Monate korrekt zu sortieren
        fig.update_xaxes(categoryorder='array', categoryarray=months_order)

        st.plotly_chart(fig, use_container_width=True)
    elif not selected_locations:
        st.info("Bitte mindestens einen Standort auswählen.")
    else:
        st.warning("Keine Daten im ausgewählten Zeitraum vorhanden.")
else:
    st.info("⬆️ Bitte eine Excel-Datei hochladen.")
