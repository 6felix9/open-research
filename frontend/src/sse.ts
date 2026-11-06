// Minimal SSE reader for fetch() responses. EventSource can't POST or send headers,
// and the OpenAI key must travel in a header, not a URL.
export async function readSse(
  body: ReadableStream<Uint8Array>,
  onEvent: (event: string, data: string) => void,
): Promise<void> {
  const reader = body.getReader()
  const decoder = new TextDecoder()
  let buf = ''
  for (;;) {
    const { value, done } = await reader.read()
    if (done) break
    buf = (buf + decoder.decode(value, { stream: true })).replace(/\r\n/g, '\n')
    let end: number
    while ((end = buf.indexOf('\n\n')) >= 0) {
      const block = buf.slice(0, end)
      buf = buf.slice(end + 2)
      let event = 'message'
      const data: string[] = []
      for (const line of block.split('\n')) {
        if (line.startsWith('event:')) event = line.slice(6).trim()
        else if (line.startsWith('data:')) data.push(line.slice(5).trimStart())
      }
      if (data.length) onEvent(event, data.join('\n'))
    }
  }
}
