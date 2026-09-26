import pandas as pd
import streamlit as st
from mplsoccer import Pitch, VerticalPitch
from statsbombpy import sb
import matplotlib.pyplot as plt
import seaborn as sns
import time

# Configura o layout do streamlit
st.set_page_config(layout= 'wide')
#=============================== FUNÇÕES
# Cria lista 
@st.cache_data
def lista_opcoes(dataframe_lista: pd.DataFrame,
                 coluna: str) -> list:
    return sorted(dataframe_lista[coluna].unique().tolist())

def mapa_passes(player_name, player_df):
    # player_filter = (df.type_name == 'Pass') & (df.player_name == player_name)
    # player_df = df.loc[player_filter, ['x', 'y', 'end_x', 'end_y']]

    pitch = Pitch(line_color='white',pitch_color='#02540b')
    fig, ax = pitch.grid(grid_height=0.9, title_height=0.06, axis=False,endnote_height=0.04, title_space=0, endnote_space=0)
    for i in player_df.index:
        x = player_df['x'][i]
        y = player_df['y'][i]
        dx = player_df['end_x'][i] - player_df['x'][i]
        dy = player_df['end_y'][i] - player_df['y'][i]
        # if df['outcome_name'][i] != 'Incomplete':
        ax['pitch'].arrow(x,y,dx,dy,color='#0dff00',length_includes_head=True,head_width=1,head_length=0.8)
        pitch.scatter(player_df['x'][i],player_df['y'][i],color='#0dff00',ax=ax['pitch'])
        # else:
        # ax['pitch'].arrow(x,y,dx,dy,color='red',length_includes_head=True,head_width=1,head_length=0.8)
        # pitch.scatter(player_df['x'][i],player_df['y'][i],color='red',ax=ax['pitch'])
    fig.suptitle("Passes de: " + player_name, fontsize = 20)
    st.pyplot(fig)
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

#---------- Metrics
col1, col2, col3, col4, col5 = st.columns((1,1,1,1,2))
with col1:
    # Total de Passes
    total_passes = (event["type"]== "Pass").sum()
    st.metric("Total de Passes",total_passes,border=True, icon="⤴️") 
with col2:
    # Total de chutes
    total_chute = (event["type"]=="Shot").sum()
    st.metric("Total de Chutes",total_chute,border=True, icon="👟")
with col3:
    # Total de Gols
    total_home_score = matches_selected_by_data["home_score"].sum()
    total_away_score = matches_selected_by_data["away_score"].sum()
    total_gols = total_home_score + total_away_score
    st.metric('Total de Gols', total_gols,border=True, icon="⚽️")
with col4:
    # Taxa de Gols
    tx_gol = ((total_gols/total_chute)*100).round(2)
    st.metric("Taxa de Gols",f"{tx_gol}%",border=True)


# Exibe ataframe da partida
st.subheader("Dados da Partida (Event)")
# periods_event = event["period"].unique()

columns_event = event.columns
columns_default = ["duration", "pass_recipient","period","player","position","possession_team","second","team"] 
# select_period = st.multiselect(label="Escolha o tempo da partida",
#                             options=periods_event,
#                             default=periods_event,
#                             key='tempo_selecionado')


qtd_row = event.shape[0]
df_length = st.number_input(label=f"Defina a quantidade de linhas (max: {qtd_row})",
                               min_value=1,
                               max_value=qtd_row,
                               value=1,
                               key="qdt_linhas"
                               )
columns_selected = st.multiselect(label="Escolha as colunas para serem exibidas",
                                  options=columns_event,
                                  default=columns_default,
                                  key="colunas_selecionadas"
                                  )

event_selected = event[columns_selected].head(df_length)
st.dataframe(event_selected)

#---------- Download, Spinner e Progress Bar
# Cria o arquivo em csv
if st.button("Preparar CSV"):
    with st.spinner("Preparando os dados...", show_time=True,width=300):
        time.sleep(3)
        barra = st.progress(0, text="Preparando o arquivo...")
        barra.progress(50, text="Convertendo para CSV...")

        csv_data = event_selected.to_csv(index=False).encode("utf-8-sig")
        barra.progress(100, text="CSV pronto!")

    st.session_state["csv_data"] = csv_data
    st.success("Arquivo pronto para baixar! ✅")
    if "csv_data" in st.session_state:
        st.download_button(
            label="Clique para baixar em CSV",
            data=st.session_state["csv_data"],
            file_name="dados_filtrados.csv",
            mime="text/csv",
            icon=":material/download:",
            on_click="ignore",
        )

#---------- Visualizações
st.markdown("---")

# Separa um dataframe com os dados de passes
possession_team = possession_team = (
                        event[event["type"] == "Pass"]
                        [["timestamp", "period", "possession_team"]]
                        .copy()
)
# Transforma o campo data em timestamp
possession_team["timestamp"] = pd.to_datetime(possession_team["timestamp"])
# Extrai o minuto
possession_team["minutes"] = possession_team["timestamp"].dt.minute
# Agrega quantidade de passes
agg_qt_pass_by_mint = (
    possession_team
    .groupby(["period","possession_team","minutes"])
    .size()
    .reset_index(name="qt_pass")
)

