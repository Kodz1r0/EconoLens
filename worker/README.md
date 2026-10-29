# AI explanations on the public site

The public site (GitHub Pages) cannot hold a secret API key, so explanations go through a small
Cloudflare Worker (`explain.js`). The site sends only computed, formatted numbers; the worker builds
the prompt, calls the Claude API and returns text; the site then checks that every number in the
text appears in those facts and falls back to the template otherwise.

## Set up (about 15 minutes, done once)

1. **Claude API key.** Sign in at console.anthropic.com, add billing, then API keys → Create key.
   In Settings → Limits set a low monthly spend limit (for example $5). Copy the key; you will paste
   it in step 4 only.
2. **Cloudflare account.** Sign up at dash.cloudflare.com (free plan).
3. **Create the worker.** Workers & Pages → Create → Create Worker → name `econolens-explain` →
   Deploy. Then Edit code, replace everything with the contents of `explain.js`, Deploy.
4. **Settings → Variables and Secrets:**
   - `ANTHROPIC_API_KEY` — type **Secret**, value = your key
   - `ALLOWED_ORIGINS` — type Text, value = `https://kodz1r0.github.io`
   - `MODEL` — optional, Text, default `claude-haiku-5-5`
5. Copy the worker URL (like `https://econolens-explain.<name>.workers.dev`) and put it in
   `docs/config.js`:
   ```js
   window.ECONOLENS_AI_ENDPOINT = "https://econolens-explain.<name>.workers.dev";
   ```
   Commit. After GitHub Pages rebuilds, the “Explain with AI” button appears for every visitor.

To switch the feature off, set the endpoint back to `""` or delete the worker.

## Safety

- The key lives only in Cloudflare secrets, never in this repository or the page.
- Only requests from `ALLOWED_ORIGINS` are accepted; facts must be short strings in a fixed shape.
- About 12 requests per visitor per 10 minutes (best effort) and `max_tokens: 500` per answer.
- The real cost cap is the monthly spend limit you set in the Claude Console.
