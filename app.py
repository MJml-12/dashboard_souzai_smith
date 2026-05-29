import streamlit as st
import pandas as pd
import altair as alt
from itertools import combinations
import gspread
from google.oauth2.service_account import Credentials

# === ページ設定 / PAGE CONFIG ===
st.set_page_config(
    page_title="いい食事取ろう！",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# === GOOGLEスプレッドシート接続 / GOOGLE SHEETS CONNECTION ===
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

@st.cache_resource
def get_worksheet():
    creds = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"], scopes=SCOPES
    )
    client = gspread.authorize(creds)
    sh = client.open_by_key(st.secrets["sheets"]["spreadsheet_id"])
    return sh.worksheet(st.secrets["sheets"]["worksheet_name"])

@st.cache_data(ttl=30)
def load_data():
    ws = get_worksheet()
    records = ws.get_all_records()
    df = pd.DataFrame(records)
    df["p/c_score"] = pd.to_numeric(df["p/c_score"], errors="coerce")
    df["タンパク"]   = pd.to_numeric(df["タンパク"],   errors="coerce")
    df["値段"]       = pd.to_numeric(df["値段"],       errors="coerce")
    return df

# === データ読み込み / LOAD DATA ===
df = load_data()

KARBO_CATS = ["パン", "おにぎり", "ご飯"]
BENTO_CATS = ["弁当"]

def get_group(cat):
    if cat in KARBO_CATS: return "karbo"    # 主食
    if cat in BENTO_CATS: return "bento"    # 弁当
    return "okazu"                          # おかず

df["group"] = df["カテゴリ"].apply(get_group)

