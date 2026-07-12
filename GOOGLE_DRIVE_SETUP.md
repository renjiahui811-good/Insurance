# Google Drive Setup (one-time)

Connect the portal to a Google Drive folder so you can pick policy files
directly inside the app. This uses a **service account** — you share one Drive
folder with a robot email, then drop files into that folder.

Do this once. After that, daily use is just: drop file into folder → pick in app.

---

## Part 1 — Create a service account in Google Cloud

1. Go to <https://console.cloud.google.com/> and sign in.
2. Top bar → project dropdown → **New Project**. Name it e.g. `insurance-portal`.
   Create it, then make sure it's the selected project.
3. Enable the Drive API: open
   <https://console.cloud.google.com/apis/library/drive.googleapis.com>,
   click **Enable**.
4. Create the service account:
   - Go to <https://console.cloud.google.com/iam-admin/serviceaccounts>
   - **Create service account** → name it `insurance-portal` → **Create and continue**
   - Skip the optional roles → **Done**.
5. Create a key:
   - Click the service account you just made → **Keys** tab →
     **Add key** → **Create new key** → **JSON** → **Create**.
   - A `.json` file downloads. **Keep it safe — it's a password.**
6. Copy the service account email — it looks like
   `insurance-portal@insurance-portal-xxxxx.iam.gserviceaccount.com`.
   You'll find it on the service account page.

---

## Part 2 — Share a Drive folder with the service account

1. In Google Drive, create a folder, e.g. **`Insurance Inbox`**.
2. Right-click it → **Share** → paste the service account email from step 6 →
   give it **Viewer** access → **Send** (uncheck "notify" if asked).
3. Open the folder and copy its **folder ID** from the URL:
   `https://drive.google.com/drive/folders/`**`THIS_LONG_ID`**

---

## Part 3 — Add the secrets in Streamlit Cloud

1. Open your app on <https://share.streamlit.io> → **Manage app** →
   **⋮** → **Settings** → **Secrets**.
2. Paste the following, then fill it from your JSON file and folder ID:

```toml
gdrive_folder_id = "THIS_LONG_ID"

[gcp_service_account]
type = "service_account"
project_id = "insurance-portal-xxxxx"
private_key_id = "..."
private_key = "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
client_email = "insurance-portal@insurance-portal-xxxxx.iam.gserviceaccount.com"
client_id = "..."
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "..."
```

> Copy each value from the downloaded JSON file. The `private_key` must keep its
> `\n` line breaks exactly as in the JSON.

3. **Save**. The app reboots automatically.

---

## Done

Reopen the app. On the policy pages you'll now see a **Source** switch with
**🗂️ Pick from Google Drive** — it lists the files in your shared folder.

**Never commit the JSON key or secrets to the repository.** They live only in
Streamlit's Secrets store.
