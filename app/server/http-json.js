import { failure } from './amap-client.js'

const MAX_BODY_BYTES = 8192

export async function jsonBody(request, label) {
  if (!/^application\/json(?:\s*;|$)/i.test(request.headers['content-type'] ?? '')) {
    request.resume()
    return { error: failure(`请使用 JSON 提交${label}。`, 'invalid_request', 415) }
  }
  if (Number(request.headers['content-length']) > MAX_BODY_BYTES) {
    request.resume()
    return { error: failure(`${label}内容过长。`, 'invalid_request', 413) }
  }

  const chunks = []
  let bytes = 0
  try {
    for await (const chunk of request) {
      bytes += chunk.length
      if (bytes <= MAX_BODY_BYTES) chunks.push(chunk)
    }
    if (bytes > MAX_BODY_BYTES) return { error: failure(`${label}内容过长。`, 'invalid_request', 413) }
    return { input: JSON.parse(Buffer.concat(chunks).toString('utf8')) }
  } catch {
    return { error: failure(`${label} JSON 格式有误。`, 'invalid_request', 400) }
  }
}