# === GLOBAL CSS ===
st.markdown("""
<style>

html, body, [class*="css"] {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

#MainMenu, footer, header { visibility: hidden; }

.block-container {
    padding: 1.2rem 1rem 2rem 1rem !important;
    max-width: 500px !important;
}

.app-header {
    margin-bottom: 1.2rem;
    padding-bottom: 0.8rem;
    border-bottom: 1px solid #D5D3CC;
}
.app-title {
    font-size: 1.55rem;
    font-weight: 600;
    color: #2D3436;
    letter-spacing: -0.02em;
    line-height: 1.2;
    margin: 0 0 4px 0;
}
.app-sub {
    font-size: 0.75rem;
    color: #636E72;
    letter-spacing: 0.05em;
    text-transform: uppercase;
    margin: 0;
}

/* STAT CARDS */
.stat-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 8px;
    margin-bottom: 1rem;
}
.stat-card {
    background: #F8F7F4;
    border: 1px solid #D5D3CC;
    border-radius: 12px;
    padding: 10px 8px 8px;
    text-align: center;
}
.stat-val {
    font-size: 1.2rem;
    font-weight: 600;
    color: #4A4A4A;
    line-height: 1.1;
    display: block;
    font-family: inherit;
}
.stat-lbl {
    font-size: 0.63rem;
    color: #636E72;
    margin-top: 3px;
    display: block;
    letter-spacing: 0.02em;
}

/* SECTION TITLE */
.section-title {
    font-size: 0.68rem;
    font-weight: 600;
    color: #636E72;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    margin: 1.2rem 0 0.5rem;
}

/* GROUP LABEL */
.group-label {
    display: flex;
    align-items: center;
    gap: 8px;
    margin: 1rem 0 0.4rem;
}
.group-badge {
    font-size: 0.62rem;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    padding: 3px 9px;
    border-radius: 20px;
}
.badge-lauk  { background: #E8E6E1;  color: #4A4A4A; }
.badge-karbo { background: #F0E8D8;  color: #8B6914; }
.badge-bento { background: #EDE8F0;  color: #6B4C7A; }

/* RANK ITEMS */
.rank-item {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 10px 12px;
    background: #FFFFFF;
    border: 1px solid #E0DED8;
    border-radius: 12px;
    margin-bottom: 6px;
}
.rank-item:hover { background: #F0EFEA; }
.rank-num {
    font-family: inherit;
    font-size: 0.75rem;
    font-weight: 500;
    color: #636E72;
    width: 18px;
    flex-shrink: 0;
    text-align: center;
}
.rank-num.gold   { color: #8B6914; }
.rank-num.silver { color: #95A5A6; }
.rank-num.bronze { color: #92765A; }
.rank-name {
    flex: 1;
    font-size: 0.85rem;
    font-weight: 500;
    color: #2D3436;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}
.rank-meta {
    display: flex;
    flex-direction: column;
    align-items: flex-end;
    flex-shrink: 0;
    gap: 2px;
}
.rank-protein {
    font-size: 0.85rem;
    font-weight: 600;
    color: #4A4A4A;
    font-family: inherit;
}
.rank-price {
    font-size: 0.68rem;
    color: #636E72;
}
.pc-badge {
    font-size: 0.6rem;
    font-weight: 600;
    padding: 2px 6px;
    border-radius: 20px;
    font-family: inherit;
}
.pc-hi  { background: #D5D0C8; color: #4A4A4A; }
.pc-mid { background: #F0E8D8;  color: #8B6914; }
.pc-lo  { background: #F0E0E0;  color: #8B3A3A; }

/* COMBO CARD */
.combo-card {
    background: #FAFAF8;
    border: 1px solid #D5D3CC;
    border-radius: 16px;
    padding: 16px;
    margin-bottom: 10px;
}
.combo-rank-label {
    font-size: 0.62rem;
    font-weight: 700;
    letter-spacing: 0.1em;
    color: #636E72;
    text-transform: uppercase;
    margin-bottom: 10px;
}
.combo-row {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 6px;
}
.combo-icon {
    font-size: 1rem;
    width: 24px;
    text-align: center;
    flex-shrink: 0;
}
.combo-name {
    flex: 1;
    font-size: 0.83rem;
    color: #2D3436;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}
.combo-price-tag {
    font-size: 0.72rem;
    color: #636E72;
    font-family: inherit;
    flex-shrink: 0;
}
.combo-footer {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-top: 10px;
    padding-top: 10px;
    border-top: 1px solid #E0DED8;
}
.combo-total-protein {
    font-size: 1.1rem;
    font-weight: 700;
    color: #4A4A4A;
    font-family: inherit;
}
.combo-total-price {
    font-size: 0.8rem;
    color: #95A5A6;
    font-family: inherit;
}
.combo-change-tag {
    font-size: 0.65rem;
    color: #636E72;
}

/* DIVIDER */
.divider {
    border: none;
    border-top: 1px solid #E0DED8;
    margin: 0.8rem 0;
}

/* Slider label */
div[data-testid="stSlider"] label,
div[data-testid="stSelectbox"] label,
div[data-testid="stNumberInput"] label {
    font-size: 0.72rem !important;
    color: #64a89f !important;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    font-weight: 600;
}

.vega-embed { border-radius: 12px; overflow: hidden; }

/* Tab styling */
div[data-testid="stTabs"] button {
    font-size: 0.8rem !important;
    font-weight: 600 !important;
}
</style>
""", unsafe_allow_html=True)


# === ヘルパー関数 / Helper Functions ===
def pc_badge(score):
    if score >= 5.0: return "pc-hi",  f"P/C {score:.1f}"
    elif score >= 2.0: return "pc-mid", f"P/C {score:.1f}"
    else: return "pc-lo",  f"P/C {score:.1f}"

RANK_ICONS = ["①","②","③","④","⑤"]
RANK_CLS   = ["gold","silver","bronze","",""]

def render_rank_list(data, max_n=5):
    if data.empty:
        st.info("該当する商品がありません")
        return
    for i, (_, row) in enumerate(data.head(max_n).iterrows()):
        bc, bt = pc_badge(row["p/c_score"])
        num_str = RANK_ICONS[i] if i < 5 else f"{i+1}"
        num_cls = RANK_CLS[i] if i < 3 else ""
        name = esc(row['商品名'])
        html = (
            f'<div class="rank-item">'
            f'<span class="rank-num {num_cls}">{num_str}</span>'
            f'<span class="rank-name">{name}</span>'
            f'<div class="rank-meta">'
            f'<span class="rank-protein">{row["タンパク"]}g</span>'
            f'<span class="rank-price">¥{int(row["値段"])}</span>'
            f'<span class="pc-badge {bc}">{bt}</span>'
            f'</div></div>'
        )
        st.markdown(html, unsafe_allow_html=True)

