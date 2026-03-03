import streamlit as st
from streamlit_option_menu import option_menu
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import pandas as pd
import time
import re
import random
import html
import json
import os  
import requests
import pytz

# =============================
# 1. CẤU HÌNH TRANG & ẨN TOOLBAR
# =============================
st.set_page_config(
    page_title="Cửa Hàng Xứ Nẫu - Đặc Sản Bình Định",
    layout="wide",
    page_icon="https://raw.githubusercontent.com/windy0209/dac-san-binh-dinh/main/default_logo.png"
)

# Ẩn thanh công cụ mặc định của Streamlit
hide_streamlit_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# =============================
# 2. KHỞI TẠO SESSION STATE
# =============================
if "da_dang_nhap" not in st.session_state:
    st.session_state.da_dang_nhap = False

if "gio_hang" not in st.session_state:
    st.session_state.gio_hang = {}

if "logo_url" not in st.session_state:
    st.session_state.logo_url = "https://raw.githubusercontent.com/windy0209/dac-san-binh-dinh/main/logo2.png"

# Các state mới cho hiển thị đơn hàng sau khi đặt
if "hien_thi_don_hang" not in st.session_state:
    st.session_state.hien_thi_don_hang = False

if "don_hang_vua_dat" not in st.session_state:
    st.session_state.don_hang_vua_dat = {}

# Quản lý tab hiện tại
if "tab_index" not in st.session_state:
    st.session_state.tab_index = 0

# =============================
# 3. KẾT NỐI GOOGLE SHEETS
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
        except:
            pass

tai_logo_tu_sheet()

# =============================
# 4. CSS TÙY CHỈNH GIAO DIỆN (TỐI ƯU MOBILE + BACKGROUND HEADER)
# =============================
st.markdown("""
<style>
    .stApp { background-color: #f8fbf8; }
    
    /* Header ngang với background hình ảnh */
    .header-container {
        display: flex;
        align-items: center;
        justify-content: space-between;
        background-image: linear-gradient(rgba(0, 0, 0, 0.3), rgba(0, 0, 0, 0.3)), url('https://raw.githubusercontent.com/windy0209/dac-san-binh-dinh/main/bg-header.png');
        background-size: cover;
        background-position: center;
        background-blend-mode: overlay;
        padding: 20px 40px;
        min-height: 180px;
        border-radius: 60px;
        margin: 20px auto 10px auto;
        max-width: 1300px;
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        border: 1px solid rgba(255,255,255,0.2);
        color: white;
    }
    .header-logo img { height: 80px; width: auto; }
    .header-info {
        display: flex;
        gap: 30px;
        font-size: 1.1rem;
    }
    .header-info div {
        display: flex;
        align-items: center;
        gap: 5px;
    }
    .header-container h2, .header-container p, .header-container div {
        color: white !important;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
    }
    .hotline, .zalo {
        color: white !important;
    }
    
    /* Slider Trang chủ */
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
    
    /* Chiều cao cố định cho tên sản phẩm */
    .product-name {
        font-weight: 700; 
        font-size: 1.1rem;
        height: 50px;
        overflow: hidden;
        display: -webkit-box;
        -webkit-line-clamp: 2;
        -webkit-box-orient: vertical;
        margin-bottom: 5px;
        color: #333;
    }
    
    /* Khung card sản phẩm */
    .product-card {
        background: white;
        border-radius: 20px;
        padding: 15px;
        box-shadow: 0 10px 25px rgba(46,125,50,0.08);
        border: 1px solid #edf2ed;
        text-align: center;
        display: flex;
        flex-direction: column;
        height: 100%;
    }
    
    /* Button & Input Styling */
    .stButton>button {
        background-color: #2e7d32;
        color: white;
        border-radius: 12px;
        font-weight: 600;
        width: 100%;
        border: none;
        transition: 0.3s;
    }
    .stButton>button:hover { background-color: #f39c12; color: white; }
    div[data-testid="stNumberInput"] { margin-bottom: -10px; }
    
    /* Điều chỉnh khoảng cách chung */
    .block-container { padding-top: 0; }

    /* Card thông tin đơn hàng (giống hình) */
    .don-hang-card {
        background: white;
        border-radius: 25px;
        padding: 30px;
        box-shadow: 0 15px 35px rgba(0,0,0,0.1);
        max-width: 700px;
        margin: 0 auto;
        border: 1px solid #e0f2e0;
    }
    .don-hang-header {
        text-align: center;
        margin-bottom: 25px;
    }
    .don-hang-header h2 {
        color: #2e7d32;
        margin-bottom: 5px;
    }
    .don-hang-info {
        background: #f0f8f0;
        border-radius: 15px;
        padding: 20px;
        margin-bottom: 20px;
    }
    .info-row {
        display: flex;
        justify-content: space-between;
        padding: 8px 0;
        border-bottom: 1px dashed #c8e6c9;
    }
    .info-row:last-child {
        border-bottom: none;
    }
    .info-label {
        font-weight: 600;
        color: #2e7d32;
    }
    .info-value {
        color: #0066cc;
        font-weight: 500;
    }
    table.don-hang-table {
        width: 100%;
        border-collapse: collapse;
        margin: 20px 0;
    }
    table.don-hang-table th {
        background: #2e7d32;
        color: white;
        padding: 12px;
        text-align: left;
    }
    table.don-hang-table td {
        padding: 12px;
        border-bottom: 1px solid #e0f2e0;
    }
    table.don-hang-table tr:last-child td {
        border-bottom: none;
    }
    .total-row {
        font-weight: 700;
        background: #f0f8f0;
    }
    
    /* ===== RESPONSIVE CHO MOBILE ===== */
    @media only screen and (max-width: 768px) {
        body, p, div, span, .stMarkdown, .stText, .stButton>button {
            font-size: 16px !important;
        }
        h1 { font-size: 28px !important; }
        h2 { font-size: 24px !important; }
        h3 { font-size: 20px !important; }
        
        .header-container {
            flex-direction: column;
            padding: 20px;
            min-height: auto;
            border-radius: 30px;
        }
        .header-logo img { height: 80px; }
        .header-info {
            flex-direction: column;
            gap: 10px;
            margin-top: 10px;
            text-align: center;
        }
        .header-info div { justify-content: center; }
        
        .stHorizontal {
            max-width: 100% !important;
            overflow-x: auto !important;
            white-space: nowrap !important;
            display: block !important;
            -webkit-overflow-scrolling: touch;
            scrollbar-width: none;
            padding: 5px 0;
        }
        .stHorizontal::-webkit-scrollbar {
            display: none;
        }
        .stHorizontal > div {
            display: inline-block !important;
            float: none !important;
        }
        .nav-link {
            padding: 8px 12px !important;
            font-size: 0.9rem !important;
            margin: 0 3px !important;
        }
        
        .slide-item { width: 160px; margin: 0 10px; }
        .slide-item img { width: 150px; height: 120px; }
        
        .row-widget.stHorizontal > div {
            min-width: 48%;
        }
        .product-card { padding: 10px; }
        .product-name { font-size: 1rem; height: 40px; }
        .gia-ban { font-size: 1.1rem !important; }
        
        .stColumns { gap: 10px; }
        .don-hang-card { padding: 20px; }
    }

    @media only screen and (max-width: 480px) {
        .slide-item { width: 130px; }
        .slide-item img { width: 120px; height: 100px; }
        .product-card { padding: 8px; }
        .product-name { font-size: 0.9rem; height: 35px; }
        .gia-ban { font-size: 1rem !important; }
        .stButton>button { font-size: 14px !important; }
        .nav-link { padding: 6px 8px !important; font-size: 0.8rem !important; }
    }
</style>
""", unsafe_allow_html=True)

