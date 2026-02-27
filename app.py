import streamlit as st
from streamlit_option_menu import option_menu
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import pandas as pd
import time
import re

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
# 4. CSS TÙY CHỈNH GIAO DIỆN (TỐI ƯU MOBILE)
# =============================
st.markdown("""
<style>
    .stApp { background-color: #f8fbf8; }
    
    /* Header ngang */
    .header-container {
        display: flex;
        align-items: center;
        justify-content: space-between;
        background: white;
        padding: 10px 30px;
        border-radius: 60px;
        margin: 20px auto 10px auto;
        max-width: 1300px;
        box-shadow: 0 5px 15px rgba(0,0,0,0.05);
        border: 1px solid #e0e0e0;
    }
    .header-logo img { height: 60px; width: auto; }
    .header-info {
        display: flex;
        gap: 30px;
        font-size: 1rem;
    }
    .header-info div {
        display: flex;
        align-items: center;
        gap: 5px;
    }
    .hotline { color: #d32f2f; font-weight: bold; }
    .zalo { color: #0068ff; font-weight: bold; }
    .qr-code img { height: 50px; width: auto; border-radius: 8px; }
    
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

    /* ===== RESPONSIVE CHO MOBILE ===== */
    @media only screen and (max-width: 768px) {
        /* Tăng kích thước chữ tổng thể */
        body, p, div, span, .stMarkdown, .stText, .stButton>button {
            font-size: 16px !important;
        }
        h1 { font-size: 28px !important; }
        h2 { font-size: 24px !important; }
        h3 { font-size: 20px !important; }
        
        /* Header xếp dọc */
        .header-container {
            flex-direction: column;
            padding: 15px;
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
        
        /* MENU NGANG: cho phép cuộn ngang nếu quá dài */
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
        
        /* Slider: giảm kích thước ảnh */
        .slide-item { width: 160px; margin: 0 10px; }
        .slide-item img { width: 150px; height: 120px; }
        
        /* Sản phẩm: 2 cột */
        .row-widget.stHorizontal > div {
            min-width: 48%;
        }
        .product-card { padding: 10px; }
        .product-name { font-size: 1rem; height: 40px; }
        .gia-ban { font-size: 1.1rem !important; }
        
        /* Điều chỉnh cột thông tin */
        .stColumns { gap: 10px; }
    }

    /* Màn hình rất nhỏ (dưới 480px) */
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
# 5. HEADER NGANG (LOGO, HOTLINE, ZALO, QR CODE)
# =============================
col1, col2, col3 = st.columns([1, 2, 1])
with col1:
    st.image(st.session_state.logo_url, width=120)
with col2:
    st.markdown("<h2 style='text-align: center; color: #2e7d32; margin: 0;'>XỨ NẪU STORE</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #666;'>Đặc sản Bình Định - Giao hàng toàn quốc</p>", unsafe_allow_html=True)
with col3:
    st.markdown("""
    <div style='text-align: right;'>
        <div style='color: #d32f2f; font-weight: bold;'>📞 0932.642.376</div>
        <div style='color: #0068ff; font-weight: bold;'>💬 Zalo: 0932.642.376</div>
        <img src='https://raw.githubusercontent.com/windy0209/dac-san-binh-dinh/main/qrcode.png' width='60' style='border-radius: 8px; margin-top: 5px;'>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")  # Đường kẻ phân cách

# =============================
# 6. MENU NGANG (ĐẶT Ở GIỮA) - LOẠI BỎ NỀN TRẮNG
# =============================
chon_menu = option_menu(
    menu_title=None,
    options=["🏠 Trang Chủ", "🛍️ Cửa Hàng", "🛒 Giỏ Hàng", "📞 Thông Tin", "📊 Quản Trị"],
    icons=["house", "shop", "cart", "telephone", "gear"],
    default_index=0,
    orientation="horizontal",
    styles={
        "container": {
            "padding": "0!important",
            "background-color": "transparent",
            "border": "none",
            "box-shadow": "none",
            "max-width": "800px",
            "margin": "0 auto 30px auto"
        },
        "icon": {"color": "#2e7d32", "font-size": "1.2rem"},
        "nav-link": {
            "font-size": "1rem",
            "text-align": "center",
            "margin": "0 5px",
            "padding": "10px 20px",
            "border-radius": "30px",
            "color": "#333",
            "background-color": "transparent"
        },
        "nav-link-selected": {
            "background-color": "#2e7d32",
            "color": "white",
            "font-weight": "600"
        },
    }
)

# =============================
# 7. HIỂN THỊ NỘI DUNG THEO MENU ĐÃ CHỌN
# =============================

# ---- TRANG CHỦ ----
if chon_menu == "🏠 Trang Chủ":
    st.markdown("<h1 style='text-align:center;color:#2e7d32;'>🏯 Tinh Hoa Ẩm Thực Bình Định</h1>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    c1.success("🌿 **Sạch & Tươi**\n\n100% Tự nhiên.")
    c2.success("🚚 **Giao Nhanh**\n\nToàn quốc.")  # Đổi từ warning sang success (xanh lá)
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

            # Bộ lọc tìm kiếm và giá
            with st.container():
                col_search, col_filter = st.columns([2, 1])
                with col_search:
                    tu_khoa = st.text_input("🔍 Tìm kiếm sản phẩm...", placeholder="Nhập tên nem, chả, tré...")
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
                st.warning("Không tìm thấy sản phẩm phù hợp với yêu cầu của bạn.")
            else:
                cols = st.columns(3, gap="medium")
                for i, (_, row) in enumerate(df_loc.iterrows()):
                    with cols[i % 3]:
                        st.markdown('<div class="product-card">', unsafe_allow_html=True)
                        
                        img = row["Hình ảnh"] if la_url_hop_le(row["Hình ảnh"]) else "https://via.placeholder.com/200"
                        st.markdown(f'<img src="{img}" style="border-radius: 15px; object-fit: cover; height: 180px; width: 100%; margin-bottom:12px;">', unsafe_allow_html=True)
                        
                        st.markdown(f'<div class="product-name" style="font-weight:700; height:50px; overflow:hidden;">{row["Sản phẩm"]}</div>', unsafe_allow_html=True)
                        # Đổi màu giá từ cam sang xanh lá
                        st.markdown(f'<div class="gia-ban" style="color:#2e7d32; font-size:1.3rem; font-weight:800; margin-bottom:5px;">{row["Giá"]:,} VNĐ</div>', unsafe_allow_html=True)
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

# ---- GIỎ HÀNG (ĐÃ CHỈNH MÀU) ----
elif chon_menu == "🛒 Giỏ Hàng":
    # Tiêu đề chính màu xanh lá
    st.markdown("<h1 style='color: #2e7d32;'>🛒 Giỏ Hàng</h1>", unsafe_allow_html=True)
    
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
                # Dòng sản phẩm màu xanh dương
                st.markdown(f"<p style='color: #0066cc; font-size: 1.1rem;'>✅ {sp['Sản phẩm']} x{sl} - {thanh_tien:,} VNĐ</p>", unsafe_allow_html=True)
        
        # Tổng tiền màu xanh lá
        st.markdown(f"<h3 style='color: #2e7d32;'>Tổng tiền: {tong:,} VNĐ</h3>", unsafe_allow_html=True)
        
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

# ---- QUẢN TRỊ ----
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
            ws_sp = ket_noi_sheet("SanPham")
            df_sp = pd.DataFrame(ws_sp.get_all_records())
            
            df_don_new = st.data_editor(df_don_old, use_container_width=True)
            
            if st.button("CẬP NHẬT ĐƠN & HOÀN KHO"):
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
                st.success("✅ Đã cập nhật trạng thái đơn hàng và kho hàng!"); time.sleep(1); st.rerun()
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
