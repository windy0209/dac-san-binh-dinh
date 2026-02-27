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
    
    /* Cấu hình phông chữ và nền */
    html, body, [class*="st-"] {
        font-family: 'Inter', sans-serif;
        color: #1A1A1A;
    }

    .stApp { 
        background-color: #FFFFFF; 
    }

    /* FIX LỖI NỀN ĐEN KHUNG SỐ LƯỢNG TRÊN ĐIỆN THOẠI */
    div[data-testid="stNumberInput"] input {
        background-color: #FFFFFF !important;
        color: #1A1A1A !important;
        -webkit-text-fill-color: #1A1A1A !important;
        opacity: 1 !important;
        border: 1px solid #E0E0E0 !important;
    }

    .block-container { padding-top: 1rem; }

    /* Tiêu đề */
    h1, h2, h3 {
        font-weight: 800 !important;
        color: #1D4330 !important;
        letter-spacing: -0.5px;
    }

    /* Thẻ sản phẩm */
    .product-card {
        background: #FFFFFF;
        border-radius: 16px;
        padding: 20px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.06);
        border: 1px solid #F0F0F0;
        text-align: center;
        transition: transform 0.3s ease;
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        margin-bottom: 10px;
    }
    
    .product-card:hover {
        transform: translateY(-5px);
        border-color: #2E7D32;
    }

    .product-name {
        font-weight: 700; 
        font-size: 1.1rem;
        color: #1A1A1A;
        margin: 10px 0;
        line-height: 1.4;
        min-height: 50px;
        display: block;
    }

    .gia-ban {
        color: #D32F2F;
        font-size: 1.3rem;
        font-weight: 800;
        margin-bottom: 8px;
    }

    /* Nút bấm lớn hơn cho điện thoại */
    .stButton>button {
        background-color: #2E7D32 !important;
        color: white !important;
        border-radius: 10px !important;
        font-weight: 700 !important;
        padding: 0.7rem 1rem !important;
        border: none !important;
        width: 100%;
    }
    .stButton>button:hover {
        background-color: #F39C12 !important;
    }

    /* Slider */
    .slider-container { width: 100%; overflow: hidden; background: #F9F9F9; padding: 25px 0; border-radius: 20px; }
    .slide-track { display: flex; width: max-content; animation: scroll 35s linear infinite; }
    .slide-item { width: 220px; margin: 0 10px; text-align: center; }
    .slide-item img { width: 200px; height: 160px; object-fit: cover; border-radius: 12px; }
    @keyframes scroll { 0% { transform: translateX(0); } 100% { transform: translateX(-50%); } }
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
            "container": {"padding": "0!important", "background-color": "transparent"},
            "nav-link": {"font-size": "14px", "font-weight": "700", "text-transform": "uppercase", "padding": "10px 5px"},
            "nav-link-selected": {"background-color": "#2E7D32"},
        }
    )

st.markdown(f"""
    <div style="text-align: right; padding-right: 15px; margin-top: -10px; margin-bottom: 15px;">
        <span style="color: #2E7D32; font-weight: 800; font-size: 1rem;">📞 HOTLINE: 0932.642.376</span>
    </div>
""", unsafe_allow_html=True)

# =============================
# 5. TRANG CHỦ
# =============================
if chon_menu == "🏠 Trang Chủ":
    st.markdown("""
        <div style='text-align:center; padding: 30px 0;'>
            <h1 style='font-size: 2.5rem;'>TINH HOA ẨM THỰC BÌNH ĐỊNH</h1>
            <p style='font-size: 1.1rem; color: #444; max-width: 800px; margin: auto; padding: 0 15px;'>
                Xứ Nẫu Store mang đến những món ngon đặc sản vùng đất võ. 
                Giao hàng tận nơi - Hương vị nguyên bản.
            </p>
        </div>
    """, unsafe_allow_html=True)
    
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
                    slider_content += f'''
                    <div class="slide-item">
                        <img src="{img}">
                        <p style="font-weight:800; font-size:1rem; margin-top:10px; color:#1D4330;">{row["Sản phẩm"]}</p>
                        <p style="color:#D32F2F; font-weight:700;">{row["Giá"]:,}đ</p>
                    </div>'''
            st.markdown(f'<div class="slider-container"><div class="slide-track">{slider_content}</div></div>', unsafe_allow_html=True)

