from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider
import json
from langchain.memory import CassandraChatMessageHistory
from astrapy.db import AstraDB
from langchain_astradb import AstraDBVectorStore
import streamlit as st
import pyodbc
import re
from clase_asesores import CrearAsesores
from langchain_cohere import CohereEmbeddings
#from clase_retrievers import CrearRetriever

#FUNCION CARLOS
#def conexion_sql_server():
#   connectionSQLSever = pyodbc.connect("DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost\SQLEXPRESS;DATABASE=ai_project;Trusted_Connection=yes;")
#   conexion = connectionSQLSever
#   return conexion

#conexion = conexion_sql_server()

def conexion_sql_server():
   connectionSQLSever = pyodbc.connect("DRIVER={ODBC Driver 17 for SQL Server};SERVER=DESKTOP-L5TQMM4;DATABASE=ai_project;Trusted_Connection=yes;")
   conexion = connectionSQLSever
   return conexion

conexion = conexion_sql_server()

@st.cache_resource(show_spinner="Conexion Astra")
def conexion_cassandra(secure_connect, token):
  cloud_config= {
    'secure_connect_bundle': secure_connect
      }
  
  with open(token) as f:
      secrets = json.load(f)

  CLIENT_ID = secrets["clientId"]
  CLIENT_SECRET = secrets["secret"]

  auth_provider = PlainTextAuthProvider(CLIENT_ID, CLIENT_SECRET)
  cluster = Cluster(cloud=cloud_config, auth_provider=auth_provider)
  session = cluster.connect()

  row = session.execute("select release_version from system.local").one()
  if row:
    print(row[0])
  else:
    print("An error occurred.")
  return session
st.cache_resource(show_spinner="Connecting to Astra")
def conexion_cassandra_vector():
   db = AstraDB(
       token="AstraCS:DZLNwDFMqTEXaZgXayJLCnNZ:28f5cdba8aff2cfff59b42e86c893f6a841a4669cdf06fc29a6bc6a5d4cffeba",
       api_endpoint="https://9c716385-228f-4a90-9ea5-594d44b69b4b-us-east1.apps.astra.datastax.com",
       namespace="chat_app_vector")
   return(f"Connected to Astra DB: {db.get_collections()}")

@st.cache_resource(show_spinner='Cargar Vector Store')
def cargar_vector_store():
   _vector_store = AstraDBVectorStore(
    embedding= CohereEmbeddings(model="embed-multilingual-v3.0"),
    collection_name="vector_store",
    api_endpoint="https://9c716385-228f-4a90-9ea5-594d44b69b4b-us-east1.apps.astra.datastax.com",
    token="AstraCS:DZLNwDFMqTEXaZgXayJLCnNZ:28f5cdba8aff2cfff59b42e86c893f6a841a4669cdf06fc29a6bc6a5d4cffeba",
    namespace="chat_app_vector")
   return _vector_store

class CassandraDBChatCMessageHistory:
    def __init__(self, session):
        self.session = session

    def obtener_sesion_particular(self, partition_id):
        query_cql_sesion = """SELECT partition_id FROM chat_app.message_store WHERE
                                partition_id = ?"""
        sesion = self.session.execute(query_cql_sesion, (partition_id))
        return sesion
    
    def obtener_sesiones(self):
        query = """SELECT partition_id as Sesiones
                FROM chat_app.message_store
                GROUP BY partition_id;
                """
        lista_sesiones = self.session.execute(query)
        #Retorna True si no existe
        return lista_sesiones
    
    def get_chat_history(self, session_id):
        #METODO DE OBTENCION PARA EL CHAT, **NO PARA LA IA** (EXPLICACION MUY IMPORTANTE)!!
        message_history = CassandraChatMessageHistory(
            session_id=session_id,
            session=self.session,
            keyspace="chat_app",
            )
        chat_history = message_history.messages
        return chat_history
   
    def add_user_msj(self, session_id, question):
       message_history = CassandraChatMessageHistory(
            session_id=session_id,
            session=self.session,
            keyspace="chat_app"
            )
       message_history.add_user_message(question)
       return question
    
    def add_ai_msj(self,session_id, answer):
       message_history = CassandraChatMessageHistory(
          session_id=session_id,
            session=self.session,
            keyspace="chat_app"
            )
       message_history.add_ai_message(answer)
       return answer
    
