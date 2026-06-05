import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')

# ── Page setup ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Bank Retention Dashboard",
    page_icon="🏦",
    layout="wide"
)

# ── Load data ───────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_csv('European_Bank_excel.csv')
    df['Churn_Status'] = df['Exited'].map({1: 'Churned', 0: 'Retained'})

    # Relationship Strength Index
    df['RSI'] = (
        (df['Tenure'] / 10) * 0.30
        + (df['Num_Of_Products'] / 4) * 0.25
        + (df['Is_Active_Member']) * 0.25
        + (df['Has_Cr._Card']) * 0.10
        + ((df['Credit_Score'] - 350) / 500) * 0.10
    ).round(3)

    df['RSI_Tier'] = pd.cut(
        df['RSI'],
        bins=[0, 0.3, 0.5, 0.7, 1.0],
        labels=['Weak', 'Moderate', 'Strong', 'Premium']
    )
    return df

df = load_data()

# ── Header ──────────────────────────────────────────────────────────────────
st.title("🏦 European Central Bank — Customer Retention Dashboard")
st.markdown("**Customer Engagement & Product Utilization Analytics  |  Aviral  |  BML Munjal University MBA 2025–27**")
st.markdown("---")

# ── Sidebar Filters ─────────────────────────────────────────────────────────
st.sidebar.title("🔍 Filters")

all_geo = ['All'] + sorted(df['Geography'].unique().tolist())
selected_geo = st.sidebar.selectbox("Country", all_geo)

all_engage = ['All'] + sorted(df['Engagement_Group'].unique().tolist())
selected_engage = st.sidebar.selectbox("Engagement Group", all_engage)

all_gender = ['All', 'Male', 'Female']
selected_gender = st.sidebar.selectbox("Gender", all_gender)

st.sidebar.markdown("---")
st.sidebar.subheader("Sliders")

product_range = st.sidebar.slider("Number of Products", 1, 4, (1, 4))
balance_range = st.sidebar.slider("Balance Range (€)", 0, 260000, (0, 260000), step=10000)
salary_range = st.sidebar.slider("Salary Range (€)", 0, 200000, (0, 200000), step=10000)

# ── Apply Filters ────────────────────────────────────────────────────────────
filtered = df.copy()
if selected_geo     != 'All': filtered = filtered[filtered['Geography']        == selected_geo]
if selected_engage  != 'All': filtered = filtered[filtered['Engagement_Group'] == selected_engage]
if selected_gender  != 'All': filtered = filtered[filtered['Gender']           == selected_gender]

filtered = filtered[
    (filtered['Num_Of_Products'] >= product_range[0]) &
    (filtered['Num_Of_Products'] <= product_range[1]) &
    (filtered['Balance'] >= balance_range[0]) &
    (filtered['Balance'] <= balance_range[1]) &
    (filtered['Estimated_Salary'] >= salary_range[0]) &
    (filtered['Estimated_Salary'] <= salary_range[1])
]

# ── KPI Cards ────────────────────────────────────────────────────────────────
st.subheader("📊 Key Performance Indicators")
k1, k2, k3, k4, k5 = st.columns(5)
churn_rate = filtered['Exited'].mean() * 100 if len(filtered) > 0 else 0
active_pct = filtered['Is_Active_Member'].mean() * 100 if len(filtered) > 0 else 0
avg_rsi = filtered['RSI'].mean() if len(filtered) > 0 else 0

k1.metric("Total Customers", f"{len(filtered):,}")
k2.metric("Churn Rate", f"{churn_rate:.1f}%")
k3.metric("Active Members", f"{active_pct:.1f}%")
k4.metric("Churned", f"{filtered['Exited'].sum():,}")
k5.metric("Avg RSI Score", f"{avg_rsi:.3f}")
st.markdown("---")

# ── TABS ─────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs([
    "📋 Engagement vs Churn",
    "📦 Product Utilization",
    "⚠️ High-Value Disengaged Detector",
    "🛡️ Retention Strength Scoring"
])

