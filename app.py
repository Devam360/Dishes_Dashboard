import streamlit as st
import pandas as pd
import plotly.express as px

# ------------------ PAGE CONFIG ------------------
st.set_page_config(page_title="Restaurant Sales Dashboard", layout="wide")

# ------------------ CUSTOM STYLING ------------------
st.markdown("""
<style>
body {
    background-color: #0e0e0e;
    color: white;
}

.stApp {
    background-color: #0e0e0e;
}

h1, h2, h3, h4, h5, h6, p, label {
    color: white !important;
}

.sidebar .sidebar-content {
    background-color: #4D0202;
}

.stRadio > div {
    background-color: #4D0202;
    padding: 10px;
    border-radius: 10px;
}

.stRadio label {
    color: white !important;
}

.stButton>button {
    background-color: #ff2e2e;
    color: white;
    border-radius: 8px;
}

.stMetric {
    background-color: #4D0202;
    padding: 10px;
    border-radius: 10px;
    color:#0e0e0e
    align:center
}
</style>
""", unsafe_allow_html=True)


# ------------------ LOAD DATA ------------------
@st.cache_data
def load_data():
    df = pd.read_csv("restaurant_sales_data.csv")
    return df

df = load_data()

# ------------------ SIDEBAR ------------------
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Overview", "Data Cleaning", "EDA", "Insights"])

# ------------------ OVERVIEW ------------------
if page == "Overview":
    st.title("🍽️ Restaurant Sales Dashboard")

    st.markdown("## Dataset Overview")

    st.write("""
This dataset contains **17,534 restaurant transactions** across multiple categories such as 
starters, main dishes, desserts, drinks, and side dishes. 

It is intentionally designed as a **dirty dataset**, meaning it includes missing and inconsistent values 
to simulate real-world data challenges.  
             
Relevant Variables Used:
- **Category:** Type of dish served (Starter, Main Course, Dessert, etc.)
- **Item:** Specific names of items sold
- **Price:** Individual prices of the corresponding item
- **Quantity:** Number of portions of the item ordered
- **Order Total:** Price * Quantity
- **Order Date:** Day of transaction
- **Payment Method:** Way of payment

### Key Characteristics:
- Missing values in columns like *Item, Price, Quantity, Order Total, Payment Method*
- Logical dependencies (Order Total = Price * Quantity)
- Time range: **Jan 2022 - Dec 2023**
- Useful for:
  - Data cleaning practice
  - Exploratory Data Analysis
  - Feature engineering
    """)

    st.write("### Sample Data")
    st.dataframe(df.head(), use_container_width=True)

    st.write("### Shape of Dataset:", df.shape)

# ------------------ DATA CLEANING ------------------
elif page == "Data Cleaning":
    st.title("🧹 Data Cleaning & Feature Engineering")

    df['Order Date'] = pd.to_datetime(df['Order Date'])

    st.write("### Missing Values Before Cleaning")
    st.table(df.isnull().sum())

    # Fill numeric logic
    df['Quantity'] = df['Quantity'].fillna(1)
    df['Price'] = df['Price'].fillna(df['Order Total'] / df['Quantity'])
    df['Order Total'] = df['Order Total'].fillna(df['Price'] * df['Quantity'])

    # Fill categorical
    df['Payment Method'] = df['Payment Method'].fillna("Unknown")
    df['Item'] = df['Item'].fillna("Unknown")

    # Remove duplicates
    df = df.drop_duplicates()

    st.write("### Missing Values After Cleaning")
    st.table(df.isnull().sum())

    # Feature engineering
    df['Year'] = df['Order Date'].dt.year
    df['Month'] = df['Order Date'].dt.month_name()
    df['Day'] = df['Order Date'].dt.day_name()
    df['Week'] = df['Order Date'].dt.isocalendar().week

    st.write("### New Features Added")
    st.write(df[['Order Date','Year','Month','Day','Week']].head())

# ------------------ EDA ------------------
elif page == "EDA":
    st.title("📊 Exploratory Data Analysis")

    df['Order Date'] = pd.to_datetime(df['Order Date'])

    st.subheader("Central Tendencies")

    st.write("### Order Total Statistics (in $)")
    st.write({
        "Mean": df['Order Total'].mean(),
        "Median": df['Order Total'].median(),
        "Min": df['Order Total'].min(),
        "Max": df['Order Total'].max(),
        "Std Dev": df['Order Total'].std()
    })

    st.write("### Quantity Statistics")
    st.write({
        "Mean": df['Quantity'].mean(),
        "Median": df['Quantity'].median(),
        "Min": df['Quantity'].min(),
        "Max": df['Quantity'].max()
    })

    # Boxplot for outliers
    st.subheader("Outlier Detection")
    fig = px.box(df, y="Order Total", title="Order Total Distribution",width=200,height=700)
    st.plotly_chart(fig)

    # Category distribution
    st.subheader("Category Distribution")
    fig = px.histogram(df, x="Category", range_y=[3400,3600])
    st.plotly_chart(fig, use_container_width=True)

# ------------------ INSIGHTS ------------------
elif page == "Insights":
    st.title("📈 Interactive Insights Dashboard")

    df['Order Date'] = pd.to_datetime(df['Order Date'])
    df['Month'] = df['Order Date'].dt.month_name()
    df['Payment Method']=df['Payment Method'].fillna('unknown')
    # ------------------ FILTERS ------------------
    st.sidebar.header("Filters")

    category_filter = st.sidebar.multiselect(
        "Select Category",
        options=df['Category'].unique(),
        default=df['Category'].unique()
    )

    payment_filter = st.sidebar.multiselect(
        "Select Payment Method",
        options=df['Payment Method'].unique(),
        default=df['Payment Method'].unique()
    )

    filtered_df = df[
        (df['Category'].isin(category_filter)) &
        (df['Payment Method'].isin(payment_filter))
    ]

    # ------------------ KPI ------------------
    col1, col2, col3 = st.columns(3)

    col1.metric("Total Revenue", f"${filtered_df['Order Total'].sum():,.0f}")
    col2.metric("Avg Order Value", f"${filtered_df['Order Total'].mean():.2f}")
    col3.metric("Total Orders", len(filtered_df))

    # ------------------ CHARTS ------------------

    st.subheader("Sales by Category")
    fig1 = px.bar(
        filtered_df.groupby("Category")['Order Total'].sum().reset_index(),
        x="Category",
        y="Order Total",
        color="Category"
    )
    st.plotly_chart(fig1, use_container_width=True)

    st.subheader("Monthly Sales Trend")
    fig2 = px.line(
        filtered_df.groupby("Month")['Order Total'].sum().reset_index(),
        x="Month",
        y="Order Total",
        markers=True
    )
    st.plotly_chart(fig2, use_container_width=True)

    st.subheader("Payment Method Distribution")
    fig3 = px.pie(
        filtered_df,
        names="Payment Method"
    )
    st.plotly_chart(fig3, use_container_width=True)

    st.subheader("Top Items")
    top_items = filtered_df.groupby("Item")['Order Total'].sum().nlargest(10).sort_values(ascending=False).reset_index()
    fig4 = px.bar(top_items, x="Order Total", y="Item", orientation="h")
    st.plotly_chart(fig4, use_container_width=True)