# Total de passes por equipe
total_pass_by_team = (
    agg_qt_pass_by_mint.groupby("possession_team")["qt_pass"]
    .sum()
    .reset_index(name="total_pass")
)

data = total_pass_by_team["total_pass"]
labels = total_pass_by_team['possession_team']
colors = sns.color_palette('Set2')

#---------- Visualização pizza
col1, col2, col3 = st.columns((0.5,1,0.5))
with col2:
    st.subheader("Posse de Bola", text_alignment = "center")
    fig, ax = plt.subplots(figsize=(1, 1))
    wedges, texts, autotexts = ax.pie(
        data,
        # labels=labels,
        colors=colors,
        startangle=90,
        autopct='%.0f%%',
        wedgeprops=dict(width=0.5)
    )
    ax.legend(wedges, 
            labels,
            loc="center left", 
            #   bbox_to_anchor=(2, 0, 0.5, 1))
            bbox_to_anchor=(1, 0.5),
            fontsize=5
    )
    st.pyplot(fig)

#---------- Visualização Linhas
# Comparação de passes
# Define uma cor para cada equipe
equipes = agg_qt_pass_by_mint[
    "possession_team"
].dropna().unique()
cores = colors # Cor já definida na visualização anterior
mapa_cores = dict(zip(equipes, cores))

# Cria as visualizações
fig, axes = plt.subplots(
    1,
    2,
    figsize=(15, 5),
    sharey=True
)

for ax, periodo in zip(axes, [1, 2]):
    dados_periodo = agg_qt_pass_by_mint[
        agg_qt_pass_by_mint["period"] == periodo
    ]
    for equipe, dados_equipe in dados_periodo.groupby(
        "possession_team"
    ):
        dados_equipe = dados_equipe.sort_values("minutes")
        ax.plot(
            dados_equipe["minutes"],
            dados_equipe["qt_pass"],
            color=mapa_cores[equipe],
            label=equipe,
            linewidth=2
        )
    ax.set_title(f"{periodo}º tempo")
    ax.set_xlabel("Minutos")
    ax.grid(
        axis="both",
        linestyle="--",
        alpha=0.3
    )
    # ax.legend(title="Equipe")
axes[0].set_ylabel("Qtd de passes")
fig.suptitle(
    "Passes Por Minuto",
    fontsize=20
)
fig.tight_layout()
# Exibe a visualização
st.pyplot(fig)
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

#----------
tab1, tab2 = st.tabs(["Jogador", "Partida"])
# Tab sobre jogadores
with tab1:
    # Lista de jogadores
    so_jogador = event["player"].drop_duplicates().dropna().reset_index()
    lista_jogador = lista_opcoes(so_jogador,"player")
    # Seletor de jogador
    jogador_selecionado = st.selectbox(
                "Escolha um jogador:",
                options=lista_jogador,
                key="jogador_filtrado"
    )
    event_player = event[event["player"]==jogador_selecionado].reset_index(drop=True)

    #----------
    # Localização de passes e chutes de jogador
    # Passes
    player_pass = (event_player[
        event_player["type"].str.lower()=="pass"]
        [["location","pass_end_location"]]
    ).dropna().reset_index()
    player_pass[["x", "y"]] = pd.DataFrame(
        player_pass["location"].tolist(),
        columns=["x", "y"],
        index=player_pass.index
    )
    player_pass[["end_x", "end_y"]] = pd.DataFrame(
        player_pass["pass_end_location"].tolist(),
        columns=["end_x", "end_y"],
        index=player_pass.index
    )
    mapa_passes(jogador_selecionado, player_pass)


    # # Chutes
    # player_shot = (event_player[
    #     (event_player["type"].str.lower()=="shot")]
    #     [["location","pass_end_location"]]
    # ).dropna().reset_index()
    # player_shot[["x", "y"]] = pd.DataFrame(
    #     player_shot["location"].tolist(),
    #     columns=["x", "y"],
    #     index=player_shot.index
    # )
    # player_shot[["end_x", "end_y"]] = pd.DataFrame(
    #     player_shot["pass_end_location"].tolist(),
    #     columns=["end_x", "end_y"],
    #     index=player_shot.index
    # )
    # if len(player_shot.count()) == 0: 
    #     st.text("Jogagor não teve chutes.")
    #     print(len(f"Quantidade de chutes: {player_shot.count()}"))
    # else: 
    #     st.text("Chutes:")
    #     pitch = VerticalPitch(corner_arcs=True, half=True)
    #     fig, ax = pitch.draw(figsize=(4, 6))
    #     pitch.scatter(player_shot['x'], 
    #                   player_shot['y'], 
    #                   ax=ax,
    #                   color="red")
    #     st.pyplot(fig)
        
    
#--------------------
# Tab sobre partida
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