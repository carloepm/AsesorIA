import streamlit as st
from clase_sql_nosql import SQLServerUsuarios ,conexion_sql_server, SQLServerAsesorC, AsesorManager, SQLServerChatC, cargar_vector_store, SQLServerArchivos
from clase_retrievers import CrearRetriever
import os
from streamlit_option_menu import option_menu
from clase_sql_nosql import CassandraDBChatCMessageHistory ,conexion_cassandra, conexion_cassandra_vector
from langchain.callbacks.base import BaseCallbackHandler
from langchain.schema import HumanMessage, AIMessage
from streamlit_option_menu import option_menu


# TITULO PAGINA
st.set_page_config(page_title='AsesorAI', page_icon='🐍', initial_sidebar_state='collapsed')

# API KEYS
os.environ["GOOGLE_API_KEY"] = "AIzaSyDqb0m1iFyZs8p1sDpwfTGt34FZO8_hN5Y"
os.environ["SERPER_API_KEY"] = "8b139823f4e8976b14208e65520107b9ba3607fa"
os.environ["COHERE_API_KEY"] = "qFSFzqm0wVLj8xESzbNy2qJk4BDVRLAgZBT24OP0"

# CONEXION SQL SERVER
conexion = conexion_sql_server()

# SESSION STATE VECTOR STORE
if '_vector_store' not in st.session_state:
    st.session_state['_vector_store'] = None

_vector_store = cargar_vector_store()
st.session_state['_vector_store'] = _vector_store

# DECLARAR RETRIEVER
def load_retriever(_vector_store):
        retriever = _vector_store.as_retriever(search_type= 'similarity',search_kwargs={'k': 6}
        )
        return retriever
_retriever = load_retriever(_vector_store)

# CLASES IMPORTADAS
clase_usuarios = SQLServerUsuarios(conexion)
clase_sqlasesor = SQLServerAsesorC(conexion)
clase_sql_chat = SQLServerChatC(conexion)
clase_asesor = AsesorManager(conexion)
clase_archivos = SQLServerArchivos(conexion,_vector_store)


# SESSION STATE USUARIO
if 'user_email' in st.session_state and st.session_state['user_email']:
    CorreoUsuario = st.session_state.get('user_email')

CorreoUsuario = st.session_state.get('user_email')

# SESSION STATE NOMBRE_ASESOR, PARTITION_ID, NOMBRE_CHAT, NUEVO_ASESOR(IA)
if 'nombre_asesor_seleccionado' not in st.session_state:
    st.session_state['nombre_asesor_seleccionado'] = None

if 'partition_id' not in st.session_state:
    st.session_state['partition_id'] = None

if 'nombre_chat' not in st.session_state:
    st.session_state['nombre_chat'] = None

if 'nuevo_asesor' not in st.session_state:
    st.session_state['nuevo_asesor'] = None

if 'lista_archivos' not in st.session_state:
    st.session_state['lista_archivos'] = []

# BOTONES MENU
with st.sidebar:
    selected = option_menu("Main Menu", ['Nuevo Asesor', 'Asesores', 'Chat'], 
        icons=['house', 'gear', 'chat'], menu_icon="cast", default_index=0)

# MARKDOWN DE USUARIO REGISTRADO
if 'logged_in' in st.session_state and st.session_state['logged_in']:
    # Mostrar el correo del usuario en la barra lateral
    st.sidebar.markdown(f"**Usuario:** {st.session_state['user_email']}")

