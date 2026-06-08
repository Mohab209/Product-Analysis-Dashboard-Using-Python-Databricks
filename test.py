import streamlit as st
import pandas as pd
import plotly.express as px
from databricks import sql


# =========================
# Page Config
# =========================

st.set_page_config(
    page_title="Product Analytics Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

colors = {
    "accent_red":       "#E63946",
    "light_background": "#F1FAEE",
    "soft_cyan":        "#A8DADC",
    "primary_blue":     "#457B9D",
    "dark_navy":        "#1D3557",
}

st.markdown(f"""
<style>
    /* ── global background ── */
    html, body,
    [data-testid="stAppViewContainer"],
    [data-testid="stMainBlockContainer"],
    .main {{
        background-color: {colors['light_background']} !important;
    }}

    /* ── sidebar ── */
    [data-testid="stSidebar"] {{
        background-color: {colors['primary_blue']} !important;
    }}
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] span {{
        color: {colors['light_background']} !important;
    }}
    [data-testid="stSidebar"] div[class*="stSelectbox"] > div,
    [data-testid="stSidebar"] select {{
        background-color: {colors['light_background']} !important;
        color: {colors['dark_navy']} !important;
        border: 2px solid {colors['accent_red']} !important;
    }}
    [data-testid="stSidebar"] div[role="listbox"],
    [data-testid="stSidebar"] div[class*="menu"],
    [data-testid="stSidebar"] div[class*="option"] {{
        background-color: {colors['light_background']} !important;
        color: {colors['dark_navy']} !important;
    }}

    /* ── body text ── */
    h1, h2, h3, p, label, span {{
        color: {colors['dark_navy']} !important;
    }}
    h1 {{
        border-bottom: 3px solid {colors['accent_red']};
        padding-bottom: 10px;
    }}

    /* ── KPI metric cards ── */
    [data-testid="metric-container"] {{
        background-color: {colors['dark_navy']} !important;
        border-radius: 12px !important;
        padding: 20px !important;
        border: none !important;
        box-shadow: none !important;
    }}
    [data-testid="stMetricLabel"] > div,
    [data-testid="stMetricLabel"] p,
    [data-testid="stMetricLabel"] span {{
        color: #A8DADC !important;
        font-size: 13px !important;
    }}
    [data-testid="stMetricValue"] > div,
    [data-testid="stMetricValue"] {{
        color: {colors['light_background']} !important;
        font-size: 26px !important;
        font-weight: 600 !important;
    }}

    /* ── dataframe ── */
    [data-testid="stDataFrame"] {{
        background-color: {colors['dark_navy']} !important;
    }}

    /* ── plotly axis text ── */
    svg text {{
        fill: {colors['dark_navy']} !important;
        font-weight: bold;
        font-size: 12px !important;
    }}
</style>
""", unsafe_allow_html=True)

st.title("📦 Product Analytics Dashboard")


# =========================
# Load Data
# =========================
@st.cache_data(ttl=3600*24)
def load_data():
    with sql.connect(
        server_hostname=st.secrets["DATABRICKS_HOST"],
        http_path=st.secrets["DATABRICKS_HTTP_PATH"],
        access_token=st.secrets["DATABRICKS_TOKEN"],
    ) as conn:
        query = "SELECT * FROM products.gold.gold_products"
        df = pd.read_sql(query, conn)
    return df


df = load_data()


# =========================
# Sidebar Filters
# =========================
categories = sorted(df["category"].dropna().unique())
selected_category = st.sidebar.selectbox("Category", ["All"] + list(categories))

if selected_category != "All":
    df = df[df["category"] == selected_category]


# =========================
# KPI icons (unicode so no extra deps)
# =========================
ICON_BOX      = "📦"
ICON_PRICE    = "🏷️"
ICON_STAR     = "⭐"
ICON_DOLLAR   = "💵"

# =========================
# KPIs
# =========================
total_products       = int(df["product_id"].count())
avg_price            = round(float(df["price"].mean()), 2)
avg_rating           = round(float(df["rating"].mean()), 2)
total_inventory_value = round(float(df["inventory_value"].sum()), 2)

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(f"{ICON_BOX}  Total Products",  total_products)
with col2:
    st.metric(f"{ICON_PRICE}  Average Price",   avg_price)
with col3:
    st.metric(f"{ICON_STAR}  Average Rating",  avg_rating)
with col4:
    st.metric(f"{ICON_DOLLAR}  Total Inventory Value",
              f"${total_inventory_value:,.2f}")


# =========================
# Shared layout helper
# =========================
def base_layout(fig, title=""):
    fig.update_layout(
        title=title,
        paper_bgcolor=colors["light_background"],
        plot_bgcolor=colors["light_background"],
        font=dict(color=colors["dark_navy"], size=12),
        title_font=dict(color=colors["dark_navy"], size=14),
        xaxis=dict(showgrid=False, title_font=dict(color=colors["dark_navy"])),
        yaxis=dict(showgrid=False, title_font=dict(color=colors["dark_navy"])),
        margin=dict(t=50, b=40, l=40, r=20),
    )
    return fig


# =========================
# Chart 1 – Inventory Value by Category
# =========================
category_inventory = (
    df.groupby("category")["inventory_value"]
    .sum()
    .reset_index()
    .sort_values("inventory_value", ascending=False)
)

fig1 = px.bar(
    category_inventory,
    x="category",
    y="inventory_value",
    text="inventory_value",
)
fig1 = base_layout(fig1, "Inventory Value by Category")
fig1.update_traces(
    marker_color=colors["accent_red"],
    texttemplate="%{text:,.0f}",
    textposition="outside",
    textfont=dict(color=colors["dark_navy"], size=11),
)
fig1.update_layout(hovermode="x unified")
st.plotly_chart(fig1, use_container_width=True)


# =========================
# Chart 2 – Price Distribution
# =========================
fig2 = px.histogram(df, x="price", nbins=5, text_auto=".0f")
fig2 = base_layout(fig2, "Price Distribution")
fig2.update_traces(
    marker_color=colors["soft_cyan"],
    textposition="outside",
    textfont=dict(color=colors["dark_navy"], size=11),
)
fig2.update_layout(hovermode="x unified")
st.plotly_chart(fig2, use_container_width=True)


# =========================
# Chart 3 – Rating vs Price
# =========================
fig3 = px.scatter(
    df,
    x="price",
    y="rating",
    hover_name="title",
    color="category",
    color_discrete_sequence=[
        colors["dark_navy"],
        colors["accent_red"],
        colors["primary_blue"],
        colors["soft_cyan"],
        "#6B8F71",
    ],
)
fig3 = base_layout(fig3, "Rating vs Price")
fig3.update_layout(
    hovermode="closest",
    legend=dict(
        font=dict(color=colors["dark_navy"], size=11),
        bgcolor=colors["light_background"],
        bordercolor=colors["dark_navy"],
        borderwidth=1,
    ),
)
st.plotly_chart(fig3, use_container_width=True)


# =========================
# Top Products Table
# =========================
st.markdown(f"""
    <h2 style="color:{colors['accent_red']};
               border-bottom:3px solid {colors['accent_red']};
               padding-bottom:10px;">
        🏆 Top Products by Inventory Value
    </h2>
""", unsafe_allow_html=True)

top_products = (
    df.sort_values("inventory_value", ascending=False)
    .head(10)
    .reset_index(drop=True)
)
top_products.index += 1   # 1-based rank shown in table

st.dataframe(top_products, use_container_width=True)
