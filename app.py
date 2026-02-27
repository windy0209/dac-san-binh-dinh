import streamlit as st
from streamlit_option_menu import option_menu
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime, timedelta, timezone
import pandas as pd
import time
import re

# =============================
# 1. CẤU HÌNH TRANG & SESSION STATE
# =============================
st.set_page_config(
    page_title="Xứ Nẫu Store - Tinh Hoa Đất Võ",
    layout="wide",
    page_icon="https://raw.githubusercontent.com/windy0209/dac-san-binh-dinh/main/default_logo.png" 
)

if "da_dang_nhap" not in st.session_state:
    st.session_state.da_dang_nhap = False

if "gio_hang" not in st.session_state:
    st.session_state.gio_hang = {}

if "logo_url" not in st.session_state:
    st.session_state.logo_url = "https://raw.githubusercontent.com/windy0209/dac-san-binh-dinh/main/logo2.png"

# =============================
# 2. KẾT NỐI GOOGLE SHEETS
# =============================
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
    except Exception:
        return None

def la_url_hop_le(url):
    return isinstance(url, str) and url.startswith(("http://", "https://"))

def tai_logo_tu_sheet():
    ws = ket_noi_sheet("CauHinh")
    if ws:
        try:
            data = ws.get_all_records()
            for row in data:
                if row.get('Ten_Cau_Hinh') == 'Logo' and la_url_hop_le(row.get('Gia_Tri')):
                    st.session_state.logo_url = row.get('Gia_Tri')
                    break
        except: pass

tai_logo_tu_sheet()

