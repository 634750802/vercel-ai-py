import uuid

import requests

from vercel import UIMessage, SSEParser, UIMessageStreamProcessor
from vercel.UIMessage import TextUIPart


def stream_text(
        provider: str,
        model: str,
        messages: list[UIMessage],
        prompt: str,
        **kwargs
):
    request_messages = list()
    request_messages.extend(messages)
    request_messages.append(UIMessage(
        id=str(uuid.uuid4()),
        role='user',
        parts=[TextUIPart(text=prompt)]
    ))
    response = requests.post(
        f'http://localhost:3000/v1/llm/{provider}/chat',
        json={
            'model': model,
            'messages': list(map(lambda m: m.to_dict(), request_messages)),
        })

    if not response.ok:
        raise BaseException(response.text)

    sse_parser = SSEParser()
    processor = UIMessageStreamProcessor()

    for line in response.iter_lines(delimiter=b'\n\n'):
        event = sse_parser.parse_sse_line(line.decode('utf-8'))
        if event.data == '[DONE]':
            break
        # print(event.data)
        # Example:
        # {"type": "start", "messageId": "2b50779c-5e07-4d00-bd9b-efa49971ae26"}
        # {"type": "start-step"}
        # {"type": "text-start", "id": "0"}
        # {"type": "text-delta", "id": "0", "delta": "Hello! It"}
        # {"type": "text-delta", "id": "0", "delta": "'s nice to meet"}
        # {"type": "text-delta", "id": "0", "delta": " you. How"}
        # {"type": "text-delta", "id": "0", "delta": " are you doing today"}
        # {"type": "text-delta", "id": "0", "delta": "? Is"}
        # {"type": "text-delta", "id": "0", "delta": " there anything I can"}
        # {"type": "text-delta", "id": "0", "delta": " help you with?"}
        # {"type": "text-end", "id": "0"}
        # {"type": "finish-step"}
        # {"type": "finish"}
        chunk = sse_parser.parse_chunk_json(event.data)
        processor.process_chunk(chunk)

    return processor.build_message()
