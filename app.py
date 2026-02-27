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
# 3. CSS CAO CẤP (FIX LỖI NỀN ĐEN TRÊN ĐIỆN THOẠI)
# =============================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');

    /* Ẩn Toolbar Streamlit */
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display:none;}
    
    /* Ép buộc nền trắng và chữ đen toàn app cho Mobile Dark Mode */
    .stApp, .stAppViewMainContainer, .stAppViewBlockContainer {
        background-color: #FFFFFF !important;
        color: #1A1A1A !important;
    }

    /* Ép nền trắng cho các khung info, success, warning */
    div[data-testid="stNotification"], div.stAlert {
        background-color: #F8F9F9 !important;
        color: #1A1A1A !important;
        border: 1px solid #E0E0E0 !important;
    }

    /* FIX khung nền cho input, form và các khối văn bản */
    div[data-testid="stForm"], .stTextInput input, .stTextArea textarea, .stNumberInput input {
        background-color: #FFFFFF !important;
        color: #1A1A1A !important;
        border: 1px solid #DEDEDE !important;
    }

    html, body, [class*="st-"] {
        font-family: 'Inter', sans-serif;
        color: #1A1A1A !important;
    }

    .block-container { padding-top: 1rem; }

    /* Tiêu đề sắc nét */
    h1, h2, h3, h4, p, span, label {
        color: #1A1A1A !important;
    }
    
    h1, h2, h3 {
        font-weight: 800 !important;
        color: #1D4330 !important;
    }

    /* Thẻ sản phẩm */
    .product-card {
        background: #FFFFFF !important;
        border-radius: 16px;
        padding: 15px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        border: 1px solid #EEEEEE;
        text-align: center;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        margin-bottom: 10px;
    }

    .product-name {
        font-weight: 700; 
        font-size: 1rem;
        margin: 8px 0;
        line-height: 1.3;
        min-height: 45px;
        color: #1A1A1A !important;
    }

    .gia-ban {
        color: #D32F2F !important;
        font-size: 1.2rem;
        font-weight: 800;
    }

    .stButton>button {
        background-color: #2E7D32 !important;
        color: #FFFFFF !important;
        border-radius: 10px !important;
        font-weight: 700 !important;
        width: 100%;
        border: none !important;
    }
