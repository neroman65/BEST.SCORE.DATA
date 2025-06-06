
import streamlit as st
import pandas as pd
import numpy as np
import io

st.title("Estrazione Dati per Best Score e Valutazione HCP")

uploaded_file = st.file_uploader("Carica il file Excel", type=["xlsx"])

def calcola_statistiche(colonna):
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

    if 'Punti' in df.columns and 'Ex Hcp N' in df.columns and 'Des Giocatore' in df.columns:
        nome_giocatore = df['Des Giocatore'].dropna().unique()[0]

        media_q2_q3_punti, mediana_punti = calcola_statistiche(df['Punti'])
        media_q2_q3_hcp, mediana_hcp = calcola_statistiche(df['Ex Hcp N'])

        hcp_max = df['Ex Hcp N'].max()
        hcp_min = df['Ex Hcp N'].min()

        risultati = pd.DataFrame({
            'Giocatore': [nome_giocatore],
            'Media Q2+Q3 Punti': [media_q2_q3_punti],
            'Mediana Punti': [mediana_punti],
            'Media Q2+Q3 Ex Hcp N': [media_q2_q3_hcp],
            'Mediana Ex Hcp N': [mediana_hcp],
            'HCP Massimo': [hcp_max],
            'HCP Minimo': [hcp_min]
        })

        st.subheader("Risultati Calcolati")
        st.dataframe(risultati)

        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            risultati.to_excel(writer, index=False, sheet_name='Statistiche')
        output.seek(0)

        st.download_button(
            label="📥 Scarica risultati in Excel",
            data=output,
            file_name="estrazione_dati_hcp_best_score.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.error("Il file deve contenere le colonne 'Punti', 'Ex Hcp N' e 'Des Giocatore'.")
