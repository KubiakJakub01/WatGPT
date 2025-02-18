import argparse

from ..constants import LLM_MODEL_NAME, LLM_PROVIDER
from ..llm_engine import LLMEngine


def parse_args():
    parser = argparse.ArgumentParser(description='RAG Chatbot')
    parser.add_argument(
        '--provider',
        type=str,
        default=LLM_PROVIDER,
        help='LLM provider (openai, groq, ollama)',
    )
    parser.add_argument(
        '--model',
        type=str,
        default=LLM_MODEL_NAME,
        help='LLM model name',
    )
    return parser.parse_args()


def main(provider: str = LLM_PROVIDER, model: str = LLM_MODEL_NAME):
    llm_engine = LLMEngine(provider=provider, model=model)

    print("\n💬 RAG Chatbot (type 'exit' to quit)")
    print('──────────────────────────────────────\n')

    while True:
        query = input('🧑‍💻 You: ')

        if query.lower() == 'exit':
            print('👋 Exiting chat.')
            break

        response = llm_engine.chat(query)
        print(f'🤖 AI: {response}\n')


if __name__ == '__main__':
    args = parse_args()
    main(args.provider, args.model)
