import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import random

# ==========================================
# 1. إعدادات الصفحة
# ==========================================
st.set_page_config(page_title="نظام الشاليهات", layout="wide", page_icon="🏡")

# ==========================================
# 🛑 كود CSS المحسن
# ==========================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');

    html, body, [data-testid="stAppViewContainer"], [data-testid="stSidebar"] {
        font-family: 'Cairo', sans-serif !important;
        direction: rtl;
        text-align: right;
    }

    h1, h2, h3, h4, h5, h6 {
        font-family: 'Cairo', sans-serif !important;
        text-align: right;
    }
    
    h1 {
        text-align: center;
        color: #0e76a8;
        margin-bottom: 2rem;
    }

    div.stButton > button {
        background-color: #0e76a8 !important;
        color: white !important;
        border-radius: 10px !important;
        font-weight: bold !important;
        border: none !important;
        width: 100%;
        padding: 0.5rem 1rem;
    }
    div.stButton > button:hover {
        background-color: #0b5e85 !important;
        color: white !important;
    }

    [data-testid="stMetric"] {
        background-color: #f0f2f6;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
        text-align: center;
        border: 1px solid #e0e0e0;
    }

    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        justify-content: flex-end;
    }
    .stTabs [data-baseweb="tab"] {
        font-family: 'Cairo', sans-serif;
    }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
