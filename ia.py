from langchain_google_genai import GoogleGenerativeAI
from langchain_core.prompts import (ChatPromptTemplate,MessagesPlaceholder,SystemMessagePromptTemplate,
                                    HumanMessagePromptTemplate)
from langchain.chains import LLMChain
from langchain.memory import ConversationBufferMemory



api_key = "AIzaSyD_1CDr74mTl2TzYy980mQM9QVUDHdJZjE"

llm = GoogleGenerativeAI(model="gemini-pro", google_api_key=api_key)

prompt= ChatPromptTemplate(
    messages=[
        SystemMessagePromptTemplate.from_template(
            "bot"
        ),
        MessagesPlaceholder(variable_name="chat_history"),
        HumanMessagePromptTemplate.from_template("{question}")
    ]
)

memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
conversation = LLMChain(
    llm=llm,
    prompt=prompt,
    verbose=True,
    memory=memory,
) 

conversation({"question":"hola"})



