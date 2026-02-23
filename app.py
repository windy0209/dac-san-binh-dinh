import streamlit as st
from streamlit_option_menu import option_menu
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import pandas as pd
import time
import re

# --- CẤU HÌNH TRANG ---
st.set_page_config(page_title="Cửa Hàng Xứ Nẫu  - Đặc Sản Bình Định", layout="wide", page_icon="🍱")

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

# --- LẤY LOGO ---
def lay_logo():
    ws = ket_noi_sheet("CauHinh")
    if ws:
        try:
            data = ws.get_all_records()
            for row in data:
                if row.get('Ten_Cau_Hinh') == 'Logo' and la_url_hop_le(row.get('Gia_Tri')):
                    return row['Gia_Tri']
        except: pass
    return "https://cdn-icons-png.flaticon.com/512/4062/4062916.png"

# --- CSS NÂNG CAO ---
st.markdown("""
    <style>
    .stApp { background-color: #f8fbf8; }
    .product-card {
        background: white; border-radius: 20px; padding: 15px;
        box-shadow: 0 10px 25px rgba(46, 125, 50, 0.08);
        border: 1px solid #edf2ed; transition: 0.3s; text-align: center;
        margin-bottom: 25px; height: 500px;
    }
    .product-card:hover { transform: translateY(-5px); box-shadow: 0 15px 35px rgba(46, 125, 50, 0.15); }
    .product-card img { border-radius: 15px; object-fit: cover; height: 180px; width: 100%; margin-bottom:10px; }
    .gia-ban { color: #f39c12; font-size: 1.4rem; font-weight: 800; }
    .stButton>button { background-color: #2e7d32; color: white; border-radius: 50px; font-weight: 600; width: 100%; }
    .stButton>button:hover { background-color: #f39c12; color: white; }
    
    /* Banner Slider CSS */
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
    st.markdown("<h2 style='text-align: center; color: #2e7d32; margin-top:-10px;'>CỬA HÀNG XỨ NẪU </h2>", unsafe_allow_html=True)
    chon_menu = option_menu(None, ["🏠 Trang Chủ", "🛍️ Cửa Hàng", "🛒 Giỏ Hàng", "📊 Quản Trị"], 
                            icons=["house", "shop", "cart3", "person-lock"], default_index=0,
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
                img = row['Hình ảnh'] if la_url_hop_le(row['Hình ảnh']) else "https://via.placeholder.com/200"
                st.markdown(f'<div class="product-card"><img src="{img}"><div style="font-weight:700; font-size:1.1rem;">{row["Sản phẩm"]}</div><div class="gia-ban">{row["Giá"]:,} VNĐ</div><div style="color:#2e7d32; font-weight:600;">📦 Còn: {int(row["Tồn kho"])}</div></div>', unsafe_allow_html=True)
                if row['Tồn kho'] > 0:
                    sl = st.number_input("SL:", 1, int(row['Tồn kho']), key=f"sl_{i}")
                    if st.button(f"THÊM VÀO GIỎ", key=f"btn_{i}"):
                        st.session_state.gio_hang[str(row['ID'])] = st.session_state.gio_hang.get(str(row['ID']), 0) + sl
                        st.toast(f"Đã thêm {row['Sản phẩm']}!", icon="✅")
                else: st.button("HẾT HÀNG", disabled=True, key=f"out_{i}")

# --- 3. GIỎ HÀNG ---
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
                    # Trừ kho
                    for id_sp, sl in st.session_state.gio_hang.items():
                        cell = ws_sp.find(str(df_sp[df_sp['ID'].astype(str) == id_sp].iloc[0]['Sản phẩm']))
                        ws_sp.update_cell(cell.row, 6, int(ws_sp.cell(cell.row, 6).value) - sl)
                    st.session_state.gio_hang = {}
                    st.success("Đã đặt hàng!")
                    st.balloons()
                    time.sleep(2); st.rerun()

# --- 4. QUẢN TRỊ ---
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
        
        with tab1:
            df_sp = pd.DataFrame(ws_sp.get_all_records())
            df_edit = st.data_editor(df_sp, num_rows="dynamic", use_container_width=True)
            if st.button("LƯU KHO"):
                ws_sp.clear()
                ws_sp.update([df_edit.columns.values.tolist()] + df_edit.values.tolist())
                st.success("Đã cập nhật!")

        with tab2:
            df_don_old = pd.DataFrame(ws_don.get_all_records())
            df_don_new = st.data_editor(df_don_old, use_container_width=True)
            if st.button("CẬP NHẬT TRẠNG THÁI & HOÀN KHO"):
                for i in range(len(df_don_old)):
                    if str(df_don_old.iloc[i]['Trạng thái']) != "Hủy" and str(df_don_new.iloc[i]['Trạng thái']) == "Hủy":
                        parts = str(df_don_new.iloc[i]['Sản phẩm']).split(", ")
                        for p in parts:
                            m = re.search(r"(.+)\s+x(\d+)", p)
                            if m:
                                name, qty = m.group(1).strip(), int(m.group(2))
                                try:
                                    c = ws_sp.find(name)
                                    ws_sp.update_cell(c.row, 6, int(ws_sp.cell(c.row, 6).value) + qty)
                                    st.write(f"📦 Đã hoàn {qty} {name}")
                                except: pass
                ws_don.clear()
                ws_don.update([df_don_new.columns.values.tolist()] + df_don_new.values.tolist())
                st.success("Thành công!"); time.sleep(1); st.rerun()

        with tab3:
            ws_ch = ket_noi_sheet("CauHinh")
            moi = st.text_input("Link Logo mới:", value=logo_url)
            if st.button("CẬP NHẬT LOGO"):
                c = ws_ch.find("Logo")
                ws_ch.update_cell(c.row, 2, moi); st.rerun()

