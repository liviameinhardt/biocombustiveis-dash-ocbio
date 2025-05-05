import streamlit as st
import pandas as pd 
import plotly.express as px

st.logo('data/logo.png', icon_image='data/logo.png',size='large')
st.set_page_config(page_title="Descarbonização da Matriz de Combustíveis", page_icon="data/favicon.ico", layout="wide")

st.title("Descarbonização da Matriz de Combustíveis")
subtitle_placeholder = st.empty()

#### Filtros e Dados ####

ciclo = st.sidebar.radio("Ciclo", ("OTTO", "Diesel","Comparativo"),horizontal=True).lower()

tipo_emissao = st.sidebar.radio("Emissões",["Totais","Per capita"],horizontal=True)
per_capita_label = "Per Capita" if tipo_emissao == "Per capita" else ""

df = pd.read_excel("data/dados.xlsx",sheet_name="7.base_trim_ufs")

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

if ciclo == "comparativo":

    if tipo_emissao == "Totais":
        total = ["emissao_total_cdiesel_tco2", "emissao_total_otto_tco2"]
        evitada = ["emissao_evitada_cdiesel_tco2", "emissao_evitada_otto_tco2"]
    else:
        total = ["emissao_per_capita_cdiesel", "emissao_per_capita_otto"]
        evitada = ["emissao_evitada_per_capita_cdiesel", "emissao_evitada_per_capita_otto"]

    df = df[total + evitada]
    columns_class = {'Totais':total, 'Evitadas':evitada}

    for col in ['Totais','Evitadas']:

        df[col] = df[columns_class[col]].sum(axis=1)

        labels = {columns_class[col][0]:'Diesel', columns_class[col][1]:'Otto'}

        fig = px.bar(df.sort_values(col)\
                            .rename(columns=labels) ,
                    y=['Diesel','Otto'], 
                    text_auto='.2s',
                    labels={"value": f"Emissões {col} {per_capita_label}", "sigla_uf": "Unidade Federativa","variable":"Ciclo"},
                    title=f"Emissões {col} {per_capita_label} de Gases de Efeito Estufa por UF | {subtitle}<br><sup>Comparação Ciclos Diesel e Otto"
                    )

        fig.update_layout(legend=dict(orientation="h",yanchor="bottom",y=1.02,xanchor="right",x=1))

        st.plotly_chart(fig,use_container_width=True)

else:
    
    if tipo_emissao == "Totais":
        total = f"emissao_total_{'c' + ciclo if ciclo == 'diesel' else ciclo}_tco2"
        evitada = f"emissao_evitada_{'c' + ciclo if ciclo == 'diesel' else ciclo}_tco2"
    else:
        total = f"emissao_per_capita_{'c' + ciclo if ciclo == 'diesel' else ciclo}"
        evitada = f"emissao_evitada_per_capita_{'c' + ciclo if ciclo == 'diesel' else ciclo}"

    df = df[[total, evitada]]


    #emissoes totais 
    fig = px.bar(df.sort_values(total),y=total, 
                labels={total:f"Emissões Totais {per_capita_label}","sigla_uf":"Unidade Federativa",f'formated_{total}':'Emissões Totais'},
                text_auto='.2s',
                title=f"Emissões Totais {per_capita_label} de Gases de Efeito Estufa por UF | Ciclo {ciclo}, {subtitle}"
                )

    st.plotly_chart(fig,use_container_width=True)

    #emissoes per capita 
    fig = px.bar(df.sort_values(evitada),y=evitada, 
                labels={evitada:f"Emissões Evitadas {per_capita_label}","sigla_uf":"Unidade Federativa",f'formated_{evitada}':'Emissões Evitadas'},
                text_auto='.2s',
                title=f"Emissões Evitadas {per_capita_label} por Combustíveis Renováveis por UF | Ciclo {ciclo}, {subtitle}"
                )

    st.plotly_chart(fig,use_container_width=True)



### download button ###
st.sidebar.markdown("---")

with open("data/dados.xlsx", "rb") as file:
    st.sidebar.download_button(
        label="Download Excel file",
        data=file,
        file_name="Biocombustiveis-OCBIO.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
