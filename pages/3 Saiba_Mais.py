import streamlit as st

st.logo('logo.png', icon_image='logo.png',size='large')
st.set_page_config(page_title="Saiba Mais", page_icon="favicon.ico", layout="wide")

st.title("QUEM SOMOS")
st.markdown("---")

st.markdown("""
Esse painel faz parte da plataforma criada pelo **Observatório do Conhecimento e Inovação em Bioeconomia** da **Fundação Getulio Vargas** para acompanhar as emissões de gases causadores do **efeito estufa na matriz de combustíveis no Brasil**.
""")

st.link_button("Saiba Mais",
                "https://agro.fgv.br/")