# CONTAINER DE OPCIONES DE MENU
add_asesor = False
if selected == "Nuevo Asesor":
    st.title("Crear nuevo asesor personal..")
    st.markdown("""Recorda que cada asesor esta programado para trabajar especificamente en las sesiones que tu desees..  
    Por ende el nombre y la descripcion son muy importantes""")
    with st.form(key="Crea tu Asesor personal", clear_on_submit=False):
        st.subheader(":green[Asesor]")
        NombreAsesorC = st.text_input(":blue[Nombre Asesor]", placeholder="Asesor")
        if NombreAsesorC:
            NombreAsesorC_value = NombreAsesorC
            verif_asesor = clase_sqlasesor.verificar_asesor(NombreAsesorC)
            if verif_asesor == False:
                st.success(":green[Asesor valido.]")
            else:
                st.error(":red[Nombre no valido.]")
    
        Descripcion = st.text_input(":blue[Descripcion]", placeholder='Descripcion')
        if Descripcion:
            Descripcion_value = Descripcion
            st.success(":green[Descripcion valida.]")
        else:
            st.error(":red[Descripcion faltante.]")
        NombreChat = st.text_input(":blue[Chat]", placeholder='Chat')
        if NombreChat:
            NombreChat_value = NombreChat
            verif_chat = clase_sql_chat.verificar_nombre_chat(NombreChat)
            if verif_chat:
                st.success(":green[Chat valido]")
            else:
                st.error(":red[Chat no valido.]")
            if verif_asesor == False and verif_chat:
                add_asesor = True
            else:
                add_asesor = False
    
        submit_button_chat = st.form_submit_button('Crear Asesor')
        if add_asesor == True and submit_button_chat:
            add_registro_asesor = clase_sqlasesor.add_asesor_C(NombreAsesorC, Descripcion, CorreoUsuario)
            add_registro_chat = clase_sql_chat.add_chat(NombreChat, CorreoUsuario, NombreAsesorC)
            st.success(":green[Asesor creado exitosamente]")
        else:
            st.error(":red[Error al crear Asesor]")

elif selected == 'Asesores':
    st.title("Asesor/es:")
    CorreoUsuario = st.session_state['user_email']
    ID_Usuario = clase_sqlasesor.obtener_id_usuario(CorreoUsuario)
    lista_asesores = clase_asesor.obtener_asesor_personal(ID_Usuario)

        # LISTA DE ASESORES PARA EL SELECTOR DE ASESORES
    nombres_asesores = [asesor[0] for asesor in lista_asesores]
    descripcion_asesores = [asesor[1] for asesor in lista_asesores]
        # SELECCION DE ASESOR, QUE EN SI ES LA RECUPERACION DEL CHAT
    nombre_asesor_seleccionado = st.radio("Seleccionar asesor:", nombres_asesores, index=None)
        
    if nombre_asesor_seleccionado:
            # ASESOR Y PARTITION_ID
        asesor_info = next((asesor for asesor in lista_asesores if asesor[0] == nombre_asesor_seleccionado), None)
        st.session_state['nombre_asesor_seleccionado'] = asesor_info[0]
        st.session_state['nombre_chat'] = asesor_info[-2]
        st.session_state['partition_id'] = asesor_info[-1] # El partition_id es el último elemento de la tupla
        nuevo_asesor = clase_asesor.asignar_asesor_personal(_retriever)
        st.session_state['nuevo_asesor'] = nuevo_asesor
        lista_documentos_sql = clase_archivos.lista_documentacion_sql(CorreoUsuario, NombreAsesorC=nombre_asesor_seleccionado)
            # LISTA DESPLEGABLE PARA SELECCIONAR DOCUMENTOS SI LOS HAY.
        if lista_documentos_sql == False:
            st.info("Documentos: Sin documentos")
            st.info(f"Descripción: {asesor_info[1]}")
        else:
            lista_documentos_nosql = clase_archivos.lista_documentacion_nosql(lista_documentos_sql)
            opciones_docs = st.selectbox('Documentos', lista_documentos_nosql)
            st.info(f"Descripción:  {asesor_info[1]}")
                # POSIBILIDAD DE BORRAR DOCUMENTO SELECCIONADO.
            if st.button('Borrar Documento'):
                archivo_y_ids = clase_archivos.obtener_datos_archivo(NombreArchivo=opciones_docs)
                lista_ids = clase_archivos.generador_ids(archivo_y_ids)
                eliminar_doc = clase_archivos.eliminar_documento(lista_ids, NombreArchivo=opciones_docs)
                st.success(f":green[Archivo: {opciones_docs} borrado correctamente.]")

