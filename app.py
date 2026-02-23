import streamlit as st
from streamlit_option_menu import option_menu
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import pandas as pd
import time
import re

# --- 1. CẤU HÌNH TRANG & SEO ---
st.set_page_config(
    page_title="Cửa Hàng Xứ Nẫu - Đặc Sản Bình Định Chính Gốc",
    layout="wide",
    page_icon="🍱"
)

# --- KHỞI TẠO TRẠNG THÁI ---
if 'da_dang_nhap' not in st.session_state:
    st.session_state.da_dang_nhap = False
if 'gio_hang' not in st.session_state:
    st.session_state.gio_hang = {} 

# --- KẾT NỐI GOOGLE SHEETS ---
@st.cache_resource
def ket_noi_sheet(ten_tab):
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        if "gcp_service_account" in st.secrets:
            creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scope)
        else:
            creds = Credentials.from_service_account_file("credentials.json", scopes=scope)
        client = gspread.authorize(creds)
        return client.open("DonHangDacSanBinhDinh").worksheet(ten_tab)
    except: return None

def la_url_hop_le(url):
    return isinstance(url, str) and (url.startswith("http://") or url.startswith("https://"))

def lay_logo():
    ws = ket_noi_sheet("CauHinh")
    if ws:
        try:
            data = ws.get_all_records()
            for row in data:
                if row.get('Ten_Cau_Hinh') == 'Logo' and la_url_hop_le(row.get('Gia_Tri')):
                    return row['Gia_Tri']
        except: pass
    return "https://raw.githubusercontent.com/windy0209/dac-san-binh-dinh/main/logo2.png"

