import math
import streamlit as st

millnames = ['',' Mil',' Mi',' Bi',' Tri']

def millify(n):
    n = float(n)
    millidx = max(0,min(len(millnames)-1,
                        int(math.floor(0 if n == 0 else math.log10(abs(n))/3))))

    return '{:.2f}{}'.format(n / 10**(3 * millidx), millnames[millidx])


@st.cache_data
def convert_for_download(df):
    return df.to_csv().encode("utf-8")