def find_best_combos(df_okazu, df_karbo, df_bento, budget, n_okazu, n_karbo, include_bento, top_n=3):
    """予算内でタンパク質合計が最大になる組み合わせを探す。"""
    results = []

    # おかず候補リストの取得
    candidates = df_okazu[df_okazu["値段"] <= budget].sort_values("p/c_score", ascending=False).head(15)

    def okazu_combos(remaining, n):
        eligible = candidates[candidates["値段"] <= remaining]
        if len(eligible) < n:
            combos = [list(eligible.itertuples())]
        else:
            combos = list(combinations(range(len(eligible)), n))
            combos = [[eligible.iloc[i] for i in c] for c in combos]
        return combos

    def score_combo(items):
        return sum(r["タンパク"] for r in items), sum(r["値段"] for r in items)

    if include_bento:
        # 弁当モード（単品）
        for _, b in df_bento[df_bento["値段"] <= budget].iterrows():
            results.append({
                "items": [{"name": b["商品名"], "price": b["値段"], "protein": b["タンパク"], "type": "bento"}],
                "total_protein": b["タンパク"],
                "total_price": b["値段"]
            })
    else:
        # 主食＋おかずの組み合わせ
        karbo_pool = df_karbo[df_karbo["値段"] <= budget].sort_values("p/c_score", ascending=False).head(10) if n_karbo > 0 else pd.DataFrame()
        
        if n_karbo == 0:
            karbo_options = [None]
        else:
            karbo_options = [row for _, row in karbo_pool.iterrows()]

        for k_item in karbo_options:
            k_cost = k_item["値段"] if k_item is not None else 0
            if k_cost > budget:
                continue
            remaining = budget - k_cost

            if n_okazu == 0:
                combo_results = [{"items": [], "protein": 0, "price": 0}]
            else:
                lc = okazu_combos(remaining, n_okazu)
                combo_results = []
                for lset in lc:
                    tp = sum(r["タンパク"] for r in lset)
                    tc = sum(r["値段"] for r in lset)
                    if tc <= remaining:
                        combo_results.append({"items": lset, "protein": tp, "price": tc})

            for cr in combo_results:
                item_list = []
                if k_item is not None:
                    item_list.append({"name": k_item["商品名"], "price": k_item["値段"],
                                      "protein": k_item["タンパク"], "type": "karbo"})
                for r in cr["items"]:
                    item_list.append({"name": r["商品名"], "price": r["値段"],
                                      "protein": r["タンパク"], "type": "okazu"})
                tp = (k_item["タンパク"] if k_item is not None else 0) + cr["protein"]
                tc = k_cost + cr["price"]
                results.append({"items": item_list, "total_protein": tp, "total_price": tc})

    results.sort(key=lambda x: x["total_protein"], reverse=True)
    # 組み合わせの重複を除外
    seen = []
    unique = []
    for r in results:
        key = frozenset(i["name"] for i in r["items"])
        if key not in seen:
            seen.append(key)
            unique.append(r)
        if len(unique) >= top_n:
            break
    return unique

TYPE_ICON = {"okazu": "", "karbo": "", "bento": ""}

def esc(text):
    """商品名のHTMLエスケープ。"""
    return (str(text)
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
            .replace("'", "&#39;"))

