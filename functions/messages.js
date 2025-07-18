export async function onRequest() {
    const messages = await MESSAGES.list();
    const result = [];
    for (const key of messages.keys) {
        const value = await MESSAGES.get(key.name, { type: "json" });
        if (value) result.push(value);
    }
    return new Response(JSON.stringify(result));
}
