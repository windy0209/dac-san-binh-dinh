import streamlit as st
from streamlit_option_menu import option_menu
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import pandas as pd
import time
import re

# --- CẤU HÌNH TRANG ---
st.set_page_config(page_title="Cửa Hàng Xứ Nẫu - Đặc Sản Bình Định", layout="wide", page_icon="🍱")

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

# --- CSS NÂNG CAO ---
st.markdown("""
    <style>
    .stApp { background-color: #f8fbf8; }
    
    /* Khung bao ngoài container sản phẩm */
    [data-testid="stVerticalBlockBorderWrapper"] {
        border: 1px solid #edf2ed !important;
        border-radius: 20px !important;
        background-color: white !important;
        box-shadow: 0 10px 25px rgba(46, 125, 50, 0.08) !important;
        padding: 15px !important;
        transition: 0.3s !important;
    }
    
    .product-info img { border-radius: 15px; object-fit: cover; height: 180px; width: 100%; }
    .gia-ban { color: #f39c12; font-size: 1.4rem; font-weight: 800; margin: 10px 0; }
    
    .stButton>button { 
        background-color: #2e7d32; color: white; border-radius: 10px; 
        font-weight: 600; width: 100%; border: none; height: 45px;
    }
    .stButton>button:hover { background-color: #f39c12; color: white; }
    
    div[data-testid="stNumberInput"] label { display: none; }

    /* Info Box CSS */
    .info-box {
        background: white; padding: 25px; border-radius: 20px;
        border-left: 5px solid #2e7d32; box-shadow: 0 5px 15px rgba(0,0,0,0.05);
        margin-bottom: 20px;
    }

    /* Banner Slider */
    .banner-container { width: 100%; height: 350px; overflow: hidden; border-radius: 20px; margin-bottom: 30px; }
    .banner-wrapper { display: flex; width: 300%; height: 100%; animation: slide 12s infinite; }
    .banner-slide { width: 100%; height: 100%; background-size: cover; background-position: center; }
    @keyframes slide {
        0%, 30% { transform: translateX(0); }
        33%, 63% { transform: translateX(-33.33%); }
        66%, 96% { transform: translateX(-66.66%); }
        100% { transform: translateX(0); }
    }
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR ---
logo_url = lay_logo()
with st.sidebar:
    if la_url_hop_le(logo_url): st.image(logo_url, width=120)
    st.markdown("<h2 style='text-align: center; color: #2e7d32; margin-top:-10px;'>CỬA HÀNG XỨ NẪU</h2>", unsafe_allow_html=True)
    chon_menu = option_menu(None, ["🏠 Trang Chủ", "🛍️ Cửa Hàng", "🛒 Giỏ Hàng", "📞 Thông Tin", "📊 Quản Trị"], 
                            icons=["house", "shop", "cart3", "info-circle", "person-lock"], default_index=0,
                            styles={"nav-link-selected": {"background-color": "#2e7d32"}})

# --- 1. TRANG CHỦ ---
if chon_menu == "🏠 Trang Chủ":
    banners = ["https://mia.vn/media/uploads/blog-du-lich/nem-cho-huyen-dac-san-binh-dinh-lam-say-long-bao-thuc-khach-1-1652173169.jpg",
               "https://vcdn1-dulich.vnecdn.net/2022/06/03/7-1654247844-3323-1654247920.jpg",
               "https://dacsanbinhdinhonline.com/wp-content/uploads/2020/03/tre-bo-rom-binh-dinh.jpg"]
    st.markdown(f'<div class="banner-container"><div class="banner-wrapper">' + 
                ''.join([f'<div class="banner-slide" style="background-image: url(\'{b}\');"></div>' for b in banners]) + 
                '</div></div>', unsafe_allow_html=True)
    
    st.markdown("<h1 style='text-align: center; color: #2e7d32;'>🏯 Tinh Hoa Ẩm Thực Bình Định</h1>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    c1.success("🌿 **Sạch & Tươi**\n\nNguyên liệu tự nhiên 100%.")
    c2.warning("🚚 **Giao Nhanh**\n\nShip toàn quốc, nhận trong ngày.")
    c3.info("💝 **Quà Tặng**\n\nĐóng gói sang trọng, tinh tế.")

# --- 2. CỬA HÀNG ---
elif chon_menu == "🛍️ Cửa Hàng":
    st.subheader("🌟 Sản Phẩm Nổi Bật")
    ws_sp = ket_noi_sheet("SanPham")
    if ws_sp:
        df = pd.DataFrame(ws_sp.get_all_records())
        df['Giá'] = pd.to_numeric(df['Giá'], errors='coerce').fillna(0)
        df['Tồn kho'] = pd.to_numeric(df['Tồn kho'], errors='coerce').fillna(0)
        
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
                            <div style="color:#2e7d32; font-weight:600; margin-bottom:10px;">📦 Còn: {int(row["Tồn kho"])}</div>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    if row['Tồn kho'] > 0:
                        c_sl, c_btn = st.columns([1, 2])
                        with c_sl: sl = st.number_input("SL", 1, int(row['Tồn kho']), key=f"sl_{i}")
                        with c_btn:
                            if st.button(f"THÊM 🛒", key=f"btn_{i}"):
                                st.session_state.gio_hang[str(row['ID'])] = st.session_state.gio_hang.get(str(row['ID']), 0) + sl
                                st.toast(f"Đã thêm {row['Sản phẩm']}!", icon="✅")
                    else: st.button("HẾT HÀNG", disabled=True, key=f"out_{i}")

# --- 3. GIỎ HÀNG --- (Giữ nguyên logic cũ)
elif chon_menu == "🛒 Giỏ Hàng":
    st.title("🛒 Giỏ Hàng")
    if not st.session_state.gio_hang: st.warning("Giỏ hàng trống.")
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
                    for id_sp, sl in st.session_state.gio_hang.items():
                        cell = ws_sp.find(str(df_sp[df_sp['ID'].astype(str) == id_sp].iloc[0]['Sản phẩm']))
                        ws_sp.update_cell(cell.row, 6, int(ws_sp.cell(cell.row, 6).value) - sl)
                    st.session_state.gio_hang = {}
                    st.success("Đã đặt hàng thành công!")
                    st.balloons()
                    time.sleep(2); st.rerun()

# --- 4. THÔNG TIN CỬA HÀNG (MỤC MỚI THÊM) ---
elif chon_menu == "📞 Thông Tin":
    st.markdown("<h1 style='color: #2e7d32;'>📞 Thông Tin Liên Hệ</h1>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"""
        <div class="info-box">
            <h3>🏠 Địa chỉ cửa hàng</h3>
            <p>123 Đường Võ Nguyên Giáp, TP. Quy Nhơn, Bình Định</p>
            <h3>☎️ Hotline / Zalo</h3>
            <p><b>0905.XXX.XXX</b> (Hỗ trợ 24/7)</p>
            <h3>🌐 Fanpage</h3>
            <p><a href="#">facebook.com/dacsanxunau</a></p>
        </div>
        """, unsafe_allow_html=True)
        
    with col2:
        st.markdown("""
        <div class="info-box">
            <h3>🚚 Chính sách giao hàng</h3>
            <ul>
                <li>Nội thành Quy Nhơn: Giao trong 30 phút.</li>
                <li>Toàn quốc: 2-3 ngày làm việc.</li>
                <li>Freeship cho đơn hàng trên 500.000 VNĐ.</li>
            </ul>
            <h3>🛡️ Cam kết chất lượng</h3>
            <p>Sản phẩm chính gốc Bình Định, không chất bảo quản, đổi trả nếu không hài lòng.</p>
        </div>
        """, unsafe_allow_html=True)

# --- 5. QUẢN TRỊ --- (Giữ nguyên logic cũ)
elif chon_menu == "📊 Quản Trị":
    if not st.session_state.da_dang_nhap:
        tk = st.text_input("Admin")
        mk = st.text_input("Mật khẩu", type="password")
        if st.button("Đăng nhập"):
            if tk == "admin" and mk == "binhdinh0209":
                st.session_state.da_dang_nhap = True; st.rerun()
    else:
        tab1, tab2, tab3 = st.tabs(["📦 KHO", "📝 ĐƠN HÀNG", "⚙️ CẤU HÌNH"])
        ws_sp = ket_noi_sheet("SanPham")
        ws_don = ket_noi_sheet("DonHang")
        # ... (Phần code quản trị còn lại không thay đổi) ...
        with tab1:
            df_sp = pd.DataFrame(ws_sp.get_all_records())
            df_edit = st.data_editor(df_sp, num_rows="dynamic", use_container_width=True)
            if st.button("LƯU KHO"):
                ws_sp.clear()
                ws_sp.update([df_edit.columns.values.tolist()] + df_edit.values.tolist())
                st.success("Đã cập nhật!")
