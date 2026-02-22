import streamlit as st
from streamlit_option_menu import option_menu
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import pandas as pd
import time
import re

# --- CẤU HÌNH TRANG ---
st.set_page_config(page_title="Đặc Sản Bình Định - Quản Lý Kho Pro", layout="wide", page_icon="🍱")

# --- KHỞI TẠO TRẠNG THÁI ---
if 'da_dang_nhap' not in st.session_state:
    st.session_state.da_dang_nhap = False
if 'gio_hang' not in st.session_state:
    st.session_state.gio_hang = {} 

# --- KẾT NỐI GOOGLE SHEETS ---
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

# --- KIỂM TRA URL HỢP LỆ ---
def la_url_hop_le(url):
    if not url or not isinstance(url, str):
        return False
    return url.startswith("http://") or url.startswith("https://")

# --- LẤY LOGO AN TOÀN ---
def lay_logo_an_toan():
    logo_mac_dinh = "https://cdn-icons-png.flaticon.com/512/4062/4062916.png"
    ws = ket_noi_sheet("CauHinh")
    if ws:
        try:
            data = ws.get_all_records()
            for row in data:
                val = row.get('Gia_Tri')
                if row.get('Ten_Cau_Hinh') == 'Logo' and la_url_hop_le(val):
                    return val
        except: pass
    return logo_mac_dinh

# --- GIAO DIỆN CSS ---
st.markdown("""<style>
    .the-san-pham { background-color: white; padding: 20px; border-radius: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); text-align: center; margin-bottom: 20px; border: 1px solid #eee; height: 500px; }
    .gia-ban { color: #d32f2f; font-weight: bold; font-size: 22px; margin: 5px 0; }
    </style>""", unsafe_allow_html=True)

# --- SIDEBAR & LOGO ---
logo_url = lay_logo_an_toan()
with st.sidebar:
    if la_url_hop_le(logo_url):
        try:
            st.image(logo_url, width=120)
        except Exception:
            st.warning("⚠️ Không thể tải logo từ liên kết này.")
    
    st.markdown("<h2 style='text-align: center; color: #d32f2f; margin-top: -10px;'>XỨ NẪU STORE</h2>", unsafe_allow_html=True)
    chon_menu = option_menu(None, ["Cửa Hàng", "Giỏ Hàng", "Thông Tin Shop", "Quản Trị Viên"], 
                            icons=["shop", "cart3", "info-circle", "person-badge-key"], default_index=0)

# --- 1. TRANG CỬA HÀNG ---
if chon_menu == "Cửa Hàng":
    st.title("🛍️ Đặc Sản Bình Định Chính Gốc")
    ws_sp = ket_noi_sheet("SanPham")
    if ws_sp is not None:
        try:
            data = ws_sp.get_all_records()
            if data:
                df_sp = pd.DataFrame(data)
                df_sp['Giá'] = pd.to_numeric(df_sp['Giá'], errors='coerce').fillna(0)
                df_sp['Tồn kho'] = pd.to_numeric(df_sp['Tồn kho'], errors='coerce').fillna(0)
                
                cot = st.columns(3)
                for i, sp in df_sp.iterrows():
                    id_sp = str(sp['ID'])
                    img_link = sp["Hình ảnh"] if la_url_hop_le(sp["Hình ảnh"]) else "https://via.placeholder.com/150"
                    with cot[i % 3]:
                        st.markdown(f'<div class="the-san-pham"><img src="{img_link}" width="100%" style="height:180px; object-fit:cover; border-radius:10px;"><h4>{sp["Sản phẩm"]}</h4><p class="gia-ban">{sp["Giá"]:,} VNĐ</p><p style="color: #2e7d32; font-weight: bold;">📦 Còn lại: {int(sp["Tồn kho"])}</p></div>', unsafe_allow_html=True)
                        if sp['Tồn kho'] > 0:
                            sl = st.number_input(f"Số lượng:", min_value=1, max_value=int(sp['Tồn kho']), key=f"sl_{i}")
                            if st.button(f"🛒 Thêm vào giỏ", key=f"btn_{i}"):
                                st.session_state.gio_hang[id_sp] = st.session_state.gio_hang.get(id_sp, 0) + sl
                                st.toast(f"Đã thêm {int(sl)} {sp['Sản phẩm']}!")
                        else: st.button("Hết hàng", disabled=True, key=f"out_{i}")
        except Exception as e:
            st.error(f"Lỗi hiển thị sản phẩm: {e}")
    else: st.error("❌ Không thể kết nối dữ liệu.")

