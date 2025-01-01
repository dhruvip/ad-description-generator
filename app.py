import streamlit as st
import json
from generator import generator, copy_and_clean_session_obj

debug = True
st.title("Ad Description Generator")

# Sidebar
st.sidebar.title("Ad Properties")
category = st.sidebar.selectbox("Select Category",options=["Cars", "Mobiles"],key="category")
st.sidebar.selectbox("Select Language", options=["English","Sinhala", "Bangla"],key="language")


with open(f'./classifications/{category}.json') as f:
    menu = json.load(f)
selected = {}
for _each in menu:
    if _each["type"] == 'selectbox':
        st.sidebar.selectbox(_each["name"], 
                             options=_each["options"],
                             key=_each["key"])
    elif _each["type"] == 'text_input':
        st.sidebar.text_input(_each["name"], key=_each["key"])
    elif _each["type"] == "multiselect":
        st.sidebar.multiselect(_each["name"],
                               options=_each["options"],
                               key=_each["key"])
col1, col2 = st.columns(2)
debug = col2.checkbox("Debug")
if col1.button('Generate',icon="💀", type="primary",use_container_width=False):
    with st.spinner('Generating...'):  
        description, prompt = generator(st.session_state)
        st.write(description)

if debug:
    st.json(st.session_state)
    st.markdown(prompt)