# ════════════════════════════════════════════════════════════════════════════
# TAB 1 — ENGAGEMENT VS CHURN
# ════════════════════════════════════════════════════════════════════════════
with tab1:
    st.header("Engagement vs Churn Overview")
    st.write("How engagement groups relate to customer churn across countries, gender, and age.")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Churn Rate by Engagement Group")
        churn_eng = filtered.groupby('Engagement_Group')['Exited'].mean().round(3) * 100
        churn_eng = churn_eng.sort_values(ascending=False)
        fig, ax = plt.subplots(figsize=(7, 5))
        bars = ax.barh(churn_eng.index, churn_eng.values,
                       color='#111111', edgecolor='white')
        for bar in bars:
            ax.text(bar.get_width() + 0.3,
                    bar.get_y() + bar.get_height() / 2,
                    f"{bar.get_width():.1f}%",
                    va='center', fontsize=9, fontweight='bold')
        ax.set_xlabel("Churn Rate (%)")
        ax.set_title("Churn Rate by Engagement Group", fontweight='bold')
        ax.grid(axis='x', linestyle='--', alpha=0.4)
        st.pyplot(fig)
        plt.close()

    with col2:
        st.subheader("Churn Rate by Country")
        churn_geo = filtered.groupby('Geography')['Exited'].mean().round(3) * 100
        churn_geo = churn_geo.sort_values(ascending=False)
        fig, ax = plt.subplots(figsize=(7, 5))
        bars = ax.bar(churn_geo.index, churn_geo.values,
                      color=['#000000', '#555555', '#999999'], edgecolor='white', width=0.5)
        for bar in bars:
            ax.text(bar.get_x() + bar.get_width() / 2,
                    bar.get_height() + 0.3,
                    f"{bar.get_height():.1f}%",
                    ha='center', fontweight='bold')
        ax.set_ylabel("Churn Rate (%)")
        ax.set_title("Churn Rate by Country", fontweight='bold')
        ax.grid(axis='y', linestyle='--', alpha=0.4)
        st.pyplot(fig)
        plt.close()

    col3, col4 = st.columns(2)

    with col3:
        st.subheader("Churn Rate by Gender")
        churn_gen = filtered.groupby('Gender')['Exited'].mean().round(3) * 100
        fig, ax = plt.subplots(figsize=(6, 4))
        bars = ax.bar(churn_gen.index, churn_gen.values,
                      color=['#111111', '#888888'], edgecolor='white', width=0.4)
        for bar in bars:
            ax.text(bar.get_x() + bar.get_width() / 2,
                    bar.get_height() + 0.3,
                    f"{bar.get_height():.1f}%",
                    ha='center', fontweight='bold')
        ax.set_ylabel("Churn Rate (%)")
        ax.set_title("Churn Rate by Gender", fontweight='bold')
        ax.grid(axis='y', linestyle='--', alpha=0.4)
        st.pyplot(fig)
        plt.close()

    with col4:
        st.subheader("Churn Rate by Age Group")
        churn_age = filtered.groupby('Age_Group')['Exited'].mean().round(3) * 100
        order = ['<30', '30-40', '40-50', '50-60', '60+']
        churn_age = churn_age.reindex([x for x in order if x in churn_age.index])
        fig, ax = plt.subplots(figsize=(6, 4))
        bars = ax.bar(churn_age.index, churn_age.values,
                      color='#333333', edgecolor='white', width=0.5)
        for bar in bars:
            ax.text(bar.get_x() + bar.get_width() / 2,
                    bar.get_height() + 0.3,
                    f"{bar.get_height():.1f}%",
                    ha='center', fontsize=9, fontweight='bold')
        ax.set_ylabel("Churn Rate (%)")
        ax.set_title("Churn Rate by Age Group", fontweight='bold')
        ax.grid(axis='y', linestyle='--', alpha=0.4)
        st.pyplot(fig)
        plt.close()

    st.subheader("Engagement Group Summary Table")
    eng_summary = filtered.groupby('Engagement_Group').agg(
        Total=('Customer_Id', 'count'),
        Churned=('Exited', 'sum'),
        Churn_Rate=('Exited', lambda x: round(x.mean() * 100, 1)),
        Avg_Age=('Age', 'mean'),
        Avg_Balance=('Balance', 'mean'),
        Avg_Salary=('Estimated_Salary', 'mean'),
    ).round(1).reset_index()
    st.dataframe(eng_summary, use_container_width=True)

