import streamlit as st
import pandas as pd 
from utils import millify

#### Configs ####


st.set_page_config(page_title="Descarbonização da Matriz de Combustíveis", page_icon=":bar_chart:", layout="wide")

st.write(
    """
    <style>
    [data-testid="stMetricDelta"] svg {
        display: none;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("Descarbonização da Matriz de Combustíveis")
subtitle_placeholder = st.empty()
# st.markdown("##")


#### Filtros e Dados ####

ciclo = st.sidebar.radio("Ciclo", ("OTTO", "Diesel"),horizontal=True).lower()

abrangencia = st.sidebar.radio("Abrangência", ("Nacional", "Regional"),horizontal=True)

if abrangencia == "Nacional":
    df = pd.read_excel("dados.xlsx",sheet_name="8.base_trim_br")
    label_col = 'pais'
    regiao = 'BRASIL'

else:
    df = pd.read_excel("dados.xlsx",sheet_name="7.base_trim_ufs")

    regiao = st.sidebar.selectbox("Região", df["desc_uf"].unique())
    df =  df[df["desc_uf"] == regiao]
    label_col = 'desc_uf'
    


agregacao_a = st.sidebar.radio("Agregação", ("Trimestre", "Ano"),
                               format_func=lambda x: {"Trimestre":"Trimestral", "Ano":"Anual"}[x],
                               horizontal=True)

if agregacao_a == "Ano":
    agregacao = st.sidebar.selectbox("Ano", df["ano"].unique(), index=len(df["ano"].unique())-1)

    df_anterior = df[df["ano"] == agregacao-1]\
            .groupby(['ano'], as_index=False).sum(numeric_only=True)\
            .drop(['ano','trim'],axis=1).T


    df = df[df["ano"] == agregacao]\
            .groupby(['ano'], as_index=False).sum(numeric_only=True)\
            .drop(['ano','trim'],axis=1).T
    

else:
    agregacao = st.sidebar.selectbox("Trimestre", df["trim_ano"].unique(),index=len(df["trim_ano"].unique())-1)

    trimestre_anterior =  list(df["trim_ano"].unique()).index(agregacao) - 1
    trimestre_anterior = df["trim_ano"].unique()[trimestre_anterior]

    df_anterior = df[df["trim_ano"] == trimestre_anterior]\
        .drop(df.columns[:9],axis=1).T
    
    df = df[df["trim_ano"] == agregacao]\
        .drop(df.columns[:9],axis=1).T
    

subtitle = f"{f'{agregacao[0]}º Trimestre {agregacao[2:]}' if agregacao_a == 'Trimestre' else agregacao} {' - '+regiao.title() if abrangencia == 'Regional' else ' - Brasil'}"
subtitle_placeholder.subheader(subtitle)

## Renomeando as colunas para o nome da região e agregação
df.columns = [f"{agregacao_a} Atual"]
df_anterior.columns = [f"{agregacao_a} Anterior"]

df = df[f"{agregacao_a} Atual"]
df_anterior = df_anterior[f"{agregacao_a} Anterior"]

#### Métricas Resumo ####

with st.container(border=True):

    col1, col2, col3 = st.columns(3)
    
    col_name = f"ic_matriz_{ciclo}_gco2_mj"
    col1.metric(
        label="Intensidade de Carbono da Matriz",
        value=f'{df.loc[col_name]:.2f}',
        delta="gCO2eq/MJ", delta_color ="off"
    )

    col_name = f"emissao_total_{'c' + ciclo if ciclo == 'diesel' else ciclo}_tco2"
    col2.metric(
        label="Emissão Total de GEE",
        # value=f'{df.loc[col_name]/1000000:.2f} Mi',
        value = millify(df.loc[col_name]),
        delta="t CO2eq", delta_color ="off",

    )


    col_name = f"emissao_evitada_{'c' + ciclo if ciclo == 'diesel' else ciclo}_tco2"
    col3.metric(
        label="Emissão Evitada pelos Combustíveis Renováveis",
        # value=f'{df.loc[col_name]/1000000:.2f} Mi',
        value = millify(df.loc[col_name]),
        delta="t CO2eq", delta_color ="off"
    )

with st.container(border=True):

    col_title, col4, col5 = st.columns(3)

    col_title.subheader('Emissões per capita')

    col_name = f"emissao_per_capita_{'c' + ciclo if ciclo == 'diesel' else ciclo}"
    col4.metric(
        label="Emissão Total per capita",
        value=f'{df.loc[col_name]:.2f}',
        delta="kg CO2eq / hab", delta_color ="off"
    )

    col_name = f"emissao_evitada_per_capita_{'c' + ciclo if ciclo == 'diesel' else ciclo}"
    col5.metric(
        label="Emissão Evitada per capita",
        value=f'{df.loc[col_name]:.2f}',
        delta="kg CO2eq / hab", delta_color ="off"
    )

#### Criar Tabelas ####

df= df.to_frame().join(df_anterior)

df["Variação %"] = (df[f"{agregacao_a} Atual"] - df[f"{agregacao_a} Anterior"]) / df[f"{agregacao_a} Anterior"] 

df.loc['consumo_diesel'] = df.loc["diesel_mj"]+df.loc["biodiesel_mj"]
df.loc['consumo_otto'] = df.loc["gasolina_a_mj"]+df.loc["etanol_hidratado_mj"]+df.loc["etanol_anidro_mj"]

ciclo_label = "Veículos Leves" if ciclo == "otto" else "ciclo diesel"

if ciclo == "otto":
    
    intensidade = df.loc[[
    'ic_matriz_otto_gco2_mj',
    "ic_gasolina_a_gco2_mj",
    "ic_etanol_hidratado_gco2_mj",
    "ic_etano_anidro_gco2_mj"]].rename(
        index={
            "ic_gasolina_a_gco2_mj": "Gasolina A (gCO2eq/MJ)",
            "ic_etanol_hidratado_gco2_mj": "Etanol Hidratado (gCO2eq/MJ)",
            "ic_etano_anidro_gco2_mj": "Etanol Anidro (gCO2eq/MJ)",
            "ic_matriz_otto_gco2_mj": "Total (gCO2eq/MJ)",
        }
    )

    participacao = df.loc[[
        "part_gasolina_a_%",
        "part_hidratado_%",
        "part_anidro_%"]].rename(
        index={
            "part_gasolina_a_%": "Gasolina A",
            "part_hidratado_%": "Etanol Hidratado",
            "part_anidro_%": "Etanol Anidro",
        })*100

elif ciclo == "diesel":
    

    intensidade = df.loc[[
        "ic_matriz_diesel_gco2_mj",
        "ic_diesel_gco2_mj",
        "ic_biodiesel_gco2_mj"]].rename(
        index={
            "ic_diesel_gco2_mj": "Diesel (gCO2eq/MJ)",
            "ic_biodiesel_gco2_mj": "Biodiesel (gCO2eq/MJ)",
            "ic_matriz_diesel_gco2_mj": "Total (gCO2eq/MJ)",
        }
    )


    participacao = df.loc[[
           "part_diesel_%",
            "part_biodiesel_%"]].rename(
        index={
            "part_diesel_%": "Diesel",
            "part_biodiesel_%": "Biodiesel",
        })*100

    

#### Tabela de Emissões ####

st.header(f"Emisões de CO2eq. na Matriz Brasileira")

total = f"emissao_total_{'c' + ciclo if ciclo == 'diesel' else ciclo}_tco2"
evitada = f"emissao_evitada_{'c' + ciclo if ciclo == 'diesel' else ciclo}_tco2"


st.write("Consumo Energético dos Combustíveis Leves")
emissao = df.loc[[
   f"consumo_{ciclo}",
    total,
    evitada,
]].rename(
    index={
       f"consumo_{ciclo}": f"Consumo Energético {ciclo_label} (TJ)",
        total: "Emissão de GEE (t CO2eq)",
        evitada: "Emissão Evitada (t CO2eq)",
    }
)

emissao = emissao.style\
    .format(millify, na_rep="--", decimal=",")\
    .format("{:.2%}", na_rep="--", decimal=",",subset="Variação %")\
    .applymap(
    lambda x: f"color: {'blue' if x > 0 else 'red'};" if isinstance(x, (int, float)) else "",
    subset = "Variação %"
)
st.table(emissao)


st.write("Intensidade de Carbono")

intensidade = intensidade.style\
    .format("{:.2f}", na_rep="--", decimal=",")\
    .format("{:.2%}", na_rep="--", decimal=",",subset="Variação %")\
    .applymap(
    lambda x: f"color: {'blue' if x > 0 else 'red'};" if isinstance(x, (int, float)) else "",
    subset = "Variação %"
)
st.table(intensidade)


st.write("Participação na Matriz")

participacao = participacao.style\
    .format("{:.2f}%", na_rep="--", decimal=",").applymap(
    lambda x: f"color: {'blue' if x > 0 else 'red'};" if isinstance(x, (int, float)) else "",
    subset = "Variação %"
)
st.table(participacao)

