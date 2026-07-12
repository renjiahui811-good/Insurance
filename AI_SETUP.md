# AI Analysis Setup

Let an AI read a full policy document and summarise it in plain language — what
it covers, exclusions, waiting periods, and gaps to review. This augments the
regex parsing, which only pulls out fields it recognises.

This is optional. Without it, upload + auto-parse + the manual form all keep
working. Two providers are supported — pick one:

| Provider | Cost | Best for |
|----------|------|----------|
| **Google Gemini** | **Free tier** (no card needed) | Recommended — free for personal use |
| Anthropic Claude | Pay-as-you-go (API credits) | Highest quality |

The app auto-detects which one you configured. If you set both, it prefers
Gemini (or set `ai_provider = "claude"` to force Claude).

---

## Option A — Google Gemini (free)

1. Go to <https://aistudio.google.com/app/apikey> and sign in with a Google account.
2. Click **Create API key** → copy it.
3. Your app → **Manage app → ⋮ → Settings → Secrets**, and add (keep your
   existing Google Drive secrets as-is):

   ```toml
   gemini_api_key = "your-gemini-key"

   # Optional — defaults to gemini-2.0-flash (free tier). Uncomment to change:
   # gemini_model = "gemini-2.5-flash"
   ```
4. Save. The app reboots automatically.

> The free tier has daily rate limits, which are plenty for personal use. No
> credit card required.

---

## Option B — Anthropic Claude (paid, highest quality)

1. Go to <https://console.anthropic.com/> → **Settings → API Keys → Create Key**.
2. Add a little credit (analysis costs a few cents per policy; less with a
   cheaper model).
3. In Streamlit Secrets:

   ```toml
   anthropic_api_key = "sk-ant-your-key"

   # Optional — defaults to claude-opus-4-8. Cheaper option:
   # anthropic_model = "claude-haiku-4-5"
   ```

---

## Use it

On the policy pages, upload/pick a document so its text is extracted, then a
**C. AI Analysis** section appears. Click **🤖 Analyze full policy with AI**. The
summary also pre-fills the Notes field, so it's saved with the record.

> API keys are secrets — they live only in Streamlit's encrypted Secrets store.
> Never commit them to the repository.
>
> AI output can be wrong or incomplete. Always verify against the official
> policy document before relying on it.