class SQLServerUsuarios:

    def __init__(self, conexion):
        self.conexion = conexion
        self.max_intentos = 6
        self.intentos = 0  

    def add_usuario(self ,NombreUsuario, CorreoUsuario, NombrePlan, Contraseña):
        self.conexion = conexion_sql_server()
        if self.conexion:
            cursor = self.conexion.cursor()
            try:
                cursor.execute("INSERT INTO Usuarios (NombreUsuario, CorreoUsuario, NombrePlan, Contraseña) VALUES (?, ?, ?, ?)", 
                                (NombreUsuario, CorreoUsuario, NombrePlan, Contraseña))
                self.conexion.commit()                
            except Exception as e:
                print(f"Error al agregar usuario: {e}")
            finally:
                cursor.close()
                self.conexion.close()

    def _verificar_nombre(self, NombreUsuario):
        self.conexion = conexion_sql_server()
        if self.conexion:
            cursor = self.conexion.cursor()
            try:
                cursor.execute("SELECT * FROM Usuarios WHERE NombreUsuario = ?", (NombreUsuario))
                if cursor.fetchone():                    
                    return True
                else: 
                    return False                            
            except Exception as e:
                print(f"Error al verificar nombre de usuario: {e}")
            finally:
                cursor.close()
                self.conexion.close()


    def _verificar_correo(self, CorreoUsuario):
        self.conexion = conexion_sql_server()
        if self.conexion:
            cursor = self.conexion.cursor()
            try:
                cursor.execute("SELECT * FROM Usuarios WHERE CorreoUsuario = ?", (CorreoUsuario))
                if cursor.fetchone():
                    return True
                else: 
                    return False
            except Exception as e:
                print(f"Error al verificar correo: {e}")
            finally:
                cursor.close()
                self.conexion.close()    
        
        
    def _verificar_contraseña(self, Contraseña):
        if self.intentos >= self.max_intentos:
            return False
        
        if (len(Contraseña) < 8 or 
            not re.search("[a-zA-Z]", Contraseña) or 
            not re.search("[0-9]", Contraseña) or 
            not re.search("[!@#$%^&*()-_=+{};:,<.>]", Contraseña)):
            return False
        else: 
            return True
    
         
    def _verificar_plan(self, NombrePlan):
        self.conexion = conexion_sql_server()
        if self.conexion:
            cursor = self.conexion.cursor()
            try: 
                cursor.execute("SELECT COUNT(*) FROM Planes WHERE NombrePlan = ?", (NombrePlan))
                planes = cursor.fetchall()
                return planes
            except Exception as e:
                print(f"Error al obtener planes {e}")
                return None
            finally:
                cursor.close()
                self.conexion.close()
    
    def validar_login(self, CorreoUsuario, Contraseña):
        self.conexion = conexion_sql_server()
        if self.conexion:
            cursor = self.conexion.cursor()
            try:
                cursor.execute("SELECT * FROM Usuarios WHERE CorreoUsuario = ? AND Contraseña = ?",(CorreoUsuario, Contraseña))
                if cursor.fetchone():
                    return True
                else: 
                    return False
            except Exception as e:
                print(f"Error al validar inicio de sesion {e}")
            finally:
                cursor.close()
                self.conexion.close()            
                
    
    def verificar_y_obtener_lista_asesores(self, CorreoUsuario):
        ID_Usuario = SQLServerAsesorC.obtener_id_usuario(self, CorreoUsuario)
        asesor_exists = AsesorManager.valid_user_asesor(self, ID_Usuario)
        if asesor_exists is not None:
            lista_asesores = AsesorManager.obtener_asesor_personal(self,ID_Usuario)
        return lista_asesores

