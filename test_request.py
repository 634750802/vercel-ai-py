from ai_stream_proxy import stream_text

if __name__ == '__main__':
    ui_message = stream_text('amazon-bedrock', 'us.anthropic.claude-sonnet-4-20250514-v1:0', [], 'Hello,')
    print(ui_message.as_text_content())
