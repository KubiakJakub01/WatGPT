from langchain.chat_models import init_chat_model
from langchain.memory import ConversationBufferMemory
from langchain.schema import HumanMessage, SystemMessage

from .constants import LLM_MODEL_NAME, LLM_PROVIDER, LLM_RAG_SYSTEM_PROMPT, PROMPTS_FILE
from .db import VectorDB
from .utils import load_prompt, log_debug


class LLMEngine:
    def __init__(self, provider: str = LLM_PROVIDER, model: str = LLM_MODEL_NAME):
        """
        Handles interaction with LLM and integrates RAG retrieval.

        :param provider: LLM provider ("openai", "groq", "ollama")
        :param model: LLM model name
        """
        self.provider = provider.lower()
        self.model = model
        self.vector_db = VectorDB()
        self.memory = ConversationBufferMemory(memory_key='chat_history', return_messages=True)

        self.llm = init_chat_model(self.model, model_provider=self.provider)
        log_debug(f'Initialized LLM model: {self.model} ({self.provider})')
        self.system_prompt = load_prompt(PROMPTS_FILE, LLM_RAG_SYSTEM_PROMPT)

    def retrieve_context(self, query: str, top_k: int = 3):
        """Fetch relevant documents from VectorDB."""
        return self.vector_db.query(query, top_k=top_k)

    def chat(self, query: str):
        """
        Perform a RAG-based LLM query with conversation memory.

        :param query: User's question
        :return: LLM-generated response
        """
        # Retrieve relevant chunks
        results = self.retrieve_context(query)
        context = (
            '\n\n---\n\n'.join([doc.page_content for doc in results])
            if results
            else 'No relevant documents found.'
        )

        # Construct conversation history
        history = self.memory.load_memory_variables({})['chat_history']

        # Construct prompt
        prompt = self.system_prompt.format(context=context)
        messages = [SystemMessage(content=prompt)]
        messages.extend(history)  # Include chat history
        messages.append(HumanMessage(content=query))  # Add user query

        log_debug('-' * 80)
        log_debug(f'Messages: {messages}')

        # Generate response
        response = self.llm.invoke(messages)

        # Store conversation history
        self.memory.save_context({'input': query}, {'output': response.content})
        sources = [
            f'{doc.metadata.get("source_file", None)}:{doc.metadata.get("page_num", None)}'
            for doc in results
        ]
        formatted_response = f'{response.content}\nŹródła: {sources}'

        log_debug(f'Response: {formatted_response}')

        return formatted_response