# --- 2. CSS NÂNG CAO (Thêm hiệu ứng Slider động cho Trang Chủ) ---
st.markdown("""
    <style>
    .stApp { background-color: #f8fbf8; }
    
    /* Hiệu ứng trượt sản phẩm liên tục (Infinite Scroll) */
    .slider {
        width: 100%;
        height: auto;
        overflow: hidden;
        background: white;
        padding: 20px 0;
        border-radius: 20px;
        box-shadow: inset 0 0 10px rgba(0,0,0,0.05);
    }
    .slide-track {
        display: flex;
        width: calc(250px * 10); /* Điều chỉnh dựa trên số lượng ảnh */
        animation: scroll 20s linear infinite;
    }
    .slide-item {
        width: 200px;
        margin: 0 25px;
        text-align: center;
    }
    .slide-item img {
        width: 100%;
        height: 150px;
        object-fit: cover;
        border-radius: 15px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    @keyframes scroll {
        0% { transform: translateX(0); }
        100% { transform: translateX(calc(-250px * 5)); } /* Trượt qua phân nửa danh sách */
    }

    /* Container sản phẩm ở trang cửa hàng */
    [data-testid="stVerticalBlockBorderWrapper"] {
        border: 1px solid #edf2ed !important;
        border-radius: 20px !important;
        background-color: white !important;
        box-shadow: 0 10px 25px rgba(46,125, 50, 0.08) !important;
        padding: 15px !important;
    }
    .product-info img { border-radius: 15px; object-fit: cover; height: 180px; width: 100%; }
    .gia-ban { color: #f39c12; font-size: 1.4rem; font-weight: 800; }
    .stButton>button { background-color: #2e7d32; color: white; border-radius: 10px; font-weight: 600; width: 100%; height: 45px; }
    .stButton>button:hover { background-color: #f39c12; }
    
    /* Info Box */
    .info-box { background: white; padding: 25px; border-radius: 20px; border-left: 5px solid #2e7d32; margin-bottom: 20px; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. SIDEBAR MENU ---
logo_url = lay_logo()
with st.sidebar:
    if la_url_hop_le(logo_url): st.image(logo_url, width=120)
    st.markdown("<h2 style='text-align: center; color: #2e7d32; margin-top:-10px;'>CỬA HÀNG XỨ NẪU</h2>", unsafe_allow_html=True)
    chon_menu = option_menu(None, ["🏠 Trang Chủ", "🛍️ Cửa Hàng", "🛒 Giỏ Hàng", "📞 Thông Tin", "📊 Quản Trị"], 
                            icons=["house", "shop", "cart3", "info-circle", "person-lock"], default_index=0,
                            styles={"nav-link-selected": {"background-color": "#2e7d32"}})

# --- 4. LOGIC CÁC TRANG ---

# --- TRANG CHỦ ---
if chon_menu == "🏠 Trang Chủ":
    st.markdown("<h1 style='text-align: center; color: #2e7d32;'>🏯 Tinh Hoa Ẩm Thực Bình Định</h1>", unsafe_allow_html=True)
    
    # Hiển thị 3 cột ưu điểm
    c1, c2, c3 = st.columns(3)
    c1.success("🌿 **Sạch & Tươi**\n\nNguyên liệu tự nhiên 100%.")
    c2.warning("🚚 **Giao Nhanh**\n\nShip toàn quốc, nhận trong ngày.")
    c3.info("💝 **Quà Tặng**\n\nĐóng gói sang trọng, tinh tế.")

    st.markdown("---")
    st.subheader("🔥 Sản Phẩm Bán Chạy")

    # Lấy dữ liệu sản phẩm để làm slider động
    ws_sp = ket_noi_sheet("SanPham")
    if ws_sp:
        df_sp = pd.DataFrame(ws_sp.get_all_records())
        # Tạo danh sách HTML cho slider (Nhân đôi danh sách để tạo hiệu ứng vô tận)
        slider_html = '<div class="slider"><div class="slide-track">'
        # Lặp 2 lần danh sách sản phẩm để trượt không bị ngắt quãng
        for _ in range(2):
            for _, row in df_sp.iterrows():
                img = row['Hình ảnh'] if la_url_hop_le(row['Hình ảnh']) else "https://via.placeholder.com/150"
                slider_html += f"""
                    <div class="slide-item">
                        <img src="{img}">
                        <p style="font-weight:600; margin-top:5px;">{row['Sản phẩm']}</p>
                        <p style="color:#f39c12; font-weight:700;">{row['Giá']:,}đ</p>
                    </div>
                """
        slider_html += '</div></div>'
        st.markdown(slider_html, unsafe_allow_html=True)

    st.markdown("---")
    st.info("💡 **Gợi ý:** Nhấn vào mục **Cửa Hàng** ở menu bên trái để chọn mua những đặc sản tươi ngon nhất!")

# --- CỬA HÀNG ---
elif chon_menu == "🛍️ Cửa Hàng":
    st.subheader("🌟 Danh Sách Sản Phẩm")
    ws_sp = ket_noi_sheet("SanPham")
    if ws_sp:
        df = pd.DataFrame(ws_sp.get_all_records())
        cols = st.columns(3)
        for i, row in df.iterrows():
            with cols[i % 3]:
                with st.container(border=True):
                    img = row['Hình ảnh'] if la_url_hop_le(row['Hình ảnh']) else "https://via.placeholder.com/200"
                    st.markdown(f"""
                        <div class="product-info" style="text-align:center;">
                            <img src="{img}">
                            <div style="font-weight:700; font-size:1.1rem; margin-top:10px;">{row["Sản phẩm"]}</div>
                            <div class="gia-ban">{row["Giá"]:,} VNĐ</div>
                            <div style="color:#2e7d32; font-weight:600; margin-bottom:10px;">📦 Còn: {row["Tồn kho"]}</div>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    if int(row['Tồn kho']) > 0:
                        c_sl, c_btn = st.columns([1, 2])
                        with c_sl: sl = st.number_input("SL", 1, 100, key=f"sl_{i}", label_visibility="collapsed")
                        with c_btn:
                            if st.button(f"THÊM 🛒", key=f"btn_{i}"):
                                st.session_state.gio_hang[str(row['ID'])] = st.session_state.gio_hang.get(str(row['ID']), 0) + sl
                                st.toast(f"Đã thêm {row['Sản phẩm']}!", icon="✅")
                    else: st.button("HẾT HÀNG", disabled=True, key=f"out_{i}")

# --- GIỎ HÀNG ---
elif chon_menu == "🛒 Giỏ Hàng":
    st.title("🛒 Giỏ Hàng Của Bạn")
    if not st.session_state.gio_hang: 
        st.warning("Giỏ hàng trống. Hãy quay lại Cửa hàng để chọn món nhé!")
    else:
        ws_sp = ket_noi_sheet("SanPham")
        df_sp = pd.DataFrame(ws_sp.get_all_records())
        tong, ds_str = 0, []
        for id_sp, sl in st.session_state.gio_hang.items():
            sp = df_sp[df_sp['ID'].astype(str) == id_sp].iloc[0]
            tong += sp['Giá'] * sl
            ds_str.append(f"{sp['Sản phẩm']} x{sl}")
            st.write(f"✅ {sp['Sản phẩm']} x{sl} - {sp['Giá']*sl:,} VNĐ")
        
        st.subheader(f"Tổng tiền: {tong:,} VNĐ")
        with st.form("checkout"):
            t, s, d = st.text_input("Họ tên *"), st.text_input("SĐT *"), st.text_area("Địa chỉ *")
            if st.form_submit_button("XÁC NHẬN ĐẶT HÀNG"):
                if t and s:
                    ws_don = ket_noi_sheet("DonHang")
                    ws_don.append_row([datetime.now().strftime("%d/%m/%Y %H:%M"), t, s, d, ", ".join(ds_str), sum(st.session_state.gio_hang.values()), f"{tong:,} VNĐ", "Mới"])
                    st.session_state.gio_hang = {}
                    st.success("Đã nhận đơn hàng! Chúng tôi sẽ gọi xác nhận ngay.")
                    st.balloons()
                    time.sleep(2); st.rerun()

# --- THÔNG TIN ---
elif chon_menu == "📞 Thông Tin":
    st.markdown("<h1 style='color: #2e7d32;'>📞 Liên Hệ Xứ Nẫu</h1>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("""<div class="info-box"><h3>🏠 Địa chỉ</h3><p>Quy Nhơn, Bình Định</p><h3>☎️ Hotline</h3><p>0905.xxx.xxx</p></div>""", unsafe_allow_html=True)
    with c2:
        st.markdown("""<div class="info-box"><h3>🚚 Giao hàng</h3><p>Ship COD toàn quốc</p><h3>🛡️ Cam kết</h3><p>Chính gốc 100%</p></div>""", unsafe_allow_html=True)

# --- QUẢN TRỊ ---
elif chon_menu == "📊 Quản Trị":
    if not st.session_state.da_dang_nhap:
        tk = st.text_input("Admin")
        mk = st.text_input("Mật khẩu", type="password")
        if st.button("Đăng nhập"):
            if tk == "admin" and mk == "binhdinh0209":
                st.session_state.da_dang_nhap = True; st.rerun()
    else:
        ws_sp = ket_noi_sheet("SanPham")
        df_sp = pd.DataFrame(ws_sp.get_all_records())
        st.data_editor(df_sp, use_container_width=True)
        if st.button("Đăng xuất"):
            st.session_state.da_dang_nhap = False; st.rerun()
