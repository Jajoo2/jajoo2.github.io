export async function onRequestPost({ request }) {
    const data = await request.json();
    const id = Date.now().toString();
    await MESSAGES.put(id, JSON.stringify(data));
    return new Response("ok");
}