def render_combo(combo, rank):
    rank_labels = ["Best Pick", "2nd Option", "3rd Option"]
    label = rank_labels[rank] if rank < 3 else f"#{rank+1}"
    rows_html = ""
    for item in combo["items"]:
        icon = TYPE_ICON.get(item["type"], "•")
        name = esc(item["name"])
        price = int(item["price"])
        protein = item["protein"]
        rows_html += (
            f'<div class="combo-row">'
            f'<span class="combo-icon">{icon}</span>'
            f'<span class="combo-name">{name}</span>'
            f'<span class="combo-price-tag">¥{price} · {protein}g</span>'
            f'</div>'
        )
    total_p = combo["total_protein"]
    total_c = int(combo["total_price"])
    html = (
        f'<div class="combo-card">'
        f'<div class="combo-rank-label">{label}</div>'
        f'{rows_html}'
        f'<div class="combo-footer">'
        f'<div><span class="combo-total-protein">{total_p:.1f}g</span>'
        f'<span class="combo-change-tag"> タンパク合計</span></div>'
        f'<div><span class="combo-total-price">¥{total_c} 合計</span></div>'
        f'</div></div>'
    )
    st.markdown(html, unsafe_allow_html=True)

# === HEADER / ヘッダー ===
st.markdown("""
<div class="app-header">
    <p class="app-sub">サミット × TTC</p>
    <h1 class="app-title">いい食事取ろう！</h1>
</div>
""", unsafe_allow_html=True)

# === TABS / タブ ===
tab1, tab2, tab3 = st.tabs(["自動おすすめ", "自分で選ぶ", "データ追加"])

# ─────────────────────────────────────
# タブ1: 自動おすすめ
# ─────────────────────────────────────
with tab1:
    st.markdown("<p class='section-title'>予算と構成を設定</p>", unsafe_allow_html=True)
    
    budget_auto = st.slider("予算 (¥)", 150, 800, 500, step=10, key="budget_auto")

    meal_type = st.radio(
        "食事スタイル",
        ["おかず + 主食", "弁当のみ", "おかずのみ"],
        horizontal=True,
        key="meal_type"
    )

    col1, col2 = st.columns(2)
    if meal_type == "おかず + 主食":
        with col1:
            n_okazu_auto = st.selectbox("おかず品数", [1, 2, 3], index=1, key="nl_auto")
        with col2:
            n_karbo_auto = st.selectbox("主食品数", [1, 2], index=0, key="nk_auto")
        include_bento = False
    elif meal_type == "弁当のみ":
        n_okazu_auto, n_karbo_auto = 0, 0
        include_bento = True
    else:
        with col1:
            n_okazu_auto = st.selectbox("おかず品数", [1, 2, 3], index=1, key="nl_auto2")
        n_karbo_auto = 0
        include_bento = False

    df_okazu  = df[df["group"] == "okazu"]
    df_karbo = df[df["group"] == "karbo"]
    df_bento = df[df["group"] == "bento"]

    combos = find_best_combos(df_okazu, df_karbo, df_bento, budget_auto,
                               n_okazu_auto, n_karbo_auto, include_bento, top_n=3)

    st.markdown("<hr class='divider'>", unsafe_allow_html=True)
    st.markdown("<p class='section-title'>おすすめ組み合わせ TOP 3</p>", unsafe_allow_html=True)

    if not combos:
        st.warning("予算内で条件を満たす組み合わせが見つかりません。予算を上げてみてください。")
    else:
        for i, combo in enumerate(combos):
            render_combo(combo, i)