</style>
""", unsafe_allow_html=True)

# العنوان الرئيسي
st.title("🏡 نظام إدارة شاليهات سفاري جروب ")

# ==========================================
# 2. دوال الاتصال والتعامل مع الداتا والإعدادات
# ==========================================
conn = st.connection("gsheets", type=GSheetsConnection)

# --- الثوابت الافتراضية (عشان لو الشيت فاضي) ---
DEFAULT_BROKERS = {
    "نجلاء": "#fff59d", 
    "مي": "#e1bee7",    
    "أحمد": "#c8e6c9",  
    "بسملة": "#ffcdd2"  
}
DEFAULT_CHALETS =  ["3 غرف 1111", "7435عماره3غرف", "3024غرفتين ارضي ", "3317غرفتين علوي ","6313غرفتين علوي","11304اليخت غرفتين","5301السفينه","5201ريفير","5202تيتانك","5201Aاطلنتس","5202Aارابيسك ","3غرف 3401a"]

# دالة لجلب الإعدادات (الشاليهات والسماسرة الجدد)
def get_config_data():
    try:
        # بنقرأ من شيت اسمه Config
        df = conn.read(worksheet="Config", ttl=0)
        df = df.dropna(how='all')
        return df
    except:
        return pd.DataFrame(columns=['Type', 'Name', 'Color'])

# دالة لإضافة إعداد جديد
def add_config_item(item_type, name, color=None):
    df = get_config_data()
    new_row = {"Type": item_type, "Name": name, "Color": color}
    updated_df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    conn.update(worksheet="Config", data=updated_df)
    st.cache_data.clear()

# دالة لتوليد لون عشوائي فاتح (Pastel)
def get_random_pastel_color():
    r = random.randint(200, 255)
    g = random.randint(200, 255)
    b = random.randint(200, 255)
    return '#%02x%02x%02x' % (r, g, b)

# === تجهيز القوائم النهائية (دمج القديم مع الجديد) ===
config_df = get_config_data()

# 1. قائمة الشاليهات
new_chalets = config_df[config_df['Type'] == 'Chalet']['Name'].tolist()
ALL_CHALETS = sorted(list(set(DEFAULT_CHALETS + new_chalets))) # set لمنع التكرار

# 2. قائمة السماسرة والألوان
ALL_BROKERS_COLORS = DEFAULT_BROKERS.copy()
new_brokers_df = config_df[config_df['Type'] == 'Broker']
for _, row in new_brokers_df.iterrows():
    ALL_BROKERS_COLORS[row['Name']] = row['Color']

ALL_BROKERS_NAMES = list(ALL_BROKERS_COLORS.keys())


# --- دوال البيانات الأساسية ---
def get_data():
    try:
        df = conn.read(worksheet="Data", ttl=0)
        df = df.dropna(how='all')
        if 'Status' not in df.columns: df['Status'] = 'مؤكد'
        if 'Deposit' not in df.columns: df['Deposit'] = 0.0
        if 'Remaining' not in df.columns: df['Remaining'] = 0.0
        return df
    except:
        return pd.DataFrame(columns=['Chalet', 'Broker', 'Start_Date', 'End_Date', 
                                   'Days', 'Price_Day', 'Total_Price', 
                                   'Status', 'Deposit', 'Remaining'])

def save_booking(new_row):
    df = get_data()
    updated_df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    conn.update(worksheet="Data", data=updated_df)
    st.cache_data.clear()

def delete_booking(index_to_delete):
    df = get_data()
    updated_df = df.drop(index_to_delete)
    conn.update(worksheet="Data", data=updated_df)
    st.cache_data.clear()

def update_booking_status(index, new_price, new_deposit, new_total):
    df = get_data()
    df.at[index, 'Status'] = 'مؤكد'
    df.at[index, 'Price_Day'] = new_price
    df.at[index, 'Deposit'] = new_deposit
    df.at[index, 'Total_Price'] = new_total
    df.at[index, 'Remaining'] = new_total - new_deposit
    conn.update(worksheet="Data", data=df)
    st.cache_data.clear()

def check_availability(chalet, start, end):
    df = get_data()
    if df.empty: return True, ""
    try:
        df['Start_Date'] = pd.to_datetime(df['Start_Date'])
        df['End_Date'] = pd.to_datetime(df['End_Date'])
        req_start = pd.to_datetime(start)
        req_end = pd.to_datetime(end)
        
        chalet_bookings = df[df['Chalet'] == chalet]
        
        for _, row in chalet_bookings.iterrows():
            if req_start < row['End_Date'] and req_end > row['Start_Date']:
                status_msg = " (غير مؤكد)" if row.get('Status') == 'غير مؤكد' else ""
                return False, f"مشغول{status_msg} من {row['Start_Date'].date()} إلى {row['End_Date'].date()} ({row['Broker']})"
    except:
        pass
    return True, "متاح"

# ==========================================
# 3. واجهة المستخدم (Tabs)
# ==========================================
# إضافة تاب الإعدادات في النهاية
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📅 الحجوزات والجدول", "⏳ الحجوزات غير المؤكدة", "❌ سجل الإلغاء", "📊 التحليل المالي", "⚙️ الإعدادات"])

# === التاب 1: الحجز والجدول ===
with tab1:
    with st.container():
        st.markdown("### ➕ إضافـة حجـز جديـد")
        with st.form("booking_form"):
            c1, c2, c3 = st.columns(3)
            with c1:
                # استخدام القوائم الديناميكية المحدثة
                chalet_name = st.selectbox("الشاليه", ALL_CHALETS)
                broker_name = st.selectbox("السمسار", ALL_BROKERS_NAMES)
            with c2:
                check_in = st.date_input("الوصول", datetime.today())
                check_out = st.date_input("المغادرة", datetime.today() + timedelta(days=1))
            with c3:
                booking_status = st.radio("حالة الحجز", ["مؤكد", "غير مؤكد"], horizontal=True)
                days = (check_out - check_in).days
                st.info(f"المدة: {days} ليالي")

            st.markdown("---")
            m1, m2, m3 = st.columns(3)
            with m1:
                price_val = 1000 if booking_status == "مؤكد" else 0
                day_price = st.number_input("سعر الليلة", value=price_val, disabled=(booking_status == "غير مؤكد"))
            with m2:
                deposit = st.number_input("العربون (Deposit)", value=0)
            with m3:
                total_price = days * day_price
                remaining = total_price - deposit
                if booking_status == "مؤكد":
                    st.success(f"الإجمالي: {total_price} | المتبقي: {remaining}")
                else:
                    st.warning("حجز مبدئي (تحت الانتظار)")

            submit = st.form_submit_button("💾 حفظ الحجز")
            
            if submit:
                if days <= 0:
                    st.error("تاريخ المغادرة خطأ!")
                else:
                    is_free, msg = check_availability(chalet_name, check_in, check_out)
                    if not is_free:
                        st.error(f"⛔ لا يمكن الحجز! الشاليه {msg}")
                    else:
                        new_data = {
                            "Chalet": chalet_name, "Broker": broker_name,
                            "Start_Date": str(check_in), "End_Date": str(check_out),
                            "Days": days, "Price_Day": day_price, "Total_Price": total_price,
                            "Status": booking_status, "Deposit": deposit, "Remaining": remaining
                        }
                        save_booking(new_data)
                        st.success("✅ تم الحفظ بنجاح!")
                        st.rerun()

    st.markdown("---")
    
    st.subheader("📅 الحجوزات")
    df = get_data()
    if not df.empty:
        grid = []
        for _, row in df.iterrows():
            try:
                s = pd.to_datetime(row['Start_Date'])
                e = pd.to_datetime(row['End_Date'])
                curr = s
                is_unconfirmed = (row.get('Status') == 'غير مؤكد')
                if is_unconfirmed:
                    cell_info = f"{row['Broker']}\n(غير مؤكد)"
                    color_key = "unconfirmed"
                else:
                    rem = row.get('Remaining', 0)
                    cell_info = f"{row['Broker']}\n({row['Total_Price']})\nباقي:{rem}"
                    color_key = row['Broker']

                while curr < e:
                    grid.append({'Date': curr, 'Chalet': row['Chalet'], 'Info': cell_info, 'ColorKey': color_key})
                    curr += timedelta(days=1)
            except: continue
            
        if grid:
            grid_df = pd.DataFrame(grid)
            current_year = datetime.now().year
            full_range = pd.date_range(start=f'{current_year}-01-01', end=f'{current_year}-12-31')
            
            matrix = grid_df.pivot_table(index='Date', columns='Chalet', values='Info', aggfunc='last')
            matrix = matrix.reindex(full_range)
            matrix.index = matrix.index.strftime('%a %d-%m')

            def colorize(val):
                if pd.isna(val): return ''
                if "(غير مؤكد)" in str(val):
                    return 'background-color: #eeeeee; color: #555; border: 1px solid white; font-style: italic;'
                
                color = "#e0e0e0"
                # استخدام خريطة الألوان المحدثة
                for name, code in ALL_BROKERS_COLORS.items():
                    if name in str(val): color = code
                return f'background-color: {color}; color: black; border: 1px solid white; font-weight: bold'

            st.dataframe(matrix.style.map(colorize), use_container_width=True, height=600)
    else:
        st.info("لا توجد بيانات.")

# === التاب 2: الحجوزات المعلقة ===
with tab2:
    st.header("⏳ الحجوزات (غير المؤكدة)")
    df_pending = get_data()
    if not df_pending.empty and 'Status' in df_pending.columns:
        df_pending = df_pending[df_pending['Status'] == 'غير مؤكد']
    else:
        df_pending = pd.DataFrame()

    if not df_pending.empty:
        st.dataframe(df_pending[['Chalet', 'Broker', 'Start_Date', 'End_Date', 'Days']], use_container_width=True)
        st.markdown("### ✍️ إجراء على حجز معلق")
        
        df_pending['Label'] = df_pending.apply(lambda x: f"{x['Chalet']} | {x['Broker']} | {x['Start_Date']}", axis=1)
        selected_pending = st.selectbox("اختر الحجز لتأكيده أو إلغاؤه:", df_pending['Label'].unique())
        
        selected_row = df_pending[df_pending['Label'] == selected_pending].iloc[0]
        real_index = df_pending[df_pending['Label'] == selected_pending].index[0]
        
        col_act1, col_act2 = st.columns(2)
        with col_act1:
            st.info(f"عدد الليالي: {selected_row['Days']}")
            confirm_price = st.number_input("سعر الليلة النهائي للتأكيد", value=1000, key="conf_price")
            confirm_deposit = st.number_input("العربون المدفوع", value=0, key="conf_dep")
            
            if st.button("✅ تأكيد الحجز واعتماده"):
                final_total = selected_row['Days'] * confirm_price
                update_booking_status(real_index, confirm_price, confirm_deposit, final_total)
                st.success("تم تأكيد الحجز بنجاح وتحول للون السمسار!")
                st.rerun()

        with col_act2:
            st.write("")
            st.write("")
            st.write("")
            if st.button("🗑️ إلغاء الحجز المبدئي"):
                delete_booking(real_index)
                st.success("تم حذف الحجز المبدئي.")
                st.rerun()
    else:
        st.success("لا توجد حجوزات معلقة حالياً.")

# === التاب 3: الإلغاء ===
with tab3:
    st.header("❌ سجل الحجوزات والإلغاء")
    df_all = get_data()
    if not df_all.empty:
        try:
            df_all['Date_Obj'] = pd.to_datetime(df_all['Start_Date'])
            df_all['Month_Year'] = df_all['Date_Obj'].dt.strftime('%Y-%m (%B)')
        except:
            df_all['Month_Year'] = 'تواريخ غير صالحة'

        all_months = sorted(df_all['Month_Year'].unique(), reverse=True)
        selected_month = st.selectbox("📅 اختر الشهر لعرض حجوزاته:", all_months)
        
        df_month = df_all[df_all['Month_Year'] == selected_month]
        st.dataframe(df_month[['Chalet', 'Broker', 'Start_Date', 'Status', 'Total_Price', 'Deposit', 'Remaining']], use_container_width=True)
        
        st.markdown("---")
        st.subheader("🗑️ حذف حجز من هذا الشهر")
        
        if not df_month.empty:
            df_month['Label'] = df_month.apply(lambda x: f"{x['Chalet']} | {x['Broker']} | {x['Start_Date']} | ({x['Status']})", axis=1)
            booking_to_cancel = st.selectbox("اختر الحجز لحذفه:", df_month['Label'].unique())
            
            if st.button("تأكيد الحذف النهائي"):
                index_to_drop = df_month[df_month['Label'] == booking_to_cancel].index
                delete_booking(index_to_drop)
                st.success("تم الحذف.")
                st.rerun()
        else:
            st.info("لا توجد حجوزات في هذا الشهر.")
    else:
        st.info("الجدول فارغ تماماً.")

# === التاب 4: التحليل المالي ===
with tab4:
    st.header("📊 لوحة المعلومات المالية (للمؤكد فقط)")
    df_an = get_data()
    
    if not df_an.empty:
        df_an['Total_Price'] = pd.to_numeric(df_an['Total_Price'], errors='coerce').fillna(0)
        df_an['Deposit'] = pd.to_numeric(df_an['Deposit'], errors='coerce').fillna(0)
        df_an['Remaining'] = pd.to_numeric(df_an['Remaining'], errors='coerce').fillna(0)
        
        df_confirmed = df_an[df_an['Status'] == 'مؤكد']
        
        if not df_confirmed.empty:
            total_rev = df_confirmed['Total_Price'].sum()
            total_deposit = df_confirmed['Deposit'].sum()
            total_remaining = df_confirmed['Remaining'].sum()
            
            c1, c2, c3 = st.columns(3)
            c1.metric("💰 إجمالي التعاقدات (مؤكد)", f"{total_rev:,.0f} ج.م")
            c2.metric("💵 العربون المحصل", f"{total_deposit:,.0f} ج.م")
            c3.metric("مديونيات (متبقي)", f"{total_remaining:,.0f} ج.م")
            
            st.divider()
            col_charts1, col_charts2 = st.columns(2)
            with col_charts1:
                st.subheader("🥧 حصة المؤجرين (السماسرة)")
                fig_pie = px.pie(df_confirmed, names='Broker', values='Total_Price', hole=0.4, color_discrete_sequence=px.colors.qualitative.Pastel)
                st.plotly_chart(fig_pie, use_container_width=True)
                
            with col_charts2:
                st.subheader("📊 إيرادات الشاليهات")
                chalet_revenue = df_confirmed.groupby('Chalet')['Total_Price'].sum().reset_index()
                fig_bar = px.bar(chalet_revenue, x='Chalet', y='Total_Price', text_auto=True, color='Chalet', color_discrete_sequence=px.colors.qualitative.Pastel)
                st.plotly_chart(fig_bar, use_container_width=True)
        else:
            st.warning("لا توجد حجوزات مؤكدة حتى الآن.")
    else:
        st.info("لا توجد بيانات.")

# === التاب 5: الإعدادات (جديد) ===
with tab5:
    st.header("⚙️ إعدادات النظام")
    st.info("يمكنك هنا إضافة شاليهات جديدة أو سماسرة جدد للنظام بشكل دائم.")
    
    col_set1, col_set2 = st.columns(2)
    
    # 1. إضافة شاليه
    with col_set1:
        with st.form("add_chalet_form"):
            st.subheader("🏠 إضافة شاليه جديد")
            new_chalet_name = st.text_input("اسم الشاليه الجديد")
            if st.form_submit_button("إضافة الشاليه"):
                if new_chalet_name and new_chalet_name not in ALL_CHALETS:
                    add_config_item("Chalet", new_chalet_name)
                    st.success(f"تم إضافة {new_chalet_name} بنجاح!")
                    st.rerun()
                elif new_chalet_name in ALL_CHALETS:
                    st.warning("هذا الشاليه موجود بالفعل.")
                else:
                    st.error("يرجى كتابة الاسم.")
    
    # 2. إضافة سمسار
    with col_set2:
        with st.form("add_broker_form"):
            st.subheader("👤 إضافة بروكر جديد")
            new_broker_name = st.text_input("اسم السمسار الجديد")
            if st.form_submit_button("إضافة بروكر"):
                if new_broker_name and new_broker_name not in ALL_BROKERS_NAMES:
                    # توليد لون عشوائي
                    rand_color = get_random_pastel_color()
                    add_config_item("Broker", new_broker_name, rand_color)
                    st.success(f"تم إضافة {new_broker_name} وتم تعيين لون له ({rand_color}) 🎨")
                    st.rerun()
                elif new_broker_name in ALL_BROKERS_NAMES:
                    st.warning("هذا السمسار موجود بالفعل.")
                else:
                    st.error("يرجى كتابة الاسم.")

    st.divider()
    st.subheader("📋 القوائم الحالية")
    
    ls1, ls2 = st.columns(2)
    with ls1:
        st.write("**الشاليهات المسجلة:**")
        st.table(pd.DataFrame(ALL_CHALETS, columns=["اسم الشاليه"]))
    
    with ls2:
        st.write("**السماسرة المسجلين وألوانهم:**")
        # عرض الألوان كخلفية
        brokers_display = []
        for name, color in ALL_BROKERS_COLORS.items():
            brokers_display.append({"السمسار": name, "كود اللون": color})
        
        st.dataframe(pd.DataFrame(brokers_display).style.applymap(lambda x: f'background-color: {x}' if x.startswith('#') else '', subset=['كود اللون']), use_container_width=True)