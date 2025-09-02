import { readUIMessageStream } from 'ai'
import fs from 'fs'

const content = fs.readFileSync('../example-stream-data.txt', 'utf-8')
const s = readUIMessageStream({
    stream: new ReadableStream({
        start (controller) {
            content.split('\n\n')
                .forEach(line => {
                    line = line.trim();
                    if (!line) {
                        return;
                    }
                    const message = line.slice(6);
                    if (message ==='[DONE]') {
                        controller.close()
                    } else {
                        controller.enqueue(JSON.parse(message))
                    }
                })
        }
    })
})

const reader = s.getReader();

let last
while (true) {
    const result = await reader.read()
    if (result.done) {
        break
    }
     last = result.value
}

fs.writeFileSync('../standard.json', JSON.stringify(last, null, 2))