</style>
""", unsafe_allow_html=True)

# =============================
# 4. HEADER & MENU NGANG
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
            "container": {"padding": "0!important", "background-color": "white"},
            "nav-link": {"font-size": "13px", "font-weight": "700", "text-transform": "uppercase", "color": "#1A1A1A"},
            "nav-link-selected": {"background-color": "#2E7D32", "color": "white"},
        }
    )

st.markdown(f'<div style="text-align: right; color: #2E7D32; font-weight: 800; padding-right:10px;">📞 HOTLINE: 0932.642.376</div>', unsafe_allow_html=True)

# =============================
# 5. TRANG CHỦ
# =============================
if chon_menu == "🏠 Trang Chủ":
    st.markdown("<div style='text-align:center; padding: 20px 0;'><h1>TINH HOA ẨM THỰC BÌNH ĐỊNH</h1><p>Giao hàng tận nơi - Hương vị nguyên bản vùng đất võ.</p></div>", unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns(3)
    with c1: st.info("🌿 **Nguyên Bản**\nCông thức gia truyền.")
    with c2: st.success("🚚 **Tận Tâm**\nĐóng gói kỹ lưỡng.")
    with c3: st.warning("💝 **Uy Tín**\nChất lượng hàng đầu.")

    st.markdown("<br><h2 style='text-align:center;'>✨ SẢN PHẨM NỔI BẬT ✨</h2>", unsafe_allow_html=True)
    ws = ket_noi_sheet("SanPham")
    if ws:
        data = ws.get_all_records()
        if data:
            slider_content = ""
            for _ in range(2):
                for row in data:
                    img = row["Hình ảnh"] if la_url_hop_le(row["Hình ảnh"]) else "https://via.placeholder.com/200"
                    slider_content += f'<div class="slide-item"><img src="{img}"><p style="font-weight:800; color:#1D4330;">{row["Sản phẩm"]}</p><p style="color:#D32F2F;">{row["Giá"]:,}đ</p></div>'
            st.markdown(f'<div class="slider-container"><div class="slide-track">{slider_content}</div></div>', unsafe_allow_html=True)

# =============================
# 6. CỬA HÀNG
# =============================
elif chon_menu == "🛍️ Cửa Hàng":
    st.markdown("<h2 style='text-align:center;'>💎 THỰC ĐƠN XỨ NẪU</h2>", unsafe_allow_html=True)
    ws = ket_noi_sheet("SanPham")
    if ws:
        data = ws.get_all_records()
        if data:
            df_goc = pd.DataFrame(data)
            col_search, col_filter = st.columns([1, 1])
            with col_search: tu_khoa = st.text_input("🔍 Tìm sản phẩm...", placeholder="Tên sản phẩm...")
            with col_filter:
                gia_max = int(df_goc["Giá"].max())
                khoang_gia = st.slider("💰 Mức giá", 0, gia_max, (0, gia_max))

            df_loc = df_goc[(df_goc["Sản phẩm"].str.contains(tu_khoa, case=False, na=False)) & (df_goc["Giá"] >= khoang_gia[0]) & (df_goc["Giá"] <= khoang_gia[1])]
            st.divider()

            if df_loc.empty: st.warning("Không tìm thấy sản phẩm.")
            else:
                cols = st.columns(2) 
                for i, (_, row) in enumerate(df_loc.iterrows()):
                    with cols[i % 2]:
                        st.markdown(f'<div class="product-card"><img src="{row["Hình ảnh"] if la_url_hop_le(row["Hình ảnh"]) else "https://via.placeholder.com/200"}" style="height: 120px; object-fit: cover; border-radius: 10px;"><div class="product-name">{row["Sản phẩm"]}</div><div class="gia-ban">{row["Giá"]:,}đ</div><p style="font-size:0.8rem;">Sẵn có: {row["Tồn kho"]}</p></div>', unsafe_allow_html=True)
                        if int(row["Tồn kho"]) > 0:
                            sl = st.number_input("SL", 1, int(row["Tồn kho"]), key=f"sl_{row['ID']}", label_visibility="collapsed")
                            if st.button("MUA 🛒", key=f"btn_{row['ID']}"):
                                st.session_state.gio_hang[str(row["ID"])] = st.session_state.gio_hang.get(str(row["ID"]), 0) + sl
                                st.toast(f"Đã thêm {row['Sản phẩm']}!", icon="✅")
                        else: st.button("HẾT", disabled=True, key=f"out_{row['ID']}")

# =============================
# 7. GIỎ HÀNG (CẬP NHẬT MÚI GIỜ VIỆT NAM)
# =============================
elif chon_menu == "🛒 Giỏ Hàng":
    st.markdown("<h2>🛒 GIỎ HÀNG</h2>", unsafe_allow_html=True)
    if not st.session_state.gio_hang: st.info("Giỏ hàng trống!")
    else:
        ws_sp = ket_noi_sheet("SanPham")
        df_sp = pd.DataFrame(ws_sp.get_all_records())
        tong, ds_order = 0, []
        for id_sp, sl in st.session_state.gio_hang.items():
            sp_rows = df_sp[df_sp['ID'].astype(str) == id_sp]
            if not sp_rows.empty:
                sp = sp_rows.iloc[0]; thanh_tien = sp['Giá'] * sl
                tong += thanh_tien; ds_order.append(f"{sp['Sản phẩm']} x{sl}")
                st.markdown(f"🔸 **{sp['Sản phẩm']}** (x{sl}) — {thanh_tien:,} VNĐ")
        st.markdown(f"### Tổng: <span style='color:#D32F2F;'>{tong:,} VNĐ</span>", unsafe_allow_html=True)
        
        with st.form("checkout_form"):
            t, s, d = st.text_input("Họ tên"), st.text_input("SĐT"), st.text_area("Địa chỉ")
            if st.form_submit_button("XÁC NHẬN ĐẶT HÀNG"):
                if t and s and d:
                    # Lấy thời gian chuẩn Việt Nam (UTC+7)
                    gio_vn = datetime.now(timezone(timedelta(hours=7))).strftime("%d/%m/%Y %H:%M")
                    ws_don = ket_noi_sheet("DonHang")
                    ws_don.append_row([gio_vn, t, s, d, ", ".join(ds_order), sum(st.session_state.gio_hang.values()), f"{tong:,} VNĐ", "Mới"])
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
        col_l, col_m, col_r = st.columns([0.1, 0.8, 0.1])
        with col_m:
            tk, mk = st.text_input("Admin"), st.text_input("Pass", type="password")
            if st.button("ĐĂNG NHẬP"):
                if tk == "admin" and mk == "binhdinh0209": st.session_state.da_dang_nhap = True; st.rerun()
    else:
        st.button("Thoát", on_click=lambda: st.session_state.update({"da_dang_nhap": False}))
        t1, t2, t3 = st.tabs(["📦 KHO", "📝 ĐƠN", "⚙️ CÀI ĐẶT"])
        ws_sp, ws_don = ket_noi_sheet("SanPham"), ket_noi_sheet("DonHang")
        with t1:
            df_sp = pd.DataFrame(ws_sp.get_all_records())
            df_edit = st.data_editor(df_sp, num_rows="dynamic", use_container_width=True)
            if st.button("LƯU KHO"):
                ws_sp.clear(); ws_sp.update([df_edit.columns.values.tolist()] + df_edit.values.tolist()); st.success("Đã lưu!")
        with t2:
            df_don_old = pd.DataFrame(ws_don.get_all_records()); df_don_new = st.data_editor(df_don_old, use_container_width=True)
            if st.button("CẬP NHẬT ĐƠN"):
                for i in range(len(df_don_old)):
                    if str(df_don_old.iloc[i]['Trạng thái']) != "Hủy" and str(df_don_new.iloc[i]['Trạng thái']) == "Hủy":
                        for item in str(df_don_new.iloc[i]['Sản phẩm']).split(", "):
                            match = re.search(r"(.+)\s+x(\d+)", item)
                            if match:
                                cell = ws_sp.find(match.group(1).strip())
                                ws_sp.update_cell(cell.row, 6, int(ws_sp.cell(cell.row, 6).value) + int(match.group(2)))
                ws_don.clear(); ws_don.update([df_don_new.columns.values.tolist()] + df_don_new.values.tolist()); st.success("Đã xong!"); st.rerun()
        with t3:
            ws_ch = ket_noi_sheet("CauHinh")
            moi = st.text_input("Logo URL:", value=st.session_state.logo_url)
            if st.button("LƯU"):
                ws_ch.update_cell(ws_ch.find("Logo").row, 2, moi); st.session_state.logo_url = moi; st.rerun()

elif chon_menu == "📞 Thông Tin":
    st.markdown("<h2 style='text-align:center;'>📍 LIÊN HỆ</h2>", unsafe_allow_html=True)
    st.markdown('<div style="background:#F9F9F9; padding:20px; border-radius:15px; text-align:center; border:1px solid #DDD;"><b>🏡 XỨ NẪU STORE</b><p>📍 96 Ngô Đức Đệ, Bình Định</p><p>📞 0932.642.376</p><img src="https://raw.githubusercontent.com/windy0209/dac-san-binh-dinh/main/qrcode.png" width="150"></div>', unsafe_allow_html=True)
    st.map(pd.DataFrame({'lat': [13.8930853], 'lon': [109.1002733]}), zoom=14)