# --- 2. QUẢN TRỊ VIÊN ---
elif chon_menu == "Quản Trị Viên":
    if not st.session_state.da_dang_nhap:
        st.subheader("🔐 Đăng nhập Admin")
        tk = st.text_input("Tài khoản")
        mk = st.text_input("Mật khẩu", type="password")
        if st.button("Đăng nhập"):
            if tk == "admin" and mk == "binhdinh0209":
                st.session_state.da_dang_nhap = True
                st.rerun()
            else: st.error("Sai tài khoản hoặc mật khẩu!")
    else:
        t1, t2, t3 = st.tabs(["📦 Kho Hàng", "📜 Quản Lý Đơn Hàng", "⚙️ Cấu Hình"])
        ws_sp = ket_noi_sheet("SanPham")
        ws_don = ket_noi_sheet("DonHang")

        with t2:
            st.subheader("Quản lý trạng thái đơn hàng")
            if ws_don and ws_sp:
                df_don_old = pd.DataFrame(ws_don.get_all_records())
                st.info("💡 Chuyển trạng thái sang 'Hủy' để hệ thống tự động hoàn kho.")
                df_don_new = st.data_editor(df_don_old, use_container_width=True, key="editor_don")
                
                if st.button("💾 Lưu trạng thái & Cập nhật kho"):
                    for i in range(len(df_don_old)):
                        old_s = str(df_don_old.iloc[i]['Trạng thái'])
                        new_s = str(df_don_new.iloc[i]['Trạng thái'])
                        if old_s != "Hủy" and new_s == "Hủy":
                            parts = str(df_don_new.iloc[i]['Sản phẩm']).split(", ")
                            for p in parts:
                                match = re.search(r"(.+)\s+x(\d+)", p)
                                if match:
                                    name_sp, qty = match.group(1).strip(), int(match.group(2))
                                    try:
                                        cell = ws_sp.find(name_sp)
                                        stock = int(ws_sp.cell(cell.row, 6).value)
                                        ws_sp.update_cell(cell.row, 6, stock + qty)
                                        st.write(f"✅ Hoàn trả {qty} {name_sp}")
                                    except: pass
                    ws_don.clear()
                    ws_don.update([df_don_new.columns.values.tolist()] + df_don_new.values.tolist())
                    st.success("Đã lưu!")
                    time.sleep(1)
                    st.rerun()

        with t1:
            if ws_sp:
                df_sp = pd.DataFrame(ws_sp.get_all_records())
                bang_sua = st.data_editor(df_sp, num_rows="dynamic", use_container_width=True)
                if st.button("💾 Lưu kho"):
                    ws_sp.clear()
                    ws_sp.update([bang_sua.columns.values.tolist()] + bang_sua.values.tolist())
                    st.success("Đã cập nhật!")

        with t3:
            ws_ch = ket_noi_sheet("CauHinh")
            if ws_ch:
                moi = st.text_input("Dán Link Logo mới (URL):", value=logo_url)
                if st.button("Cập nhật Logo"):
                    try:
                        cell = ws_ch.find("Logo")
                        ws_ch.update_cell(cell.row, 2, moi)
                        st.success("Đã thay đổi!")
                        time.sleep(1)
                        st.rerun()
                    except: st.error("Hãy tạo dòng 'Logo' trong Tab CauHinh!")

# --- 3. GIỎ HÀNG ---
elif chon_menu == "Giỏ Hàng":
    st.title("🛒 Giỏ Hàng")
    if not st.session_state.gio_hang: st.info("Giỏ hàng đang trống.")
    else:
        ws_sp = ket_noi_sheet("SanPham")
        if ws_sp:
            df_sp = pd.DataFrame(ws_sp.get_all_records())
            df_sp['Giá'] = pd.to_numeric(df_sp['Giá'], errors='coerce').fillna(0)
            tong_tien, ds_order = 0, []
            for id_sp, sl in st.session_state.gio_hang.items():
                sp = df_sp[df_sp['ID'].astype(str) == id_sp].iloc[0]
                tong_tien += sp['Giá'] * sl
                ds_order.append(f"{sp['Sản phẩm']} x{sl}")
                st.write(f"🔹 {sp['Sản phẩm']} x{sl} : {sp['Giá']*sl:,} VNĐ")
            st.subheader(f"Tổng: {tong_tien:,} VNĐ")
            with st.form("form_order"):
                ten, sdt, dc = st.text_input("Họ tên *"), st.text_input("SĐT *"), st.text_area("Địa chỉ *")
                if st.form_submit_button("Xác nhận"):
                    if ten and sdt and dc:
                        ws_don = ket_noi_sheet("DonHang")
                        ws_don.append_row([datetime.now().strftime("%d/%m/%Y %H:%M"), ten, sdt, dc, ", ".join(ds_order), sum(st.session_state.gio_hang.values()), f"{tong_tien:,} VNĐ", "Mới"])
                        for id_sp, sl in st.session_state.gio_hang.items():
                            item_name = df_sp[df_sp['ID'].astype(str) == id_sp].iloc[0]['Sản phẩm']
                            cell = ws_sp.find(str(item_name))
                            old = int(ws_sp.cell(cell.row, 6).value)
                            ws_sp.update_cell(cell.row, 6, old - sl)
                        st.success("Đặt hàng thành công!")
                        st.session_state.gio_hang = {}
                        time.sleep(1)
                        st.rerun()

# --- 4. THÔNG TIN SHOP ---
elif chon_menu == "Thông Tin Shop":
    st.title("🏠 Xứ Nẫu Quán - Đặc Sản Bình Định")
    col_tt1, col_tt2 = st.columns([1, 1])
    with col_tt1:
        st.markdown("""
        ### Liên Hệ Với Chúng Tôi
        * **📍 Địa chỉ:** 96 Ngô Đức Đệ, Phường Bình Định, TX. An Nhơn, Bình Định.
        * **📞 Hotline:** 0901.234.567
        * **📧 Email:** miendatvo0209@gmail.com
        """)
    with col_tt2:
        toa_do_shop = pd.DataFrame({'lat': [13.8930853], 'lon': [109.1002733]})
        st.write("📍 **Vị trí trên bản đồ:**")
        st.map(toa_do_shop, zoom=14, use_container_width=True)

