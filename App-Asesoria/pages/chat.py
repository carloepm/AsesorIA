import streamlit as st
from clase_sql_nosql import CassandraDBChatCMessageHistory, SQLServerAsesorC ,AsesorManager ,conexion_cassandra, conexion_cassandra_vector, cargar_vector_store, conexion_sql_server, SQLServerArchivos
from clase_retrievers import CrearRetriever
from langchain.callbacks.base import BaseCallbackHandler
from langchain.schema import HumanMessage, AIMessage
from streamlit_option_menu import option_menu
import os


#APY COHERE
os.environ["COHERE_API_KEY"] = "qFSFzqm0wVLj8xESzbNy2qJk4BDVRLAgZBT24OP0"

#CONEXION SQL SERVER
conexion = conexion_sql_server()
#CLASE SQL ARCHIVOS
archivos = SQLServerArchivos(conexion)

st.set_page_config(page_title='Chat', page_icon=':speech_balloon:')
clase_sql_asesor = SQLServerAsesorC(conexion)
clase_asesor = AsesorManager(conexion)

class StreamHandler(BaseCallbackHandler):
    def __init__(self, container, initial_text=""):
        self.container = container
        self.text = initial_text

    def on_llm_new_token(self, token: str, **kwargs):
        self.text += token
        self.container.markdown(self.text + "▌")

# Conexion a Cassandra
secure_connect = 'C:/Users/nicos/Downloads/secure-connect-asesoria (1).zip'
token = "C:/Users/nicos/Downloads/asesoria-token (1).json"
session = conexion_cassandra(secure_connect, token)

#Chat History
historial = CassandraDBChatCMessageHistory(session)

#Conexion Cassandra VectorStore
db = conexion_cassandra_vector()

# TRAER VECTOR STORE PARA GUARDAR DOCUMENTOS
if '_vector_store' in st.session_state and st.session_state['_vector_store']:
    _vector_store = st.session_state['_vector_store']

_vector_store = st.session_state.get('_vector_store')

CorreoUsuario = st.session_state['user_email']

# Obtener sesiones de chat
sesiones = historial.obtener_sesiones()
lista_sesiones = []
for sesion in sesiones:
    lista_sesiones.append(sesion[0])
st.write(lista_sesiones)

st.title("Tu Asesoría personal ha llegado..")
st.markdown("""La IA generativa es considerada como la nueva revolución industrial.
¿Por qué? Estudios más recientes muestran un **37% de eficiencia** en las actividades laborales y cotidianas.""")

# BOTON MENU
with st.sidebar:
    selected = option_menu("Main Menu", ['Asesores', 'Chat'], 
        icons=['house', 'chat'], menu_icon="cast", default_index=1)
    if selected == "Asesores":
        st.switch_page('C:/Dropbox/AsesorAI-Gemini/App-Asesoria/pages/page_asesor.py')
    elif selected == 'Chat':
        pass

# FORMULARIO PARA SUBIR DATOS
st.sidebar.title("Agregar conocimientos")
with st.sidebar:
    with st.form('upload'):
        documentos = st.file_uploader('Proporciona documentación adicional para establecer más contexto', type=['pdf'])
        submitted = st.form_submit_button('Almacenar en tus datos')
        if submitted:
            NombreArchivo = documentos.name
            TipoArchivo = documentos.type
            ID_Asesor_C = archivos.obtener_id_asesor_c(CorreoUsuario)
            documentos.name = documentos.name + str(ID_Asesor_C)
            retrievers = CrearRetriever(documentos)
            archivo_ids = retrievers.vectorize_text(documentos, _vector_store, NombreArchivo, ID_Asesor_C)
            archivo_datastax = archivo_ids[0]
            total_ids = archivo_ids[1]
            add_archivo = archivos.add_archivo(NombreArchivo, TipoArchivo, ID_Asesor_C, archivo_datastax, total_ids)

# ASESOR SELECCIONADO
st.sidebar.title("Asesor seleccionado:")
if 'nombre_asesor_seleccionado' in st.session_state and st.session_state['nombre_asesor_seleccionado']:
    nombre_asesor = st.session_state['nombre_asesor_seleccionado']
    st.sidebar.markdown(f"**Asesor:** {nombre_asesor}")

# PARTITION_ID DE ASESOR SELECCIONADO
if 'partition_id' in st.session_state and st.session_state['partition_id']:
    session = st.session_state['partition_id']

session = st.session_state.get('partition_id')

# NOMBRE CHAT
if 'nombre_chat' in st.session_state and st.session_state['nombre_chat']:
    nombre_chat = st.session_state['nombre_chat']

nombre_chat = st.session_state.get('nombre_chat')

# TRAER OBJETO ASESOR
if 'nuevo_asesor' in st.session_state and st.session_state['nuevo_asesor']:
    nuevo_asesor = st.session_state['nuevo_asesor']

nuevo_asesor = st.session_state.get('nuevo_asesor')

# SESION DE CHAT DEL ASESOR SELECCIONADO
st.sidebar.title("Sesion de chat:")
st.sidebar.markdown(f"**Chat:** {nombre_chat}")
session_selected = session


st.sidebar.title("Usuario registrado")
if 'logged_in' in st.session_state and st.session_state['logged_in']:
    user_email = st.session_state['user_email']
    st.sidebar.markdown(f"**Usuario:** {user_email}")

# Mostrar el historial de chat correspondiente cuando se selecciona una sesión
if session_selected:
    chat_sesion = historial.get_chat_history(session_selected)
    if not chat_sesion:
        msj_entrada = st.chat_message("assistant")
        msj_entrada.write("Hola! Bienvenido a ASESOR AI, ¡trabajemos juntos para el mejor desarrollo!")
        msj_entrada = st.write(f"Bienvenido a tu **Chat de {nombre_chat}**. ",
    "Has creado a tu propio asesor personal, destinado a asistirte y ayudarte en diferentes tareas que necesites. "
    "Recuerda que puedes agregar conocimientos para que puedas obtener asesoría de calidad. "
    "También hay un equipo de profesionales con el objetivo de atender tus dudas puntuales. "
    "Disfruta este camino con la mejor asesoría.")
    else:
        for mensaje in chat_sesion:
            if isinstance(mensaje, HumanMessage):
                with st.chat_message('human'):
                    st.write("Usuario:", mensaje.content)
            elif isinstance(mensaje, AIMessage):
                with st.chat_message('assistant'):
                    st.write("Asesor:", mensaje.content)
            st.write("---")
# Draw the chat input box
    if question := st.chat_input("Consulta asesor"):
    
    # Store the user's question in a session object for redrawing next time
        historial.add_user_msj(session_selected, question)

    # Draw the user's question
        with st.chat_message('human'):
            st.markdown(question)

    # UI placeholder to start filling with agent response
        with st.chat_message('assistant'):
            response_placeholder = st.empty()

        inputs = {
        'input': question,
        'chat_history': chat_sesion}

        result = nuevo_asesor.invoke(inputs, config={'callbacks': [StreamHandler(response_placeholder)]})

        answer = result["output"]

    # Store the bot's answer in a session object for redrawing next time
        historial.add_ai_msj(session_selected, answer)

    # Write the final answer without the cursor
        response_placeholder.markdown(answer)