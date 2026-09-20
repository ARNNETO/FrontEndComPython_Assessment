import pandas as pd
import streamlit as st
from mplsoccer import Pitch
from statsbombpy import sb

#=============================== FUNÇÕES
# Cria lista 
@st.cache_data
def lista_opcoes(dataframe_lista: pd.DataFrame,
                 coluna: str) -> list:
    return sorted(dataframe_lista[coluna].unique().tolist())

#=============================== DATAFRAME
with st.container(): 
    # Importa dataframes
    competitions = sb.competitions()
    # Ajusta o dataframe
    competitions["competition_name"] = competitions["competition_name"].replace("1. Bundesliga","Bundesliga")

#=============================== LISTAS PARA FILTROS
# Lista campeonato
lista_campeonato = lista_opcoes(competitions,"competition_name")
# Lista temporada
lista_temporada = lista_opcoes(competitions,"season_name")

#=============================== SIDEBAR
with st.sidebar:
    # Lista campeonato
    lista_campeonato = lista_opcoes(competitions,"competition_name")
    # Filtra campeonado
    st.subheader("Escolha o que melhor te atende")
    campeonato_selecionado = st.selectbox (
        "Escolha um campeonato",
        options=lista_campeonato,
        key="campeonato_filtrado"
    )
      
    df_temporada = competitions[
        competitions["competition_name"] == campeonato_selecionado
        ]

    # Lista temporada
    lista_temporada = lista_opcoes(df_temporada,"season_name")

    # Filtro temporada
    temporada_selecionada = st.selectbox(
        "Escolha uma temporada",
        options=lista_temporada,
        key="temporada_filtrada"
    )


competition_selected = competitions[(competitions["competition_name"]==campeonato_selecionado)
                                & (competitions["season_name"]==temporada_selecionada)
]

# Coleta IDs
competition_id = competition_selected["competition_id"].iloc[0]
season_id = competition_selected["season_id"].iloc[0]
competicao = competition_selected["competition_name"].iloc[0]

# Importa dataframe da partica conforme IDs competição e partida
matches = sb.matches(competition_id=competition_id ,season_id=season_id)
matches["matche"] = matches["home_team"] + " x " + matches["away_team"]



st.markdown(
        f"""
        <span style="font-size: 24px; font-weight: bold;">
            Campeonato: 
        </span>
        <span style="font-size: 24px;">
            {campeonato_selecionado}
        </span>
        """,
        unsafe_allow_html=True
    )

st.markdown(
        f"""
        <span style="font-size: 24px; font-weight: bold;">
            Temporada: 
        </span>
        <span style="font-size: 24px;">
            {temporada_selecionada}
        </span>
        """,
        unsafe_allow_html=True
    )

# Cria lista de partidas
lista_partidas = lista_opcoes(matches,"matche")

# Seletor de partida
partida = st.selectbox(
            "Escolha uma partida:",
            options=lista_partidas,
            key="partida_filtrada"
)
#=============================== TABS
tab1, tab2 = st.tabs(["Jogador", "Partida"])

with tab1:
    st.text('Out of work')

with tab2:
    
    st.subheader("Dataframe Selecionado")
    st.dataframe(competition_selected)

    st.write("### Matches")
    st.dataframe(matches.head())
    st.write(matches.columns)

    # competicao = 
    
    pitch = Pitch(pitch_color='grass', 
                  line_color='white',
                  stripe=True)  
    fig, ax = pitch.draw(figsize=(4, 6))
    st.pyplot(fig)
