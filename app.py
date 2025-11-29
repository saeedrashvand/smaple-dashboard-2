import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# --- ۱. تنظیمات صفحه و استایل ---
st.set_page_config(
    page_title="داشبورد مدیریت کارخانه شیشه",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="expanded"
)

# تزریق CSS برای ظاهر حرفه‌ای و راست‌چین
st.markdown("""
<style>
    /* فونت و جهت متن */
    .main {
        direction: rtl;
        font-family: 'Tahoma', sans-serif;
        background-color: #f8f9fa;
    }
    h1, h2, h3, h4 {
        text-align: right;
        font-family: 'Tahoma', sans-serif;
        color: #2c3e50;
    }
    /* کارت‌های متریک */
    div[data-testid="metric-container"] {
        background-color: #ffffff;
        border: 1px solid #e0e0e0;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.05);
        direction: rtl;
        text-align: right;
    }
    /* تنظیمات منو و جداول */
    .stSelectbox, .stDataFrame {
        direction: rtl;
    }
    div[class*="stRadio"] > label > div[data-testid="stMarkdownContainer"] > p {
        font-size: 18px;
    }
</style>
""", unsafe_allow_html=True)

# --- ۲. تولید داده‌های مصنوعی (Mock Data) ---
@st.cache_data
def load_data():
    # داده‌های تولید روزانه (۳۰ روز اخیر)
    dates = pd.date_range(end=datetime.today(), periods=30)
    production_data = pd.DataFrame({
        "تاریخ": dates,
        "تولید (متر مربع)": np.random.randint(500, 1500, size=30),
        "ضایعات (کیلوگرم)": np.random.randint(50, 200, size=30),
        "دمای کوره (C)": np.random.randint(680, 720, size=30),
        "شیفت": np.random.choice(["صبح", "عصر", "شب"], size=30)
    })
    
    # داده‌های محصولات
    products = ["شیشه سکوریت ۱۰ میل", "شیشه دوجداره", "شیشه لمینت", "آینه نقره", "شیشه فلوت ساده"]
    sales_data = pd.DataFrame({
        "محصول": products,
        "فروش (میلیون تومان)": np.random.randint(500, 3000, size=5),
        "موجودی انبار (برگ)": np.random.randint(100, 1000, size=5),
        "رضایت مشتری": [4.5, 4.2, 4.8, 4.0, 3.9]
    })
    
    return production_data, sales_data

df_prod, df_sales = load_data()

# --- ۳. سایدبار (منوی کناری) ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", width=80)
    st.title("پنل مدیریت کارخانه")
    st.markdown("نسخه ۱.۲.۰")
    st.markdown("---")
    
    menu = st.radio(
        "بخش مورد نظر را انتخاب کنید:",
        ["نمای کلی (داشبورد)", "خط تولید و کوره", "انبار و فروش", "کنترل کیفیت"],
        index=0
    )
    
    st.markdown("---")
    st.info("اتصال به دیتابیس: ✅ برقرار")

# --- ۴. بخش‌های مختلف داشبورد ---

# >>> بخش ۱: نمای کلی <<<
if menu == "نمای کلی (داشبورد)":
    st.title("📊 داشبورد مدیریتی - نمای کلی")
    st.markdown(f"تاریخ گزارش: {datetime.now().strftime('%Y-%m-%d')}")
    
    # KPI Cards (ردیف اول)
    col1, col2, col3, col4 = st.columns(4)
    
    total_prod = df_prod["تولید (متر مربع)"].sum()
    avg_temp = df_prod["دمای کوره (C)"].mean()
    total_revenue = df_sales["فروش (میلیون تومان)"].sum()
    waste_ratio = round((df_prod["ضایعات (کیلوگرم)"].sum() / total_prod) * 10, 2)

    col1.metric("تولید کل ماه", f"{total_prod:,} m²", "+5%")
    col2.metric("مجموع درآمد", f"{total_revenue:,} M", "+12%")
    col3.metric("میانگین دمای کوره", f"{int(avg_temp)} °C", "Normal")
    col4.metric("نرخ ضایعات", f"{waste_ratio}%", "-1.5%", delta_color="inverse")

    # نمودار روند تولید
    st.markdown("### 📈 روند تولید ۳۰ روز گذشته")
    fig_line = px.area(df_prod, x="تاریخ", y="تولید (متر مربع)", 
                       title="حجم تولید روزانه", markers=True)
    fig_line.update_traces(line_color='#3498db', fillcolor='rgba(52, 152, 219, 0.2)')
    st.plotly_chart(fig_line, use_container_width=True)

