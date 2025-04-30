import streamlit as st
import pandas as pd 
from utils import millify_nodecimals
import plotly.express as px

st.logo('logo.png', icon_image='logo.png',size='large')
st.set_page_config(page_title="Descarbonização da Matriz de Combustíveis", page_icon="favicon.ico", layout="wide")

st.title("Descarbonização da Matriz de Combustíveis")
subtitle_placeholder = st.empty()

#### Filtros e Dados ####

ciclo = st.sidebar.radio("Ciclo", ("OTTO", "Diesel"),horizontal=True).lower()

tipo_emissao = st.sidebar.radio("Emissões",["Totais","Per capita"],horizontal=True)


df = pd.read_excel("dados.xlsx",sheet_name="7.base_trim_ufs")

label_col = 'desc_uf'

agregacao_a = st.sidebar.radio("Agregação", ("Trimestre", "Ano"),
                               format_func=lambda x: {"Trimestre":"Trimestral", "Ano":"Anual"}[x],
                               horizontal=True)


if agregacao_a == "Ano":
    agregacao = st.sidebar.selectbox("Ano", df["ano"].unique(), index=len(df["ano"].unique())-1)

    df = df[df["ano"] == agregacao]\
            .groupby(['sigla_uf'], as_index=True).sum(numeric_only=True)\
            .drop(['ano','trim'],axis=1)
    

else:
    agregacao = st.sidebar.selectbox("Trimestre", df["trim_ano"].unique(),index=len(df["trim_ano"].unique())-1)
    
    df = df[df["trim_ano"] == agregacao]\
        .set_index(['sigla_uf'], drop=False)\
        .drop(df.columns[:9],axis=1)
    

subtitle = f"{f'{agregacao[0]}º Trimestre {agregacao[2:]}' if agregacao_a == 'Trimestre' else agregacao} "
subtitle_placeholder.subheader(subtitle)


### Graficos ###

if tipo_emissao == "Totais":
    total = f"emissao_total_{'c' + ciclo if ciclo == 'diesel' else ciclo}_tco2"
    evitada = f"emissao_evitada_{'c' + ciclo if ciclo == 'diesel' else ciclo}_tco2"

else:
    total = f"emissao_per_capita_{'c' + ciclo if ciclo == 'diesel' else ciclo}"
    evitada = f"emissao_evitada_per_capita_{'c' + ciclo if ciclo == 'diesel' else ciclo}"

df = df[[total,evitada]]
for col in df.columns:
    df[f'formated_{col}'] = df[col].apply(millify_nodecimals)

#emissoes totais 
fig = px.bar(df.sort_values(total),y=total, 
             labels={total:"Emissões Totais","sigla_uf":"Unidade Federativa",f'formated_{total}':'Emissões Totais'},
             text=f"formated_{total}",
             title=f"Emissões Totais de Gases de Efeito Estufa por UF | Ciclo {ciclo}, {subtitle}"
             )

st.plotly_chart(fig,use_container_width=True)

#emissoes per capita 
fig = px.bar(df.sort_values(evitada),y=evitada, 
             labels={evitada:"Emissões Evitadas","sigla_uf":"Unidade Federativa",f'formated_{evitada}':'Emissões Evitadas'},
             text=f"formated_{evitada}",
             title=f"Emissões Evitadas por Combustíveis Renováveis por UF | Ciclo {ciclo}, {subtitle}"
             )

st.plotly_chart(fig,use_container_width=True)