# =============================
# 6. CỬA HÀNG
# =============================
elif chon_menu == "🛍️ Cửa Hàng":
    st.markdown("<h2 style='text-align:center;'>💎 THỰC ĐƠN XỨ NẪU</h2>", unsafe_allow_html=True)
    
    ws = ket_noi_sheet("SanPham")
    if ws:
        data = ws.get_all_records()
        if not data:
            st.info("Đang cập nhật danh sách...")
        else:
            df_goc = pd.DataFrame(data)
            col_search, col_filter = st.columns([1, 1])
            with col_search:
                tu_khoa = st.text_input("🔍 Tìm kiếm...", placeholder="Tên sản phẩm...")
            with col_filter:
                gia_max = int(df_goc["Giá"].max())
                khoang_gia = st.slider("💰 Mức giá", 0, gia_max, (0, gia_max))

            df_loc = df_goc[
                (df_goc["Sản phẩm"].str.contains(tu_khoa, case=False, na=False)) &
                (df_goc["Giá"] >= khoang_gia[0]) &
                (df_goc["Giá"] <= khoang_gia[1])
            ]

            st.divider()

            if df_loc.empty:
                st.warning("Không tìm thấy sản phẩm.")
            else:
                # 2 cột trên điện thoại, 4 cột trên máy tính
                cols = st.columns(2 if st.session_state.get('is_mobile', False) else 4)
                # Lưu ý: Streamlit chưa có nhận diện thiết bị chuẩn, ta dùng grid 2-4 linh hoạt
                # Ở đây mình dùng st.columns(2) để đảm bảo hiển thị đẹp trên cả mobile
                cols = st.columns(2) if len(df_loc) > 1 else st.columns(1)
                
                # Tuy nhiên để chuyên nghiệp nhất, ta dùng 2 cột cố định cho mobile
                cols = st.columns(2) 
                for i, (_, row) in enumerate(df_loc.iterrows()):
                    with cols[i % 2]:
                        st.markdown('<div class="product-card">', unsafe_allow_html=True)
                        img = row["Hình ảnh"] if la_url_hop_le(row["Hình ảnh"]) else "https://via.placeholder.com/200"
                        st.markdown(f'<img src="{img}" style="border-radius: 12px; object-fit: cover; height: 140px; width: 100%;">', unsafe_allow_html=True)
                        st.markdown(f'<div class="product-name">{row["Sản phẩm"]}</div>', unsafe_allow_html=True)
                        st.markdown(f'<div class="gia-ban">{row["Giá"]:,}đ</div>', unsafe_allow_html=True)
                        st.markdown(f'<p style="color:#666; font-size:0.8rem; margin-bottom:5px;">Sẵn có: {row["Tồn kho"]}</p>', unsafe_allow_html=True)
                        
                        if int(row["Tồn kho"]) > 0:
                            # Khung số lượng đã được fix nền trắng bằng CSS ở trên
                            sl = st.number_input("SL", 1, int(row["Tồn kho"]), key=f"sl_{row['ID']}", label_visibility="collapsed")
                            if st.button("MUA 🛒", key=f"btn_{row['ID']}"):
                                st.session_state.gio_hang[str(row["ID"])] = st.session_state.gio_hang.get(str(row["ID"]), 0) + sl
                                st.toast(f"Đã thêm {row['Sản phẩm']}!", icon="✅")
                        else:
                            st.button("HẾT", disabled=True, key=f"out_{row['ID']}")
                        st.markdown('</div>', unsafe_allow_html=True)

# =============================
# 7. GIỎ HÀNG
# =============================
elif chon_menu == "🛒 Giỏ Hàng":
    st.markdown("<h2>🛒 GIỎ HÀNG</h2>", unsafe_allow_html=True)
    if not st.session_state.gio_hang:
        st.info("Giỏ hàng trống!")
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
                st.markdown(f"🔸 **{sp['Sản phẩm']}** (x{sl}) — {thanh_tien:,} VNĐ")
        
        st.markdown(f"### Tổng: <span style='color:#D32F2F;'>{tong:,} VNĐ</span>", unsafe_allow_html=True)
        
        with st.form("checkout_form"):
            t = st.text_input("Họ tên")
            s = st.text_input("Số điện thoại")
            d = st.text_area("Địa chỉ")
            if st.form_submit_button("XÁC NHẬN ĐẶT HÀNG"):
                if t and s and d:
                    ws_don = ket_noi_sheet("DonHang")
                    ws_don.append_row([datetime.now().strftime("%d/%m/%Y %H:%M"), t, s, d, ", ".join(ds_order), sum(st.session_state.gio_hang.values()), f"{tong:,} VNĐ", "Mới"])
                    for id_sp, sl in st.session_state.gio_hang.items():
                        cell = ws_sp.find(id_sp)
                        current_stock = int(ws_sp.cell(cell.row, 6).value)
                        ws_sp.update_cell(cell.row, 6, current_stock - sl)
                    st.session_state.gio_hang = {}
                    st.success("Đặt hàng thành công!"); st.balloons(); time.sleep(2); st.rerun()

