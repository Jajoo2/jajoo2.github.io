export default {
  async fetch(request, env, ctx) {
    return new Response('Hello World   Programmed to whatver and  not to soemthingg', {
      headers: { 'content-type': 'text/plain' },
    })
  }
}
