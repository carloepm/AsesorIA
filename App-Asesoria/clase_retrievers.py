from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
import tempfile
import os
import streamlit as st
from langchain_cohere import CohereEmbeddings
from pydantic import BaseModel, Field

class Document(BaseModel):
    """Interface for interacting with a document."""

    page_content: str
    metadata: dict = Field(default_factory=dict)

class CrearRetriever:
    #Archivo temporal por su corto tiempo de ejecucion, pero puede existir la posibilidad de almacenarlo en Cassandra BBDD Vectorial.
    #Pulir la clase para almacenar mas tipos de documentos, no se descartan los videos.
    def __init__(self, documentos):
        self.documentos = documentos
    
    @staticmethod
    def vectorize_text(documentos, _vector_store, NombreArchivo, ID_Asesor_C):
        if documentos is not None:
        
        # Write to temporary file
            temp_dir = tempfile.TemporaryDirectory()
            file = documentos
            temp_filepath = os.path.join(temp_dir.name, file.name)
            with open(temp_filepath, 'wb') as f:
                f.write(file.getvalue())

        # Load the PDF
            docs = []
            loader = PyPDFLoader(temp_filepath)
            docs.extend(loader.load())

        # Create the text splitter
        text_splitter = RecursiveCharacterTextSplitter(
        chunk_size = 1000,
        chunk_overlap  = 20
        )

        # Vectorize the PDF and load it into the Astra DB Vector Store
        embeddings = CohereEmbeddings(model="embed-multilingual-v3.0")
        documents = text_splitter.split_documents(docs)

        docs2 = []
        for d in documents:
            metadata = {"source": NombreArchivo, "ID_Asesor_C": ID_Asesor_C}
            doc = Document(page_content=d.page_content, metadata=metadata)
            docs2.append(doc)

        ids = [f"{NombreArchivo}_{ID_Asesor_C}_{i}" for i in range(len(docs2))]
        archivo_datastax = f"{NombreArchivo}_{ID_Asesor_C}" # ID DEL ARCHIVO PARA SQL
        total_ids = len(ids) # TOTALIDAD DE IDS PARA SQL
        _vector_store.from_documents(docs2, embeddings, namespace="chat_app_vector", collection_name='vector_store',
                            token="AstraCS:DZLNwDFMqTEXaZgXayJLCnNZ:28f5cdba8aff2cfff59b42e86c893f6a841a4669cdf06fc29a6bc6a5d4cffeba",
                            api_endpoint="https://9c716385-228f-4a90-9ea5-594d44b69b4b-us-east1.apps.astra.datastax.com",
                            ids = ids)
        
        return archivo_datastax, total_ids
        
    @st.cache_resource(show_spinner='Creando Retriever')
    def load_retriever(_vector_store):
        retriever = _vector_store.as_retriever(search_type= 'similarity',search_kwargs={'k': 6}
        )
        return retriever

        
    