let messages = [];

export async function onRequest(context) {
  const { request } = context;

  if (request.method === "POST") {
    const data = await request.json();
    messages.push(data);
    return new Response('Message stored', { status: 200 });
  }

  if (request.method === "GET") {
    return new Response(JSON.stringify(messages), {
      headers: { "Content-Type": "application/json" },
    });
  }

  return new Response('Method not allowed', { status: 405 });
}
