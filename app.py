import streamlit as st
from streamlit_option_menu import option_menu
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
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
# 3. CSS CAO CẤP (SỬA LỖI HIỂN THỊ CHỮ)
# =============================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');

    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display:none;}
    
    html, body, [class*="st-"] {
        font-family: 'Inter', sans-serif;
        color: #1A1A1A;
    }

    .stApp { background-color: #FFFFFF; }
    .block-container { padding-top: 1rem; }

    h1, h2, h3 {
        font-weight: 800 !important;
        color: #1D4330 !important;
        letter-spacing: -0.5px;
    }

    /* Thẻ sản phẩm tối ưu hiển thị chữ */
    .product-card {
        background: #FFFFFF;
        border-radius: 16px;
        padding: 18px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        border: 1px solid #F0F0F0;
        text-align: center;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        height: 100%; /* Giúp các ô cùng hàng cao bằng nhau */
        min-height: 480px; 
        transition: all 0.3s ease;
    }
    
    .product-card:hover {
        transform: translateY(-5px);
        border-color: #2E7D32;
        box-shadow: 0 10px 25px rgba(46,125,50,0.1);
    }

    .product-name {
        font-weight: 700; 
        font-size: 1.15rem;
        color: #1A1A1A;
        margin: 15px 0 10px 0;
        line-height: 1.4;
        min-height: 3.5em; /* Đảm bảo đủ chỗ cho 2-3 dòng chữ */
        display: flex;
        align-items: center;
        justify-content: center;
    }

    .gia-ban {
        color: #D32F2F;
        font-size: 1.4rem;
        font-weight: 800;
        margin-bottom: 5px;
    }

    .stButton>button {
        background-color: #2E7D32 !important;
        color: white !important;
        border-radius: 10px !important;
        font-weight: 700 !important;
        width: 100%;
        border: none !important;
    }
    
    .stButton>button:hover {
        background-color: #F39C12 !important;
    }

    .slider-container { width: 100%; overflow: hidden; background: #F9F9F9; padding: 20px 0; border-radius: 20px; }
    .slide-track { display: flex; width: max-content; animation: scroll 40s linear infinite; }
    .slide-item { width: 250px; margin: 0 15px; text-align: center; }
    .slide-item img { width: 220px; height: 170px; object-fit: cover; border-radius: 12px; }
    @keyframes scroll { 0% { transform: translateX(0); } 100% { transform: translateX(-50%); } }
</style>
""", unsafe_allow_html=True)

# =============================
# 4. HEADER & MENU NGANG
# =============================
col_logo, col_nav = st.columns([1, 4])
with col_logo:
    st.image(st.session_state.logo_url, width=110)

with col_nav:
    chon_menu = option_menu(
        menu_title=None, 
        options=["🏠 Trang Chủ", "🛍️ Cửa Hàng", "🛒 Giỏ Hàng", "📞 Thông Tin", "📊 Quản Trị"],
        icons=['house', 'shop', 'cart3', 'info-circle', 'shield-lock'], 
        default_index=0, 
        orientation="horizontal",
        styles={
            "container": {"padding": "0!important", "background-color": "transparent"},
            "nav-link": {"font-size": "15px", "font-weight": "700", "text-transform": "uppercase"},
            "nav-link-selected": {"background-color": "#2E7D32"},
        }
    )

st.markdown(f"""<div style="text-align: right; padding-right: 20px; margin-top: -15px;"><span style="color: #2E7D32; font-weight: 800;">📞 HOTLINE: 0932.642.376</span></div>""", unsafe_allow_html=True)

# =============================
# 5. TRANG CHỦ
# =============================
if chon_menu == "🏠 Trang Chủ":
    st.markdown("<div style='text-align:center; padding: 30px 0;'><h1 style='font-size: 3rem;'>ĐẬM ĐÀ VỊ QUÊ - TÌNH XỨ NẪU</h1></div>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    c1.info("🌿 **Sạch Từ Tâm**\n\nNguyên liệu 100% bản địa.")
    c2.success("🚚 **Giao Tận Cửa**\n\nĐóng gói chuyên nghiệp, ship toàn quốc.")
    c3.warning("💝 **Quà Ý Nghĩa**\n\nMón quà đậm chất quê hương.")

    st.markdown("<h2 style='text-align:center;'>✨ SẢN PHẨM NỔI BẬT</h2>", unsafe_allow_html=True)
    ws = ket_noi_sheet("SanPham")
    if ws:
        data = ws.get_all_records()
        if data:
            slider_content = "".join([f'<div class="slide-item"><img src="{row["Hình ảnh"] if la_url_hop_le(row["Hình ảnh"]) else "https://via.placeholder.com/200"}"><p style="font-weight:700; color:#1D4330; margin-top:10px;">{row["Sản phẩm"]}</p></div>' for row in data*2])
            st.markdown(f'<div class="slider-container"><div class="slide-track">{slider_content}</div></div>', unsafe_allow_html=True)

# =============================
# 6. CỬA HÀNG (ĐÃ SỬA LỖI CHỮ)
# =============================
elif chon_menu == "🛍️ Cửa Hàng":
    st.markdown("<h2 style='text-align:center;'>💎 DANH MỤC ĐẶC SẢN</h2>", unsafe_allow_html=True)
    ws = ket_noi_sheet("SanPham")
    if ws:
        data = ws.get_all_records()
        if data:
            df_goc = pd.DataFrame(data)
            col_search, col_filter = st.columns([2, 1])
            with col_search:
                tu_khoa = st.text_input("🔍 Tìm kiếm món ngon...", placeholder="Nhập tên sản phẩm...")
            with col_filter:
                khoang_gia = st.slider("💰 Khoảng giá (VNĐ)", 0, int(df_goc["Giá"].max()), (0, int(df_goc["Giá"].max())))

            df_loc = df_goc[(df_goc["Sản phẩm"].str.contains(tu_khoa, case=False, na=False)) & (df_goc["Giá"] >= khoang_gia[0]) & (df_goc["Giá"] <= khoang_gia[1])]
            st.divider()

            if not df_loc.empty:
                cols = st.columns(4, gap="medium")
                for i, (_, row) in enumerate(df_loc.iterrows()):
                    with cols[i % 4]:
                        st.markdown(f'''
                        <div class="product-card">
                            <img src="{row["Hình ảnh"] if la_url_hop_le(row["Hình ảnh"]) else "https://via.placeholder.com/200"}" style="border-radius: 12px; object-fit: cover; height: 170px; width: 100%;">
                            <div class="product-name">{row["Sản phẩm"]}</div>
                            <div class="gia-ban">{row["Giá"]:,} VNĐ</div>
                            <p style="color:#666; font-size:0.9rem; margin-bottom:15px;">Sẵn có: {row["Tồn kho"]}</p>
                        ''', unsafe_allow_html=True)
                        
                        if int(row["Tồn kho"]) > 0:
                            sl = st.number_input("SL", 1, int(row["Tồn kho"]), key=f"sl_{row['ID']}", label_visibility="collapsed")
                            if st.button("CHỌN MUA 🛒", key=f"btn_{row['ID']}"):
                                st.session_state.gio_hang[str(row["ID"])] = st.session_state.gio_hang.get(str(row["ID"]), 0) + sl
                                st.toast(f"Đã thêm {row['Sản phẩm']}!", icon="✨")
                        else:
                            st.button("HẾT HÀNG", disabled=True, key=f"out_{row['ID']}")
                        st.markdown('</div>', unsafe_allow_html=True)

# =============================
# 7. GIỎ HÀNG
# =============================
elif chon_menu == "🛒 Giỏ Hàng":
    st.markdown("<h2>🛒 ĐƠN HÀNG CỦA BẠN</h2>", unsafe_allow_html=True)
    if not st.session_state.gio_hang:
        st.info("Giỏ hàng đang trống.")
    else:
        ws_sp = ket_noi_sheet("SanPham")
        df_sp = pd.DataFrame(ws_sp.get_all_records())
        tong, ds_order = 0, []
        for id_sp, sl in st.session_state.gio_hang.items():
            sp = df_sp[df_sp['ID'].astype(str) == id_sp].iloc[0]
            tong += sp['Giá'] * sl
            ds_order.append(f"{sp['Sản phẩm']} x{sl}")
            st.write(f"✅ **{sp['Sản phẩm']}** (x{sl}) - {sp['Giá']*sl:,} VNĐ")
        
        st.markdown(f"### Tổng: <span style='color:#D32F2F;'>{tong:,} VNĐ</span>", unsafe_allow_html=True)
        with st.form("order_form"):
            t, s, d = st.text_input("Tên"), st.text_input("SĐT"), st.text_area("Địa chỉ")
            if st.form_submit_button("XÁC NHẬN ĐẶT HÀNG") and t and s and d:
                ket_noi_sheet("DonHang").append_row([datetime.now().strftime("%d/%m/%Y %H:%M"), t, s, d, ", ".join(ds_order), sum(st.session_state.gio_hang.values()), f"{tong:,} VNĐ", "Mới"])
                for id_sp, sl in st.session_state.gio_hang.items():
                    cell = ws_sp.find(id_sp)
                    ws_sp.update_cell(cell.row, 6, int(ws_sp.cell(cell.row, 6).value) - sl)
                st.session_state.gio_hang = {}
                st.success("Đã đặt hàng!"); st.balloons(); time.sleep(1); st.rerun()

# =============================
# 8. QUẢN TRỊ & THÔNG TIN
# =============================
elif chon_menu == "📊 Quản Trị":
    if not st.session_state.da_dang_nhap:
        tk, mk = st.text_input("Admin"), st.text_input("Mật khẩu", type="password")
        if st.button("ĐĂNG NHẬP") and tk == "admin" and mk == "binhdinh0209":
            st.session_state.da_dang_nhap = True; st.rerun()
    else:
        st.button("🚪 Thoát", on_click=lambda: st.session_state.update({"da_dang_nhap": False}))
        t1, t2 = st.tabs(["📦 KHO", "📝 ĐƠN"])
        with t1:
            ws_sp = ket_noi_sheet("SanPham")
            df_edit = st.data_editor(pd.DataFrame(ws_sp.get_all_records()), use_container_width=True)
            if st.button("CẬP NHẬT KHO"):
                ws_sp.clear(); ws_sp.update([df_edit.columns.values.tolist()] + df_edit.values.tolist()); st.success("OK")
        with t2:
            ws_don = ket_noi_sheet("DonHang")
            st.data_editor(pd.DataFrame(ws_don.get_all_records()), use_container_width=True)

elif chon_menu == "📞 Thông Tin":
    st.markdown("<h3>🏡 XỨ NẪU STORE</h3><p>📍 96 Ngô Đức Đệ, Bình Định</p><p>📞 0932.642.376</p>", unsafe_allow_html=True)
    st.map(pd.DataFrame({'lat': [13.8930853], 'lon': [109.1002733]}), zoom=14)
