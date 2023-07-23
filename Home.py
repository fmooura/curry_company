import streamlit as st
from PIL import Image

st.set_page_config(
    page_title="Home"
)

#image_path = '/Users/conta/'
image = Image.open('logo.png')
st.sidebar.image(image, width=120)
st.sidebar.markdown('# Cury Company')
st.sidebar.markdown('### O melhor da região!')
st.sidebar.markdown("""---""")

st.write("# Curry Company Dashboard")
st.markdown(
    """ Esse dashboard foi criado pra teste. Existem varias abas e varios dados""")

    