import json
import re

from langchain.chat_models import init_chat_model
from langchain.memory import ConversationBufferMemory
from langchain.schema import BaseMessage, HumanMessage, SystemMessage
from tabulate import tabulate

from .constants import (
    LLM_MODEL_NAME,
    LLM_PROVIDER,
    LLM_QUERY_EXTRACTION_PROMPT,
    LLM_RAG_SYSTEM_PROMPT,
    PROMPTS_FILE,
)
from .db import SqlDB, VectorDB
from .utils import convert_natural_date_to_iso, load_prompt, log_debug


class LLMEngine:
    def __init__(self, provider: str = LLM_PROVIDER, model: str = LLM_MODEL_NAME):
        """
        Handles interaction with LLM, integrates RAG retrieval, and queries timetable data.
        """
        self.provider = provider.lower()
        self.model = model
        self.vector_db = VectorDB()
        self.chunk_db = SqlDB()
        self.memory = ConversationBufferMemory(memory_key='chat_history', return_messages=True)

        self.llm = init_chat_model(self.model, model_provider=self.provider)
        log_debug(f'Initialized LLM model: {self.model} ({self.provider})')

        # Load system prompts
        self.system_prompt = load_prompt(PROMPTS_FILE, LLM_RAG_SYSTEM_PROMPT)
        self.query_extraction_prompt = load_prompt(PROMPTS_FILE, LLM_QUERY_EXTRACTION_PROMPT)

    def extract_query_details(self, query: str) -> tuple[str | None, str | None]:
        """
        Uses LLM to extract structured details from user query.

        :param query: User's question
        :return: Extracted data in format {"group_code": str | None, "raw_date": str | None}
        """
        response = self.llm.invoke(
            [SystemMessage(content=self.query_extraction_prompt), HumanMessage(content=query)]
        )

        try:
            extracted_data_match = re.search(r'\{.*\}', str(response.content))
            extracted_data = (
                json.loads(extracted_data_match.group()) if extracted_data_match else None
            )
            if isinstance(extracted_data, dict):
                group_code = extracted_data.get('group_code', None)
                raw_date = extracted_data.get('raw_date', None)
                date = convert_natural_date_to_iso(raw_date)
                log_debug(f'Extracted group code: {group_code}, date: {date}')

                return group_code, date
        except Exception as e:  # pylint: disable=broad-exception-caught
            log_debug(f'Failed to parse LLM response: {response.content} - {e}')

        return None, None

    def retrieve_context(self, query: str, top_k: int = 3):
        """Fetch relevant documents from VectorDB."""
        return self.vector_db.query(query, top_k=top_k)

    def retrieve_timetable(self, date: str, group_code: str):
        """Fetch timetable data from ChunkDB."""
        if group_code and date:
            # Fetch lessons for that group & date
            lessons = self.chunk_db.fetch_lessons_namedtuple(group_code)
            if lessons:
                timetable_info = '\n'.join(
                    [
                        f'{lesson.lesson_date} {lesson.block_id}: {lesson.course_code} '
                        f'({lesson.teacher_name}) in {lesson.room}, {lesson.building}'
                        for lesson in lessons
                        if lesson.lesson_date == date  # Filter only for that day
                    ]
                )
                log_debug(f'Found timetable info: {timetable_info}')
                headers = ['Data', 'Blok', 'Kod przedmiotu', 'Nauczyciel', 'Sala', 'Budynek']
                lessons_data = [
                    [
                        lesson.lesson_date,
                        lesson.block_id,
                        lesson.course_code,
                        lesson.teacher_name,
                        lesson.room,
                        lesson.building,
                    ]
                    for lesson in lessons
                    if lesson.lesson_date == date
                ]
                timetable_info = tabulate(lessons_data, headers=headers, tablefmt='fancy_grid')

                return f'Twoje zajęcia na {date}:\n{timetable_info}'
            return f'Nie znaleziono zajęć dla grupy {group_code} na {date}.'
        return None

    def chat(self, query: str):
        """
        Determines whether to use the timetable database or RAG for answering the query.

        :param query: User's question
        :return: Response from LLM (based on RAG or database)
        """
        # Try extracting timetable-related details (group & date)
        group_code, date = self.extract_query_details(query)

        # If both group and date are extracted, use timetable-based retrieval
        if group_code and date:
            response = self.retrieve_timetable(date, group_code)
            if response:
                return response

        # Otherwise, use RAG-based retrieval
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
        messages: list[BaseMessage] = [SystemMessage(content=prompt)]
        messages.extend(history)  # Include chat history
        messages.append(HumanMessage(content=query))  # Add user query

        log_debug('-' * 80)
        log_debug(f'Messages: {messages}')

        # Generate response
        response = self.llm.invoke(messages)

        # Store conversation history
        self.memory.save_context({'input': query}, {'output': str(response.content)})
        sources = [
            f'{doc.metadata.get("title", "No Title")} - {doc.metadata.get("source_url", "No URL")} - {doc.metadata.get("file_url", "No URL")}'
            for doc in results
        ]

        formatted_response = f'{response.content}\nŹródła: {sources}'

        log_debug(f'Response: {formatted_response}')

        return formatted_response
