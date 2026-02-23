import streamlit as st
from streamlit_option_menu import option_menu
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import pandas as pd
import time

# =============================
# 1. CẤU HÌNH TRANG
# =============================
st.set_page_config(
    page_title="Cửa Hàng Xứ Nẫu - Đặc Sản Bình Định",
    layout="wide",
    page_icon="🍱"
)

# =============================
# 2. SESSION STATE
# =============================
if "da_dang_nhap" not in st.session_state:
    st.session_state.da_dang_nhap = False

if "gio_hang" not in st.session_state:
    st.session_state.gio_hang = {}

# =============================
# 3. KẾT NỐI GOOGLE SHEETS
# =============================
@st.cache_resource
def ket_noi_sheet(ten_tab):
    try:
        scope = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/drive"
        ]

        if "gcp_service_account" in st.secrets:
            creds = Credentials.from_service_account_info(
                st.secrets["gcp_service_account"],
                scopes=scope
            )
        else:
            creds = Credentials.from_service_account_file(
                "credentials.json",
                scopes=scope
            )

        client = gspread.authorize(creds)
        return client.open("DonHangDacSanBinhDinh").worksheet(ten_tab)

    except:
        return None


def la_url_hop_le(url):
    return isinstance(url, str) and url.startswith(("http://", "https://"))

# =============================
# 4. CSS
# =============================
st.markdown("""
<style>
.stApp { background-color: #f8fbf8; }

/* Slider */
.slider-container {
    width: 100%;
    overflow: hidden;
    background: white;
    padding: 25px 0;
    border-radius: 25px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.05);
    margin-top: 20px;
}

.slide-track {
    display: flex;
    width: max-content;
    animation: scroll 40s linear infinite;
}

.slide-item {
    width: 230px;
    margin: 0 20px;
    text-align: center;
    flex-shrink: 0;
}

.slide-item img {
    width: 220px;
    height: 170px;
    object-fit: cover;
    border-radius: 18px;
    box-shadow: 0 8px 15px rgba(0,0,0,0.1);
}

@keyframes scroll {
    0% { transform: translateX(0); }
    100% { transform: translateX(-50%); }
}

/* Info box */
.info-box {
    background: white;
    padding: 25px;
    border-radius: 20px;
    box-shadow: 0 8px 20px rgba(0,0,0,0.05);
    border-left: 6px solid #2e7d32;
    margin-bottom: 20px;
}
</style>
""", unsafe_allow_html=True)

# =============================
# 5. SIDEBAR
# =============================
with st.sidebar:
    st.image("https://raw.githubusercontent.com/windy0209/dac-san-binh-dinh/main/logo2.png", width=120)
    st.markdown("<h2 style='text-align:center;color:#2e7d32'>CỬA HÀNG XỨ NẪU</h2>", unsafe_allow_html=True)

    chon_menu = option_menu(
        None,
        ["🏠 Trang Chủ", "🛍️ Cửa Hàng", "🛒 Giỏ Hàng", "📞 Thông Tin", "📊 Quản Trị"],
        icons=["house", "shop", "cart3", "info-circle", "person-lock"],
        default_index=0,
        styles={"nav-link-selected": {"background-color": "#2e7d32"}}
    )

# =============================
# 6. TRANG CHỦ
# =============================
if chon_menu == "🏠 Trang Chủ":

    st.markdown("<h1 style='text-align:center;color:#2e7d32;'>🏯 Tinh Hoa Ẩm Thực Bình Định</h1>", unsafe_allow_html=True)
    st.subheader("🔥 Đặc Sản Đang Bán Chạy")

# =============================
# 7. CỬA HÀNG
# =============================
elif chon_menu == "🛍️ Cửa Hàng":
    st.subheader("🌟 Danh Sách Sản Phẩm")

# =============================
# 8. GIỎ HÀNG
# =============================
elif chon_menu == "🛒 Giỏ Hàng":
    st.title("🛒 Giỏ Hàng")

# =============================
# 9. THÔNG TIN CỬA HÀNG
# =============================
elif chon_menu == "📞 Thông Tin":

    st.markdown("<h1 style='color:#2e7d32;'>📞 Thông Tin Cửa Hàng</h1>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        <div class="info-box">
            <h3>🏪 Địa chỉ</h3>
            <p>123 Đường Võ Nguyên Giáp<br>
            TP. Quy Nhơn, Bình Định</p>

            <h3>☎️ Hotline</h3>
            <p><b>0905.xxx.xxx</b> (Hỗ trợ 24/7)</p>

            <h3>🌐 Fanpage</h3>
            <p>facebook.com/dacsanxunau</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="info-box">
            <h3>🚚 Chính sách giao hàng</h3>
            <ul>
                <li>Nội thành Quy Nhơn: 30 phút.</li>
                <li>Toàn quốc: 2-3 ngày.</li>
                <li>Freeship đơn trên 500.000đ.</li>
            </ul>

            <h3>🛡 Cam kết</h3>
            <p>Sản phẩm chính gốc Bình Định.<br>
            Không chất bảo quản.<br>
            Đổi trả nếu không hài lòng.</p>
        </div>
        """, unsafe_allow_html=True)

# =============================
# 10. QUẢN TRỊ
# =============================
elif chon_menu == "📊 Quản Trị":
    st.title("Trang quản trị")
