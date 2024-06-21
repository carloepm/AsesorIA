import time
import streamlit as st
def disable():
    st.session_state.disabled = True

def enable():
    if "disabled" in st.session_state and st.session_state.disabled == True:
        st.session_state.disabled = False

if "disabled" not in st.session_state:
    st.session_state.disabled = False

# Create the form
with st.form("my_form"):
    keyword = st.text_input('Product Name?')
    placeholder = st.empty()
    placeholder.text("")


    chk_scrap = st.checkbox('Fenix Scraping')
    chk_image = st.checkbox('Download Image')
    chk_fb = st.checkbox('Facebook')
    chk_caro = st.checkbox('Carousell')

    submitted = st.form_submit_button("Submit", on_click=disable, disabled=st.session_state.disabled)

if submitted:
    if chk_scrap:
        if keyword:
            try:
                # Simulating a lengthy running job
                time.sleep(5)
                st.success("Fenix Scraping completed successfully")
            except Exception as e:
                st.warning(e)
        else:
            st.warning('Please enter product name!')

    if chk_image:
        if keyword:
            try:
                # Simulating a lengthy running job
                time.sleep(5)
                st.success("Image download completed successfully")
            except Exception as e:
                st.warning(e)
        else:
            st.warning('Please enter product name!')

# Enable the submit button after the jobs have completed
enable()


import streamlit as st
from streamlit_option_menu import option_menu

# 1. as sidebar menu
with st.sidebar:
    selected = option_menu("Main Menu", ['Asesores', 'Chat'], 
        icons=['house', 'gear'], menu_icon="cast", default_index=0)
    if selected == "Asesores":
#        st.switch_page('C:/Dropbox/AsesorAI-Gemini/App-Asesoria/pages/page_asesor.py')
        st.write('Asesores')
    elif selected == 'Chat':
        st.write('chat')
#        st.switch_page('C:/Dropbox/AsesorAI-Gemini/App-Asesoria/pages/chat.py')

    

# 4. Manual item selection
#if st.session_state.get('switch_button', False):
#    st.session_state['menu_option'] = (st.session_state.get('menu_option', 0) + 1) % 4
#    manual_select = st.session_state['menu_option']
#else:
#    manual_select = None
    