class SQLServerAsesorC:

    def __init__(self, conexion):
        self.conexion = conexion
    
    def obtener_id_usuario(self, CorreoUsuario):
        obtener_id_query = """SELECT ID_Usuario FROM Usuarios WHERE CorreoUsuario = ?"""
        with self.conexion.cursor() as cursor:
            cursor.execute(obtener_id_query, (CorreoUsuario,))
            row = cursor.fetchone()
        if row is not None:
            ID_Usuario = row[0]
            return ID_Usuario
        else:
            # Manejar el caso en el que no se encuentra ningún usuario con el correo especificado
            return None

    def add_asesor_C(self, NombreAsesorC, Descripcion, CorreoUsuario):
        ID_Usuario = self.obtener_id_usuario(CorreoUsuario)
        add_asesor_query = """INSERT INTO [Asesor_C] ([NombreAsesorC], [Descripcion], [ID_Usuario]) VALUES (?,?,?);"""
        with self.conexion.cursor() as cursor:
            cursor.execute(add_asesor_query, (NombreAsesorC, Descripcion, ID_Usuario))
        self.conexion.commit()

    def verificar_asesor(self, NombreAsesorC):
        verif_asesor = """SELECT ID_Usuario FROM Asesor_C WHERE NombreAsesorC = ?"""
        with self.conexion.cursor() as cursor:
            cursor.execute(verif_asesor, (NombreAsesorC,))
            result = cursor.fetchone()
            if result is not None:
                count = result[0]
                return count > 0
            else:
                # Si no se encontraron resultados, retornar False
                return False
    
    #def verificar_descripcion(self, Descripcion):
        #if Descripcion == str:
            #return True
        #else:
            #False

class AsesorManager:
    def __init__(self, conexion):
        self.conexion = conexion

    def asignar_asesor_personal(self,_retriever):
        # Crear un nuevo asesor personal para el usuario y guardarlo en la estructura de datos
        nuevo_asesor_personal = CrearAsesores.CrearAsesor(_retriever)
        return nuevo_asesor_personal
    
    def obtener_asesor_personal(self, ID_Usuario):
        # Retorna una lista de asesores agrupados por Usuarios
        query_nombre_descripcion = """SELECT a.NombreAsesorC, a.Descripcion FROM Asesor_C as a WHERE a.ID_Usuario = ? ;"""
        with self.conexion.cursor() as cursor:
            cursor.execute(query_nombre_descripcion,(ID_Usuario,))
            nombre_descrip = cursor.fetchall()
        query_chat_partition_id = """SELECT c.NombreChat as NombreChat, c.partition_id AS partition_id FROM Chat_C as c WHERE c.ID_Usuario = ? ;"""
        with self.conexion.cursor() as cursor:
              cursor.execute(query_chat_partition_id, (ID_Usuario))
              chat_partition_id = cursor.fetchall()
              
        lista_asesores = []
        for asesor_info, chat_info in zip(nombre_descrip, chat_partition_id):
            lista_asesores.append((*asesor_info, *chat_info))
        return lista_asesores 
    
    def valid_user_asesor(self, ID_Usuario):
        user_asesor = """SELECT NombreAsesorC FROM Asesor_C WHERE ID_Usuario = ?"""
        with self.conexion.cursor() as cursor:
            cursor.execute(user_asesor, (ID_Usuario, ))
            result = cursor.fetchone()
            if result is not None:
                count = result[0]
                return count > 0
            else:
                # Si no se encontraron resultados, retornar False
                return False

class SQLServerChatC:
    def __init__(self, conexion):
        self.conexion = conexion
    
    def obtener_id_asesor(self, NombreAsesorC, ID_Usuario):
        query_id_asesor = """SELECT ID_Asesor_C FROM Asesor_C WHERE NombreAsesorC = ? and ID_Usuario = ?"""
        with self.conexion.cursor() as cursor:
            cursor.execute(query_id_asesor,(NombreAsesorC, ID_Usuario,))
            row = cursor.fetchone()
        if row is not None:
            ID_Asesor_C = row[0]
            return ID_Asesor_C
        else:
            # Manejar el caso en el que no se encuentra ningún usuario con el correo especificado
            return None

    def add_chat(self, NombreChat, CorreoUsuario, NombreAsesorC):
        ID_Usuario = SQLServerAsesorC.obtener_id_usuario(self, CorreoUsuario)
        ID_Asesor_C = self.obtener_id_asesor(NombreAsesorC, ID_Usuario)
        add_chat_session = """INSERT INTO [Chat_C] ([NombreChat], [ID_Usuario], [ID_Asesor_C])
                            VALUES (?,?,?)"""
        with self.conexion.cursor() as cursor:
            cursor.execute(add_chat_session, (NombreChat, ID_Usuario, ID_Asesor_C))
        self.conexion.commit()

    def verificar_nombre_chat(self, NombreChat):
        if len(NombreChat) < 30:
            return True
        else:
            False


# VECTOR STORE PARA LA CLASE SQLSERVERARCHIVOS
#_vector_store = cargar_vector_store()

