
import streamlit as st
import pandas as pd
import numpy as np
import io

st.title("Estrazione Dati per Best Score e Valutazione HCP")

uploaded_file = st.file_uploader("Carica il file Excel", type=["xlsx"])

def calcola_quartili_e_mediana(colonna):
    dati = colonna.dropna().sort_values().reset_index(drop=True)
    n = len(dati)
    base_quartile_size = n // 4
    remainder = n % 4

    if remainder == 0:
        sizes = [base_quartile_size] * 4
    else:
        sizes = [base_quartile_size + 1, base_quartile_size, base_quartile_size, base_quartile_size + 1]

    q1 = dati.iloc[:sizes[0]]
    q2 = dati.iloc[sizes[0]:sizes[0] + sizes[1]]
    q3 = dati.iloc[sizes[0] + sizes[1]:sizes[0] + sizes[1] + sizes[2]]
    q4 = dati.iloc[sizes[0] + sizes[1] + sizes[2]:]

    media_q2_q3 = (q2.sum() + q3.sum()) / (len(q2) + len(q3))
    mediana = dati.median()
    return media_q2_q3, mediana

if uploaded_file:
    df = pd.read_excel(uploaded_file)

    required_columns = ['Punti', 'Ex Hcp N', 'Des Giocatore', 'Data', 'Des Circolo Gara', 'Des Circolo Gio']
    if all(col in df.columns for col in required_columns):
        df = df[required_columns].dropna()
        df['Data'] = pd.to_datetime(df['Data'])

        nome_giocatore = df['Des Giocatore'].iloc[0]
        nome_circolo = df['Des Circolo Gio'].iloc[0]

        # Calcoli statistici sulle colonne Punti e HCP
        media_q2_q3_punti, mediana_punti = calcola_quartili_e_mediana(df['Punti'])
        media_q2_q3_hcp, mediana_hcp = calcola_quartili_e_mediana(df['Ex Hcp N'])

        hcp_max = df['Ex Hcp N'].max()
        hcp_min = df['Ex Hcp N'].min()

        # Analisi temporale: massimo intervallo senza risultati
        date_sorted = df['Data'].sort_values().reset_index(drop=True)
        diffs = date_sorted.diff().dropna()
        massimo_gap = diffs.max().days

        # Percentuali di gioco
        total_rounds = len(df)
        giochi_al_proprio_circolo = df[df['Des Circolo Gara'] == nome_circolo]
        percentuale_circolo_proprio = (len(giochi_al_proprio_circolo) / total_rounds) * 100
        media_proprio = giochi_al_proprio_circolo['Punti'].mean()
        media_esterni = df[df['Des Circolo Gara'] != nome_circolo]['Punti'].mean()

        # Costruzione report
        risultati = pd.DataFrame({
            'Giocatore': [nome_giocatore],
            'Circolo di appartenenza': [nome_circolo],
            'Media Q2+Q3 Punti': [media_q2_q3_punti],
            'Mediana Punti': [mediana_punti],
            'Media Q2+Q3 Ex Hcp N': [media_q2_q3_hcp],
            'Mediana Ex Hcp N': [mediana_hcp],
            'HCP Massimo': [hcp_max],
            'HCP Minimo': [hcp_min],
            'Periodo max senza risultati (giorni)': [massimo_gap],
            'Percentuale partite nel proprio circolo': [percentuale_circolo_proprio],
            'Media punti nel proprio circolo': [media_proprio],
            'Media punti negli altri circoli': [media_esterni]
        })

        st.subheader("Scheda Giocatore")
        st.dataframe(risultati)

        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            risultati.to_excel(writer, index=False, sheet_name='Statistiche')
        output.seek(0)

        st.download_button(
            label="📥 Scarica scheda giocatore",
            data=output,
            file_name=f"{nome_giocatore}.dati.bestscore.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.error("Il file deve contenere le colonne: 'Punti', 'Ex Hcp N', 'Des Giocatore', 'Data', 'Des Circolo Gara', 'Des Circolo Gio'.")
