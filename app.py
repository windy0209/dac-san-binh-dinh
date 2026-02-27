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
# 3. CSS CAO CẤP (KHẮC PHỤC LỖI HIỂN THỊ CHỮ)
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

    .block-container { padding-top: 1rem; }

    /* Tiêu đề */
    h1, h2, h3 {
        font-weight: 800 !important;
        color: #1D4330 !important;
        letter-spacing: -0.5px;
    }

    /* Thẻ sản phẩm - Sửa lỗi cắt chữ */
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
    }
    
    .product-card:hover {
        transform: translateY(-5px);
        border-color: #2E7D32;
    }

    /* Sửa lại phông chữ tên sản phẩm hiển thị đầy đủ */
    .product-name {
        font-weight: 700; 
        font-size: 1.15rem;
        color: #1A1A1A;
        margin: 12px 0;
        line-height: 1.4;
        min-height: 60px; /* Đảm bảo đủ chỗ cho tên dài nhưng vẫn đều hàng */
        display: block; /* Chuyển về block để hiển thị hết chữ */
    }

    .gia-ban {
        color: #D32F2F;
        font-size: 1.35rem;
        font-weight: 800;
        margin-bottom: 8px;
    }

    /* Nút bấm */
    .stButton>button {
        background-color: #2E7D32 !important;
        color: white !important;
        border-radius: 10px !important;
        font-weight: 700 !important;
        padding: 0.6rem 1rem !important;
        border: none !important;
    }
    .stButton>button:hover {
        background-color: #F39C12 !important;
    }

    /* Slider */
    .slider-container { width: 100%; overflow: hidden; background: #F9F9F9; padding: 30px 0; border-radius: 20px; }
    .slide-track { display: flex; width: max-content; animation: scroll 35s linear infinite; }
    .slide-item { width: 250px; margin: 0 15px; text-align: center; }
    .slide-item img { width: 220px; height: 180px; object-fit: cover; border-radius: 12px; }
    @keyframes scroll { 0% { transform: translateX(0); } 100% { transform: translateX(-50%); } }
</style>
""", unsafe_allow_html=True)

# =============================
# 4. HEADER & MENU NGANG
# =============================
col_logo, col_nav = st.columns([1, 4])

with col_logo:
    st.image(st.session_state.logo_url, width=120)

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

st.markdown(f"""
    <div style="text-align: right; padding-right: 20px; margin-top: -15px;">
        <span style="color: #2E7D32; font-weight: 800; font-size: 1.1rem;">📞 HOTLINE ĐẶT HÀNG: 0932.642.376</span>
    </div>
""", unsafe_allow_html=True)

# =============================
# 5. TRANG CHỦ
# =============================
if chon_menu == "🏠 Trang Chủ":
    st.markdown("""
        <div style='text-align:center; padding: 40px 0;'>
            <h1 style='font-size: 3rem;'>TINH HOA ẨM THỰC BÌNH ĐỊNH</h1>
            <p style='font-size: 1.2rem; color: #444; max-width: 850px; margin: auto;'>
                Xứ Nẫu Store tự hào mang đến những món ngon đặc trưng từ vùng đất võ. 
                Từng sản phẩm là một câu chuyện về hương vị truyền thống và sự tận tâm.
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns(3)
    c1.markdown("### 🌿 Nguyên Bản\nGiữ trọn công thức truyền thống lâu đời của người dân Bình Định.")
    c2.markdown("### 🚚 Tận Tâm\nGiao hàng nhanh chóng, đóng gói kỹ lưỡng, bảo quản tuyệt đối.")
    c3.markdown("### 💝 Uy Tín\nSự hài lòng của quý khách là niềm tự hào lớn nhất của chúng tôi.")

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
                        <p style="font-weight:800; font-size:1.1rem; margin-top:10px; color:#1D4330;">{row["Sản phẩm"]}</p>
                        <p style="color:#D32F2F; font-weight:700;">{row["Giá"]:,}đ</p>
                    </div>'''
            st.markdown(f'<div class="slider-container"><div class="slide-track">{slider_content}</div></div>', unsafe_allow_html=True)

# =============================
# 6. CỬA HÀNG (HIỂN THỊ TÊN ĐẦY ĐỦ)
# =============================
elif chon_menu == "🛍️ Cửa Hàng":
    st.markdown("<h2 style='text-align:center;'>💎 THỰC ĐƠN XỨ NẪU</h2>", unsafe_allow_html=True)
    
    ws = ket_noi_sheet("SanPham")
    if ws:
        data = ws.get_all_records()
        if not data:
            st.info("Danh mục đang được cập nhật...")
        else:
            df_goc = pd.DataFrame(data)
            col_search, col_filter = st.columns([2, 1])
            with col_search:
                tu_khoa = st.text_input("🔍 Tìm kiếm đặc sản...", placeholder="Nhập tên nem, chả, tré...")
            with col_filter:
                gia_max = int(df_goc["Giá"].max())
                khoang_gia = st.slider("💰 Mức giá (VNĐ)", 0, gia_max, (0, gia_max))

            df_loc = df_goc[
                (df_goc["Sản phẩm"].str.contains(tu_khoa, case=False, na=False)) &
                (df_goc["Giá"] >= khoang_gia[0]) &
                (df_goc["Giá"] <= khoang_gia[1])
            ]

            st.divider()

            if df_loc.empty:
                st.warning("Không tìm thấy sản phẩm yêu cầu.")
            else:
                # Sử dụng grid linh hoạt
                cols = st.columns(4, gap="medium")
                for i, (_, row) in enumerate(df_loc.iterrows()):
                    with cols[i % 4]:
                        st.markdown('<div class="product-card">', unsafe_allow_html=True)
                        img = row["Hình ảnh"] if la_url_hop_le(row["Hình ảnh"]) else "https://via.placeholder.com/200"
                        st.markdown(f'<img src="{img}" style="border-radius: 12px; object-fit: cover; height: 170px; width: 100%;">', unsafe_allow_html=True)
                        # Phần tên hiển thị đầy đủ
                        st.markdown(f'<div class="product-name">{row["Sản phẩm"]}</div>', unsafe_allow_html=True)
                        st.markdown(f'<div class="gia-ban">{row["Giá"]:,} VNĐ</div>', unsafe_allow_html=True)
                        st.markdown(f'<p style="color:#555; font-size:0.85rem; font-weight:600;">Sẵn có: {row["Tồn kho"]}</p>', unsafe_allow_html=True)
                        
                        if int(row["Tồn kho"]) > 0:
                            sl = st.number_input("Chọn SL", 1, int(row["Tồn kho"]), key=f"sl_{row['ID']}", label_visibility="collapsed")
                            if st.button("CHỌN MUA 🛒", key=f"btn_{row['ID']}"):
                                st.session_state.gio_hang[str(row["ID"])] = st.session_state.gio_hang.get(str(row["ID"]), 0) + sl
                                st.toast(f"Đã thêm {row['Sản phẩm']} vào giỏ!", icon="✅")
                        else:
                            st.button("TẠM HẾT", disabled=True, key=f"out_{row['ID']}")
                        st.markdown('</div>', unsafe_allow_html=True)
                        st.write("") # Khoảng đệm giữa các hàng

# =============================
# 7. GIỎ HÀNG
# =============================
elif chon_menu == "🛒 Giỏ Hàng":
    st.markdown("<h2>🛒 DANH SÁCH ĐÃ CHỌN</h2>", unsafe_allow_html=True)
    if not st.session_state.gio_hang:
        st.info("Chưa có món ngon nào trong giỏ hàng!")
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
                st.markdown(f"🔸 **{sp['Sản phẩm']}** (x{sl}) — <span style='color:#D32F2F; font-weight:700;'>{thanh_tien:,} VNĐ</span>", unsafe_allow_html=True)
        
        st.markdown(f"<h3 style='border-top: 1px solid #DDD; padding-top: 15px;'>Tổng thanh toán: <span style='color:#D32F2F;'>{tong:,} VNĐ</span></h3>", unsafe_allow_html=True)
        
        with st.form("checkout_form"):
            st.markdown("#### 🚚 THÔNG TIN NHẬN HÀNG")
            t = st.text_input("Họ và tên")
            s = st.text_input("Số điện thoại")
            d = st.text_area("Địa chỉ chi tiết")
            if st.form_submit_button("HOÀN TẤT ĐẶT HÀNG"):
                if t and s and d:
                    ws_don = ket_noi_sheet("DonHang")
                    ws_don.append_row([datetime.now().strftime("%d/%m/%Y %H:%M"), t, s, d, ", ".join(ds_order), sum(st.session_state.gio_hang.values()), f"{tong:,} VNĐ", "Mới"])
                    # Cập nhật tồn kho
                    for id_sp, sl in st.session_state.gio_hang.items():
                        cell = ws_sp.find(id_sp)
                        current_stock = int(ws_sp.cell(cell.row, 6).value)
                        ws_sp.update_cell(cell.row, 6, current_stock - sl)
                    st.session_state.gio_hang = {}
                    st.success("Cảm ơn bạn! Đơn hàng đã được ghi nhận."); st.balloons(); time.sleep(2); st.rerun()

# =============================
# 8. QUẢN TRỊ & THÔNG TIN
# =============================
elif chon_menu == "📊 Quản Trị":
    if not st.session_state.da_dang_nhap:
        col_l, col_m, col_r = st.columns([1,1.5,1])
        with col_m:
            st.markdown("### 🔐 HỆ THỐNG QUẢN TRỊ")
            tk = st.text_input("Tài khoản")
            mk = st.text_input("Mật khẩu", type="password")
            if st.button("ĐĂNG NHẬP"):
                if tk == "admin" and mk == "binhdinh0209":
                    st.session_state.da_dang_nhap = True; st.rerun()
                else: st.error("Lỗi đăng nhập!")
    else:
        st.button("🚪 Thoát quản trị", on_click=lambda: st.session_state.update({"da_dang_nhap": False}))
        t1, t2, t3 = st.tabs(["📦 KHO HÀNG", "📝 ĐƠN HÀNG", "⚙️ CẤU HÌNH"])
        ws_sp = ket_noi_sheet("SanPham")
        ws_don = ket_noi_sheet("DonHang")
        
        with t1:
            df_sp = pd.DataFrame(ws_sp.get_all_records())
            df_edit = st.data_editor(df_sp, num_rows="dynamic", use_container_width=True)
            if st.button("LƯU KHO"):
                ws_sp.clear()
                ws_sp.update([df_edit.columns.values.tolist()] + df_edit.values.tolist())
                st.success("Kho đã lưu!")
        with t2:
            df_don_old = pd.DataFrame(ws_don.get_all_records())
            df_don_new = st.data_editor(df_don_old, use_container_width=True)
            if st.button("LƯU ĐƠN & HOÀN KHO"):
                for i in range(len(df_don_old)):
                    if str(df_don_old.iloc[i]['Trạng thái']) != "Hủy" and str(df_don_new.iloc[i]['Trạng thái']) == "Hủy":
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
                                except: pass
                ws_don.clear()
                ws_don.update([df_don_new.columns.values.tolist()] + df_don_new.values.tolist())
                st.success("Đã cập nhật!"); st.rerun()
        with t3:
            ws_ch = ket_noi_sheet("CauHinh")
            moi = st.text_input("Link Logo mới:", value=st.session_state.logo_url)
            if st.button("LƯU LOGO"):
                cell = ws_ch.find("Logo")
                ws_ch.update_cell(cell.row, 2, moi)
                st.session_state.logo_url = moi
                st.success("Đã đổi!"); st.rerun()

elif chon_menu == "📞 Thông Tin":
    st.markdown("<h2 style='text-align:center;'>📍 LIÊN HỆ VỚI CHÚNG TÔI</h2>", unsafe_allow_html=True)
    col_info, col_map = st.columns([1, 1.2], gap="large")
    with col_info:
        st.markdown(f"""
        <div style="background:#FBFBFB; padding:30px; border-radius:20px; border: 1px solid #F0F0F0;">
            <h3 style="color: #1D4330; margin-top: 0;">🏡 XỨ NẪU STORE</h3>
            <p style="font-size:1.1rem;"><b>📍 Địa chỉ:</b> 96 Ngô Đức Đệ, Bình Định, TX. An Nhơn, Bình Định</p>
            <p style="font-size:1.1rem;"><b>📞 Hotline/Zalo:</b> <span style="color:#D32F2F; font-weight:800;">0932.642.376</span></p>
            <p style="font-size:1.1rem;"><b>📧 Email:</b> miendatvo86@gmail.com</p>
            <hr>
            <div style="text-align:center;">
                <img src="https://raw.githubusercontent.com/windy0209/dac-san-binh-dinh/main/qrcode.png" width="160" style="border: 4px solid white; box-shadow: 0 4px 10px rgba(0,0,0,0.05);">
                <p style="margin-top:10px; font-weight:700;">QUÉT ZALO - TƯ VẤN NGAY</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
    with col_map:
        toa_do = pd.DataFrame({'lat': [13.8930853], 'lon': [109.1002733]})
        st.map(toa_do, zoom=14)