# =============================
# 8. QUẢN TRỊ & THÔNG TIN
# =============================
elif chon_menu == "📊 Quản Trị":
    if not st.session_state.da_dang_nhap:
        col_l, col_m, col_r = st.columns([0.1, 0.8, 0.1])
        with col_m:
            tk = st.text_input("Admin")
            mk = st.text_input("Pass", type="password")
            if st.button("ĐĂNG NHẬP"):
                if tk == "admin" and mk == "binhdinh0209":
                    st.session_state.da_dang_nhap = True; st.rerun()
    else:
        st.button("Thoát", on_click=lambda: st.session_state.update({"da_dang_nhap": False}))
        t1, t2, t3 = st.tabs(["📦 KHO", "📝 ĐƠN", "⚙️ CÀI ĐẶT"])
        ws_sp = ket_noi_sheet("SanPham")
        ws_don = ket_noi_sheet("DonHang")
        
        with t1:
            df_sp = pd.DataFrame(ws_sp.get_all_records())
            df_edit = st.data_editor(df_sp, num_rows="dynamic", use_container_width=True)
            if st.button("LƯU KHO"):
                ws_sp.clear()
                ws_sp.update([df_edit.columns.values.tolist()] + df_edit.values.tolist())
                st.success("Đã lưu!")
        with t2:
            df_don_old = pd.DataFrame(ws_don.get_all_records())
            df_don_new = st.data_editor(df_don_old, use_container_width=True)
            if st.button("CẬP NHẬT ĐƠN"):
                for i in range(len(df_don_old)):
                    if str(df_don_old.iloc[i]['Trạng thái']) != "Hủy" and str(df_don_new.iloc[i]['Trạng thái']) == "Hủy":
                        chuoi_sp = str(df_don_new.iloc[i]['Sản phẩm'])
                        for item in chuoi_sp.split(", "):
                            match = re.search(r"(.+)\s+x(\d+)", item)
                            if match:
                                ten_sp, sl_hoan = match.group(1).strip(), int(match.group(2))
                                try:
                                    cell = ws_sp.find(ten_sp)
                                    ton = int(ws_sp.cell(cell.row, 6).value)
                                    ws_sp.update_cell(cell.row, 6, ton + sl_hoan)
                                except: pass
                ws_don.clear()
                ws_don.update([df_don_new.columns.values.tolist()] + df_don_new.values.tolist())
                st.success("Đã xong!"); st.rerun()
        with t3:
            ws_ch = ket_noi_sheet("CauHinh")
            moi = st.text_input("Logo URL:", value=st.session_state.logo_url)
            if st.button("LƯU"):
                cell = ws_ch.find("Logo")
                ws_ch.update_cell(cell.row, 2, moi)
                st.session_state.logo_url = moi
                st.rerun()

elif chon_menu == "📞 Thông Tin":
    st.markdown("<h2 style='text-align:center;'>📍 LIÊN HỆ</h2>", unsafe_allow_html=True)
    st.markdown(f"""
    <div style="background:#F9F9F9; padding:20px; border-radius:15px; text-align:center;">
        <p><b>🏡 XỨ NẪU STORE</b></p>
        <p>📍 96 Ngô Đức Đệ, Bình Định</p>
        <p>📞 0932.642.376</p>
        <img src="https://raw.githubusercontent.com/windy0209/dac-san-binh-dinh/main/qrcode.png" width="150">
    </div>
    """, unsafe_allow_html=True)
    toa_do = pd.DataFrame({'lat': [13.8930853], 'lon': [109.1002733]})
    st.map(toa_do, zoom=14)