# >>> بخش ۲: خط تولید و کوره <<<
elif menu == "خط تولید و کوره":
    st.title("🏭 وضعیت خط تولید و کوره‌ها")
    
    col_left, col_right = st.columns(2)
    
    with col_left:
        st.subheader("کنترل دمای کوره سکوریت")
        # نمودار گیج (Gauge) برای دما
        current_temp = df_prod["دمای کوره (C)"].iloc[-1]
        fig_gauge = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = current_temp,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': "دمای لحظه‌ای (°C)"},
            gauge = {
                'axis': {'range': [None, 800], 'tickwidth': 1, 'tickcolor': "darkblue"},
                'bar': {'color': "#e74c3c"},
                'bgcolor': "white",
                'borderwidth': 2,
                'bordercolor': "gray",
                'steps': [
                    {'range': [0, 650], 'color': '#f1c40f'},
                    {'range': [650, 750], 'color': '#2ecc71'},
                    {'range': [750, 800], 'color': '#e74c3c'}],
                }))
        st.plotly_chart(fig_gauge, use_container_width=True)

    with col_right:
        st.subheader("تولید بر اساس شیفت کاری")
        fig_bar = px.bar(df_prod, x="شیفت", y="تولید (متر مربع)", color="شیفت",
                         title="مقایسه عملکرد شیفت‌ها")
        st.plotly_chart(fig_bar, use_container_width=True)

# >>> بخش ۳: انبار و فروش <<<
elif menu == "انبار و فروش":
    st.title("📦 مدیریت موجودی و فروش")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("سهم بازار محصولات")
        fig_pie = px.pie(df_sales, values='فروش (میلیون تومان)', names='محصول', 
                         hole=0.4, title="درآمد به تفکیک محصول")
        fig_pie.update_traces(textinfo='percent+label')
        st.plotly_chart(fig_pie, use_container_width=True)
        
    with col2:
        st.subheader("وضعیت موجودی انبار")
        st.dataframe(df_sales[["محصول", "موجودی انبار (برگ)"]].style.highlight_min(axis=0, color="#ffcdd2"), use_container_width=True)

# >>> بخش ۴: کنترل کیفیت <<<
elif menu == "کنترل کیفیت":
    st.title("✅ کنترل کیفیت و ضایعات")
    
    # داده ساختگی برای دلایل خرابی
    defects = pd.DataFrame({
        "علت خرابی": ["شکستگی حین سکوریت", "حباب هوا", "خش و خط", "لبه‌زنی نامناسب", "ابعاد اشتباه"],
        "تعداد": [45, 30, 80, 25, 10]
    })
    
    st.subheader("تحلیل پارتو (Pareto) ضایعات")
    fig_bar_defect = px.bar(defects, x="علت خرابی", y="تعداد", text="تعداد",
                            color="تعداد", color_continuous_scale="Reds")
    st.plotly_chart(fig_bar_defect, use_container_width=True)
    
    st.info("💡 پیشنهاد هوش مصنوعی: میزان 'خش و خط' در شیفت شب افزایش یافته است. لطفاً تسمه‌های نقاله چک شوند.")

# --- فوتر ---
st.markdown("---")
st.caption("طراحی شده با توسط شرکت Www.nhsk.ir برای ارائه به کارفرما | پلتفرم")
