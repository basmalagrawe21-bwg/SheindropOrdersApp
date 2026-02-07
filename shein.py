import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import pandas as pd
import urllib.parse

# --- إعداد Google Sheets ---
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

creds = Credentials.from_service_account_info(
    st.secrets["gcp_service_account"],
    scopes=scope
)

client = gspread.authorize(creds)
sheet = client.open("Sheindrop Orders").sheet1

# --- إعداد الصفحة ---
st.set_page_config(page_title="Sheindrop Orders App", layout="centered")

# --- Sidebar: لغة و Admin Login ---
lang = st.sidebar.selectbox("Language / اللغة", ["Arabic", "English"], key="language_selector")

texts = {
    "Arabic": {
        "title": "نظام طلبات Sheindrop - الكويت",
        "header": "سجّل بياناتك لإتمام الطلب",
        "name": "الاسم الكامل",
        "phone": "رقم الهاتف",
        "address": "عنوان التوصيل",
        "cart_link": "رابط حقيبة Shein",
        "price": "المبلغ الكلي (دينار كويتي)",
        "payment": "طريقة الدفع",
        "submit": "إرسال الطلب الآن",
        "admin_btn": "دخول الإدارة",
        "success": "تم حفظ طلبك بنجاح!",
        "whatsapp_btn": "أرسل الطلب عبر WhatsApp"
    },
    "English": {
        "title": "Sheindrop Orders - Kuwait",
        "header": "Register your details to place order",
        "name": "Full Name",
        "phone": "Phone Number",
        "address": "Delivery Address",
        "cart_link": "Shein Cart Link",
        "price": "Total Amount (KWD)",
        "payment": "Payment Method",
        "submit": "Submit Order",
        "admin_btn": "Admin Login",
        "success": "Your order has been saved successfully!",
        "whatsapp_btn": "Send Order via WhatsApp"
    }
}

T = texts[lang]
st.title(T["title"])

# --- نموذج الطلب ---
with st.form("order_form"):
    st.subheader(T["header"])
    name = st.text_input(T["name"])
    phone = st.text_input(T["phone"])
    address = st.text_area(T["address"])
    cart_link = st.text_input(T["cart_link"])
    total_price = st.number_input(T["price"], min_value=0.0, step=0.1)
    payment = st.selectbox(T["payment"], ["PayPal", "Wompi / ومض 98923220"])
    
    submitted = st.form_submit_button(T["submit"])
    
    if submitted:
        if name and phone and cart_link:
            sheet.append_row([
                datetime.now().strftime("%Y-%m-%d %H:%M"),
                name,
                phone,
                address,
                cart_link,
                total_price,
                payment
            ])
            st.success(T["success"])

            whatsapp_number = "96598923220"
            if lang == "Arabic":
                message = f"طلب جديد:\nالاسم: {name}\nرقم الهاتف: {phone}\nالعنوان: {address}\nالمبلغ: {total_price} KWD\nطريقة الدفع: {payment}"
            else:
                message = f"New Order:\nName: {name}\nPhone: {phone}\nAddress: {address}\nAmount: {total_price} KWD\nPayment Method: {payment}"

            encoded_message = urllib.parse.quote(message)
            whatsapp_url = f"https://wa.me/{whatsapp_number}?text={encoded_message}"
            
            st.markdown(
                f"<a href='{whatsapp_url}' target='_blank' "
                f"style='display:block;text-align:center;"
                f"background-color:#25D366;color:white;"
                f"font-size:22px;padding:15px;border-radius:10px;"
                f"text-decoration:none'>{T['whatsapp_btn']}</a>",
                unsafe_allow_html=True
            )
        else:
            st.warning("يرجى ملء جميع البيانات المطلوبة.")

# --- Admin Dashboard ---
st.sidebar.markdown("---")
if st.sidebar.button(T["admin_btn"]):
    pw = st.sidebar.text_input("Password", type="password")
    if pw == st.secrets["ADMIN_PASSWORD"]:
        data = sheet.get_all_records()
        df = pd.DataFrame(data)
        st.subheader("لوحة تحكم المدير - الطلبات المستلمة")
        st.write(df)
