import streamlit as st
import pandas as pd
import os
import urllib.parse
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm

# --- إعدادات الصفحة ---
st.set_page_config(page_title="Sheindrop Orders Kuwait", layout="centered", page_icon="🛍️")

# --- اختيار اللغة ---
lang = st.sidebar.selectbox(
    "Language / اللغة",
    ["Arabic", "English"],
    key="language_selector"
)

texts = {
    "Arabic": {
        "title": "نظام طلبات Sheindrop - الكويت",
        "header": "سجّل بياناتك لإتمام الطلب",
        "name": "الاسم الكامل",
        "phone": "رقم الهاتف",
        "address": "عنوان التوصيل (المنطقة، القطعة، الشارع)",
        "cart_link": "رابط حقيبة شي إن",
        "price": "المبلغ الكلي (دينار كويتي)",
        "pay_method": "طريقة الدفع",
        "submit": "إرسال الطلب الآن",
        "success": "تم حفظ طلبك بنجاح! سنتواصل معك قريباً.",
        "admin_btn": "دخول الإدارة",
        "password": "كلمة المرور",
        "filter": "فلترة حسب طريقة الدفع",
        "no_orders": "لا توجد طلبات حالياً.",
        "whatsapp_btn": "📲 إرسال إشعار واتساب",
        "new_order_alert": "🔔 طلب جديد!",
        "total_sales": "إجمالي المبيعات",
        "today": "اليوم",
        "this_week": "هذا الأسبوع",
        "generate_pdf": "📄 تحميل تقرير اليوم PDF"
    },
    "English": {
        "title": "Sheindrop Orders - Kuwait",
        "header": "Register your details to order",
        "name": "Full Name",
        "phone": "Phone Number",
        "address": "Delivery Address (Area, Block, Street)",
        "cart_link": "Shein Cart Link",
        "price": "Total Amount (KWD)",
        "pay_method": "Payment Method",
        "submit": "Submit Order Now",
        "success": "Order saved successfully! We will contact you soon.",
        "admin_btn": "Admin Login",
        "password": "Password",
        "filter": "Filter by Payment Method",
        "no_orders": "No orders yet.",
        "whatsapp_btn": "📲 Send WhatsApp Notification",
        "new_order_alert": "🔔 New Order!",
        "total_sales": "Total Sales",
        "today": "Today",
        "this_week": "This Week",
        "generate_pdf": "📄 Download Today's PDF Report"
    }
}

T = texts[lang]

st.markdown(f"<h1 style='text-align:center;color:#4B0082;'>{T['title']}</h1>", unsafe_allow_html=True)

# --- ملف Excel لحفظ الطلبات ---
excel_file = "orders.xlsx"
if not os.path.exists(excel_file):
    df = pd.DataFrame(columns=["Date", "Name", "Phone", "Address", "Cart Link", "Price (KWD)", "Payment"])
    df.to_excel(excel_file, index=False)

# --- وظيفة إنشاء تقرير PDF ---
def generate_pdf(df_today, filename="today_report.pdf"):
    c = canvas.Canvas(filename, pagesize=A4)
    width, height = A4
    c.setFont("Helvetica-Bold", 16)
    c.drawString(2*cm, height-2*cm, "Sheindrop Orders - Daily Report")
    
    c.setFont("Helvetica", 12)
    c.drawString(2*cm, height-3*cm, f"Date: {datetime.now().strftime('%Y-%m-%d')}")
    c.drawString(2*cm, height-3.7*cm, f"Total Orders: {len(df_today)}")
    c.drawString(2*cm, height-4.4*cm, f"Total Sales: {df_today['Price (KWD)'].sum():.2f} KWD")
    
    # جدول الطلبات
    y = height - 6*cm
    for idx, row in df_today.iterrows():
        line = f"{idx+1}. {row['Name']} | {row['Phone']} | {row['Price (KWD)']:.2f} KWD | {row['Payment']}"
        c.drawString(2*cm, y, line)
        y -= 1*cm
        if y < 2*cm:
            c.showPage()
            y = height - 2*cm
            c.setFont("Helvetica", 12)
    
    c.save()

