#  いい食事取ろう！— Smith Souzai Dashboard

> **Optimize your lunch at Smith 東中野 with data.**
> A Streamlit dashboard that recommends the best high-protein meal combinations within your budget, built from real souzai product data collected at a supermarket near TTC(TOKYO TECHNICAL COLLEGE).


---

##  Project Overview

| Item | Details |
|------|---------|
| **Goal** | Help TTC students eat well on a tight budget |
| **Data source** | ~86 souzai products from Smith 東中野 |
| **Storage** | Google Sheets (cloud, real-time shared) |
| **Framework** | Python · Streamlit · Altair |
| **Deployed** | Streamlit Cloud |

---

##  Features

###  Tab 1 — Auto Recommendation (自動おすすめ)
- Set your budget and meal style (Staple + Side dish / Bento / Side dish only)
- Choose how many items you want
- App automatically finds **Top 3 combinations** with the highest total protein within budget
- Bread (パン) no longer dominates — staple foods and side dishes are ranked separately

###  Tab 2 — Manual Browse (自分で選ぶ)
- Filter products by budget
- Sort by protein, P/C score, or price
- Rankings split into three groups: **Lauk (おかず) / Karbo (主食) / Bento (弁当)**
- Bar chart showing top P/C score items

###  Tab 3 — Add Data (データ追加)
- Input new souzai products directly from the app
- P/C score is calculated automatically
- Data saved to Google Sheets instantly — visible to all users in real time
- Undo button to delete the last entry

---

## P/C Score Formula

```
P/C Score = Protein (g) ÷ Price (¥) × 100
```

| Score | Level | Meaning |
|-------|-------|---------|
| ≥ 5.0 | High | Excellent protein per yen |
| 2.0 – 5.0 | Mid | Average |
| < 2.0 | Low | Poor value |

---

##  Project Structure

```
dashboard_souzai_smith/
├── app.py                  # Main Streamlit application
├── smith_clean.csv         # Cleaned dataset (fallback / reference)
├── requirements.txt        # Python dependencies
├── .gitignore
└── .streamlit/
    └── secrets.toml        # Google credentials (NOT committed to Git)
```

---

##  Getting Started (Local)

### 1. Clone the repository

```bash
git clone https://github.com/MJml-12/dashboard_souzai_smith.git
cd dashboard_souzai_smith
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Set up Google Sheets credentials

Create `.streamlit/secrets.toml`:

```toml
[gcp_service_account]
type = "service_account"
project_id = "your-project-id"
private_key_id = "..."
private_key = "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
client_email = "your-service-account@your-project.iam.gserviceaccount.com"
client_id = "..."
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "..."

[sheets]
spreadsheet_id = "your-google-sheet-id"
worksheet_name = "your-sheet-tab-name"
```

> Never commit `secrets.toml` to GitHub. It is already listed in `.gitignore`.

### 4. Run the app

```bash
streamlit run app.py
```

---

## Deploy to Streamlit Cloud

1. Push your code to GitHub (without `secrets.toml`)
2. Go to [share.streamlit.io](https://share.streamlit.io) → **New app**
3. Select your repository, branch `main`, file `app.py`
4. Click **Advanced settings** → paste your `secrets.toml` content into the **Secrets** box
5. Click **Deploy**

---

## Tech Stack

| Tool | Purpose |
|------|---------|
| Python 3.10+ | Core language |
| Streamlit | Web app framework |
| Pandas | Data processing |
| Altair | Data visualization |
| gspread | Google Sheets API client |
| google-auth | Authentication for Google APIs |
| Google Sheets | Cloud database (shared, real-time) |

---

## Known Limitations

- Data is limited to Smith 東中野 only
- P/C score focuses on protein per yen — does not account for full nutritional balance (fat, carbs)
- Simultaneous writes from multiple users may cause a race condition (CSV-level issue; mitigated by Google Sheets)
- No user authentication on data input tab

---

## Future Plans

- Expand data collection to nearby stores
- Add a full nutritional score (fat / carb balance)
- User login to track personal meal history
- Weekly meal plan recommendation feature
- Migrate to SQLite or Supabase for a more robust database

---

## Author

**Muhammad Jamal** — Data Science student at TTC (Tokyo, 2nd year)
GitHub: [@MJml-12](https://github.com/MJml-12)

---

*Built as a final project for RJP class, 2026.*
