import streamlit as st
from streamlit_option_menu import option_menu
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import pandas as pd
import time
import re

# --- 1. CẤU HÌNH TRANG & SEO ---
# Việc đặt tên tiêu đề đầy đủ giúp Google nhận diện từ khóa "Đặc sản Bình Định" tốt hơn.
st.set_page_config(
    page_title="Cửa Hàng Xứ Nẫu - Đặc Sản Bình Định Chính Gốc",
    layout="wide",
    page_icon="🍱"
)

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
    # Link Raw để đảm bảo hiển thị trên web
    return "https://raw.githubusercontent.com/windy0209/dac-san-binh-dinh/main/logo2.png"

# --- 2. CSS NÂNG CAO (Giao diện thẻ sản phẩm) ---
st.markdown("""
    <style>
    .stApp { background-color: #f8fbf8; }
    
    /* Hiệu ứng khung sản phẩm */
    [data-testid="stVerticalBlockBorderWrapper"] {
        border: 1px solid #edf2ed !important;
        border-radius: 20px !important;
        background-color: white !important;
        box-shadow: 0 10px 25px rgba(46,125, 50, 0.08) !important;
        padding: 15px !important;
        transition: 0.3s !important;
    }
    [data-testid="stVerticalBlockBorderWrapper"]:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 35px rgba(46, 125, 50, 0.15) !important;
    }

    .product-info img { border-radius: 15px; object-fit: cover; height: 180px; width: 100%; }
    .gia-ban { color: #f39c12; font-size: 1.4rem; font-weight: 800; margin: 10px 0; }
    
    /* Định dạng nút bấm & ô số lượng */
    .stButton>button { 
        background-color: #2e7d32; color: white; border-radius: 10px; 
        font-weight: 600; width: 100%; border: none; height: 45px;
    }
    .stButton>button:hover { background-color: #f39c12; color: white; }
    div[data-testid="stNumberInput"] label { display: none; }

    /* Info Box cho mục Thông Tin */
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

# --- 3. SIDEBAR MENU ---
logo_url = lay_logo()
with st.sidebar:
    if la_url_hop_le(logo_url): st.image(logo_url, width=120)
    st.markdown("<h2 style='text-align: center; color: #2e7d32; margin-top:-10px;'>CỬA HÀNG XỨ NẪU</h2>", unsafe_allow_html=True)
    chon_menu = option_menu(None, ["🏠 Trang Chủ", "🛍️ Cửa Hàng", "🛒 Giỏ Hàng", "📞 Thông Tin", "📊 Quản Trị"], 
                            icons=["house", "shop", "cart3", "info-circle", "person-lock"], default_index=1,
                            styles={"nav-link-selected": {"background-color": "#2e7d32"}})

# --- 4. LOGIC CÁC TRANG ---

# --- TRANG CHỦ ---
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

# --- CỬA HÀNG ---
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
                # Sử dụng border=True để bao trọn nút bấm vào khung
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
                    else:
                        st.button("HẾT HÀNG", disabled=True, key=f"out_{i}")

# --- GIỎ HÀNG ---
elif chon_menu == "🛒 Giỏ Hàng":
    st.title("🛒 Giỏ Hàng")
    if not st.session_state.gio_hang: st.warning("Giỏ hàng của bạn đang trống.")
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
            t, s, d = st.text_input("Họ tên *"), st.text_input("SĐT *"), st.text_area("Địa chỉ nhận hàng *")
            if st.form_submit_button("XÁC NHẬN ĐẶT HÀNG"):
                if t and s and d:
                    ws_don = ket_noi_sheet("DonHang")
                    ws_don.append_row([datetime.now().strftime("%d/%m/%Y %H:%M"), t, s, d, ", ".join(ds_str), sum(st.session_state.gio_hang.values()), f"{tong:,} VNĐ", "Mới"])
                    # Cập nhật tồn kho
                    for id_sp, sl in st.session_state.gio_hang.items():
                        cell = ws_sp.find(str(df_sp[df_sp['ID'].astype(str) == id_sp].iloc[0]['Sản phẩm']))
                        ws_sp.update_cell(cell.row, 6, int(ws_sp.cell(cell.row, 6).value) - sl)
                    st.session_state.gio_hang = {}
                    st.success("Đặt hàng thành công! Chúng tôi sẽ liên hệ bạn sớm.")
                    st.balloons()
                    time.sleep(2); st.rerun()
                else: st.error("Vui lòng điền đầy đủ thông tin sao (*)")

# --- THÔNG TIN CỬA HÀNG ---
elif chon_menu == "📞 Thông Tin":
    st.markdown("<h1 style='color: #2e7d32;'>📞 Thông Tin Liên Hệ</h1>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        <div class="info-box">
            <h3>🏠 Địa chỉ cửa hàng</h3>
            <p>123 Đường Võ Nguyên Giáp, TP. Quy Nhơn, Bình Định</p>
            <h3>☎️ Hotline / Zalo</h3>
            <p><b>0905.XXX.XXX</b> (Liên hệ để có giá sỉ)</p>
            <h3>🌐 Website</h3>
            <p>dac-san-binh-dinh.streamlit.app</p>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class="info-box">
            <h3>🚚 Giao hàng toàn quốc</h3>
            <p>Hỗ trợ ship COD toàn quốc. Freeship đơn hàng trên 500k tại nội thành Quy Nhơn.</p>
            <h3>🛡️ Cam kết</h3>
            <p>Thực phẩm sạch, không hóa chất, đúng chuẩn hương vị truyền thống Xứ Nẫu.</p>
        </div>
        """, unsafe_allow_html=True)

# --- QUẢN TRỊ ---
elif chon_menu == "📊 Quản Trị":
    if not st.session_state.da_dang_nhap:
        tk = st.text_input("Tên đăng nhập")
        mk = st.text_input("Mật khẩu", type="password")
        if st.button("Đăng nhập"):
            if tk == "admin" and mk == "binhdinh0209":
                st.session_state.da_dang_nhap = True; st.rerun()
            else: st.error("Sai thông tin!")
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
                st.success("Đã cập nhật dữ liệu kho!")

        with tab2:
            df_don_old = pd.DataFrame(ws_don.get_all_records())
            df_don_new = st.data_editor(df_don_old, use_container_width=True)
            if st.button("CẬP NHẬT TRẠNG THÁI"):
                ws_don.clear()
                ws_don.update([df_don_new.columns.values.tolist()] + df_don_new.values.tolist())
                st.success("Thành công!"); time.sleep(1); st.rerun()

        with tab3:
            ws_ch = ket_noi_sheet("CauHinh")
            moi = st.text_input("Link Logo mới (Raw GitHub):", value=logo_url)
            if st.button("CẬP NHẬT LOGO"):
                c = ws_ch.find("Logo")
                ws_ch.update_cell(c.row, 2, moi); st.rerun()
