# Librerias
import streamlit as st
from clase_sql_nosql import SQLServerUsuarios,SQLServerAsesorC ,AsesorManager,conexion_sql_server

# Conexion SQL Server & Clases
conexion = conexion_sql_server()
clase_usuarios = SQLServerUsuarios(conexion)
clase_asesores = AsesorManager(conexion)
clase_sql_asesores = SQLServerAsesorC(conexion)

st.set_page_config(page_title='Streamlit', page_icon='🐍', initial_sidebar_state='collapsed')
# Session State login
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'user_email' not in st.session_state:
    st.session_state['user_email'] = None

st.title("Bienvenido a :blue[ASESOR AI]")
st.markdown("""Unite a la mejor asesoría con IA Generativa.  
Por qué? Estudios más recientes muestran un **37% de eficiencia** en las actividades laborales y cotidianas!""")

with st.form(key='login', clear_on_submit=False):
    st.subheader(':green[Sing In]')
    CorreoUsuario = st.text_input(':blue[Correo]', placeholder='Correo')
    if CorreoUsuario:
        CorreoUsuario_login = CorreoUsuario
        if clase_usuarios._verificar_correo(CorreoUsuario):
            st.success(':green[Correo válido.]')
        else:
            st.error(':red[Correo erróneo o no esta registrado.]')
    
    Contraseña = st.text_input(':blue[Contraseña]', placeholder='Contraseña', type= 'password')
    if Contraseña:
        Contraseña_login = Contraseña
        if clase_usuarios.validar_login(CorreoUsuario, Contraseña):
            st.success(':green[Ingreso exitoso, bienvenido..]')
            st.session_state['logged_in'] = True
            st.session_state['user_email'] = CorreoUsuario

            ID_Usuario = clase_sql_asesores.obtener_id_usuario(CorreoUsuario)
            asesor_exists = clase_asesores.obtener_asesor_personal(ID_Usuario)
            if asesor_exists is not None:
                st.switch_page('C:/Dropbox/AsesorAI-Gemini/App-Asesoria/pages/page_asesor.py')
        #CONDICIONAL SI TIENE ASESORES CREADOS PARA DERIVAR A CHAT DONDE TENDRA MENU PARA CREAR ASESOR O SELECCIONAR EXISTENTE
            else:
        #**CADA PATH ES DIFERENTE DEBIDO A LA LOCALIDAD DE CADA REPOSITORIO "LOCAL"**
                st.switch_page('C:/Dropbox/AsesorAI-Gemini/App-Asesoria/pages/page_asesor.py')
        else:
            st.error(':red[Contraseña errónea.]')

    login_button = st.form_submit_button('Ingresar')

signup = False
# Inicializar Session State
if 'NombrePlan' not in st.session_state:
    st.session_state['NombrePlan'] = 'value'
    
# Botones de planes
def handle_plan_free():
    st.session_state["NombrePlan"] = "Plan Free"

def handle_plan_premium():
    st.session_state["NombrePlan"] = "Plan Premium"

def handle_plan_pro():
    st.session_state["NombrePlan"] = "Plan Pro"


st.header('Que esperás para unirte a nosotros? Crea una cuenta personal para la mejor asesoría.')
st.subheader("""Contamos el plan gratuito más completo del mercado, lo demas **es INCREIBLE**""")

# Crear los botones con la opción on_click
col1, col2, col3 = st.columns(3)
if col1.button(":blue[Plan Free]", key='plan_free'):
    handle_plan_free()
if col2.button(":green[Plan Premium]", key='plan_premium'):
    handle_plan_premium()
if col3.button(":orange[Plan Pro]", key='plan_pro'):
    handle_plan_pro()


# Mostrar el valor de la variable
NombrePlan = st.session_state.get("NombrePlan", None)

# Formulario
with st.form(key='signup', clear_on_submit=False):
    st.subheader(':green[Sign Up]')
    NombreUsuario = st.text_input(':blue[Nombre]', placeholder='Nombre')
    if NombreUsuario:
        NombreUsuario_value = NombreUsuario
        if clase_usuarios._verificar_nombre(NombreUsuario):
            st.error(":red[Ingrese un nombre de usuario diferente.]")
        else:
            st.success(":green[Usuario valido]")
            st.info("Nuevo usuario: " + NombreUsuario)

    CorreoUsuario = st.text_input(':blue[Correo]', placeholder='Correo')
    if CorreoUsuario:
        CorreoUsuario_value = CorreoUsuario
        if clase_usuarios._verificar_correo(CorreoUsuario):
            st.error(":red[Correo electrónico existente.]")
        else:
            st.success(":green[Correo valido.]")
            st.info("Correo registrado: " + CorreoUsuario)

    Contraseña = st.text_input(':blue[Contraseña]', placeholder='Contraseña', type='password')
    if Contraseña:
        Contraseña_value = Contraseña
        valid = clase_usuarios._verificar_contraseña(Contraseña)
        if not valid:
            st.error(print(":red[Contraseña Incorrecta]"))
        else:
            st.success(":green[Contraseña correcta.]")

    valid_user = clase_usuarios._verificar_nombre(NombreUsuario)
    valid_correo = clase_usuarios._verificar_correo(CorreoUsuario)
    valid = clase_usuarios._verificar_contraseña(Contraseña)
  
    # Verificar si todos los campos están completos y si son validos
    if NombreUsuario and CorreoUsuario and Contraseña and NombrePlan and valid_user == False and valid_correo == False and valid:
        signup = True
    else:
        signup = False
    
    # Agregar un botón de envío al final del formulario
    submit_button = st.form_submit_button("Registrar")
    if submit_button and signup:
            autenticacion = clase_usuarios.add_usuario(NombreUsuario, CorreoUsuario, NombrePlan, Contraseña)
            st.success(":green[Registro exitoso.]")
#            st.session_state['logged_in'] = True
#            st.session_state['user_email'] = CorreoUsuario
#            st.switch_page('C:/Dropbox/AsesorsIA/App-Asesoria/pages/page_asesor.py')
                
    else:
        st.error(":red[Revisar registro: Datos faltantes o erroneos.]")

