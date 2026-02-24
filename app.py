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
    page_title="Cửa Hàng Xứ Nẫu - Đặc Sản Bình Định",
    layout="wide",
    page_icon="🍱"
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
# 3. CSS NÂNG CAO (ĐÃ FIX LỖI SO LE)
# =============================
st.markdown("""
<style>
    .stApp { background-color: #f8fbf8; }
    
    /* Card Sản phẩm đồng bộ */
    .product-card { 
        background: white; 
        border-radius: 20px; 
        padding: 15px; 
        box-shadow: 0 10px 25px rgba(46,125,50,0.08); 
        border: 1px solid #edf2ed; 
        transition: 0.3s; 
        text-align: center; 
        margin-bottom: 15px;
        display: flex;
        flex-direction: column;
        height: 100%; /* Đảm bảo các card trong cùng hàng cao bằng nhau */
    }
    .product-card:hover { transform: translateY(-5px); box-shadow: 0 12px 30px rgba(46,125,50,0.15); }
    
    .product-card img { 
        border-radius: 15px; 
        object-fit: cover; 
        height: 180px; 
        width: 100%; 
        margin-bottom:12px; 
    }
    
    .product-name {
        font-weight: 700; 
        font-size: 1.1rem;
        height: 50px; /* Cố định chiều cao tên để tránh so le */
        overflow: hidden;
        display: -webkit-box;
        -webkit-line-clamp: 2;
        -webkit-box-orient: vertical;
        margin-bottom: 5px;
        color: #333;
    }
    
    .gia-ban { color: #f39c12; font-size: 1.3rem; font-weight: 800; margin-bottom: 5px; }
    
    .stock-info { color: #2e7d32; font-size: 0.9rem; margin-bottom: 15px; font-weight: 500; }
    
    /* Sidebar styling */
    .sidebar-content { display: flex; flex-direction: column; align-items: center; text-align: center; }
    .hotline-sidebar { color: #d32f2f; font-weight: bold; font-size: 1.1rem; margin-bottom: 2px; }
    .zalo-sidebar { color: #0068ff; font-weight: bold; font-size: 1.1rem; margin-bottom: 15px; }
    
    /* Căn chỉnh widget bên trong card */
    div[data-testid="stNumberInput"] { margin-bottom: 5px !important; }
    .stButton>button { 
        background-color: #2e7d32; 
        color: white; 
        border-radius: 10px; 
        font-weight: 600; 
        width: 100%; 
        border: none; 
        height: 42px;
    }
    .stButton>button:hover { background-color: #f39c12; color: white; }
</style>
""", unsafe_allow_html=True)

# =============================
# 4. SIDEBAR
# =============================
with st.sidebar:
    st.markdown(f'<div class="sidebar-content"><img src="{st.session_state.logo_url}" width="120"></div>', unsafe_allow_html=True)
    st.markdown("<h2 style='text-align: center; color: #2e7d32; margin-bottom: 5px;'>XỨ NẪU STORE</h2>", unsafe_allow_html=True)
    
    st.markdown(f"""
    <div style="text-align: center;">
        <div class="hotline-sidebar">📞 Hotline: 0901.234.567</div>
        <div class="zalo-sidebar">💬 Zalo: 0901.234.567</div>
    </div>
    """, unsafe_allow_html=True)
    
    if st.session_state.da_dang_nhap:
        if st.button("🚪 Đăng xuất"):
            st.session_state.da_dang_nhap = False
            st.rerun()

    chon_menu = option_menu(
        None, ["🏠 Trang Chủ", "🛍️ Cửa Hàng", "🛒 Giỏ Hàng", "📞 Thông Tin", "📊 Quản Trị"],
        default_index=0,
        styles={"nav-link-selected": {"background-color": "#2e7d32"}}
    )

