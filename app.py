import streamlit as st
from streamlit_option_menu import option_menu
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import pandas as pd
import time
import re
import json

# =============================
# 1. CẤU HÌNH TRANG & SEO
# =============================
st.set_page_config(
    page_title="Đặc Sản Bình Định - Cửa Hàng Xứ Nẫu | Nem Chả, Tré Chính Gốc",
    layout="wide",
    page_icon="https://raw.githubusercontent.com/windy0209/dac-san-binh-dinh/main/default_logo.png",
    initial_sidebar_state="expanded"  # Tự động mở menu trên điện thoại
)

# =============================
# ẨN CÁC THÀNH PHẦN KHÔNG CẦN THIẾT (NHƯNG GIỮ LẠI NÚT MENU)
# =============================
st.markdown("""
<style>
/* Làm trong suốt header để giữ lại nút Menu (Mũi tên/Ba gạch) */
header {
    background-color: rgba(0,0,0,0) !important;
}

/* Ẩn toolbar Streamlit nhưng giữ lại nút Menu */
[data-testid="stToolbar"] {display: none !important;}

/* Ẩn Footer và các link GitHub/Profile */
footer {visibility: hidden !important;}
[data-testid="stStatusWidget"] {display: none !important;}
[data-testid="stDecoration"] {display: none !important;}
a[href*="profile"], a[href*="github"] {display: none !important;}

/* Fix lỗi hiển thị trên Mobile */
@media (max-width: 768px) {
    .stApp { margin-top: -50px; }
}
</style>
""", unsafe_allow_html=True)

# --- MÃ TỐI ƯU GOOGLE (SEO Meta Tags) ---
st.markdown(
    """
    <head>
        <meta name="description" content="Cửa hàng Xứ Nẫu chuyên cung cấp đặc sản Bình Định chính gốc: Nem chợ Huyện, chả bò, tré, bánh ít lá gai. Giao hàng toàn quốc, uy tín, chất lượng.">
        <meta name="keywords" content="đặc sản Bình Định, nem chợ huyện, tré bình định, chả bò bình định, rượu bầu đá, bánh ít lá gai, cửa hàng xứ nẫu">
        <meta property="og:title" content="Đặc Sản Bình Định - Cửa Hàng Xứ Nẫu">
        <meta property="og:description" content="Tinh hoa ẩm thực miền đất võ. Giao hàng nhanh toàn quốc.">
        <meta property="og:image" content="https://raw.githubusercontent.com/windy0209/dac-san-binh-dinh/main/logo2.png">
        <link rel="canonical" href="https://your-app-url.streamlit.app/">
    </head>
    """,
    unsafe_allow_html=True
)

# --- CẤU TRÚC DỮ LIỆU SCHEMA ---
schema_data = {
    "@context": "https://schema.org",
    "@type": "Store",
    "name": "Cửa Hàng Xứ Nẫu - Đặc Sản Bình Định",
    "image": "https://raw.githubusercontent.com/windy0209/dac-san-binh-dinh/main/logo2.png",
    "telephone": "0932642376",
    "address": {
        "@type": "PostalAddress",
        "streetAddress": "96 Ngô Đức Đệ, Phường Bình Định",
        "addressLocality": "An Nhơn",
        "addressRegion": "Bình Định",
        "addressCountry": "VN"
    },
    "priceRange": "20.000đ - 500.000đ",
    "openingHours": "Mo-Su 07:30-21:00"
}
st.markdown(f'<script type="application/ld+json">{json.dumps(schema_data)}</script>', unsafe_allow_html=True)

