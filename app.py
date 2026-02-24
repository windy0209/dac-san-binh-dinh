import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import qrcode
from io import BytesIO
import base64
import time

# ==============================
# CONFIG
# ==============================
st.set_page_config(
    page_title="XỨ NẪU STORE - PRO MAX",
    layout="wide",
    page_icon="🍱"
)

if "gio_hang" not in st.session_state:
    st.session_state.gio_hang = {}

if "da_dang_nhap" not in st.session_state:
    st.session_state.da_dang_nhap = False

if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = False

# ==============================
# GOOGLE SHEET
# ==============================
@st.cache_resource
def ket_noi_sheet(tab):
    scope = ["https://spreadsheets.google.com/feeds",
             "https://www.googleapis.com/auth/drive"]

    if "gcp_service_account" in st.secrets:
        creds = Credentials.from_service_account_info(
            st.secrets["gcp_service_account"], scopes=scope)
    else:
        creds = Credentials.from_service_account_file(
            "credentials.json", scopes=scope)

    client = gspread.authorize(creds)
    return client.open("DonHangDacSanBinhDinh").worksheet(tab)

# ==============================
# DARK MODE TOGGLE
# ==============================
with st.sidebar:
    st.title("🍱 XỨ NẪU STORE")
    if st.toggle("🌙 Dark Mode"):
        st.session_state.dark_mode = True
    else:
        st.session_state.dark_mode = False

bg = "#111" if st.session_state.dark_mode else "#f5f7f5"
text = "white" if st.session_state.dark_mode else "black"

st.markdown(f"""
<style>
.stApp {{
background:{bg};
color:{text};
}}

.product-card {{
background:white;
padding:20px;
border-radius:20px;
box-shadow:0 10px 30px rgba(0,0,0,0.08);
margin-bottom:25px;
}}

.stButton>button {{
width:100%;
border-radius:12px;
background:#2e7d32;
color:white;
font-weight:600;
}}

</style>
""", unsafe_allow_html=True)

# ==============================
# MENU
# ==============================
menu = option_menu(
    None,
    ["🏠 Trang Chủ", "🛍️ Cửa Hàng", "🛒 Giỏ Hàng", "📊 Admin"],
    icons=["house", "shop", "cart", "bar-chart"],
    orientation="horizontal"
)

# ==============================
# TRANG CHỦ
# ==============================
if menu == "🏠 Trang Chủ":
    st.title("🏯 Đặc Sản Bình Định")
    st.success("Tinh hoa ẩm thực miền Trung")

# ==============================
# CỬA HÀNG
# ==============================
elif menu == "🛍️ Cửa Hàng":

    ws = ket_noi_sheet("SanPham")
    df = pd.DataFrame(ws.get_all_records())

    search = st.text_input("🔍 Tìm sản phẩm")
    if search:
        df = df[df["Sản phẩm"].str.contains(search, case=False)]

    cols = st.columns(3)

    for i, row in df.iterrows():
        with cols[i % 3]:
            st.markdown('<div class="product-card">', unsafe_allow_html=True)
            st.image(row["Hình ảnh"], use_container_width=True)
            st.subheader(row["Sản phẩm"])
            st.write(f"💰 {row['Giá']:,} VNĐ")
            st.write(f"📦 Tồn: {row['Tồn kho']}")

            if st.button("Thêm vào giỏ", key=i):
                st.session_state.gio_hang[str(row["ID"])] = \
                    st.session_state.gio_hang.get(str(row["ID"]), 0) + 1
                st.toast("Đã thêm!", icon="✅")
            st.markdown('</div>', unsafe_allow_html=True)

# ==============================
# GIỎ HÀNG + QR THANH TOÁN
# ==============================
elif menu == "🛒 Giỏ Hàng":

    st.title("🛒 Giỏ Hàng")

    if not st.session_state.gio_hang:
        st.warning("Chưa có sản phẩm.")
    else:
        ws = ket_noi_sheet("SanPham")
        df = pd.DataFrame(ws.get_all_records())

        tong = 0
        for id_sp, sl in st.session_state.gio_hang.items():
            sp = df[df["ID"].astype(str) == id_sp].iloc[0]
            thanh_tien = sp["Giá"] * sl
            tong += thanh_tien
            st.write(f"{sp['Sản phẩm']} x{sl} = {thanh_tien:,} VNĐ")

        st.subheader(f"💵 Tổng: {tong:,} VNĐ")

        # QR Code
        data = f"Thanh toan {tong} VND cho XU NAU STORE"
        qr = qrcode.make(data)
        buf = BytesIO()
        qr.save(buf)
        img_str = base64.b64encode(buf.getvalue()).decode()

        st.markdown(f"""
        <img src="data:image/png;base64,{img_str}" width="250">
        """, unsafe_allow_html=True)

        if st.button("Xác nhận đã thanh toán"):
            ws_don = ket_noi_sheet("DonHang")
            ws_don.append_row([
                datetime.now().strftime("%d/%m/%Y %H:%M"),
                "Online",
                tong
            ])
            st.success("Đơn hàng đã ghi nhận!")
            st.session_state.gio_hang = {}
            time.sleep(2)
            st.rerun()

# ==============================
# ADMIN DASHBOARD
# ==============================
elif menu == "📊 Admin":

    if not st.session_state.da_dang_nhap:
        tk = st.text_input("Tài khoản")
        mk = st.text_input("Mật khẩu", type="password")

        if st.button("Đăng nhập"):
            if tk == "admin" and mk == "binhdinh0209":
                st.session_state.da_dang_nhap = True
                st.rerun()
            else:
                st.error("Sai thông tin")

    else:
        ws_sp = ket_noi_sheet("SanPham")
        ws_don = ket_noi_sheet("DonHang")

        df_sp = pd.DataFrame(ws_sp.get_all_records())
        df_don = pd.DataFrame(ws_don.get_all_records())

        col1, col2, col3 = st.columns(3)

        col1.metric("Tổng sản phẩm", len(df_sp))
        col2.metric("Tổng đơn hàng", len(df_don))
        col3.metric("Tổng tồn kho", df_sp["Tồn kho"].sum())

        st.subheader("Quản lý kho")
        df_edit = st.data_editor(df_sp, use_container_width=True)

        if st.button("Lưu thay đổi"):
            ws_sp.clear()
            ws_sp.update([df_edit.columns.values.tolist()] +
                         df_edit.values.tolist())
            st.success("Đã cập nhật!")
