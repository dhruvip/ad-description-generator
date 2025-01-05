import streamlit as st
import json
from generator import generator, copy_and_clean_session_obj

def set_generate():
    st.session_state.generate = True

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
        description_gpt4o, prompt = generator(st.session_state, model='gpt-4o')
        description_gpt35, prompt = generator(st.session_state, model='gpt-3.5-turbo')
        description_gpt4omini, prompt = generator(st.session_state, model='gpt-4o-mini')
        description_mistral, prompt = generator(st.session_state, model='mistralai')
        set_generate()


tab1, tab2, tab3, tab4 = st.tabs(["Chat Gpt 4o", "Chat GPt 3.5", "Chat GPT 4.0 mini","Mistral"])

with tab1 :
    if 'generate' not in st.session_state:
        st.write("Select Ad attributes and click on generate")
    else:
        st.write(description_gpt4o)
with tab2 :
    if 'generate' not in st.session_state:
        st.write("Select Ad attributes and click on generate")
    else:
        st.write(description_gpt35)
with tab3 :
    if 'generate' not in st.session_state:
        st.write("Select Ad attributes and click on generate")
    else:
        st.write(description_gpt4omini)
with tab4 :
    if 'generate' not in st.session_state:
        st.write("Select Ad attributes and click on generate")
    else:
        st.write(description_mistral)

if debug:
    st.json(st.session_state)
    st.markdown(prompt)

