import pandas as pd
import streamlit as st
from mplsoccer import Pitch, VerticalPitch
from statsbombpy import sb

# Configura o layout do streamlit
st.set_page_config(layout= 'wide')
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

#=============================== SIDEBAR
# Lista campeonato
lista_campeonato = lista_opcoes(competitions,"competition_name")
# Lista temporada
lista_temporada = lista_opcoes(competitions,"season_name")

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
    # Dataframe com o campeonato selecionado
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
    # Dataframe com a campeonato e temporada selecionados
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

    # Lista de partidas
    lista_partidas = lista_opcoes(matches,"matche")
    # Seletor de partida
    partida_selecionada = st.selectbox(
                "Escolha uma partida:",
                options=lista_partidas,
                key="partida_filtrada"
    )


    matches_selected = matches[matches["matche"]==partida_selecionada]

    # Data da partida
    lista_datas = lista_opcoes(matches_selected,"match_date")
    # Seletor de partida
    data_selecionada = st.selectbox(
                "Escolha uma data:",
                options=lista_datas,
                key="data_filtrada"
    )
    matches_selected_by_data = matches_selected[matches_selected["match_date"]==data_selecionada]

#=============================== AREA PRINCIPAL
# Exibe campeonado
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
# Exibe temporada
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
# Exibe Partida
st.markdown(
        f"""
        <span style="font-size: 24px; font-weight: bold;">
            Partida: 
        </span>
        <span style="font-size: 24px;">
            {partida_selecionada}
        </span>
        """,
        unsafe_allow_html=True
    )
st.subheader("")

#---------- Dataframe Match
# ID da partida
match_id = matches_selected_by_data["match_id"].iloc[0]
# Dataframe da partida
event = sb.events(match_id=match_id)

st.dataframe(matches_selected_by_data)

#---------- Metrics
col1, col2, col3 = st.columns(3)
with col1:
    # Total de Gols
    total_gols = matches_selected_by_data["home_score"] + matches_selected_by_data["away_score"]
    st.metric('Total de gols', total_gols)
with col2:
    # Total de Passes
    total_passes = (event["type"]== "Pass").sum()
    st.metric("Total de passes",total_passes)
with col3:
    # Total de chutes
    total_chute = (event["type"]=="Shot").sum()
    st.metric("Total de chutes",total_chute)

# Exibe ataframe da partida
st.dataframe(event)


#=============================== TABS
# Coleta nome dos times
home_team = matches_selected_by_data["home_team"].iloc[0]
away_team = matches_selected_by_data["away_team"].iloc[0]

# Localização de passes e chutes do time mandante
# Passes
home_team_pass = (event[
    (event["possession_team"]==home_team)
    & (event["type"]=="Pass")]
    ["location"]
).reset_index()
home_team_pass[["x","y"]]= home_team_pass["location"].tolist()
# Chutes
home_team_shot = (event[
    (event["possession_team"]==home_team)
    & (event["type"]=="Shot")]
    ["location"]
).reset_index()
home_team_shot[["x","y"]]= home_team_shot["location"].tolist()

#----------
# Localização de passes e chutes do time visitante
# Passes
away_team_pass = (event[
    (event["possession_team"]==away_team)
    & (event["type"]=="Pass")]
    ["location"]
).reset_index()
away_team_pass[["x","y"]]= away_team_pass["location"].tolist()
# Chutes
away_team_shot = (event[
    (event["possession_team"]==away_team)
    & (event["type"]=="Shot")]
    ["location"]
).reset_index()
away_team_shot[["x","y"]]= away_team_shot["location"].tolist()



tab1, tab2 = st.tabs(["Jogador", "Partida"])

with tab1:
    st.text('Out of work')

with tab2:
    col1, col2 = st.columns(2)
    with col1:
        # Nome do time mandante
        st.badge(home_team, color="green")

        #Gráfico de passes
        st.text("Passes:")
        pitch = Pitch(pitch_color='grass', 
                    line_color='white',
                    stripe=True)  
        fig, ax = pitch.draw(figsize=(4, 6))
        ax.scatter(home_team_pass['x'], home_team_pass['y'], c='orange')
        st.pyplot(fig)

        # Gráfico de chutes
        st.text("Chutes:")
        pitch = VerticalPitch(corner_arcs=True, half=True)
        fig, ax = pitch.draw(figsize=(4, 6))
        pitch.scatter(home_team_shot['x'], 
                      home_team_shot['y'], 
                      ax=ax,
                      color="red")
        st.pyplot(fig)

    with col2:
        # Nome do time visitante
        st.badge(away_team, color="blue")

        #Gráfico de passes
        st.text("Passes:")
        pitch = Pitch(pitch_color='grass', 
                    line_color='white',
                    stripe=True)  
        fig, ax = pitch.draw(figsize=(4, 6))
        ax.scatter(away_team_pass['x'], away_team_pass['y'], c='orange')
        st.pyplot(fig)

        # Gráfico de chutes
        st.text("Chutes:")
        pitch = VerticalPitch(corner_arcs=True, half=True)
        fig, ax = pitch.draw(figsize=(4, 6))
        pitch.scatter(away_team_shot['x'], 
                      away_team_shot['y'], 
                      ax=ax,
                      color="red")
        st.pyplot(fig)