# =============================
# 3. CSS CAO CẤP (FIX NỀN ĐEN INPUT & SLIDER)
# =============================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');

    /* Ép nền trắng toàn bộ ứng dụng */
    .stApp, .stAppHeader, .stMain, .block-container {
        background-color: #FFFFFF !important;
        color: #1A1A1A !important;
    }

    /* FIX LỖI NỀN ĐEN KHUNG NHẬP CHỮ TRÊN ĐIỆN THOẠI */
    input, textarea, [data-testid="stNumberInput"] input {
        background-color: #FFFFFF !important;
        color: #1A1A1A !important;
        -webkit-text-fill-color: #1A1A1A !important; /* Quan trọng cho iPhone */
        opacity: 1 !important; /* Tránh bị mờ trên Android */
        border: 1px solid #DEDEDE !important;
    }

    /* Ẩn thanh công cụ mặc định */
    header, footer, #MainMenu {visibility: hidden !important;}

    /* Tiêu đề */
    h1, h2, h3, h4, p, span, label {
        color: #1A1A1A !important;
        font-family: 'Inter', sans-serif;
    }
    h1, h2, h3 { font-weight: 800 !important; color: #1D4330 !important; }

    /* SLIDER TRANG CHỦ */
    .slider-box { width: 100%; overflow: hidden; background: #FFFFFF; padding: 20px 0; border-radius: 15px; }
    .slide-track { 
        display: flex; 
        width: calc(250px * 20); 
        animation: scroll 30s linear infinite; 
    }
    .slide-item { width: 230px; margin: 0 15px; text-align: center; flex-shrink: 0; }
    .slide-item img { width: 100%; height: 160px; object-fit: cover; border-radius: 12px; box-shadow: 0 4px 10px rgba(0,0,0,0.1); }

    @keyframes scroll {
        0% { transform: translateX(0); }
        100% { transform: translateX(calc(-250px * 10)); }
    }

    /* CARD CỬA HÀNG */
    .product-card {
        background: #FFFFFF !important;
        border-radius: 15px;
        padding: 12px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        border: 1px solid #EEEEEE;
        margin-bottom: 15px;
        text-align: center;
    }
    .product-card img {
        width: 100% !important;
        height: 180px !important;
        object-fit: cover !important;
        border-radius: 10px !important;
        margin-bottom: 10px !important;
    }
    .product-name {
        font-weight: 700;
        font-size: 1rem;
        min-height: 45px;
        color: #1D4330 !important;
    }
    .gia-ban { color: #D32F2F !important; font-size: 1.2rem; font-weight: 800; }

    /* Nút bấm */
    .stButton>button {
        background-color: #2E7D32 !important;
        color: white !important;
        font-weight: 700 !important;
        border-radius: 8px !important;
    }
</style>
""", unsafe_allow_html=True)

# =============================
# 4. HEADER & MENU
# =============================
col_logo, col_nav = st.columns([1, 4])
with col_logo:
    st.image(st.session_state.logo_url, width=100)

with col_nav:
    chon_menu = option_menu(
        menu_title=None, 
        options=["🏠 Trang Chủ", "🛍️ Cửa Hàng", "🛒 Giỏ Hàng", "📞 Thông Tin", "📊 Quản Trị"],
        icons=['house', 'shop', 'cart3', 'info-circle', 'shield-lock'], 
        default_index=0, 
        orientation="horizontal",
        styles={
            "container": {"background-color": "white", "padding": "0"},
            "nav-link": {"font-size": "13px", "font-weight": "700", "color": "#1A1A1A"},
            "nav-link-selected": {"background-color": "#2E7D32", "color": "white"},
        }
    )

# =============================
# 5. TRANG CHỦ
# =============================
if chon_menu == "🏠 Trang Chủ":
    st.markdown("<div style='text-align:center;'><h1>TINH HOA ẨM THỰC BÌNH ĐỊNH</h1><p>Giao hàng tận nơi - Hương vị nguyên bản vùng đất võ.</p></div>", unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns(3)
    with c1: st.info("🌿 **Nguyên Bản**")
    with c2: st.success("🚚 **Tận Tâm**")
    with c3: st.warning("💝 **Uy Tín**")

    st.markdown("<h3 style='text-align:center;'>✨ SẢN PHẨM NỔI BẬT ✨</h3>", unsafe_allow_html=True)
    ws = ket_noi_sheet("SanPham")
    if ws:
        data = ws.get_all_records()
        if data:
            slider_html = ""
            display_data = data + data 
            for row in display_data:
                img_url = row["Hình ảnh"] if la_url_hop_le(row["Hình ảnh"]) else "https://via.placeholder.com/200"
                slider_html += f'''
                <div class="slide-item">
                    <img src="{img_url}">
                    <p style="margin-top:8px; font-weight:700; color:#1D4330;">{row["Sản phẩm"]}</p>
                    <p style="color:#D32F2F; font-weight:800;">{row["Giá"]:,}đ</p>
                </div>'''
            st.markdown(f'<div class="slider-box"><div class="slide-track">{slider_html}</div></div>', unsafe_allow_html=True)

# =============================
# 6. CỬA HÀNG
# =============================
elif chon_menu == "🛍️ Cửa Hàng":
    st.markdown("<h2 style='text-align:center;'>💎 THỰC ĐƠN XỨ NẪU</h2>", unsafe_allow_html=True)
    ws = ket_noi_sheet("SanPham")
    if ws:
        data = ws.get_all_records()
        if data:
            df = pd.DataFrame(data)
            c_search, c_filter = st.columns(2)
            with c_search: tk = st.text_input("🔍 Tìm đặc sản...", placeholder="Nhập tên...")
            with c_filter:
                g_max = int(df["Giá"].max())
                k_gia = st.slider("💰 Giá (VNĐ)", 0, g_max, (0, g_max))

            df_loc = df[(df["Sản phẩm"].str.contains(tk, case=False, na=False)) & (df["Giá"] >= k_gia[0]) & (df["Giá"] <= k_gia[1])]
            
            st.divider()
            cols = st.columns(2)
            for i, (_, row) in enumerate(df_loc.iterrows()):
                with cols[i % 2]:
                    img_path = row["Hình ảnh"] if la_url_hop_le(row["Hình ảnh"]) else "https://via.placeholder.com/200"
                    st.markdown(f'''
                    <div class="product-card">
                        <img src="{img_path}">
                        <div class="product-name">{row["Sản phẩm"]}</div>
                        <div class="gia-ban">{row["Giá"]:,}đ</div>
                        <p style="font-size:0.8rem;">Sẵn có: {row["Tồn kho"]}</p>
                    </div>''', unsafe_allow_html=True)
                    if int(row["Tồn kho"]) > 0:
                        sl = st.number_input("SL", 1, int(row["Tồn kho"]), key=f"sl_{row['ID']}", label_visibility="collapsed")
                        if st.button("MUA 🛒", key=f"btn_{row['ID']}"):
                            st.session_state.gio_hang[str(row["ID"])] = st.session_state.gio_hang.get(str(row["ID"]), 0) + sl
                            st.toast(f"Đã thêm {row['Sản phẩm']}!")
                    else: st.button("HẾT", disabled=True, key=f"out_{row['ID']}")

# =============================
# 7. GIỎ HÀNG
# =============================
elif chon_menu == "🛒 Giỏ Hàng":
    st.markdown("<h2>🛒 GIỎ HÀNG CỦA BẠN</h2>", unsafe_allow_html=True)
    if not st.session_state.gio_hang:
        st.info("Giỏ hàng đang trống.")
    else:
        ws_sp = ket_noi_sheet("SanPham")
        df_sp = pd.DataFrame(ws_sp.get_all_records())
        tong = 0
        ds_ten = []
        for id_sp, sl in st.session_state.gio_hang.items():
            sp = df_sp[df_sp['ID'].astype(str) == id_sp].iloc[0]
            tt = sp['Giá'] * sl
            tong += tt
            ds_ten.append(f"{sp['Sản phẩm']} (x{sl})")
            st.write(f"✅ {sp['Sản phẩm']} x{sl}: {tt:,}đ")
        
        st.subheader(f"Tổng cộng: {tong:,} VNĐ")
        with st.form("checkout"):
            t = st.text_input("Họ tên *")
            s = st.text_input("Số điện thoại *")
            d = st.text_area("Địa chỉ nhận hàng *")
            if st.form_submit_button("XÁC NHẬN ĐẶT HÀNG"):
                if t and s and d:
                    gio_vn = (datetime.now(timezone.utc) + timedelta(hours=7)).strftime("%d/%m/%Y %H:%M")
                    ws_don = ket_noi_sheet("DonHang")
                    ws_don.append_row([gio_vn, t, s, d, ", ".join(ds_ten), sum(st.session_state.gio_hang.values()), f"{tong:,}đ", "Mới"])
                    for id_sp, sl in st.session_state.gio_hang.items():
                        cell = ws_sp.find(id_sp)
                        ws_sp.update_cell(cell.row, 6, int(ws_sp.cell(cell.row, 6).value) - sl)
                    st.session_state.gio_hang = {}
                    st.success("Đặt hàng thành công!"); st.balloons(); time.sleep(2); st.rerun()

# =============================
# 8. QUẢN TRỊ & THÔNG TIN
# =============================
elif chon_menu == "📊 Quản Trị":
    if not st.session_state.da_dang_nhap:
        st.subheader("🔐 Quản trị hệ thống")
        tk, mk = st.text_input("Admin"), st.text_input("Password", type="password")
        if st.button("Đăng nhập"):
            if tk == "admin" and mk == "binhdinh0209": st.session_state.da_dang_nhap = True; st.rerun()
    else:
        st.button("Thoát", on_click=lambda: st.session_state.update({"da_dang_nhap": False}))
        t1, t2 = st.tabs(["📦 KHO", "📝 ĐƠN"])
        ws_sp, ws_don = ket_noi_sheet("SanPham"), ket_noi_sheet("DonHang")
        with t1:
            df_sp = pd.DataFrame(ws_sp.get_all_records())
            df_edit = st.data_editor(df_sp, num_rows="dynamic", use_container_width=True)
            if st.button("LƯU KHO"):
                ws_sp.clear(); ws_sp.update([df_edit.columns.values.tolist()] + df_edit.values.tolist()); st.success("Đã cập nhật!")
        with t2:
            df_don = pd.DataFrame(ws_don.get_all_records())
            st.data_editor(df_don, use_container_width=True)

elif chon_menu == "📞 Thông Tin":
    st.markdown("<h2 style='text-align:center;'>📍 LIÊN HỆ</h2>", unsafe_allow_html=True)
    st.markdown(f'''
    <div style="background:#F9F9F9; padding:20px; border-radius:15px; text-align:center; border:1px solid #DDD;">
        <p><b>🏡 Địa chỉ:</b> 96 Ngô Đức Đệ, Bình Định</p>
        <p><b>☎️ Hotline:</b> 0932.642.376</p>
        <img src="https://raw.githubusercontent.com/windy0209/dac-san-binh-dinh/main/qrcode.png" width="150">
    </div>
    ''', unsafe_allow_html=True)
    st.map(pd.DataFrame({'lat': [13.8930853], 'lon': [109.1002733]}), zoom=14)