# ════════════════════════════════════════════════════════════════════════════
# TAB 2 — PRODUCT UTILIZATION
# ════════════════════════════════════════════════════════════════════════════
with tab2:
    st.header("Product Utilization Impact Analysis")
    st.write("How the number of bank products affects customer retention.")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("⭐ Churn Rate by Number of Products")
        st.caption("This is the most important chart in the project")
        churn_prod = filtered.groupby('Num_Of_Products')['Exited'].mean().round(3) * 100
        fig, ax = plt.subplots(figsize=(7, 5))
        colors = ['#555555', '#111111', '#CC0000', '#FF0000']
        bars = ax.bar(churn_prod.index.astype(str), churn_prod.values,
                      color=colors[:len(churn_prod)], edgecolor='white', width=0.5)
        for bar in bars:
            ax.text(bar.get_x() + bar.get_width() / 2,
                    bar.get_height() + 1,
                    f"{bar.get_height():.1f}%",
                    ha='center', fontweight='bold', fontsize=12)
        ax.set_xlabel("Number of Products")
        ax.set_ylabel("Churn Rate (%)")
        ax.set_title("Churn Rate by Products Held", fontweight='bold', fontsize=14)
        ax.grid(axis='y', linestyle='--', alpha=0.4)
        st.pyplot(fig)
        plt.close()

        st.info("📌 **Key Finding:** 2 products is the sweet spot (7.6% churn). "
                "3+ products have 82–100% churn — product over-saturation destroys loyalty.")

    with col2:
        st.subheader("Product Distribution")
        prod_dist = filtered['Num_Of_Products'].value_counts().sort_index()
        fig, ax = plt.subplots(figsize=(7, 5))
        ax.pie(prod_dist.values,
               labels=[f"{i} product{'s' if i > 1 else ''}\n(n={v:,})"
                       for i, v in zip(prod_dist.index, prod_dist.values)],
               autopct='%1.1f%%',
               colors=['#333333', '#666666', '#999999', '#CCCCCC'],
               startangle=140,
               textprops={'fontsize': 10})
        ax.set_title("Products Held Distribution", fontweight='bold')
        st.pyplot(fig)
        plt.close()

    col3, col4 = st.columns(2)

    with col3:
        st.subheader("Credit Card vs Churn")
        cc = filtered.groupby('Has_Cr._Card')['Exited'].mean().round(3) * 100
        fig, ax = plt.subplots(figsize=(6, 4))
        labels = ['No Card', 'Has Card']
        bars = ax.bar(labels, cc.values,
                      color=['#111111', '#888888'], edgecolor='white', width=0.4)
        for bar in bars:
            ax.text(bar.get_x() + bar.get_width() / 2,
                    bar.get_height() + 0.2,
                    f"{bar.get_height():.1f}%",
                    ha='center', fontweight='bold')
        ax.set_ylabel("Churn Rate (%)")
        ax.set_title("Credit Card Stickiness", fontweight='bold')
        ax.grid(axis='y', linestyle='--', alpha=0.4)
        st.pyplot(fig)
        plt.close()

        st.warning("Credit cards do NOT reduce churn — almost identical rates (20.2% vs 20.8%).")

    with col4:
        st.subheader("Products by Country")
        prod_geo = filtered.groupby(['Geography', 'Num_Of_Products']).size().unstack(fill_value=0)
        fig, ax = plt.subplots(figsize=(7, 4))
        prod_geo.plot(kind='bar', ax=ax,
                      color=['#111111', '#555555', '#999999', '#CCCCCC'],
                      edgecolor='white', width=0.7)
        ax.set_title("Product Count by Country", fontweight='bold')
        ax.set_ylabel("Customers")
        ax.set_xlabel("")
        ax.tick_params(axis='x', rotation=0)
        ax.legend(title='Products', fontsize=8)
        ax.grid(axis='y', linestyle='--', alpha=0.4)
        st.pyplot(fig)
        plt.close()

