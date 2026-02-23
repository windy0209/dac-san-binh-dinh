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
# 4. CSS NÂNG CAO
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
    transition: transform 0.3s ease;
}

.slide-item:hover {
    transform: scale(1.05);
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

/* Card sản phẩm */
[data-testid="stVerticalBlockBorderWrapper"] {
    border-radius: 20px !important;
    background: white !important;
    box-shadow: 0 10px 25px rgba(46,125,50,0.08) !important;
    padding: 15px !important;
}

.gia-ban {
    color: #f39c12;
    font-size: 1.3rem;
    font-weight: 800;
    margin: 5px 0;
}

.stButton>button {
    background-color: #2e7d32;
    color: white;
    border-radius: 12px;
    font-weight: 600;
    width: 100%;
    height: 40px;
    border: none;
}

.stButton>button:hover {
    background-color: #f39c12;
}
</style>
""", unsafe_allow_html=True)

# =============================
# 5. SIDEBAR (Căn giữa Logo và Tên)
# =============================
with st.sidebar:
    # Sử dụng HTML/CSS để ép logo và text vào giữa
    st.markdown(
        """
        <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center;">
            <img src="https://raw.githubusercontent.com/windy0209/dac-san-binh-dinh/main/logo2.png" width="120" style="margin-bottom: 10px;">
            <h2 style="color: #2e7d32; margin-top: 0;">CỬA HÀNG XỨ NẪU</h2>
        </div>
        """,
        unsafe_allow_html=True
    )

    chon_menu = option_menu(
        None,
        ["🏠 Trang Chủ", "🛍️ Cửa Hàng", "🛒 Giỏ Hàng", "📞 Thông Tin", "📊 Quản Trị"],
        
        default_index=0,
        styles={"nav-link-selected": {"background-color": "#2e7d32"}}
    )

# =============================
# 6. TRANG CHỦ (SLIDER FIXED)
# =============================
if chon_menu == "🏠 Trang Chủ":

    st.markdown("<h1 style='text-align:center;color:#2e7d32;'>🏯 Tinh Hoa Ẩm Thực Bình Định</h1>", unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    c1.success("🌿 **Sạch & Tươi**\n\nNguyên liệu tự nhiên 100%.")
    c2.warning("🚚 **Giao Nhanh**\n\nShip toàn quốc.")
    c3.info("💝 **Quà Tặng**\n\nĐóng gói sang trọng.")

    st.markdown("---")
    st.subheader("🔥 Đặc Sản Đang Bán Chạy")

    ws = ket_noi_sheet("SanPham")
    if ws:
        data = ws.get_all_records()

        slider_content = ""

        for _ in range(2):  # nhân đôi để chạy mượt
            for row in data:
                img = row["Hình ảnh"] if la_url_hop_le(row["Hình ảnh"]) else "https://via.placeholder.com/200"
                slider_content += f"""
<div class="slide-item">
<img src="{img}">
<p style="font-weight:600;margin:10px 0 0 0;color:#333;">{row['Sản phẩm']}</p>
<p style="color:#f39c12;font-weight:700;margin:0;">{row['Giá']:,}đ</p>
</div>
"""

        full_html = f"""
<div class="slider-container">
<div class="slide-track">
{slider_content}
</div>
</div>
"""

        st.markdown(full_html.strip(), unsafe_allow_html=True)

# =============================
# 7. CỬA HÀNG
# =============================
elif chon_menu == "🛍️ Cửa Hàng":

    st.subheader("🌟 Danh Sách Sản Phẩm")
    ws = ket_noi_sheet("SanPham")

    if ws:
        df = pd.DataFrame(ws.get_all_records())
        cols = st.columns(3)

        for i, row in df.iterrows():
            with cols[i % 3]:
                with st.container(border=True):

                    img = row["Hình ảnh"] if la_url_hop_le(row["Hình ảnh"]) else "https://via.placeholder.com/200"

                    st.markdown(f"""
<div style="text-align:center;">
<img src="{img}" style="width:100%;height:180px;object-fit:cover;border-radius:15px;">
<div style="font-weight:700;font-size:1.1rem;margin-top:10px;">{row["Sản phẩm"]}</div>
<div class="gia-ban">{row["Giá"]:,} VNĐ</div>
<div style="color:#2e7d32;font-weight:600;">📦 Còn: {row["Tồn kho"]}</div>
</div>
""", unsafe_allow_html=True)

                    if int(row["Tồn kho"]) > 0:
                        sl = st.number_input("SL", 1, 100, key=f"sl_{i}")
                        if st.button("THÊM 🛒", key=f"btn_{i}"):
                            st.session_state.gio_hang[str(row["ID"])] = \
                                st.session_state.gio_hang.get(str(row["ID"]), 0) + sl
                            st.toast("Đã thêm vào giỏ!", icon="✅")
                    else:
                        st.button("HẾT HÀNG", disabled=True)

# =============================
# 8. GIỎ HÀNG
# =============================
elif chon_menu == "🛒 Giỏ Hàng":

    st.title("🛒 Giỏ Hàng")

    if not st.session_state.gio_hang:
        st.warning("Giỏ hàng trống.")
    else:
        ws = ket_noi_sheet("SanPham")
        df = pd.DataFrame(ws.get_all_records())

        tong = 0
        for id_sp, sl in st.session_state.gio_hang.items():
            sp = df[df["ID"].astype(str) == id_sp].iloc[0]
            tong += sp["Giá"] * sl
            st.write(f"{sp['Sản phẩm']} x{sl} - {sp['Giá']*sl:,} VNĐ")

        st.subheader(f"Tổng tiền: {tong:,} VNĐ")

# =============================
# 9. QUẢN TRỊ
# =============================
elif chon_menu == "📊 Quản Trị":

    if not st.session_state.da_dang_nhap:
        tk = st.text_input("Tên đăng nhập")
        mk = st.text_input("Mật khẩu", type="password")
        if st.button("Đăng nhập"):
            if tk == "admin" and mk == "binhdinh0209":
                st.session_state.da_dang_nhap = True
                st.rerun()
    else:
        ws = ket_noi_sheet("SanPham")
        df = pd.DataFrame(ws.get_all_records())
        st.data_editor(df, use_container_width=True)

        if st.button("Đăng xuất"):
            st.session_state.da_dang_nhap = False
            st.rerun()

# =============================
# 10. THÔNG TIN
# =============================
elif chon_menu == "📞 Thông Tin":
    st.markdown("<h1 style='text-align:center;color:#2e7d32;'>📍 Thông Tin Cửa Hàng</h1>", unsafe_allow_html=True)
    
    col_info, col_map = st.columns([1, 1.2], gap="large")

    with col_info:
        st.markdown(f"""
        <div class="info-card">
            <h3 style="color: #2e7d32; margin-top: 0;">🏡 Cửa Hàng Xứ Nẫu</h3>
            <p><b>📍 Địa chỉ:</b> 123 Đường Xuân Diệu, TP. Quy Nhơn, Bình Định</p>
            <p><b>📞 Hotline:</b> <a href="tel:0901234567" style="color: #f39c12; text-decoration: none; font-weight: bold;">0901.234.567</a></p>
            <p><b>📧 Email:</b> contact@xunau.vn</p>
            <hr>
            <h4 style="color: #2e7d32;">⏰ Giờ Hoạt Động</h4>
            <p>Sáng: 07:30 - 11:30<br>Chiều: 13:30 - 21:00</p>
            <p><i>(Mở cửa tất cả các ngày trong tuần)</i></p>
            <div style="margin-top: 20px;">
                <img src="https://img.icons8.com/color/48/000000/facebook-new.png"/>
                <img src="https://img.icons8.com/color/48/000000/zalo.png"/>
                <img src="https://img.icons8.com/color/48/000000/tiktok.png"/>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col_map:
        # Bạn có thể thay src bằng link Google Maps thật của bạn
        st.markdown("""
        <iframe src="https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d3875.313460673322!2d109.2215802758832!3d13.7595304971253!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x316f6b033604f847%3A0x696805f15949a707!2zVFAuIFF1eSBOaMahbiwgQsOsbmggxJDhu4tuaCwgVmnhu4d0IE5hbQ!5e0!3m2!1svi!2s!4v1700000000000!5m2!1svi!2s" 
        width="100%" height="400" style="border:0; border-radius:20px; box-shadow: 0 10px 25px rgba(0,0,0,0.1);" 
        allowfullscreen="" loading="lazy"></iframe>
        """, unsafe_allow_html=True)