# Khởi tạo Session State
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
# 3. CSS NÂNG CAO
# =============================
st.markdown("""
<style>
    .stApp { background-color: #f8fbf8; }
    .slider-container { width: 100%; overflow: hidden; background: white; padding: 25px 0; border-radius: 25px; box-shadow: 0 10px 30px rgba(0,0,0,0.05); margin-top: 20px; }
    .slide-track { display: flex; width: max-content; animation: scroll 40s linear infinite; }
    .slide-item { width: 230px; margin: 0 20px; text-align: center; flex-shrink: 0; }
    .slide-item img { width: 220px; height: 170px; object-fit: cover; border-radius: 18px; box-shadow: 0 8px 15px rgba(0,0,0,0.1); }
    @keyframes scroll { 0% { transform: translateX(0); } 100% { transform: translateX(-50%); } }
    .product-name { font-weight: 700; font-size: 1.1rem; height: 50px; overflow: hidden; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; margin-bottom: 5px; color: #333; }
    .product-card { background: white; border-radius: 20px; padding: 15px; box-shadow: 0 10px 25px rgba(46,125,50,0.08); border: 1px solid #edf2ed; text-align: center; display: flex; flex-direction: column; height: 100%; }
    .sidebar-content { display: flex; flex-direction: column; align-items: center; text-align: center; }
    .hotline-sidebar { color: #d32f2f; font-weight: bold; font-size: 1.1rem; margin-bottom: 5px; }
    .zalo-sidebar { color: #0068ff; font-weight: bold; font-size: 1.1rem; margin-bottom: 15px; }
    .stButton>button { background-color: #2e7d32; color: white; border-radius: 12px; font-weight: 600; width: 100%; border: none; }
    .stButton>button:hover { background-color: #f39c12; color: white; }
</style>
""", unsafe_allow_html=True)

# =============================
# 4. SIDEBAR (MENU ĐIỀU HƯỚNG)
# =============================
with st.sidebar:
    st.markdown(f'<div class="sidebar-content"><img src="{st.session_state.logo_url}" width="120" alt="Logo Đặc Sản Bình Định"></div>', unsafe_allow_html=True)
    st.markdown("<h2 style='text-align: center; color: #2e7d32; margin-bottom: 5px;'>XỨ NẪU STORE</h2>", unsafe_allow_html=True)
    st.markdown("""<div style="text-align: center;"><div class="hotline-sidebar">📞 Hotline: 0932.642.376</div><div class="zalo-sidebar">💬 Zalo: 0932.642.376</div></div>""", unsafe_allow_html=True)
    
    if st.session_state.da_dang_nhap:
        if st.button("🚪 Đăng xuất"):
            st.session_state.da_dang_nhap = False
            st.rerun()

    chon_menu = option_menu(
        None, ["🏠 Trang Chủ", "🛍️ Cửa Hàng", "🛒 Giỏ Hàng", "📞 Thông Tin", "📊 Quản Trị"],
        default_index=0,
        styles={"nav-link-selected": {"background-color": "#2e7d32"}}
    )

    st.markdown("---")
    st.image("https://raw.githubusercontent.com/windy0209/dac-san-binh-dinh/main/qrcode.png", caption="Quét mã để liên hệ", use_container_width=True)

