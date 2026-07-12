# AI Analysis Setup (Claude)

Let Claude read a full policy document and summarise it in plain language —
what it covers, exclusions, waiting periods, and gaps to review. This augments
the regex parsing, which only pulls out fields it recognises.

This is optional. Without it, upload + auto-parse + the manual form all keep
working.

## 1. Get an Anthropic API key

1. Go to <https://console.anthropic.com/> and sign in (or sign up).
2. Open **Settings → API Keys → Create Key**.
3. Copy the key (starts with `sk-ant-...`). Add billing credit if prompted —
   analysis costs a few cents per policy.

## 2. Add it to Streamlit Secrets

Your app → **Manage app** → **⋮** → **Settings** → **Secrets**. Add one line
alongside your existing secrets (keep the Google Drive block as-is):

```toml
anthropic_api_key = "sk-ant-your-key-here"

# Optional — defaults to claude-opus-4-8 (most capable). Uncomment to change:
# anthropic_model = "claude-sonnet-5"
```

Save. The app reboots automatically.

## 3. Use it

On the policy pages, upload/pick a document so its text is extracted, then a
**C. AI Analysis (Claude)** section appears. Click **🤖 Analyze full policy with
AI**. The summary also pre-fills the Notes field, so it's saved with the record.

> The API key is a secret — it lives only in Streamlit's encrypted Secrets store.
> Never commit it to the repository.
>
> AI output can be wrong or incomplete. Always verify against the official
> policy document before relying on it.
