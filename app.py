import streamlit as st
from streamlit_option_menu import option_menu
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import pandas as pd
import time
import re

# =============================
# 1. CẤU HÌNH TRANG
# =============================
st.set_page_config(
    page_title="Cửa Hàng Xứ Nẫu - Đặc Sản Bình Định",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# =============================
# ẨN TOOLBAR + FOOTER
# =============================
st.markdown("""
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
[data-testid="stToolbar"] {display: none !important;}
[data-testid="stDecoration"] {display: none !important;}
</style>
""", unsafe_allow_html=True)

# =============================
# SESSION STATE
# =============================
if "da_dang_nhap" not in st.session_state:
    st.session_state.da_dang_nhap = False

if "gio_hang" not in st.session_state:
    st.session_state.gio_hang = {}

if "logo_url" not in st.session_state:
    st.session_state.logo_url = "https://raw.githubusercontent.com/windy0209/dac-san-binh-dinh/main/logo2.png"

# =============================
# GOOGLE SHEETS
# =============================
@st.cache_resource
def ket_noi_sheet(ten_tab):
    try:
        scope = ["https://spreadsheets.google.com/feeds", 
                 "https://www.googleapis.com/auth/drive"]
        if "gcp_service_account" in st.secrets:
            creds = Credentials.from_service_account_info(
                st.secrets["gcp_service_account"], scopes=scope)
        else:
            creds = Credentials.from_service_account_file(
                "credentials.json", scopes=scope)
        client = gspread.authorize(creds)
        return client.open("DonHangDacSanBinhDinh").worksheet(ten_tab)
    except:
        return None

def la_url_hop_le(url):
    return isinstance(url, str) and url.startswith(("http://", "https://"))

# =============================
# CSS GIAO DIỆN PRO
# =============================
st.markdown("""
<style>
.stApp { background-color: #f4f8f4; }

/* NAVBAR */
.navbar {
    background: white;
    padding: 10px 40px;
    border-radius: 20px;
    box-shadow: 0 8px 20px rgba(0,0,0,0.05);
    margin-bottom: 20px;
}

/* CARD */
.product-card {
    background: white;
    border-radius: 20px;
    padding: 15px;
    box-shadow: 0 10px 25px rgba(46,125,50,0.08);
    border: 1px solid #edf2ed;
    text-align: center;
}

/* BUTTON */
.stButton>button {
    background-color: #2e7d32;
    color: white;
    border-radius: 12px;
    font-weight: 600;
    width: 100%;
    border: none;
}
.stButton>button:hover {
    background-color: #f39c12;
    color: white;
}
</style>
""", unsafe_allow_html=True)

# =============================
# MENU NGANG (TOP NAV)
# =============================
st.markdown('<div class="navbar">', unsafe_allow_html=True)

chon_menu = option_menu(
    None,
    ["🏠 Trang Chủ", "🛍️ Cửa Hàng", "🛒 Giỏ Hàng", "📞 Thông Tin", "📊 Quản Trị"],
    icons=["house", "shop", "cart", "geo-alt", "bar-chart"],
    orientation="horizontal",
    styles={
        "container": {"padding": "0!important"},
        "nav-link": {
            "font-size": "16px",
            "font-weight": "600",
            "text-align": "center",
            "margin": "0px",
            "--hover-color": "#eee",
        },
        "nav-link-selected": {
            "background-color": "#2e7d32",
            "color": "white",
        },
    },
)

st.markdown('</div>', unsafe_allow_html=True)

# =============================
# TRANG CHỦ
# =============================
if chon_menu == "🏠 Trang Chủ":
    st.markdown("<h1 style='text-align:center;color:#2e7d32;'>🏯 Tinh Hoa Ẩm Thực Bình Định</h1>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    c1.success("🌿 100% Tự nhiên")
    c2.warning("🚚 Giao hàng toàn quốc")
    c3.info("💝 Quà tặng sang trọng")

# =============================
# CỬA HÀNG
# =============================
elif chon_menu == "🛍️ Cửa Hàng":
    st.markdown("<h2 style='text-align:center; color:#2e7d32;'>🌟 Danh Sách Sản Phẩm</h2>", unsafe_allow_html=True)

    ws = ket_noi_sheet("SanPham")
    if ws:
        data = ws.get_all_records()
        if data:
            df = pd.DataFrame(data)
            cols = st.columns(3)
            for i, row in df.iterrows():
                with cols[i % 3]:
                    st.markdown('<div class="product-card">', unsafe_allow_html=True)
                    img = row["Hình ảnh"] if la_url_hop_le(row["Hình ảnh"]) else "https://via.placeholder.com/200"
                    st.image(img)
                    st.markdown(f"**{row['Sản phẩm']}**")
                    st.markdown(f"### {row['Giá']:,} VNĐ")
                    if st.button("Thêm vào giỏ 🛒", key=row["ID"]):
                        st.session_state.gio_hang[str(row["ID"])] = 1
                        st.toast("Đã thêm vào giỏ!")
                    st.markdown('</div>', unsafe_allow_html=True)

# =============================
# GIỎ HÀNG
# =============================
elif chon_menu == "🛒 Giỏ Hàng":
    st.title("🛒 Giỏ Hàng")
    if not st.session_state.gio_hang:
        st.warning("Giỏ hàng trống.")

# =============================
# THÔNG TIN
# =============================
elif chon_menu == "📞 Thông Tin":
    st.markdown("<h1 style='text-align:center;color:#2e7d32;'>📍 Thông Tin Cửa Hàng</h1>", unsafe_allow_html=True)
    st.write("📍 96 Ngô Đức Đệ, Bình Định")
    st.write("📞 0932.642.376")
    st.write("⏰ 07:30 - 21:00")

# =============================
# QUẢN TRỊ
# =============================
elif chon_menu == "📊 Quản Trị":
    if not st.session_state.da_dang_nhap:
        tk = st.text_input("Tài khoản")
        mk = st.text_input("Mật khẩu", type="password")
        if st.button("Đăng nhập"):
            if tk == "admin" and mk == "binhdinh0209":
                st.session_state.da_dang_nhap = True
                st.rerun()
            else:
                st.error("Sai thông tin!")
    else:
        st.success("Đăng nhập thành công!")