# ════════════════════════════════════════════════════════════════════════════
# TAB 3 — HIGH-VALUE DISENGAGED DETECTOR
# ════════════════════════════════════════════════════════════════════════════
with tab3:
    st.header("⚠️ High-Value Disengaged Customer Detector")
    st.write("Identifies inactive customers with high balances who haven't left yet — your top retention priority.")

    # Thresholds
    st.sidebar.markdown("---")
    st.sidebar.subheader("VIP Detector Settings")
    min_bal = st.sidebar.number_input("Min Balance for VIP (€)", value=100000, step=10000)

    at_risk = filtered[
        (filtered['Is_Active_Member'] == 0) &
        (filtered['Balance'] > min_bal) &
        (filtered['Exited'] == 0)
    ].sort_values('Balance', ascending=False)

    col1, col2, col3 = st.columns(3)
    col1.metric("At-Risk VIP Customers", f"{len(at_risk):,}")
    col2.metric("Total Balance at Risk", f"€{at_risk['Balance'].sum():,.0f}")
    col3.metric("Avg Balance per VIP", f"€{at_risk['Balance'].mean():,.0f}" if len(at_risk) > 0 else "€0")

    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("At-Risk VIPs by Country")
        if len(at_risk) > 0:
            vip_geo = at_risk['Geography'].value_counts()
            fig, ax = plt.subplots(figsize=(6, 4))
            bars = ax.bar(vip_geo.index, vip_geo.values,
                          color='#CC0000', edgecolor='white', width=0.5)
            for bar in bars:
                ax.text(bar.get_x() + bar.get_width() / 2,
                        bar.get_height() + 1,
                        str(int(bar.get_height())),
                        ha='center', fontweight='bold')
            ax.set_title("At-Risk VIPs by Country", fontweight='bold')
            ax.set_ylabel("Count")
            ax.grid(axis='y', linestyle='--', alpha=0.4)
            st.pyplot(fig)
            plt.close()
        else:
            st.info("No at-risk VIPs found with current filters.")

    with col2:
        st.subheader("At-Risk VIPs by Age Group")
        if len(at_risk) > 0:
            vip_age = at_risk['Age_Group'].value_counts()
            fig, ax = plt.subplots(figsize=(6, 4))
            bars = ax.bar(vip_age.index, vip_age.values,
                          color='#880000', edgecolor='white', width=0.5)
            for bar in bars:
                ax.text(bar.get_x() + bar.get_width() / 2,
                        bar.get_height() + 0.5,
                        str(int(bar.get_height())),
                        ha='center', fontweight='bold')
            ax.set_title("At-Risk VIPs by Age Group", fontweight='bold')
            ax.set_ylabel("Count")
            ax.grid(axis='y', linestyle='--', alpha=0.4)
            st.pyplot(fig)
            plt.close()
        else:
            st.info("No at-risk VIPs found with current filters.")

    st.subheader("Top 50 At-Risk VIP Customers — Action List")
    if len(at_risk) > 0:
        st.dataframe(
            at_risk[['Customer_Id', 'Geography', 'Gender', 'Age',
                     'Balance', 'Estimated_Salary', 'Credit_Score',
                     'Num_Of_Products', 'Tenure', 'Engagement_Group']
            ].head(50).reset_index(drop=True),
            use_container_width=True
        )
    else:
        st.info("Adjust filters to find at-risk VIP customers.")

