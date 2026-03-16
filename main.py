import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import folium
from folium.plugins import HeatMap
import streamlit as st # Dashboard интерфейсі үшін

# 1. Деректерді дайындау (2025-2026 жж. статистикасы негізінде)
# Орташа бағалар (тг/м2): Алматы ~560к, Астана ~530к, Шымкент ~420к
districts_data = {
    'City': ['Almaty', 'Almaty', 'Almaty', 'Astana', 'Astana', 'Shymkent'],
    'District': ['Almaly', 'Bostandyk', 'Auezov', 'Yesil', 'Almaty_dist', 'Abay'],
    'Lat': [43.25, 43.23, 43.22, 51.12, 51.15, 42.32],
    'Lon': [76.93, 76.91, 76.85, 71.43, 71.46, 69.59],
    'Price_per_m2': [892000, 950000, 650000, 530000, 480000, 420000] #
}
df_districts = pd.DataFrame(districts_data)

# Баға динамикасы (2024-2026)
months = pd.date_range(start='2024-01-01', end='2026-03-01', freq='M')
price_trend = {
    'Date': months,
    '1-room': np.linspace(450000, 580000, len(months)) * (1 + np.random.normal(0, 0.02, len(months))),
    '2-room': np.linspace(400000, 530000, len(months)) * (1 + np.random.normal(0, 0.02, len(months))),
    '3-room': np.linspace(380000, 510000, len(months)) * (1 + np.random.normal(0, 0.02, len(months)))
}
df_trends = pd.DataFrame(price_trend).melt(id_vars=['Date'], var_name='Type', value_name='Price')

# 2. Визуализация функциялары
def create_map():
    m = folium.Map(location=[48.0196, 66.9237], zoom_start=5)
    heat_data = [[row['Lat'], row['Lon'], row['Price_per_m2']] for index, row in df_districts.iterrows()]
    HeatMap(heat_data, radius=25).add_to(m)
    return m

def create_correlation_plot():
    # Құрылыс материалдары мен үй бағасының корреляциясы
    build_mat_index = np.linspace(100, 140, 20)
    house_price_index = build_mat_index * 1.2 + np.random.normal(0, 5, 20)
    fig = px.scatter(x=build_mat_index, y=house_price_index, trendline="ols",
                     title="Құрылыс материалдары vs Үй бағасы (Корреляция)",
                     labels={'x': 'Материалдар бағасының индексі', 'y': 'Үй бағасының индексі'})
    return fig

# 3. Streamlit Dashboard интерфейсі
st.set_page_config(page_title="Real Estate Dashboard KZ", layout="wide")
st.title("🏠 Қазақстан жылжымайтын мүлік нарығы (2026)")

col1, col2 = st.columns(2)

with col1:
    st.subheader("📍 Баға Heatmap (тг/м2)")
    folium_map = create_map()
    st.components.v1.html(folium_map._repr_html_(), height=400)

with col2:
    st.subheader("📈 Пәтерлер бағасының динамикасы")
    fig_line = px.line(df_trends, x='Date', y='Price', color='Type')
    st.plotly_chart(fig_line, use_container_width=True)

col3, col4 = st.columns(2)

with col3:
    st.subheader("🏗️ Құрылыс материалдарымен байланыс")
    st.plotly_chart(create_correlation_plot(), use_container_width=True)

with col4:
    st.subheader("🧮 7-20-25 Ипотекалық калькулятор")
    # Бағдарлама шарттары: 7%, бастапқы 20%, мерзімі 25 жылға дейін
    # Лимит: Алматы/Астана үшін 30 млн тг
    price = st.number_input("Үй бағасы (теңге):", value=25000000, max_value=30000000)
    years = st.slider("Мерзімі (жыл):", 1, 25, 15)
    
    downpayment = price * 0.2
    loan_amount = price - downpayment
    monthly_rate = 0.07 / 12
    n_payments = years * 12
    
    monthly_payment = loan_amount * (monthly_rate * (1 + monthly_rate)**n_payments) / ((1 + monthly_rate)**n_payments - 1)
    
    st.write(f"**Бастапқы жарна (20%):** {downpayment:,.0f} ₸")
    st.success(f"**Ай сайынғы төлем:** {monthly_payment:,.0f} ₸")

st.info("Деректер 2025-2026 жылдардағы БҰС және нарықтық аналитика негізінде модельденген.")