# =============================
# 5. HEADER NGANG (LOGO, HOTLINE, ZALO)
# =============================
st.markdown(f"""
<div class="header-container">
    <div class="header-logo">
        <img src="{st.session_state.logo_url}" alt="Logo">
    </div>
    <div style="text-align: center;">
        <h2 style="margin: 0;">XỨ NẪU STORE</h2>
        <p style="margin: 5px 0 0 0;">Đặc sản Bình Định - Giao hàng toàn quốc</p>
    </div>
    <div style="text-align: right;">
        <div style="font-weight: bold;">📞 0932.642.376</div>
        <div style="font-weight: bold;">💬 Zalo: 0932.642.376</div>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# =============================
# 6. MENU NGANG (CÓ ĐIỀU KHIỂN TAB INDEX)
# =============================
tabs = ["🏠 Trang Chủ", "🛍️ Cửa Hàng", "🛒 Giỏ Hàng", "🔍 Tra Cứu Đơn Hàng", "📞 Thông Tin", "📊 Quản Trị"]
chon_menu = option_menu(
    menu_title=None,
    options=tabs,
    default_index=st.session_state.tab_index,
    orientation="horizontal",
    styles={
        "container": {
            "padding": "0!important",
            "background-color": "transparent",
            "border": "none",
            "box-shadow": "none",
            "max-width": "1000px",
            "margin": "0 auto 30px auto"
        },
        "icon": {"color": "#2e7d32", "font-size": "1.2rem"},
        "nav-link": {
            "font-size": "1rem",
            "text-align": "center",
            "margin": "0 5px",
            "padding": "10px 20px",
            "border-radius": "30px",
            "color": "#0066cc",
            "background-color": "transparent"
        },
        "nav-link-selected": {
            "background-color": "#2e7d32",
            "color": "white",
            "font-weight": "600"
        },
    }
)

# Cập nhật tab_index nếu người dùng chọn menu khác
if chon_menu != tabs[st.session_state.tab_index]:
    st.session_state.tab_index = tabs.index(chon_menu)
    # Nếu chuyển tab khác, tắt hiển thị đơn hàng (nếu đang hiển thị)
    st.session_state.hien_thi_don_hang = False
    st.rerun()

# =============================
# 7. HÀM LÀM SẠCH GIÁ, ĐỊNH DẠNG VÀ CHUẨN HÓA SĐT
# =============================
def clean_price(price):
    if pd.isna(price):
        return 0
    cleaned = re.sub(r'[^\d]', '', str(price))
    return int(cleaned) if cleaned else 0

def format_vnd(amount):
    """Định dạng số thành tiền Việt: dấu chấm + VNĐ"""
    return f"{amount:,}".replace(',', '.') + " VNĐ"

def chuan_hoa_sdt(sdt):
    """Chuẩn hóa số điện thoại: loại bỏ ký tự không phải số, nếu 9 số thì thêm 0, nếu 10 số thì giữ, else trả về None."""
    if pd.isna(sdt):
        return None
    so = re.sub(r'[^\d]', '', str(sdt))
    if len(so) == 9:
        return '0' + so
    elif len(so) == 10:
        return so
    else:
        return None

# =============================
# 8. HÀM HIỂN THỊ THÔNG TIN ĐƠN HÀNG (GIỐNG HÌNH) - ĐÃ SỬA LỖI
# =============================
def hien_thi_thong_tin_don_hang():
    don = st.session_state.don_hang_vua_dat

    # Tạo các dòng sản phẩm, mỗi dòng là một chuỗi HTML hoàn chỉnh, có escape tên sản phẩm
    rows_html = ""
    for sp in don['san_pham']:
        rows_html += (
            "<tr>"
            f"<td>{html.escape(sp['ten'])}</td>"
            f"<td>{sp['so_luong']}</td>"
            f"<td>{format_vnd(sp['don_gia'])}</td>"
            f"<td>{format_vnd(sp['thanh_tien'])}</td>"
            "</tr>"
        )

    # Toàn bộ nội dung HTML của card đơn hàng
    html_content = f"""
    <div class="don-hang-card">
        <div class="don-hang-header">
            <h2>🎉 CẢM ƠN BẠN. ĐƠN HÀNG CỦA BẠN ĐÃ ĐƯỢC NHẬN.</h2>
        </div>
        <div class="don-hang-info">
            <div class="info-row">
                <span class="info-label">MÃ ĐƠN HÀNG:</span>
                <span class="info-value">{html.escape(don['ma_don'])}</span>
            </div>
            <div class="info-row">
                <span class="info-label">NGÀY:</span>
                <span class="info-value">{html.escape(don['ngay'])}</span>
            </div>
            <div class="info-row">
                <span class="info-label">TỔNG CỘNG:</span>
                <span class="info-value">{format_vnd(don['tong_thanh_toan'])}</span>
            </div>
            <div class="info-row">
                <span class="info-label">PHƯƠNG THỨC THANH TOÁN:</span>
                <span class="info-value">{html.escape(don['phuong_thuc_tt'])}</span>
            </div>
        </div>
        <h3 style="color: #2e7d32;">Chi Tiết Đơn Hàng</h3>
        <table class="don-hang-table">
            <thead>
                <tr><th>Sản phẩm</th><th>Số lượng</th><th>Đơn giá</th><th>Thành tiền</th></tr>
            </thead>
            <tbody>
                {rows_html}
            </tbody>
            <tfoot>
                <tr class="total-row">
                    <td colspan="3" style="text-align:right;">Tổng tiền hàng:</td>
                    <td>{format_vnd(don['tong_hang'])}</td>
                </tr>
                <tr class="total-row">
                    <td colspan="3" style="text-align:right;">Phí ship:</td>
                    <td>{format_vnd(don['phi_ship'])}</td>
                </tr>
                <tr class="total-row">
                    <td colspan="3" style="text-align:right;">Tổng thanh toán:</td>
                    <td>{format_vnd(don['tong_thanh_toan'])}</td>
                </tr>
            </tfoot>
        </table>
    </div>
    """

    st.markdown(html_content, unsafe_allow_html=True)

    if st.button("⬅ Tiếp tục mua sắm"):
        st.session_state.hien_thi_don_hang = False
        st.session_state.tab_index = 0  # Về trang chủ
        st.rerun()

# =============================
# 9. HIỂN THỊ NỘI DUNG THEO MENU
# =============================

# ---- TRANG CHỦ ----
if chon_menu == "🏠 Trang Chủ":
    st.markdown("<h1 style='text-align:center;color:#2e7d32;'>🏯 Tinh Hoa Ẩm Thực Bình Định</h1>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    c1.success("🌿 **SẠCH & TƯƠI MỖI NGÀY**\n\n100% nguyên liệu tự nhiên – không chất bảo quản. Tươi mới như vừa thu hoạch, an tâm cho cả gia đình.")
    c2.success("🚚 **GIAO NHANH TOÀN QUỐC**\n\nĐóng gói kỹ lưỡng – vận chuyển hỏa tốc. Nhận hàng nhanh, vẫn giữ trọn độ tươi ngon.")
    c3.info("💝 **QUÀ TẶNG SANG TRỌNG**\n\nThiết kế tinh tế – sẵn sàng biếu tặng. Trao quà đẹp mắt, gửi trọn tâm ý.")

    st.markdown("<h3 style='color: #2e7d32;'>🔥 Đặc Sản Đang Bán Chạy</h3>", unsafe_allow_html=True)
    
    ws = ket_noi_sheet("SanPham")
    if ws:
        data = ws.get_all_records()
        if data:
            df_slider = pd.DataFrame(data)
            df_slider["Giá"] = df_slider["Giá"].apply(clean_price)
            
            slider_content = ""
            for _ in range(2):
                for _, row in df_slider.iterrows():
                    img = row["Hình ảnh"] if la_url_hop_le(row["Hình ảnh"]) else "https://via.placeholder.com/200"
                    gia_formatted = format_vnd(row["Giá"])
                    slider_content += f'<div class="slide-item"><img src="{img}"><p style="font-weight:600;margin:10px 0 0 0; color: #0066cc;">{row["Sản phẩm"]}</p><p class="gia-ban" style="color: #0066cc;">{gia_formatted}</p></div>'
            st.markdown(f'<div class="slider-container"><div class="slide-track">{slider_content}</div></div>', unsafe_allow_html=True)

# ---- CỬA HÀNG ----
elif chon_menu == "🛍️ Cửa Hàng":
    st.markdown("<h2 style='text-align:center; color:#2e7d32;'>🌟 Danh Sách Sản Phẩm</h2>", unsafe_allow_html=True)
    
    ws = ket_noi_sheet("SanPham")
    if ws:
        data = ws.get_all_records()
        if not data:
            st.info("Hiện chưa có sản phẩm nào trong kho.")
        else:
            df_goc = pd.DataFrame(data)
            df_goc["Giá"] = df_goc["Giá"].apply(clean_price)

            with st.container():
                col_search, col_filter = st.columns([2, 1])
                with col_search:
                    tu_khoa = st.text_input("🔍 Tìm kiếm sản phẩm...", placeholder="Nhập tên nem, chả, tré...")
                with col_filter:
                    if not df_goc.empty and df_goc["Giá"].max() > 0:
                        gia_max = int(df_goc["Giá"].max())
                    else:
                        gia_max = 1_000_000
                    khoang_gia = st.slider("💰 Lọc theo giá (VNĐ)", 0, gia_max, (0, gia_max), step=10000)

            df_loc = df_goc[
                (df_goc["Sản phẩm"].str.contains(tu_khoa, case=False, na=False)) &
                (df_goc["Giá"] >= khoang_gia[0]) &
                (df_goc["Giá"] <= khoang_gia[1])
            ]

            st.divider()

            if df_loc.empty:
                st.warning("Không tìm thấy sản phẩm phù hợp với yêu cầu của bạn.")
            else:
                cols = st.columns(3, gap="medium")
                for i, (_, row) in enumerate(df_loc.iterrows()):
                    with cols[i % 3]:
                        st.markdown('<div class="product-card">', unsafe_allow_html=True)
                        
                        img = row["Hình ảnh"] if la_url_hop_le(row["Hình ảnh"]) else "https://via.placeholder.com/200"
                        st.markdown(f'<img src="{img}" style="border-radius: 15px; object-fit: cover; height: 180px; width: 100%; margin-bottom:12px;">', unsafe_allow_html=True)
                        
                        st.markdown(f'<div class="product-name" style="font-weight:700; height:50px; overflow:hidden;">{row["Sản phẩm"]}</div>', unsafe_allow_html=True)
                        
                        # Hiển thị mô tả sản phẩm với chiều cao cố định 60px để đồng bộ giữa các card
                        mo_ta = row.get("Mô tả", "")
                        if mo_ta:
                            st.markdown(f'<div style="color:#666; font-size:0.9rem; height:60px; overflow-y:auto; margin-bottom:10px;">{mo_ta}</div>', unsafe_allow_html=True)
                        else:
                            st.markdown('<div style="height:60px; margin-bottom:10px;"></div>', unsafe_allow_html=True)
                        
                        gia_formatted = format_vnd(row["Giá"])
                        st.markdown(f'<div class="gia-ban" style="color:#2e7d32; font-size:1.3rem; font-weight:800; margin-bottom:5px;">{gia_formatted}</div>', unsafe_allow_html=True)
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

# ---- GIỎ HÀNG (ĐÃ SỬA LỖI SĐT + BỔ SUNG CÁC TRƯỜNG MỚI + ÉP KIỂU INT + ĐỌC ĐỊA CHỈ TỪ GITHUB) ----
elif chon_menu == "🛒 Giỏ Hàng":
    # --- ĐẢM BẢO CÁC BIẾN SESSION STATE ĐÃ TỒN TẠI ---
    if "dia_chi_tinh" not in st.session_state:
        st.session_state.dia_chi_tinh = "-- Chọn tỉnh/thành --"
    if "dia_chi_huyen" not in st.session_state:
        st.session_state.dia_chi_huyen = "-- Chọn quận/huyện --"
    if "dia_chi_xa" not in st.session_state:
        st.session_state.dia_chi_xa = "-- Chọn phường/xã --"
    if "dia_chi_huyen_tay" not in st.session_state:
        st.session_state.dia_chi_huyen_tay = ""
    if "dia_chi_xa_tay" not in st.session_state:
        st.session_state.dia_chi_xa_tay = ""

    # Nếu đang hiển thị đơn hàng vừa đặt, ưu tiên hiển thị thông tin
    if st.session_state.hien_thi_don_hang:
        hien_thi_thong_tin_don_hang()
    else:
        st.markdown("<h1 style='color: #2e7d32;'>🛒 Giỏ Hàng</h1>", unsafe_allow_html=True)
        
        if not st.session_state.gio_hang:
            st.markdown("<p style='color: #0066cc; font-size: 1.1rem;'>⚠️ Giỏ hàng trống.</p>", unsafe_allow_html=True)
        else:
            ws_sp = ket_noi_sheet("SanPham")
            df_sp = pd.DataFrame(ws_sp.get_all_records())
            df_sp["Giá"] = df_sp["Giá"].apply(clean_price)
            
            tong = 0
            ds_san_pham = []
            for id_sp, sl in st.session_state.gio_hang.items():
                sp_rows = df_sp[df_sp['ID'].astype(str) == id_sp]
                if not sp_rows.empty:
                    sp = sp_rows.iloc[0]
                    don_gia = int(sp['Giá'])
                    thanh_tien = don_gia * sl
                    tong += thanh_tien
                    ds_san_pham.append({
                        'id': id_sp,
                        'ten': sp['Sản phẩm'],
                        'so_luong': sl,
                        'don_gia': don_gia,
                        'thanh_tien': thanh_tien
                    })
                    st.markdown(f"<p style='color: #0066cc; font-size: 1.1rem;'>✅ {sp['Sản phẩm']} x{sl} - {format_vnd(thanh_tien)}</p>", unsafe_allow_html=True)
            
            # --- Đọc dữ liệu địa chỉ từ GitHub ---
            @st.cache_data
            def load_dia_chi():
                #url = "https://raw.githubusercontent.com/windy0209/dac-san-binh-dinh/main/dia_chi.json"
                try:
                    response = requests.get(url)
                    response.raise_for_status()
                    data = response.json()
                    return data
                except Exception as e:
                    st.warning(f"Không thể tải file từ GitHub: {e}. Sẽ dùng danh sách tỉnh dự phòng.")
                    return None

            dia_chi_data = load_dia_chi()
            
            if dia_chi_data:
                tinh_list = ["-- Chọn tỉnh/thành --"] + [item['name'] for item in dia_chi_data]
                quan_huyen_map = {}
                phuong_xa_map = {}
                for tinh in dia_chi_data:
                    tinh_name = tinh['name']
                    qh_list = ["-- Chọn quận/huyện --"] + [qh['name'] for qh in tinh.get('quan_huyen', [])]
                    quan_huyen_map[tinh_name] = qh_list
                    for qh in tinh.get('quan_huyen', []):
                        qh_name = qh['name']
                        px_list = ["-- Chọn phường/xã --"] + [px['name'] for px in qh.get('phuong_xa', [])]
                        phuong_xa_map[qh_name] = px_list
            else:
                tinh_list = [
                    "-- Chọn tỉnh/thành --",
                    "An Giang", "Bà Rịa - Vũng Tàu", "Bạc Liêu", "Bắc Giang", "Bắc Kạn", "Bắc Ninh",
                    "Bến Tre", "Bình Dương", "Bình Định", "Bình Phước", "Bình Thuận", "Cà Mau",
                    "Cao Bằng", "Cần Thơ", "Đà Nẵng", "Đắk Lắk", "Đắk Nông", "Điện Biên", "Đồng Nai",
                    "Đồng Tháp", "Gia Lai", "Hà Giang", "Hà Nam", "Hà Nội", "Hà Tĩnh", "Hải Dương",
                    "Hải Phòng", "Hậu Giang", "Hòa Bình", "Thành phố Hồ Chí Minh", "Hưng Yên",
                    "Khánh Hòa", "Kiên Giang", "Kon Tum", "Lai Châu", "Lạng Sơn", "Lào Cai", "Lâm Đồng",
                    "Long An", "Nam Định", "Nghệ An", "Ninh Bình", "Ninh Thuận", "Phú Thọ", "Phú Yên",
                    "Quảng Bình", "Quảng Nam", "Quảng Ngãi", "Quảng Ninh", "Quảng Trị", "Sóc Trăng",
                    "Sơn La", "Tây Ninh", "Thái Bình", "Thái Nguyên", "Thanh Hóa", "Thừa Thiên Huế",
                    "Tiền Giang", "Trà Vinh", "Tuyên Quang", "Vĩnh Long", "Vĩnh Phúc", "Yên Bái"
                ]
                quan_huyen_map = {}
                phuong_xa_map = {}

            # --- CÁC CALLBACK ---
            def cap_nhat_tinh():
                st.session_state.dia_chi_huyen = "-- Chọn quận/huyện --"
                st.session_state.dia_chi_xa = "-- Chọn phường/xã --"
                st.session_state.dia_chi_huyen_tay = ""
                st.session_state.dia_chi_xa_tay = ""
                st.rerun()

            def cap_nhat_huyen():
                st.session_state.dia_chi_xa = "-- Chọn phường/xã --"
                st.session_state.dia_chi_xa_tay = ""
                st.rerun()

            def cap_nhat_huyen_tay():
                st.session_state.dia_chi_xa = "-- Chọn phường/xã --"
                st.session_state.dia_chi_xa_tay = ""
                st.rerun()

            # --- PHẦN CHỌN ĐỊA CHỈ (NGOÀI FORM) ---
            st.subheader("🏠 Địa chỉ nhận hàng")
            
            col1, col2 = st.columns(2)
            with col1:
                tinh_index = tinh_list.index(st.session_state.dia_chi_tinh) if st.session_state.dia_chi_tinh in tinh_list else 0
                st.selectbox(
                    "Tỉnh/Thành phố *",
                    options=tinh_list,
                    index=tinh_index,
                    key="dia_chi_tinh",
                    on_change=cap_nhat_tinh
                )
            
            with col2:
                tinh_hien_tai = st.session_state.dia_chi_tinh
                if tinh_hien_tai != "-- Chọn tỉnh/thành --" and tinh_hien_tai in quan_huyen_map:
                    quan_options = quan_huyen_map[tinh_hien_tai]
                    huyen_index = quan_options.index(st.session_state.dia_chi_huyen) if st.session_state.dia_chi_huyen in quan_options else 0
                    st.selectbox(
                        "Quận/Huyện *",
                        options=quan_options,
                        index=huyen_index,
                        key="dia_chi_huyen",
                        on_change=cap_nhat_huyen
                    )
                    huyen_text = st.session_state.dia_chi_huyen if st.session_state.dia_chi_huyen != "-- Chọn quận/huyện --" else ""
                else:
                    st.selectbox("Quận/Huyện *", options=["-- Chọn quận/huyện --"], index=0, disabled=True)
                    huyen_tay = st.text_input(
                        "Nhập tên quận/huyện",
                        value=st.session_state.dia_chi_huyen_tay,
                        key="dia_chi_huyen_tay",
                        on_change=cap_nhat_huyen_tay
                    )
                    huyen_text = huyen_tay
            
            col3, col4 = st.columns(2)
            with col3:
                if huyen_text and huyen_text != "-- Chọn quận/huyện --" and huyen_text in phuong_xa_map:
                    xa_options = phuong_xa_map[huyen_text]
                    xa_index = xa_options.index(st.session_state.dia_chi_xa) if st.session_state.dia_chi_xa in xa_options else 0
                    st.selectbox(
                        "Phường/Xã *",
                        options=xa_options,
                        index=xa_index,
                        key="dia_chi_xa"
                    )
                    xa_text = st.session_state.dia_chi_xa if st.session_state.dia_chi_xa != "-- Chọn phường/xã --" else ""
                else:
                    st.selectbox("Phường/Xã *", options=["-- Chọn phường/xã --"], index=0, disabled=True)
                    xa_text = st.text_input(
                        "Nhập tên phường/xã",
                        value=st.session_state.dia_chi_xa_tay,
                        key="dia_chi_xa_tay"
                    )
            
            with col4:
                so_nha = st.text_input("Số nhà, tên đường *", placeholder="VD: 123 Nguyễn Huệ", key="so_nha")
            
            # Xác định địa chỉ hoàn chỉnh
            tinh = st.session_state.dia_chi_tinh
            if tinh in quan_huyen_map:
                huyen_thuc = st.session_state.dia_chi_huyen if st.session_state.dia_chi_huyen != "-- Chọn quận/huyện --" else ""
            else:
                huyen_thuc = st.session_state.dia_chi_huyen_tay

            if huyen_thuc in phuong_xa_map:
                xa_thuc = st.session_state.dia_chi_xa if st.session_state.dia_chi_xa != "-- Chọn phường/xã --" else ""
            else:
                xa_thuc = st.session_state.dia_chi_xa_tay

            dia_chi_day_du = f"{so_nha}, {xa_thuc}, {huyen_thuc}, {tinh}".strip(", ")
            
            # --- FORM THANH TOÁN ---
            with st.form("checkout_form"):
                st.subheader("📋 Thông tin giao hàng")
                ho_ten = st.text_input("Họ tên *", key="ho_ten_form")
                so_dt = st.text_input("Số điện thoại *", placeholder="VD: 0932642376", key="so_dt_form")
                
                st.subheader("🚚 Vận chuyển")
                khu_vuc = st.radio(
                    "Khu vực giao hàng",
                    ["Hồ Chí Minh (+30,000 VNĐ phí ship)", "Tỉnh/Thành khác (liên hệ)"],
                    index=0,
                    key="khu_vuc_form"
                )
                phi_ship = 30000 if "Hồ Chí Minh" in khu_vuc else 0
                
                khung_gio = st.selectbox(
                    "Khung giờ giao hàng (dự kiến)",
                    ["8:00 - 11:00", "11:00 - 13:00", "13:00 - 16:00", "16:00 - 19:00", "19:00 - 21:00"],
                    key="khung_gio_form"
                )
                
                st.subheader("💳 Thanh toán")
                phuong_thuc = st.radio(
                    "Phương thức thanh toán",
                    ["Tiền mặt khi nhận hàng", "Chuyển khoản ngân hàng", "Ví Momo", "Thẻ tín dụng"],
                    index=0,
                    key="phuong_thuc_form"
                )
                
                ghi_chu = st.text_area("Ghi chú (không bắt buộc)", placeholder="Ghi chú về đơn hàng...", key="ghi_chu_form")
                
                st.markdown("---")
                col1, col2, col3 = st.columns(3)
                col1.metric("Tổng tiền hàng", format_vnd(tong))
                col2.metric("Phí ship", format_vnd(phi_ship))
                col3.metric("Tổng thanh toán", format_vnd(tong + phi_ship))
                
                submitted = st.form_submit_button("XÁC NHẬN ĐẶT HÀNG")
                
                if submitted:
                    if not ho_ten or not so_dt or not dia_chi_day_du or not so_nha:
                        st.error("Vui lòng điền đầy đủ họ tên, SĐT và địa chỉ (chọn tỉnh, nhập huyện/xã và số nhà).")
                    else:
                        sdt_chuan = chuan_hoa_sdt(so_dt)
                        if sdt_chuan is None:
                            st.error("Số điện thoại không hợp lệ! Vui lòng nhập 10 số (có thể có số 0 ở đầu).")
                        else:
                            # Lấy thời gian Việt Nam
                            tz_vn = pytz.timezone('Asia/Ho_Chi_Minh')
                            now_vn = datetime.now(tz_vn)
                            ma_don = "DH" + now_vn.strftime("%y%m%d%H%M%S") + str(random.randint(10, 99))
                            ngay_dat = now_vn.strftime("%d/%m/%Y %H:%M")
                            
                            san_pham_str = ", ".join([f"{sp['ten']} x{sp['so_luong']}" for sp in ds_san_pham])
                            tong_sl = sum(sp['so_luong'] for sp in ds_san_pham)
                            
                            ws_don = ket_noi_sheet("DonHang")
                            ws_don.append_row([
                                ma_don,
                                ngay_dat,
                                ho_ten,
                                sdt_chuan,
                                dia_chi_day_du,
                                san_pham_str,
                                int(tong_sl),
                                int(tong),
                                int(phi_ship),
                                int(tong + phi_ship),
                                phuong_thuc,
                                khung_gio,
                                ghi_chu,
                                "Mới"
                            ])
                            
                            for sp in ds_san_pham:
                                cell = ws_sp.find(str(sp['ten']))
                                current_stock = int(ws_sp.cell(cell.row, 6).value)
                                ws_sp.update_cell(cell.row, 6, current_stock - sp['so_luong'])
                            
                            st.session_state.don_hang_vua_dat = {
                                'ma_don': ma_don,
                                'ngay': now_vn.strftime("%d/%m/%Y"),
                                'tong_hang': int(tong),
                                'phi_ship': int(phi_ship),
                                'tong_thanh_toan': int(tong + phi_ship),
                                'phuong_thuc_tt': phuong_thuc,
                                'san_pham': ds_san_pham
                            }
                            st.session_state.hien_thi_don_hang = True
                            st.session_state.gio_hang = {}
                            st.rerun()
# ---- TRA CỨU ĐƠN HÀNG ----
elif chon_menu == "🔍 Tra Cứu Đơn Hàng":
    st.markdown("<h1 style='color: #2e7d32; text-align:center;'>🔍 Tra cứu đơn hàng</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #0066cc; text-align:center;'>Nhập số điện thoại để xem lịch sử đơn hàng của bạn.</p>", unsafe_allow_html=True)
    
    with st.form("tra_cuu_form"):
        so_dien_thoai = st.text_input("📱 Số điện thoại", placeholder="VD: 0932642376")
        tra_cuu_btn = st.form_submit_button("TRA CỨU")
    
    if tra_cuu_btn and so_dien_thoai:
        sdt_chuan = chuan_hoa_sdt(so_dien_thoai)
        if sdt_chuan is None:
            st.error("Số điện thoại không hợp lệ! Vui lòng nhập 10 số (có thể có số 0 ở đầu).")
        else:
            ws_don = ket_noi_sheet("DonHang")
            if ws_don:
                data = ws_don.get_all_records()
                if data:
                    df = pd.DataFrame(data)
                    
                    # Tìm cột số điện thoại
                    col_sdt = None
                    for col in df.columns:
                        if 'sđt' in col.lower() or 'điện thoại' in col.lower() or 'sdt' in col.lower():
                            col_sdt = col
                            break
                    if col_sdt is None:
                        st.error("❌ Không tìm thấy cột số điện thoại trong dữ liệu.")
                    else:
                        # Chuẩn hóa cột SĐT trong dataframe
                        df[col_sdt] = df[col_sdt].apply(chuan_hoa_sdt)
                        # Lọc theo số đã chuẩn hóa
                        df_loc = df[df[col_sdt] == sdt_chuan]
                        
                        if not df_loc.empty:
                            st.success(f"✅ Tìm thấy {len(df_loc)} đơn hàng.")
                            
                            # Sắp xếp theo thời gian giảm dần
                            col_time = next((c for c in df_loc.columns if 'thời gian' in c.lower() or 'ngày' in c.lower()), None)
                            if col_time:
                                df_loc = df_loc.sort_values(col_time, ascending=False)
                            
                            # Chọn các cột hiển thị (có thể thêm nhiều cột mới)
                            cols_hien_thi = ['Mã đơn', 'Thời gian', 'Họ tên', 'Sản phẩm', 'Tổng thanh toán', 'Phương thức thanh toán', 'Trạng thái']
                            cols_ton_tai = [c for c in cols_hien_thi if c in df_loc.columns]
                            
                            if not cols_ton_tai:
                                st.warning("Không có cột nào phù hợp để hiển thị.")
                            else:
                                df_hien_thi = df_loc[cols_ton_tai].copy()
                                # Định dạng tổng tiền nếu có
                                if 'Tổng thanh toán' in df_hien_thi.columns:
                                    df_hien_thi['Tổng thanh toán'] = df_hien_thi['Tổng thanh toán'].apply(lambda x: format_vnd(clean_price(x)))
                                st.dataframe(df_hien_thi, use_container_width=True, hide_index=True)
                        else:
                            st.warning("❌ Không tìm thấy đơn hàng nào với số điện thoại này.")
                else:
                    st.info("ℹ️ Chưa có đơn hàng nào trong hệ thống.")
            else:
                st.error("🔌 Không thể kết nối đến dữ liệu đơn hàng.")
    elif tra_cuu_btn:
        st.warning("⚠️ Vui lòng nhập số điện thoại.")

# ---- THÔNG TIN ----
elif chon_menu == "📞 Thông Tin":
    st.markdown("<h1 style='text-align:center;color:#2e7d32;'>📍 Thông Tin Cửa Hàng</h1>", unsafe_allow_html=True)
    col_info, col_map = st.columns([1, 1.2], gap="large")
    with col_info:
        st.markdown(f"""
        <div style="background:white; padding:25px; border-radius:20px; box-shadow:0 10px 25px rgba(0,0,0,0.05);">
            <h3 style="color: #2e7d32; margin-top: 0;">🏡 Cửa Hàng Xứ Nẫu</h3>
            <p style="color: #0066cc;"><b>📍 Địa chỉ:</b> 96 Ngô Đức Đệ, Phường Bình Định, TX. An Nhơn, Bình Định</p>
            <p style="color: #0066cc;"><b>📞 Hotline:</b> 0932.642.376</p>
            <p style="color: #0066cc;"><b>📧 Email:</b> miendatvo86@gmail.com</p>
            <hr>
            <h4 style="color: #2e7d32;">⏰ Giờ Hoạt Động</h4>
            <p style="color: #0066cc;">07:30 - 21:00 (Hàng ngày)</p>
        </div>
        """, unsafe_allow_html=True)
    with col_map:
        toa_do = pd.DataFrame({'lat': [13.8930853], 'lon': [109.1002733]})
        st.map(toa_do, zoom=14)

# ---- QUẢN TRỊ ----
elif chon_menu == "📊 Quản Trị":
    if not st.session_state.da_dang_nhap:
        col_l, col_m, col_r = st.columns([1,1.5,1])
        with col_m:
            st.markdown("<h3 style='color: #0066cc;'>🔐 Đăng nhập quyền quản trị</h3>", unsafe_allow_html=True)
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
            df_sp_display = df_sp.copy()
            if "Giá" in df_sp_display.columns:
                df_sp_display["Giá"] = df_sp_display["Giá"].apply(clean_price)
            df_edit = st.data_editor(df_sp_display, num_rows="dynamic", use_container_width=True)
            if st.button("LƯU KHO"):
                ws_sp.clear()
                ws_sp.update([df_edit.columns.values.tolist()] + df_edit.values.tolist())
                st.success("Đã cập nhật kho!")
        
        with t2:
            df_don_old = pd.DataFrame(ws_don.get_all_records())
            
            # Đảm bảo cột trạng thái tồn tại
            if 'Trạng thái' not in df_don_old.columns:
                df_don_old['Trạng thái'] = 'Mới'
            
            # Cấu hình cột selectbox cho trạng thái
            column_config = {
                "Trạng thái": st.column_config.SelectboxColumn(
                    "Trạng thái",
                    options=["Mới", "Nhận đơn", "Giao xong", "Hủy"],
                    required=True
                )
            }
            
            df_don_new = st.data_editor(
                df_don_old,
                column_config=column_config,
                use_container_width=True,
                num_rows="dynamic",
                key="don_hang_editor"
            )
            
            if st.button("CẬP NHẬT ĐƠN & HOÀN KHO"):
                ws_sp = ket_noi_sheet("SanPham")
                
                for i in range(len(df_don_old)):
                    trang_thai_cu = str(df_don_old.iloc[i]['Trạng thái'])
                    trang_thai_moi = str(df_don_new.iloc[i]['Trạng thái'])
                    
                    if trang_thai_cu != "Hủy" and trang_thai_moi == "Hủy":
                        chuoi_sp = str(df_don_new.iloc[i]['Sản phẩm'])
                        danh_sach_tach = chuoi_sp.split(", ")
                        
                        for item in danh_sach_tach:
                            match = re.search(r"(.+)\s+x(\d+)", item)
                            if match:
                                ten_sp = match.group(1).strip()
                                so_luong_hoan = int(match.group(2))
                                
                                try:
                                    cell = ws_sp.find(ten_sp)
                                    ton_hien_tai = int(ws_sp.cell(cell.row, 6).value)
                                    ws_sp.update_cell(cell.row, 6, ton_hien_tai + so_luong_hoan)
                                    st.info(f"🔄 Đã hoàn {so_luong_hoan} đơn vị '{ten_sp}' vào kho.")
                                except Exception as e:
                                    st.error(f"Lỗi khi hoàn kho cho {ten_sp}: {e}")
                
                ws_don.clear()
                ws_don.update([df_don_new.columns.values.tolist()] + df_don_new.values.tolist())
                st.success("✅ Đã cập nhật trạng thái đơn hàng và kho hàng!")
                time.sleep(1)
                st.rerun()
        
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

# =============================
# 10. FLOATING BUTTONS (GỌI & ZALO)
# =============================
st.markdown("""
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css">
<style>
.floating-buttons {
    position: fixed;
    bottom: 30px;
    right: 30px;
    z-index: 9999;
    display: flex;
    flex-direction: column;
    gap: 15px;
}
.floating-buttons a {
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 12px 20px;
    border-radius: 50px;
    background-color: #2e7d32;
    color: white;
    font-size: 18px;
    font-weight: 600;
    box-shadow: 0 6px 15px rgba(0,0,0,0.3);
    transition: all 0.3s ease;
    text-decoration: none;
    border: 2px solid white;
    gap: 10px;
    min-width: 160px;
}
.floating-buttons a i {
    font-size: 24px;
}
.floating-buttons a:hover {
    transform: scale(1.05);
    background-color: #f39c12;
}
.zalo-logo {
    width: 28px;
    height: 28px;
    object-fit: contain;
}
@media (max-width: 768px) {
    .floating-buttons {
        bottom: 20px;
        right: 20px;
    }
    .floating-buttons a {
        padding: 8px 16px;
        font-size: 16px;
        min-width: 140px;
    }
    .floating-buttons a i {
        font-size: 20px;
    }
}
</style>
<div class="floating-buttons">
    <a href="tel:0932642376" class="phone">
        <i class="fas fa-phone-alt"></i> 0932.642.376
    </a>
    <a href="https://zalo.me/0932642376" class="zalo" target="_blank">
        <i class="fas fa-comment-dots"></i> Chat Zalo
    </a>
</div>
""", unsafe_allow_html=True)














