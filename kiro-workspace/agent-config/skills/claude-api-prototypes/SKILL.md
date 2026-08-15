---
name: claude-api-prototypes
description: Call a model from inside an HTML prototype through the built-in browser helper, including a messages array, system prompt, and client-side tools. Use when a prototype needs real generated output rather than canned text.
---

# Model calls in prototypes

HTML artifacts can call the model through a built-in helper. No SDK, no API key.

```html
<script>
(async () => {
  const text = await window.claude.complete("Summarize this: ...");
  const text2 = await window.claude.complete({
    messages: [{ role: 'user', content: '...' }],
  });
})();
</script>
```

Defaults: the small fast model, 1024-token output cap.

The request body also accepts `model` (haiku and sonnet families only), `max_tokens` up to 32000, `system`, `tool_choice`, and client `tools` in standard Messages API shapes, except each tool also carries `run: async (input) => string`. The helper executes tool calls in-page and loops, up to eight model calls, resolving with the final text. A handler that throws becomes an error tool result. Server tools such as web search are rejected. No streaming. Rate limit is 15 calls per minute per user, loop iterations included. A shared artifact runs under the viewer's quota.

Design around the constraints: show a loading state, handle a rejected or rate-limited call with a visible fallback, and keep prompts short enough that the interaction feels immediate. If the prototype will be exported as a standalone offline file, the helper will not be available - say so before building, since it changes the deliverable.