elif selected == 'Chat':
    nombre_asesor_seleccionado = st.session_state.get('nombre_asesor_seleccionado')
    if nombre_asesor_seleccionado:
    
        # CONEXION CASSANDRA DB CHAT HISTORY
        secure_connect = 'C:/Users/nicos/Downloads/secure-connect-asesoria (1).zip'
        token = "C:/Users/nicos/Downloads/asesoria-token (1).json"
        session = conexion_cassandra(secure_connect, token)

                # CHAT HISTORY
        historial = CassandraDBChatCMessageHistory(session)

                #Conexion Cassandra VectorStore
        db = conexion_cassandra_vector()

            # TRAER VECTOR STORE PARA GUARDAR DOCUMENTOS (VER SI ES NECESARIO)
            #if '_vector_store' in st.session_state and st.session_state['_vector_store']:
            #     _vector_store = st.session_state['_vector_store']

        _vector_store = st.session_state.get('_vector_store')

        CorreoUsuario = st.session_state['user_email']

                # OBTENER SESIONES DE CHAT
            #sesiones = historial.obtener_sesiones()
            #lista_sesiones = []
            #for sesion in sesiones:
            #    lista_sesiones.append(sesion[0])
                

        st.title("Tu Asesoría personal ha llegado..")
        st.markdown("""La IA generativa es considerada como la nueva revolución industrial.
            ¿Por qué? Estudios más recientes muestran un **37% de eficiencia** en las actividades laborales y cotidianas.""")


                # FORMULARIO PARA SUBIR DATOS
        st.sidebar.title("Agregar conocimientos")
        with st.sidebar:
            with st.form('upload'):
                documentos = st.file_uploader('Proporciona documentación adicional para establecer más contexto', type=['pdf'])
                submitted = st.form_submit_button('Almacenar en tus datos')
                if submitted:
                    NombreArchivo = documentos.name
                    TipoArchivo = documentos.type
                    ID_Asesor_C = clase_archivos.obtener_id_asesor_c(CorreoUsuario, NombreAsesorC=nombre_asesor_seleccionado)
                    documentos.name = documentos.name + str(ID_Asesor_C)
                    retrievers = CrearRetriever(documentos)
                    archivo_ids = retrievers.vectorize_text(documentos, _vector_store, NombreArchivo, ID_Asesor_C)
                    archivo_datastax = archivo_ids[0]
                    total_ids = archivo_ids[1]
                    add_archivo = clase_archivos.add_archivo(NombreArchivo, TipoArchivo, ID_Asesor_C, archivo_datastax, total_ids)

                # ASESOR SELECCIONADO
        st.sidebar.title("Asesor seleccionado:")
            #if 'nombre_asesor_seleccionado' in st.session_state and st.session_state['nombre_asesor_seleccionado']:
            #    nombre_asesor_seleccionado = st.session_state['nombre_asesor_seleccionado']
        st.sidebar.markdown(f"**Asesor:** {nombre_asesor_seleccionado}")

                # PARTITION_ID DE ASESOR SELECCIONADO
                #if 'partition_id' in st.session_state and st.session_state['partition_id']:
                #    session = st.session_state['partition_id']

        session = st.session_state.get('partition_id')
                
            # NOMBRE CHAT
            #if 'nombre_chat' in st.session_state and st.session_state['nombre_chat']:
            #    nombre_chat = st.session_state['nombre_chat']
        nombre_chat = st.session_state.get('nombre_chat')

                # TRAER OBJETO ASESOR
            #if 'nuevo_asesor' in st.session_state and st.session_state['nuevo_asesor']:
            #    nuevo_asesor = st.session_state['nuevo_asesor']

        nuevo_asesor = st.session_state.get('nuevo_asesor')

                # SESION DE CHAT DEL ASESOR SELECCIONADO
        st.sidebar.title("Sesion de chat:")
        st.sidebar.markdown(f"**Chat:** {nombre_chat}")
        session_selected = session


        st.sidebar.title("Usuario registrado")
            #if 'logged_in' in st.session_state and st.session_state['logged_in']:
        user_email = st.session_state.get('user_email')
        st.sidebar.markdown(f"**Usuario:** {user_email}")

        class StreamHandler(BaseCallbackHandler):
            def __init__(self, container, initial_text=""):
                self.container = container
                self.text = initial_text

            def on_llm_new_token(self, token: str, **kwargs):
                self.text += token
                self.container.markdown(self.text + "▌")

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
    else:
        st.warning("Seleccionar Asesor para poder ingresar al chat")