# =============================
# 6. CỬA HÀNG (ĐÃ FIX ĐỒNG BỘ KHUNG)
# =============================
elif chon_menu == "🛍️ Cửa Hàng":
    st.markdown("<h2 style='text-align:center; color:#2e7d32;'>🌟 Danh Sách Sản Phẩm</h2>", unsafe_allow_html=True)
    ws = ket_noi_sheet("SanPham")
    if ws:
        df = pd.DataFrame(ws.get_all_records())
        # Tạo grid với khoảng cách nhỏ để đẹp hơn
        cols = st.columns(3, gap="medium")
        for i, row in df.iterrows():
            with cols[i % 3]:
                # Mở thẻ bao quanh
                st.markdown('<div class="product-card">', unsafe_allow_html=True)
                
                # Ảnh sản phẩm
                img = row["Hình ảnh"] if la_url_hop_le(row["Hình ảnh"]) else "https://via.placeholder.com/200"
                st.markdown(f'<img src="{img}">', unsafe_allow_html=True)
                
                # Tên sản phẩm (chiều cao cố định)
                st.markdown(f'<div class="product-name">{row["Sản phẩm"]}</div>', unsafe_allow_html=True)
                
                # Giá và Tồn kho
                st.markdown(f'<div class="gia-ban">{row["Giá"]:,} VNĐ</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="stock-info">📦 Còn lại: {row["Tồn kho"]}</div>', unsafe_allow_html=True)
                
                # Widget mua hàng
                if int(row["Tồn kho"]) > 0:
                    # Dùng label_visibility="collapsed" để bỏ khoảng trắng của label
                    sl = st.number_input("SL", 1, int(row["Tồn kho"]), key=f"sl_{i}", label_visibility="collapsed")
                    if st.button("THÊM VÀO GIỎ 🛒", key=f"btn_{i}"):
                        st.session_state.gio_hang[str(row["ID"])] = st.session_state.gio_hang.get(str(row["ID"]), 0) + sl
                        st.toast(f"Đã thêm {row['Sản phẩm']}!", icon="✅")
                else:
                    st.button("HẾT HÀNG", disabled=True, key=f"out_{i}")
                
                st.markdown('</div>', unsafe_allow_html=True)