class SQLServerArchivos:
    def __init__(self, conexion, _vector_store):
        self.conexion = conexion
        self._vector_store = _vector_store
    
    def add_archivo(self, NombreArchivo, TipoArchivo, ID_Asesor_C, archivo_datastax ,total_ids):
        query_archivo = """INSERT INTO [Archivos] ([NombreArchivo], [TipoArchivo], [ID_Asesor_C], [archivo_datastax], [total_ids])
                            VALUES (?,?,?,?,?)"""
        
        with self.conexion.cursor() as cursor:
            cursor.execute(query_archivo, (NombreArchivo, TipoArchivo, ID_Asesor_C, archivo_datastax , total_ids))
        self.conexion.commit()

    def obtener_id_asesor_c(self, CorreoUsuario, NombreAsesorC):
        ID_Usuario = SQLServerAsesorC.obtener_id_usuario(self, CorreoUsuario)
        ID_Asesor_C = SQLServerChatC.obtener_id_asesor(self, NombreAsesorC, ID_Usuario)
        
        return ID_Asesor_C

    # METODO PARA EXTRAER DOCUMENTACION EN SQL
    def lista_documentacion_sql(self, CorreoUsuario, NombreAsesorC):
        query_id_asesor_c = """SELECT ID_Asesor_C FROM Asesor_C WHERE NombreAsesorC = ?"""
        with self.conexion.cursor() as cursor:
            cursor.execute(query_id_asesor_c, NombreAsesorC)
            ID_Asesor_C = cursor.fetchone()[0]
            query_documentacion = """SELECT NombreArchivo FROM Usuarios as u
                        INNER JOIN Asesor_C as ac
                        ON u.ID_Usuario = ac.ID_Usuario
                        INNER JOIN Archivos as ar
                        ON ac.ID_Asesor_C = ar.ID_Asesor_C
                        WHERE u.CorreoUsuario = ? and ac.ID_Asesor_C = ?"""
            cursor.execute(query_documentacion, CorreoUsuario, ID_Asesor_C)
            lista_documentos_sql = [doc[0] for doc in cursor.fetchall()]
            if lista_documentos_sql == []:
                return False
            else:
                return lista_documentos_sql
    
    # METODO UNICO PARA OBTENER LISTA DE DOCUMENTOS PARA EL SISTEMA.
    def lista_documentacion_nosql(self, lista_documentos_sql):
        lista_documentos_vector = []
        for documento in lista_documentos_sql:
            lista_documentos_vector.append(self._vector_store.similarity_search_with_score_id(query=documento, k=1, filter= {'source':documento}))
        tuplas = []
        for d in lista_documentos_vector:
            tuplas.append(d[0])
        lista_documentos_nosql = []
        for t in tuplas:
            lista_documentos_nosql.append(t[0].metadata['source'])
        return lista_documentos_nosql

    # DATOS NECESARIOS PARA PODER ELIMINAR LOS ARCHIVOS DE AMBOS LADOS
    def obtener_datos_archivo(self, NombreArchivo):
        query_datos_archivo = """SELECT archivo_datastax, total_ids FROM Archivos
                                    WHERE NombreArchivo = ?"""
        with self.conexion.cursor() as cursor:
            cursor.execute(query_datos_archivo, NombreArchivo)
            archivo_y_ids = cursor.fetchone()

        return archivo_y_ids

    # IDS PARA ELIMINAR DOCUMENTOS.
    def generador_ids(self, archivo_y_ids):
        lista_ids = []
        for a in range(archivo_y_ids[1]):
            lista_ids.append(archivo_y_ids[0] + "_" + str(a))

        return lista_ids

    # METODO QUE ELIMINA EL DOCUMENTO DE SQL Y NOSQL        
    def eliminar_documento(self, lista_ids, NombreArchivo):
        query_id_archivo = """SELECT idArchivo FROM Archivos WHERE NombreArchivo = ?"""
        with self.conexion.cursor() as cursor:
            cursor.execute(query_id_archivo, NombreArchivo)
            idArchivo = cursor.fetchone()[0]
            eliminar_sql_query_archivo = """DELETE FROM Archivos WHERE idArchivo = ?"""
            cursor.execute(eliminar_sql_query_archivo, idArchivo)
            eliminar = self._vector_store.delete(lista_ids)
        return eliminar