# ════════════════════════════════════════════════════════════════════════════
# TAB 4 — RETENTION STRENGTH SCORING
# ════════════════════════════════════════════════════════════════════════════
with tab4:
    st.header("🛡️ Retention Strength Scoring Panel")
    st.write("The Relationship Strength Index (RSI) combines tenure, product depth, activity, "
             "credit card ownership, and credit score into a single 0–1 score.")

    st.markdown("""
    **RSI Formula:**
    `RSI = (Tenure/10)×0.30 + (Products/4)×0.25 + (IsActive)×0.25 + (HasCard)×0.10 + ((CreditScore−350)/500)×0.10`

    **Interpretation:** Weak (< 0.3) | Moderate (0.3–0.5) | Strong (0.5–0.7) | Premium (> 0.7)
    """)

    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("RSI Distribution")
        fig, ax = plt.subplots(figsize=(7, 5))
        ax.hist(filtered['RSI'], bins=30, color='#222222', edgecolor='white', alpha=0.9)
        ax.axvline(x=0.3, color='red', linestyle='--', label='Weak threshold')
        ax.axvline(x=0.5, color='orange', linestyle='--', label='Moderate threshold')
        ax.axvline(x=0.7, color='green', linestyle='--', label='Strong threshold')
        ax.legend(fontsize=9)
        ax.set_xlabel("RSI Score")
        ax.set_ylabel("Number of Customers")
        ax.set_title("Distribution of Relationship Strength Index", fontweight='bold')
        ax.grid(axis='y', linestyle='--', alpha=0.4)
        st.pyplot(fig)
        plt.close()

    with col2:
        st.subheader("Churn Rate by RSI Tier")
        rsi_churn = filtered.groupby('RSI_Tier', observed=True)['Exited'].mean().round(3) * 100
        fig, ax = plt.subplots(figsize=(7, 5))
        colors = ['#CC0000', '#FF8800', '#888888', '#228B22']
        bars = ax.bar(rsi_churn.index.astype(str), rsi_churn.values,
                      color=colors[:len(rsi_churn)], edgecolor='white', width=0.5)
        for bar in bars:
            ax.text(bar.get_x() + bar.get_width() / 2,
                    bar.get_height() + 0.5,
                    f"{bar.get_height():.1f}%",
                    ha='center', fontweight='bold')
        ax.set_xlabel("RSI Tier")
        ax.set_ylabel("Churn Rate (%)")
        ax.set_title("Churn Rate by Relationship Strength", fontweight='bold')
        ax.grid(axis='y', linestyle='--', alpha=0.4)
        st.pyplot(fig)
        plt.close()

    col3, col4 = st.columns(2)

    with col3:
        st.subheader("RSI Tier Breakdown")
        rsi_dist = filtered['RSI_Tier'].value_counts()
        fig, ax = plt.subplots(figsize=(6, 5))
        ax.pie(rsi_dist.values,
               labels=[f"{t}\n(n={v:,})" for t, v in zip(rsi_dist.index, rsi_dist.values)],
               autopct='%1.1f%%',
               colors=['#CC0000', '#FF8800', '#888888', '#228B22'],
               startangle=140,
               textprops={'fontsize': 10})
        ax.set_title("RSI Tier Distribution", fontweight='bold')
        st.pyplot(fig)
        plt.close()

    with col4:
        st.subheader("Avg RSI by Engagement Group")
        rsi_eng = filtered.groupby('Engagement_Group')['RSI'].mean().round(3)
        rsi_eng = rsi_eng.sort_values(ascending=False)
        fig, ax = plt.subplots(figsize=(7, 5))
        bars = ax.barh(rsi_eng.index, rsi_eng.values,
                       color='#333333', edgecolor='white')
        for bar in bars:
            ax.text(bar.get_width() + 0.005,
                    bar.get_y() + bar.get_height() / 2,
                    f"{bar.get_width():.3f}",
                    va='center', fontsize=9)
        ax.set_xlabel("Average RSI Score")
        ax.set_title("Relationship Strength by Engagement Group", fontweight='bold')
        ax.grid(axis='x', linestyle='--', alpha=0.4)
        st.pyplot(fig)
        plt.close()

    st.subheader("RSI Summary Table")
    rsi_table = filtered.groupby('RSI_Tier', observed=True).agg(
        Total=('Customer_Id', 'count'),
        Churned=('Exited', 'sum'),
        Churn_Rate=('Exited', lambda x: round(x.mean() * 100, 1)),
        Avg_Balance=('Balance', 'mean'),
        Avg_Tenure=('Tenure', 'mean'),
        Avg_Products=('Num_Of_Products', 'mean'),
    ).round(1).reset_index()
    st.dataframe(rsi_table, use_container_width=True)

    st.subheader("Full Customer Data with RSI Scores")
    st.write(f"Showing {len(filtered):,} customers based on your filters")
    st.dataframe(
        filtered[['Customer_Id', 'Geography', 'Gender', 'Age', 'Tenure',
                  'Balance', 'Num_Of_Products', 'Is_Active_Member',
                  'Credit_Score', 'Engagement_Group', 'RSI', 'RSI_Tier',
                  'Churn_Status']
        ].sort_values('RSI', ascending=True).reset_index(drop=True),
        use_container_width=True
    )

# ── Footer ───────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("*Aviral  |  MBA 2025–27  |  BML Munjal University  |  The European Central Bank x Unified Mentor*")
