import streamlit as st

st.logo('data/logo.png', icon_image='data/logo.png',size='large')
st.set_page_config(page_title="Saiba Mais", page_icon="data/favicon.ico", layout="wide")

st.title("QUEM SOMOS")
st.markdown("---")

st.markdown("""
Esse painel faz parte da plataforma criada pelo **Observatório do Conhecimento e Inovação em Bioeconomia** da **Fundação Getulio Vargas** para acompanhar as emissões de gases causadores do **efeito estufa na matriz de combustíveis no Brasil**.
""")

st.link_button("Saiba Mais",
                "https://agro.fgv.br/")



### download button ###
st.sidebar.markdown("---")

with open("data/dados.xlsx", "rb") as file:
    st.sidebar.download_button(
        label="Download Excel file",
        data=file,
        file_name="Biocombustiveis-OCBIO.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