# =============================
# 5. TRANG CHỦ
# =============================
if chon_menu == "🏠 Trang Chủ":
    st.markdown("<h1 style='text-align:center;color:#2e7d32;'>🏯 Tinh Hoa Đặc Sản Bình Định Chính Gốc</h1>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    c1.success("🌿 **Sạch & Tươi**\n\n100% Tự nhiên, không chất bảo quản.")
    c2.warning("🚚 **Giao Nhanh**\n\nShip COD toàn quốc, kiểm tra hàng thoải mái.")
    c3.info("💝 **Quà Tặng**\n\nĐặc sản làm quà sang trọng, ý nghĩa.")

    st.subheader("🔥 Đặc Sản Đang Bán Chạy Nhất")
    ws = ket_noi_sheet("SanPham")
    if ws:
        data = ws.get_all_records()
        if data:
            slider_content = ""
            for _ in range(2):
                for row in data:
                    img = row["Hình ảnh"] if la_url_hop_le(row["Hình ảnh"]) else "https://via.placeholder.com/200"
                    slider_content += f'<div class="slide-item"><img src="{img}" alt="{row["Sản phẩm"]}"><p style="font-weight:600;margin:10px 0 0 0;">{row["Sản phẩm"]}</p><p style="color:#f39c12;font-weight:bold;">{row["Giá"]:,}đ</p></div>'
            st.markdown(f'<div class="slider-container"><div class="slide-track">{slider_content}</div></div>', unsafe_allow_html=True)

# =============================
# 6. CỬA HÀNG
# =============================
elif chon_menu == "🛍️ Cửa Hàng":
    st.markdown("<h2 style='text-align:center; color:#2e7d32;'>🌟 Danh Mục Sản Phẩm Xứ Nẫu</h2>", unsafe_allow_html=True)
    ws = ket_noi_sheet("SanPham")
    if ws:
        data = ws.get_all_records()
        if not data:
            st.info("Hiện chưa có sản phẩm nào trong kho.")
        else:
            df_goc = pd.DataFrame(data)
            with st.container():
                col_search, col_filter = st.columns([2, 1])
                with col_search:
                    tu_khoa = st.text_input("🔍 Tìm đặc sản...", placeholder="Ví dụ: Nem Chợ Huyện, Tré, Chả Bò...")
                with col_filter:
                    gia_max = int(df_goc["Giá"].max())
                    khoang_gia = st.slider("💰 Lọc theo giá (VNĐ)", 0, gia_max, (0, gia_max), step=10000)

            df_loc = df_goc[
                (df_goc["Sản phẩm"].str.contains(tu_khoa, case=False, na=False)) &
                (df_goc["Giá"] >= khoang_gia[0]) &
                (df_goc["Giá"] <= khoang_gia[1])
            ]

            st.divider()
            if df_loc.empty:
                st.warning("Không tìm thấy sản phẩm phù hợp.")
            else:
                cols = st.columns(3, gap="medium")
                for i, (_, row) in enumerate(df_loc.iterrows()):
                    with cols[i % 3]:
                        st.markdown('<div class="product-card">', unsafe_allow_html=True)
                        img = row["Hình ảnh"] if la_url_hop_le(row["Hình ảnh"]) else "https://via.placeholder.com/200"
                        st.markdown(f'<img src="{img}" alt="{row["Sản phẩm"]}" style="border-radius: 15px; object-fit: cover; height: 180px; width: 100%; margin-bottom:12px;">', unsafe_allow_html=True)
                        st.markdown(f'<div class="product-name">{row["Sản phẩm"]}</div>', unsafe_allow_html=True)
                        st.markdown(f'<div style="color:#f39c12; font-size:1.3rem; font-weight:800; margin-bottom:5px;">{row["Giá"]:,} VNĐ</div>', unsafe_allow_html=True)
                        st.markdown(f'<div style="color:#2e7d32; font-size:0.9rem; margin-bottom:15px; font-weight:500;">📦 Còn lại: {row["Tồn kho"]}</div>', unsafe_allow_html=True)
                        
                        if int(row["Tồn kho"]) > 0:
                            sl = st.number_input("SL", 1, int(row["Tồn kho"]), key=f"sl_{row['ID']}", label_visibility="collapsed")
                            if st.button("THÊM VÀO GIỎ 🛒", key=f"btn_{row['ID']}"):
                                st.session_state.gio_hang[str(row["ID"])] = st.session_state.gio_hang.get(str(row["ID"]), 0) + sl
                                st.toast(f"Đã thêm {row['Sản phẩm']}!", icon="✅")
                        else:
                            st.button("HẾT HÀNG", disabled=True, key=f"out_{row['ID']}")
                        st.markdown('</div>', unsafe_allow_html=True)
                        st.write("")

# =============================
# 7. GIỎ HÀNG
# =============================
elif chon_menu == "🛒 Giỏ Hàng":
    st.title("🛒 Giỏ Hàng Của Bạn")
    if not st.session_state.gio_hang:
        st.warning("Giỏ hàng của bạn đang trống. Hãy chọn vài món đặc sản nhé!")
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
                st.write(f"✅ **{sp['Sản phẩm']}** x{sl} - {thanh_tien:,} VNĐ")
        
        st.subheader(f"Tổng thanh toán: {tong:,} VNĐ")
        with st.form("checkout"):
            t = st.text_input("Họ và tên khách hàng *")
            s = st.text_input("Số điện thoại liên hệ *")
            d = st.text_area("Địa chỉ nhận hàng tại TP.HCM/Toàn quốc *")
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
                    st.success("Đặt hàng thành công! Chúng tôi sẽ gọi xác nhận ngay."); st.balloons(); time.sleep(2); st.rerun()

# =============================
# 8. QUẢN TRỊ
# =============================
elif chon_menu == "📊 Quản Trị":
    if not st.session_state.da_dang_nhap:
        col_l, col_m, col_r = st.columns([1,1.5,1])
        with col_m:
            st.markdown("### 🔐 Đăng nhập hệ thống quản lý")
            tk = st.text_input("Tài khoản quản trị")
            mk = st.text_input("Mật khẩu", type="password")
            if st.button("ĐĂNG NHẬP"):
                if tk == "admin" and mk == "binhdinh0209":
                    st.session_state.da_dang_nhap = True; st.rerun()
                else: st.error("Sai thông tin đăng nhập!")
    else:
        t1, t2, t3 = st.tabs(["📦 KHO HÀNG", "📝 ĐƠN HÀNG", "⚙️ CẤU HÌNH"])
        ws_sp = ket_noi_sheet("SanPham")
        ws_don = ket_noi_sheet("DonHang")
        
        with t1:
            df_sp = pd.DataFrame(ws_sp.get_all_records())
            df_edit = st.data_editor(df_sp, num_rows="dynamic", use_container_width=True)
            if st.button("LƯU THAY ĐỔI KHO"):
                ws_sp.clear()
                ws_sp.update([df_edit.columns.values.tolist()] + df_edit.values.tolist())
                st.success("Đã cập nhật dữ liệu kho hàng!")

        with t2:
            df_don_old = pd.DataFrame(ws_don.get_all_records())
            df_don_new = st.data_editor(df_don_old, use_container_width=True)
            if st.button("CẬP NHẬT TRẠNG THÁI ĐƠN"):
                for i in range(len(df_don_old)):
                    if str(df_don_old.iloc[i]['Trạng thái']) != "Hủy" and str(df_don_new.iloc[i]['Trạng thái']) == "Hủy":
                        chuoi_sp = str(df_don_new.iloc[i]['Sản phẩm']) 
                        for item in chuoi_sp.split(", "):
                            match = re.search(r"(.+)\s+x(\d+)", item)
                            if match:
                                ten_sp, so_luong = match.group(1).strip(), int(match.group(2))
                                cell = ws_sp.find(ten_sp)
                                ton_cu = int(ws_sp.cell(cell.row, 6).value)
                                ws_sp.update_cell(cell.row, 6, ton_cu + so_luong)
                ws_don.clear()
                ws_don.update([df_don_new.columns.values.tolist()] + df_don_new.values.tolist())
                st.success("Đã cập nhật đơn hàng!"); time.sleep(1); st.rerun()

        with t3:
            st.subheader("Cài đặt Logo và Thương hiệu")
            ws_ch = ket_noi_sheet("CauHinh")
            moi = st.text_input("Nhập Link Logo mới (URL):", value=st.session_state.logo_url)
            if st.button("CẬP NHẬT LOGO"):
                try:
                    cell = ws_ch.find("Logo")
                    ws_ch.update_cell(cell.row, 2, moi)
                    st.session_state.logo_url = moi
                    st.success("Đã đổi Logo!"); time.sleep(1); st.rerun()
                except: st.error("Lỗi: Không tìm thấy mục 'Logo' trong Sheet!")

# =============================
# 9. THÔNG TIN
# =============================
elif chon_menu == "📞 Thông Tin":
    st.markdown("<h1 style='text-align:center;color:#2e7d32;'>📍 Địa Chỉ & Liên Hệ Cửa Hàng</h1>", unsafe_allow_html=True)
    col_info, col_map = st.columns([1, 1.2], gap="large")
    with col_info:
        st.markdown(f"""
        <div style="background:white; padding:25px; border-radius:20px; box-shadow:0 10px 25px rgba(0,0,0,0.05);">
            <h3 style="color: #2e7d32; margin-top: 0;">🏡 Cửa Hàng Đặc Sản Xứ Nẫu</h3>
            <p><b>📍 Địa chỉ:</b> 96 Ngô Đức Đệ, Phường Bình Định, TX. An Nhơn, Bình Định</p>
            <p><b>📞 Hotline:</b> 0932.642.376</p>
            <p><b>💬 Zalo:</b> 0932.642.376 (Hỗ trợ 24/7)</p>
            <p><b>📧 Email:</b> miendatvo86@gmail.com</p>
            <hr>
            <h4 style="color: #2e7d32;">⏰ Giờ Mở Cửa</h4>
            <p>Thứ 2 - Chủ Nhật: 07:30 - 21:00</p>
            <p><i>Chuyên sỉ và lẻ nem chả, bánh ít, rượu bầu đá chính hiệu Bình Định.</i></p>
        </div>
        """, unsafe_allow_html=True)
    with col_map:
        toa_do = pd.DataFrame({'lat': [13.8930853], 'lon': [109.1002733]})
        st.map(toa_do, zoom=14)