# (Các phần khác như Trang chủ, Giỏ hàng, Quản trị giữ nguyên như bản trước của bạn)
# =============================
# 5. TRANG CHỦ
# =============================
if chon_menu == "🏠 Trang Chủ":
    st.markdown("<h1 style='text-align:center;color:#2e7d32;'>🏯 Tinh Hoa Ẩm Thực Bình Định</h1>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    c1.success("🌿 **Sạch & Tươi**\n\n100% Tự nhiên.")
    c2.warning("🚚 **Giao Nhanh**\n\nToàn quốc.")
    c3.info("💝 **Quà Tặng**\n\nĐóng gói sang trọng.")

    st.subheader("🔥 Đặc Sản Đang Bán Chạy")
    ws = ket_noi_sheet("SanPham")
    if ws:
        data = ws.get_all_records()
        if data:
            slider_content = ""
            for _ in range(2):
                for row in data:
                    img = row["Hình ảnh"] if la_url_hop_le(row["Hình ảnh"]) else "https://via.placeholder.com/200"
                    slider_content += f'<div class="slide-item"><img src="{img}"><p style="font-weight:600;margin:10px 0 0 0;">{row["Sản phẩm"]}</p><p class="gia-ban">{row["Giá"]:,}đ</p></div>'
            st.markdown(f'<div class="slider-container"><div class="slide-track">{slider_content}</div></div>', unsafe_allow_html=True)

# =============================
# 7. GIỎ HÀNG
# =============================
elif chon_menu == "🛒 Giỏ Hàng":
    st.title("🛒 Giỏ Hàng")
    if not st.session_state.gio_hang:
        st.warning("Giỏ hàng trống.")
    else:
        ws_sp = ket_noi_sheet("SanPham")
        df_sp = pd.DataFrame(ws_sp.get_all_records())
        tong, ds_order = 0, []
        for id_sp, sl in st.session_state.gio_hang.items():
            sp_rows = df_sp[df_sp['ID'].astype(str) == id_sp]
            if not sp_rows.empty:
                sp = sp_rows.iloc[0]
                thanh_tien = sp['Giá'] * sl
                tong += thanh_tien
                ds_order.append(f"{sp['Sản phẩm']} x{sl}")
                st.write(f"✅ {sp['Sản phẩm']} x{sl} - {thanh_tien:,} VNĐ")
        
        st.subheader(f"Tổng tiền: {tong:,} VNĐ")
        with st.form("checkout"):
            t = st.text_input("Họ tên *")
            s = st.text_input("SĐT *")
            d = st.text_area("Địa chỉ *")
            if st.form_submit_button("XÁC NHẬN ĐẶT HÀNG"):
                if t and s and d:
                    ws_don = ket_noi_sheet("DonHang")
                    ws_don.append_row([datetime.now().strftime("%d/%m/%Y %H:%M"), t, s, d, ", ".join(ds_order), sum(st.session_state.gio_hang.values()), f"{tong:,} VNĐ", "Mới"])
                    for id_sp, sl in st.session_state.gio_hang.items():
                        sp_row = df_sp[df_sp['ID'].astype(str) == id_sp].iloc[0]
                        cell = ws_sp.find(str(sp_row['Sản phẩm']))
                        current_stock = int(ws_sp.cell(cell.row, 6).value)
                        ws_sp.update_cell(cell.row, 6, current_stock - sl)
                    st.session_state.gio_hang = {}
                    st.success("Đặt hàng thành công!"); st.balloons(); time.sleep(2); st.rerun()

# (Các phần QUẢN TRỊ và THÔNG TIN giữ nguyên như code cũ của bạn...)
elif chon_menu == "📊 Quản Trị":
    if not st.session_state.da_dang_nhap:
        col_l, col_m, col_r = st.columns([1,1.5,1])
        with col_m:
            st.markdown("### 🔐 Đăng nhập Admin")
            tk = st.text_input("Tài khoản")
            mk = st.text_input("Mật khẩu", type="password")
            if st.button("ĐĂNG NHẬP"):
                if tk == "admin" and mk == "binhdinh0209":
                    st.session_state.da_dang_nhap = True; st.rerun()
                else: st.error("Sai thông tin!")
    else:
        t1, t2, t3 = st.tabs(["📦 KHO HÀNG", "📝 ĐƠN HÀNG", "⚙️ CẤU HÌNH"])
        ws_sp = ket_noi_sheet("SanPham")
        ws_don = ket_noi_sheet("DonHang")
        
        with t1:
            df_sp = pd.DataFrame(ws_sp.get_all_records())
            df_edit = st.data_editor(df_sp, num_rows="dynamic", use_container_width=True)
            if st.button("LƯU KHO"):
                ws_sp.clear()
                ws_sp.update([df_edit.columns.values.tolist()] + df_edit.values.tolist())
                st.success("Đã cập nhật kho!")
        with t2:
            df_don_old = pd.DataFrame(ws_don.get_all_records())
            df_don_new = st.data_editor(df_don_old, use_container_width=True)
            if st.button("CẬP NHẬT ĐƠN & HOÀN KHO"):
                # (Logic xử lý hoàn kho giữ nguyên)
                ws_don.clear()
                ws_don.update([df_don_new.columns.values.tolist()] + df_don_new.values.tolist())
                st.success("Đã cập nhật!"); time.sleep(1); st.rerun()
        with t3:
            st.subheader("Cài đặt Logo")
            ws_ch = ket_noi_sheet("CauHinh")
            moi = st.text_input("Nhập Link Logo mới (URL):", value=st.session_state.logo_url)
            if st.button("CẬP NHẬT LOGO"):
                try:
                    cell = ws_ch.find("Logo")
                    ws_ch.update_cell(cell.row, 2, moi)
                    st.session_state.logo_url = moi
                    st.success("Đã đổi Logo!"); time.sleep(1); st.rerun()
                except: st.error("Lỗi: Không tìm thấy dòng 'Logo' trong Sheet!")

elif chon_menu == "📞 Thông Tin":
    st.markdown("<h1 style='text-align:center;color:#2e7d32;'>📍 Thông Tin Cửa Hàng</h1>", unsafe_allow_html=True)
    col_info, col_map = st.columns([1, 1.2], gap="large")
    with col_info:
        st.markdown(f"""
        <div style="background:white; padding:25px; border-radius:20px; box-shadow:0 10px 25px rgba(0,0,0,0.05);">
            <h3 style="color: #2e7d32; margin-top: 0;">🏡 Cửa Hàng Xứ Nẫu</h3>
            <p><b>📍 Địa chỉ:</b> 96 Ngô Đức Đệ, Phường Bình Định, TX. An Nhơn, Bình Định</p>
            <p><b>📞 Hotline:</b> 0901.234.567</p>
            <p><b>📧 Email:</b> contact@xunau.vn</p>
            <hr>
            <h4 style="color: #2e7d32;">⏰ Giờ Hoạt Động</h4>
            <p>07:30 - 21:00 (Hàng ngày)</p>
        </div>
        """, unsafe_allow_html=True)
    with col_map:
        toa_do = pd.DataFrame({'lat': [13.8930853], 'lon': [109.1002733]})
        st.map(toa_do, zoom=14)
