import streamlit as st
import pandas as pd 
import plotly.express as px
import plotly.graph_objects as go

st.logo('data/logo.png', icon_image='data/logo.png',size='large')
st.set_page_config(page_title="Descarbonização da Matriz de Combustíveis", page_icon="data/favicon.ico", layout="wide")

st.title("Descarbonização da Matriz de Combustíveis")
subtitle_placeholder = st.empty()


#### Filtros e Dados ####

ciclo = st.sidebar.radio("Ciclo", ("OTTO", "Diesel","Comparativo"),horizontal=True).lower()

abrangencia = st.sidebar.radio("Abrangência", ("Nacional", "Regional"),horizontal=True)

if abrangencia == "Nacional":
    df = pd.read_excel("data/dados.xlsx",sheet_name="8.base_trim_br")
    label_col = 'pais'
    regiao = 'BRASIL'

else:
    df = pd.read_excel("data/dados.xlsx",sheet_name="7.base_trim_ufs")

    regiao = st.sidebar.selectbox("Região", df["desc_uf"].unique())
    df =  df[df["desc_uf"] == regiao]
    label_col = 'desc_uf'
    
subtitle =  f"{df['ano'].min()} - {df['ano'].max()} | {regiao.title()}"
st.subheader(subtitle)

if ciclo == "comparativo":

    col_names = {'emissao_total_cdiesel_tco2': "Emissão Total - Diesel (t CO2eq)",
                'emissao_total_otto_tco2': "Emissão Total - Otto (t CO2eq)",
                'emissao_evitada_cdiesel_tco2': "Emissão Evitada - Diesel (t CO2eq)",
                'emissao_evitada_otto_tco2': "Emissão Evitada - Otto (t CO2eq)",
    }

    fig = go.Figure()

    for col, col_name in col_names.items():
        fig.add_trace(go.Scatter(
            x=df.index, 
            y=df[col], 
            name=col_name,
            mode='lines+markers',
        ))

    fig.update_layout(
        title=f"Emissões Totais de GEE e Evitadas por Renováveis por UF | {subtitle}",
        xaxis_title="Trimestre",
        yaxis_title="Emissões (t CO2eq)",
        legend_title="Tipo de Emissão"
    )

    st.plotly_chart(fig,use_container_width=True)

    ### Intensidade de Carbono da Matriz de Combustível ###
    
    fig = go.Figure()

    col_names = {
        "ic_matriz_diesel_gco2_mj": "Diesel (gCO2eq/MJ)",
        "ic_matriz_otto_gco2_mj": "Otto (gCO2eq/MJ)",
    }

    for col, col_name in col_names.items():
        fig.add_trace(go.Scatter(
            x=df.index, 
            y=df[col], 
            name=col_name,
            mode='lines+markers',
        ))

    fig.update_layout(
        title=f"Intensidade Total de Carbono da Matriz de Combustível {subtitle}",
        xaxis_title="Trimestre",
        yaxis_title="gCO2eq/MJ",
        legend_title="Tipo de Combustível",

    )

    st.plotly_chart(fig,use_container_width=True)


else:

    
    total = f"emissao_total_{'c' + ciclo if ciclo == 'diesel' else ciclo}_tco2"
    evitada = f"emissao_evitada_{'c' + ciclo if ciclo == 'diesel' else ciclo}_tco2"
    ic_total = f"ic_matriz_{ciclo}_gco2_mj"

    col_names = {        
            total: "Emissão de GEE (t CO2eq)",
            evitada: "Emissão Evitada (t CO2eq)",

            ic_total: "Total (gCO2eq/MJ)",

            "ic_gasolina_a_gco2_mj": "Gasolina A (gCO2eq/MJ)",
            "ic_etanol_hidratado_gco2_mj": "Etanol Hidratado (gCO2eq/MJ)",
            "ic_etano_anidro_gco2_mj": "Etanol Anidro (gCO2eq/MJ)",
        
            "part_gasolina_a_%": "Gasolina A",
            "part_hidratado_%": "Etanol Hidratado",
            "part_anidro_%": "Etanol Anidro",

            "ic_diesel_gco2_mj": "Diesel (gCO2eq/MJ)",
            "ic_biodiesel_gco2_mj": "Biodiesel (gCO2eq/MJ)",

            "part_diesel_%": "Diesel",
            "part_biodiesel_%": "Biodiesel",}

    df = df.set_index("trim_ano")[list(col_names.keys())]

    ## Gráficos ##

    fig = go.Figure()

    fig.add_trace(go.Scatter(x=df.index, y=df[total], mode='lines+markers', name='Totais'))
    fig.add_trace(go.Scatter(x=df.index, y=df[evitada], mode='lines+markers', name='Evitadas'))

    fig.update_layout(
        title=f"Emissões Totais de GEE e Evitadas por Renováveis por UF | Ciclo {ciclo}, {subtitle}",
        xaxis_title="Trimestre",
        yaxis_title="Emissões (t CO2eq)",
        legend_title="Tipo de Emissão"
    )

    st.plotly_chart(fig,use_container_width=True)


    #intensidade de carbono
    if ciclo == "otto":
        ic_cols = [
            "ic_gasolina_a_gco2_mj",
            "ic_etanol_hidratado_gco2_mj",
            "ic_etano_anidro_gco2_mj",
            ]

    else:
        ic_cols = [
            "ic_diesel_gco2_mj",
            "ic_biodiesel_gco2_mj"
        ]

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df.index, 
        y=df[ic_total], 
        mode='lines+markers',
        name=col_names[ic_total],
        marker=dict(size=10),
    ))

    for col in ic_cols:
        fig.add_trace(go.Scatter(
            x=df.index, 
            y=df[col], 
            name=col_names[col],
            mode='lines+markers',
        ))

    fig.update_layout(
        title=f"Intensidade de Carbono da Matriz de Combustível - Ciclo {ciclo}, {subtitle}",
        xaxis_title="Trimestre",
        yaxis_title="gCO2eq/MJ",
        legend_title="Tipo de Combustível",

    )

    st.plotly_chart(fig, use_container_width=True)

    #participacao 
    if ciclo == "otto":
        ic_cols = ["part_gasolina_a_%",
                "part_hidratado_%",
                "part_anidro_%",]

    else:
        ic_cols = ["part_diesel_%",
                    "part_biodiesel_%"]

    fig = go.Figure()

    for col in ic_cols:

        fig.add_trace(go.Scatter(
            x=df.index, 
            y=df[col]*100, 
            name=col_names[col],
            mode='lines+markers',
        ))

    fig.update_layout(
        title=f"Participação dos Energéticos na Matriz de Combustíveis - Ciclo {ciclo}, {subtitle}",
        xaxis_title="Trimestre",
        yaxis_title="%",
        legend_title="Tipo de Combustível",
    )

    st.plotly_chart(fig, use_container_width=True)



### download button ###
st.sidebar.markdown("---")

with open("data/dados.xlsx", "rb") as file:
    st.sidebar.download_button(
        label="Download Excel file",
        data=file,
        file_name="Biocombustiveis-OCBIO.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
