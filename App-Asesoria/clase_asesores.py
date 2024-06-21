from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
from langchain.agents import initialize_agent
from langchain_community.utilities.google_serper import GoogleSerperAPIWrapper
from langchain.tools import Tool
from langchain.prompts import MessagesPlaceholder
from langchain_google_genai import ChatGoogleGenerativeAI
import google.generativeai as genai
from langchain_community.llms import Cohere
from langchain.retrievers.contextual_compression import ContextualCompressionRetriever
from langchain_cohere import CohereRerank
import streamlit as st

class CrearAsesores:
#Quizas se pueda en un futuro dar al cliente la posibilidad de elegir la especialidad de su asesor, ya que algunos son mas fuertes en diferentes areas.
#POR AHORA SOLO EL CONVERSACIONAL
    def __init__(self):
        self.tools = None
        self.prompt = None
        
    @st.cache_resource(show_spinner='Creando Asesor')
    def CrearAsesor(_retriever):
    #TEMPLATE PROXIMAMENTE MODIFICABLE
        template ="""
        DESCRIPCION DEL CHAT:
        Sos un Chat Inteligente que ayuda a los usuarios de la mejor manera posible.
        Despues del saludo te debes presentar diciendo quien sos y que herramientas tenes para el usuario.

        INSTRUCCIONES:
        1- Posees una herramienta llamada db_tool {db_tool}, con ella obtendrás informacion de tus documentos.
        2- Siempre que necesites usar una herramienta, primero utilizá db_tool.
        3- Cuando se te solicite específicamente buscar en la web, podes usar search_tool {search_tool} 

        REGLAS DEL CHAT:
        Debes ser amable, comunicarte en el idiome en el que los usuarios te escriben.
        Tus respuestas deben ser efifaces y eficientes
        Debes recordar el chat_history.
        Chat_history: {chat_history}

        Mensaje de usuario: {input}

        Respuesta:"""

        prompt = PromptTemplate(template= template, input_variables=["input","context","chat_history"])

        model = ChatGoogleGenerativeAI(model="gemini-1.0-pro",
                                   client=genai,
                                   temperature=0.5
                                   )
        
        compressor = CohereRerank()
        compression_retriever = ContextualCompressionRetriever(base_compressor=compressor, base_retriever=_retriever)

#        def extraer_texto(compression_retriever, question):
#            docs = compression_retriever.get_relevant_documents(question)
#            informacion = ''
#            for d in docs:
#                texto_limpio = re.sub(r"\n|:|'", " ", d.page_content)
#                informacion += texto_limpio
#            return informacion
        

#        chain = RetrievalQA.from_chain_type(
#            llm=Cohere(temperature=0.5), retriever=compression_retriever
#            )
        
#        db_tool = Tool(
#                name= "db_tool",
#                description= "Herramienta util para obtener información de tus documentos",
#                func = chain.run
#        )

        db_tool = Tool(
                name= "db_tool",
                description= "Herramienta util para obtener información de tus documentos o datos",
                func = lambda question: compression_retriever.get_relevant_documents(question)
        )


        search = GoogleSerperAPIWrapper()

        search_tool = Tool(
            name="search_tool",
            description="Herramiento solo para cuando te solicitan buscar en el navegador.",
            func=search.run,
            )
        
        tools = [db_tool, search_tool]
        memory = ConversationBufferMemory(memory_key="chat_history", input_key='input', return_messages=True, output_key = 'output')
        
        #chain = LLMChain(llm=llm,prompt=prompt,verbose=True,memory=memory)
        chat_history = MessagesPlaceholder(variable_name="chat_history")
        
        #USAMOS INITIALIZE AGENT YA QUE PERMITE ESTRUCTURAR EL OUTPUT DEL AGENTE
        agent = initialize_agent(tools,
                         llm=model,
                         agent="conversational-react-description",
                         verbose=True, agent_kwargs={
                        "prompt":[prompt],
                        "memory_prompts": [chat_history],
                        "input_variables": ["input","context"]},
                        memory = memory,
                        handle_parsing_errors=True
                        )

        return agent
    