# ─────────────────────────────────────
# タブ2: 自分で選ぶ
# ─────────────────────────────────────
with tab2:
    st.markdown("<p class='section-title'>フィルター</p>", unsafe_allow_html=True)
    
    budget_man = st.slider("予算上限 (¥)", 100, 800, 400, step=10, key="budget_man")
    
    sort_by = st.radio("並び替え", ["タンパク量", "P/Cスコア", "値段（安い順）"],
                        horizontal=True, key="sort_man")

    def sorted_df(data):
        if sort_by == "タンパク量":
            return data.sort_values("タンパク", ascending=False).reset_index(drop=True)
        elif sort_by == "P/Cスコア":
            return data.sort_values("p/c_score", ascending=False).reset_index(drop=True)
        else:
            return data.sort_values("値段", ascending=True).reset_index(drop=True)

    df_f = df[df["値段"] <= budget_man]

    # 統計カード
    st.markdown("<hr class='divider'>", unsafe_allow_html=True)
    count     = len(df_f)
    avg_prot  = f"{df_f['タンパク'].mean():.1f}g" if not df_f.empty else "ー"
    min_price = f"¥{int(df_f['値段'].min())}"     if not df_f.empty else "ー"
    st.markdown(f"""
    <div class="stat-grid">
        <div class="stat-card">
            <span class="stat-val">{count}</span>
            <span class="stat-lbl">対象品目</span>
        </div>
        <div class="stat-card">
            <span class="stat-val">{avg_prot}</span>
            <span class="stat-lbl">平均タンパク</span>
        </div>
        <div class="stat-card">
            <span class="stat-val">{min_price}</span>
            <span class="stat-lbl">最安値</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # おかずセクション
    df_okazu_f = sorted_df(df_f[df_f["group"] == "okazu"])
    st.markdown("""
    <div class="group-label">
        <span class="group-badge badge-lauk">おかず</span>
    </div>
    """, unsafe_allow_html=True)
    render_rank_list(df_okazu_f, max_n=5)

    # 主食セクション
    df_karbo_f = sorted_df(df_f[df_f["group"] == "karbo"])
    st.markdown("""
    <div class="group-label">
        <span class="group-badge badge-karbo">主食</span>
    </div>
    """, unsafe_allow_html=True)
    render_rank_list(df_karbo_f, max_n=5)

    # 弁当セクション
    df_bento_f = sorted_df(df_f[df_f["group"] == "bento"])
    st.markdown("""
    <div class="group-label">
        <span class="group-badge badge-bento">弁当</span>
    </div>
    """, unsafe_allow_html=True)
    render_rank_list(df_bento_f, max_n=5)

    # バーチャート（おかずのみ）
    st.markdown("<p class='section-title'>コスパ上位 — おかずのみ (g/¥100)</p>", unsafe_allow_html=True)
    if not df_okazu_f.empty:
        bar_df = df_okazu_f.head(7)[["商品名","p/c_score"]].copy()
        bar_df.columns = ["商品名","score"]
        bar_df["level"] = bar_df["score"].apply(
            lambda s: "High" if s >= 5.0 else ("Mid" if s >= 2.0 else "Low"))
        bar = (
            alt.Chart(bar_df)
            .mark_bar(cornerRadiusTopRight=6, cornerRadiusBottomRight=6)
            .encode(
                y=alt.Y("商品名:N", sort="-x", title=None,
                        axis=alt.Axis(labelFontSize=11, labelColor="#7F8C8D")),
                x=alt.X("score:Q", title="g / ¥100",
                        axis=alt.Axis(labelFontSize=10, labelColor="#7F8C8D")),
                color=alt.Color("level:N",
                    scale=alt.Scale(domain=["High","Mid","Low"],
                                    range=["#7D8E96","#B8A88A","#C4A4A4"]),
                    legend=None),
                tooltip=["商品名", alt.Tooltip("score:Q", title="P/C", format=".2f")]
            )
            .properties(height=200)
            .configure_view(strokeWidth=0, fill="#F5F4F0")
            .configure_axis(grid=False, domain=False)
            .configure(background="#0F1923")
        )
        st.altair_chart(bar, use_container_width=True)

# ─────────────────────────────────────
# タブ3: データ追加
# ─────────────────────────────────────
with tab3:
    st.markdown("<p class='section-title'>新しい商品を追加</p>", unsafe_allow_html=True)

    # Info box / 説明ボックス
    st.markdown("""
    <div style="background:rgba(13,148,136,0.06);border:1px solid rgba(13,148,136,0.2);
    border-radius:12px;padding:12px 14px;margin-bottom:1rem;font-size:0.8rem;color:#64a89f;">
    Data is saved to Google Sheets instantly. Rankings update in real time for all users. / 入力したデータはGoogle Sheetsに即座に保存され、全ユーザーのランキングがリアルタイムで更新されます。
    </div>
    """, unsafe_allow_html=True)

    ALL_CATS = sorted(df["カテゴリ"].dropna().unique().tolist())

    with st.form("add_item_form", clear_on_submit=True):
        col_a, col_b = st.columns(2)
        with col_a:
            new_name = st.text_input("商品名", placeholder="例: 鶏むね肉の塩焼き")
        with col_b:
            new_cat = st.selectbox("カテゴリ", ALL_CATS)

        col_c, col_d, col_e = st.columns(3)
        with col_c:
            new_type = st.selectbox("販売タイプ", ["per pack", "per 100gr"])
        with col_d:
            new_price = st.number_input("値段 (¥)", min_value=50, max_value=2000,
                                        value=200, step=10)
        with col_e:
            new_protein = st.number_input("タンパク (g)", min_value=0.0,
                                          max_value=100.0, value=10.0, step=0.1)

        submitted = st.form_submit_button("追加する", use_container_width=True)

    if submitted:
        # 入力チェック / Input validation
        if not new_name.strip():
            st.error("商品名を入力してください。")
        elif new_price <= 0:
            st.error("値段は0より大きくしてください。")
        else:
            # P/Cスコアとレベルを計算 / Compute P/C score and level 
            pc = round((new_protein / new_price) * 100, 2)
            if pc >= 5.0:
                level = "high"
            elif pc >= 2.0:
                level = "mid"
            else:
                level = "low"

            from datetime import datetime
            ts = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

            new_row = {
                "Timestamp": ts,
                "販売タイプ": new_type,
                "商品名": new_name.strip(),
                "カテゴリ": new_cat,
                "値段": float(new_price),
                "タンパク": float(new_protein),
                "p/c_score": pc,
                "pc_level": level
            }

            # スプレッドシートに新しいデータを追加 / Append new row to Google Sheets
            ws = get_worksheet()
            ws.append_row(value_input_option="USER_ENTERED",values=[
                new_row["Timestamp"],
                new_row["販売タイプ"],
                new_row["商品名"],
                new_row["カテゴリ"],
                new_row["値段"],
                new_row["タンパク"],
                new_row["p/c_score"],
                new_row["pc_level"],
            ])
            load_data.clear()

            st.success(f"「{new_name.strip()}」を追加しました！ P/Cスコア: {pc}")
            st.rerun()

    # ── 最近追加されたデータ / Recently added items ──
    st.markdown("<p class='section-title'>最近追加されたデータ</p>", unsafe_allow_html=True)

    df_show = df.tail(5).iloc[::-1].reset_index(drop=True)
    if df_show.empty:
        st.info("まだデータがありません")
    else:
        for i, row in df_show.iterrows():
            bc, bt = pc_badge(row["p/c_score"])
            name = esc(row["商品名"])
            html = (
                f'<div class="rank-item">'
                f'<span class="rank-num" style="color:#64a89f;font-size:0.65rem">'
                f'{str(row["Timestamp"])[:10]}</span>'
                f'<span class="rank-name">{name}</span>'
                f'<div class="rank-meta">'
                f'<span class="rank-protein">{row["タンパク"]}g</span>'
                f'<span class="rank-price">¥{int(row["値段"])}</span>'
                f'<span class="pc-badge {bc}">{bt}</span>'
                f'</div></div>'
            )
            st.markdown(html, unsafe_allow_html=True)

    # ── 最後のデータを削除 (undo) / Delete last entry ──
    st.markdown("<hr class='divider'>", unsafe_allow_html=True)
    st.markdown("<p class='section-title'>最後のデータを削除</p>", unsafe_allow_html=True)
    st.markdown("""
    <div style="font-size:0.75rem;color:#64a89f;margin-bottom:0.6rem;">
    Use only to undo a mistaken entry. This action cannot be undone. / 誤って追加したときだけ使用してください。この操作は元に戻せません。
    </div>
    """, unsafe_allow_html=True)
    if st.button("最後の1件を削除", use_container_width=False):
        ws = get_worksheet()
        last_row = len(ws.get_all_values())
        if last_row > 1:
            ws.delete_rows(last_row)
            load_data.clear()
            st.warning("最後のデータを削除しました。")
            st.rerun()
        else:
            st.error("削除するデータがありません。")
