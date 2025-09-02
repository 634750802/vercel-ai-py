from ai_stream_proxy import stream_text

if __name__ == '__main__':
    stream_text_response = stream_text('amazon-bedrock', 'us.anthropic.claude-sonnet-4-20250514-v1:0', [], 'Hello,')

    print(stream_text_response.stream_id)
    print(stream_text_response.read_message().as_text_content())
