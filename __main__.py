import json

from vercel import create_streaming_processor, TextDeltaChunk, sse_stream_to_message
from vercel import TextStartChunk

if __name__ == "__main__":
    with open('./example-stream-data.txt') as f:
        sse_data = f.read()
    message, processor = sse_stream_to_message(sse_data)
    with open('./result.json', 'w') as f:
        f.write(json.dumps(message.to_dict(), indent=2))
