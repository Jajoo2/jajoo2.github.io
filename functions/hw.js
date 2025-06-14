export async function onRequest(context) {
  const { request, env } = context;
  const kv = env.CHAT_KV; // KV namespace binding??

  if (request.method === "POST") {
    const data = await request.json();
    const id = Date.now().toString();
    await kv.put(id, JSON.stringify(data));
    return new Response('Message stored', { status: 200 });
  }

  if (request.method === "GET") {
    const list = [];
    for await (const key of kv.list()) {
      const value = await kv.get(key.name);
      list.push(JSON.parse(value));
    }
    return new Response(JSON.stringify(list), {
      headers: { "Content-Type": "application/json" },
    });
  }

  return new Response('Method not allowed', { status: 405 });
}
