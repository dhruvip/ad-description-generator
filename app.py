import streamlit as st
import json
from generator import generator, copy_and_clean_session_obj

def set_generate():
    st.session_state.generate = True

def reset_session_obj():
    for k, v in st.session_state.items():
        if k in ['transmission','body','fuel_type']:
            #  fuel_type: diesel\n- condition: New\n- transmission: manual\n- body: saloon
            st.session_state[k] = ''

debug = True

st.title("Ad Description Generator")

# Sidebar
st.sidebar.title("Ad Properties")
category = st.sidebar.selectbox("Select Category",options=["Cars", "Mobiles", "Motorbikes"],key="category")
st.sidebar.selectbox("Select Language", options=["English","Sinhala", "Bangla"],key="language")
st.sidebar.selectbox("Select Location", options=["Ampara", "Anuradhapura", "Badulla", "Batticaloa", "Colombo", "Galle", "Gampaha", "Hambantota", "Jaffna", "Kalutara", "Kandy", "Kegalle", "Kilinochchi", "Kurunegala", "Mannar", "Matale", "Matara", "Monaragala", "Mullaitivu", "Nuwara Eliya", "Polonnaruwa", "Puttalam", "Ratnapura", "Trincomalee", "Vavuniya", "Sigiriya", "Kandy", "Galle", "Colombo", "Nuwara Eliya", "Arugam Bay", "Anuradhapura", "Yala National Park", "Ella", "Dambulla", "Mirissa", "Polonnaruwa", "Bentota", "Hikkaduwa", "Trincomalee", "Negombo", "Jaffna", "Unawatuna", "Adam's Peak", "Udawalawe National Park"],key="location")

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
        description_gpt4o, prompt, cd_gpt4o = generator(st.session_state, model='gpt-4o')
        description_gpt35, prompt, cd_gpt35 = generator(st.session_state, model='gpt-3.5-turbo')
        description_gpt4omini, prompt, cd_gpt4omini = generator(st.session_state, model='gpt-4o-mini')
        description_mistral, prompt, cd_mistral = generator(st.session_state, model='mistralai')
        set_generate()

st.markdown(':green[**Note: Please refresh the page before changing the category**]')

tab1, tab2, tab3, tab4 = st.tabs(["Chat Gpt 4o", "Chat GPt 3.5", "Chat GPT 4.0 mini","Mistral"])

with tab1 :
    if 'generate' not in st.session_state:
        st.write("Select Ad attributes and click on generate")
    else:
        st.write(description_gpt4o)
        st.markdown(f':red[{cd_gpt4o}]')
with tab2 :
    if 'generate' not in st.session_state:
        st.write("Select Ad attributes and click on generate")
    else:
        st.write(description_gpt35)
        st.markdown(f':red[{cd_gpt35}]')
with tab3 :
    if 'generate' not in st.session_state:
        st.write("Select Ad attributes and click on generate")
    else:
        st.write(description_gpt4omini)
        st.markdown(f':red[{cd_gpt4omini}]')
with tab4 :
    if 'generate' not in st.session_state:
        st.write("Select Ad attributes and click on generate")
    else:
        st.write(description_mistral)
        st.markdown(f':red[{cd_mistral}]')

if debug:
    st.json(st.session_state)
    st.markdown(prompt)