# --- نظام المدير ---
st.sidebar.markdown("---")
st.sidebar.subheader(T["admin_btn"])
admin_pw = st.sidebar.text_input(T["password"], type="password")

if "is_admin" not in st.session_state:
    st.session_state.is_admin = False

if admin_pw:
    try:
        if admin_pw == st.secrets["ADMIN_PASSWORD"]:
            st.session_state.is_admin = True
    except:
        st.warning("Secrets not found! Please create .streamlit/secrets.toml with ADMIN_PASSWORD.")

if st.session_state.is_admin:
    st.subheader("💼 لوحة تحكم المدير - الطلبات المستلمة")
    df = pd.read_excel(excel_file)
    
    # فلترة حسب طريقة الدفع
    payment_options = ["All"] + df["Payment"].unique().tolist()
    selected_payment = st.selectbox(T["filter"], payment_options)
    if selected_payment != "All":
        df = df[df["Payment"] == selected_payment]
    
    if not df.empty:
        df['Date'] = pd.to_datetime(df['Date'])
        today = datetime.now().date()
        df_today = df[df['Date'].dt.date == today]
        
        total_today = df_today['Price (KWD)'].sum()
        st.info(f"{T['total_sales']} - {T['today']}: {total_today} KWD")
        st.dataframe(df.style.highlight_max(subset=["Price (KWD)"], color="lightgreen"))
        
        # --- زر تحميل تقرير PDF ---
        if st.button(T["generate_pdf"]):
            generate_pdf(df_today)
            with open("today_report.pdf", "rb") as f:
                st.download_button("Download PDF", f, file_name="today_report.pdf")
    else:
        st.info(T["no_orders"])

# --- نموذج الطلب ---
with st.form("order_form"):
    st.subheader(T["header"])
    name = st.text_input(T["name"])
    phone = st.text_input(T["phone"])
    address = st.text_area(T["address"])
    cart = st.text_input(T["cart_link"])
    price = st.number_input(T["price"], min_value=0.0, step=0.1)
    payment = st.selectbox(
        T["pay_method"], 
        ["PayPal", "Wompi / ومض", "رقم تحويل ومض: 98923220"]
    )
    
    submitted = st.form_submit_button(T["submit"])
    
    if submitted:
        if name and phone and cart:
            new_row = {
                "Date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "Name": name,
                "Phone": phone,
                "Address": address,
                "Cart Link": cart,
                "Price (KWD)": price,
                "Payment": payment
            }
            df = pd.read_excel(excel_file)
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            df.to_excel(excel_file, index=False)
            st.success(f"✅ {T['success']}")

            # --- زر WhatsApp ---
            whatsapp_number = "96598923220"
            if lang == "Arabic":
                message = f"طلب جديد:\nالاسم: {name}\nرقم الهاتف: {phone}\nالمبلغ: {price} KWD\nطريقة الدفع: {payment}"
            else:
                message = f"New Order:\nName: {name}\nPhone: {phone}\nAmount: {price} KWD\nPayment Method: {payment}"

            encoded_message = urllib.parse.quote(message)
            whatsapp_url = f"https://wa.me/{whatsapp_number}?text={encoded_message}"
            
            st.markdown(
                f"<a href='{whatsapp_url}' target='_blank' style='display:block;text-align:center;background-color:#25D366;color:white;font-size:22px;padding:15px;border-radius:10px;text-decoration:none'>{T['whatsapp_btn']}</a>",
                unsafe_allow_html=True
            )

            # --- تنبيه ---
            st.balloons()
            st.toast(T["new_order_alert"])
        else:
            st.warning("يرجى ملء البيانات الأساسية." if lang=="Arabic" else "Please fill in all required fields.")
