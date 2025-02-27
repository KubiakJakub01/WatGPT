from transformers import AutoTokenizer


class TextChunker:
    def __init__(self, tokenizer_model: str = 'gpt2'):
        self.tokenizer = AutoTokenizer.from_pretrained(tokenizer_model)
        self.tokenizer.model_max_length = 100000

    def chunk_text_token_based(
        self, text: str, max_tokens: int = 1024, overlap_tokens: int = 20
    ) -> list[str]:
        tokens = self.tokenizer.encode(text, add_special_tokens=False)
        total_tokens = len(tokens)
        if total_tokens == 0:
            return ['']

        chunks = []
        start = 0
        while start < total_tokens:
            end = start + max_tokens
            chunk_tokens = tokens[start:end]
            chunk_text = self.tokenizer.decode(chunk_tokens, skip_special_tokens=True)
            chunks.append(chunk_text)
            start += max(1, max_tokens - overlap_tokens)
        print(f'CHUNKS FROM Text chunker:\n{chunks}')
        return chunks

    def chunk_text(self, text: str, size=1024, overlap=20) -> list[str]:
        if not text:
            return []
        chunks = []
        start = 0
        length = len(text)
        while start < length:
            end = start + size
            chunk = text[start:end]
            chunks.append(chunk)
            start += max(1, size - overlap)
        return chunks
