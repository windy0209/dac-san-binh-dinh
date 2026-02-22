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
        creds = Credentials.from_service_account_file("credentials.json", scopes=scope)
        client = gspread.authorize(creds)
        return client.open("DonHangDacSanBinhDinh").worksheet(ten_tab)
    except Exception:
        return None

# --- LẤY LOGO AN TOÀN ---
def lay_logo_an_toan():
    logo_mac_dinh = "https://cdn-icons-png.flaticon.com/512/4062/4062916.png"
    try:
        ws = ket_noi_sheet("CauHinh")
        if ws:
            data = ws.get_all_records()
            for row in data:
                if row.get('Ten_Cau_Hinh') == 'Logo' and row.get('Gia_Tri'):
                    return row['Gia_Tri']
    except:
        pass
    return logo_mac_dinh

# --- SIDEBAR & LOGO ---
logo_url = lay_logo_an_toan()
with st.sidebar:
    if logo_url:
        st.image(logo_url, width=120)
    st.markdown("<h2 style='text-align: center; color: #d32f2f; margin-top: -10px;'>XỨ NẪU STORE</h2>", unsafe_allow_html=True)
    chon_menu = option_menu(None, ["Cửa Hàng", "Giỏ Hàng", "Thông Tin Shop", "Quản Trị Viên"], 
                            icons=["shop", "cart3", "info-circle", "person-badge-key"], default_index=0)

# --- TRANG CỬA HÀNG ---
if chon_menu == "Cửa Hàng":
    st.title("🛍️ Đặc Sản Bình Định Chính Gốc")
    ws_sp = ket_noi_sheet("SanPham")
    if ws_sp:
        data = ws_sp.get_all_records()
        if data:
            df_sp = pd.DataFrame(data)
            df_sp['Giá'] = pd.to_numeric(df_sp['Giá'], errors='coerce').fillna(0)
            df_sp['Tồn kho'] = pd.to_numeric(df_sp['Tồn kho'], errors='coerce').fillna(0)
            
            cot = st.columns(3)
            for i, sp in df_sp.iterrows():
                id_sp = str(sp['ID'])
                with cot[i % 3]:
                    st.markdown(f"""
                        <div style="background-color: white; padding: 20px; border-radius: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); text-align: center; margin-bottom: 20px; border: 1px solid #eee; height: 490px;">
                            <img src="{sp['Hình ảnh']}" width="100%" style="height:180px; object-fit:cover; border-radius:10px;" onerror="this.src='https://via.placeholder.com/150'">
                            <h4>{sp['Sản phẩm']}</h4>
                            <p style="color: #d32f2f; font-weight: bold; font-size: 22px;">{sp['Giá']:,} VNĐ</p>
                            <p style="color: #2e7d32; font-weight: bold; font-size: 14px;">📦 Còn lại: {int(sp['Tồn kho'])}</p>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    if sp['Tồn kho'] > 0:
                        sl_chon = st.number_input(f"Số lượng:", min_value=1, max_value=int(sp['Tồn kho']), key=f"sl_{i}")
                        if st.button(f"🛒 Thêm vào giỏ", key=f"btn_{i}"):
                            hien_tai = st.session_state.gio_hang.get(id_sp, 0)
                            if (hien_tai + sl_chon) <= sp['Tồn kho']:
                                st.session_state.gio_hang[id_sp] = hien_tai + sl_chon
                                st.toast(f"Đã thêm {int(sl_chon)} {sp['Sản phẩm']}!", icon='✅')
                            else: st.error("Không đủ hàng!")
                    else: st.button("Hết hàng", disabled=True, key=f"out_{i}")

# --- TRANG QUẢN TRỊ VIÊN ---
elif chon_menu == "Quản Trị Viên":
    if not st.session_state.da_dang_nhap:
        st.subheader("🔐 Đăng nhập Admin")
        tk = st.text_input("Tài khoản")
        mk = st.text_input("Mật khẩu", type="password")
        if st.button("Đăng nhập"):
            if tk == "admin" and mk == "binhdinh0209":
                st.session_state.da_dang_nhap = True
                st.rerun()
    else:
        t1, t2, t3 = st.tabs(["📦 Kho Hàng", "📜 Quản Lý Đơn Hàng", "⚙️ Cấu Hình"])
        
        with t2:
            st.subheader("Quản lý trạng thái đơn hàng")
            ws_don = ket_noi_sheet("DonHang")
            ws_sp = ket_noi_sheet("SanPham")
            
            if ws_don and ws_sp:
                df_don_old = pd.DataFrame(ws_don.get_all_records())
                st.info("💡 Khi chuyển trạng thái sang 'Hủy', hệ thống sẽ tự động cộng lại hàng vào kho.")
                df_don_new = st.data_editor(df_don_old, use_container_width=True, key="editor_don")
                
                if st.button("💾 Lưu trạng thái & Cập nhật kho"):
                    # Tìm các dòng bị thay đổi trạng thái sang "Hủy"
                    for i in range(len(df_don_old)):
                        old_status = str(df_don_old.iloc[i]['Trạng thái'])
                        new_status = str(df_don_new.iloc[i]['Trạng thái'])
                        
                        # Chỉ xử lý nếu trạng thái cũ KHÔNG PHẢI là Hủy, và trạng thái mới LÀ Hủy
                        if old_status != "Hủy" and new_status == "Hủy":
                            san_pham_str = str(df_don_new.iloc[i]['Sản phẩm'])
                            # Tách chuỗi: "Nem Chợ Huyện x2, Chả bò x1"
                            parts = san_pham_str.split(", ")
                            for p in parts:
                                match = re.search(r"(.+)\s+x(\d+)", p)
                                if match:
                                    name_sp = match.group(1).strip()
                                    qty = int(match.group(2))
                                    
                                    # Tìm và cập nhật lại kho cho sản phẩm này
                                    try:
                                        cell = ws_sp.find(name_sp)
                                        # Cột 6 là Tồn kho
                                        current_stock = int(ws_sp.cell(cell.row, 6).value)
                                        ws_sp.update_cell(cell.row, 6, current_stock + qty)
                                        st.write(f"✅ Đã hoàn trả {qty} {name_sp} vào kho.")
                                    except:
                                        st.warning(f"❌ Không tìm thấy sản phẩm '{name_sp}' để hoàn kho.")

                    # Cập nhật lại toàn bộ bảng đơn hàng
                    ws_don.clear()
                    ws_don.update([df_don_new.columns.values.tolist()] + df_don_new.values.tolist())
                    st.success("Đã cập nhật đơn hàng và kho thành công!")
                    time.sleep(2)
                    st.rerun()

        # --- CÁC TAB KHÁC GIỮ NGUYÊN ---
        with t1:
            df_sp = pd.DataFrame(ws_sp.get_all_records())
            bang_sua = st.data_editor(df_sp, num_rows="dynamic", use_container_width=True)
            if st.button("💾 Lưu kho"):
                ws_sp.clear()
                ws_sp.update([bang_sua.columns.values.tolist()] + bang_sua.values.tolist())
                st.success("Đã cập nhật kho!")
        
        with t3:
            ws_ch = ket_noi_sheet("CauHinh")
            if ws_ch:
                moi = st.text_input("Dán Link Logo mới:", value=logo_url)
                if st.button("Cập nhật Logo"):
                    cell = ws_ch.find("Logo")
                    ws_ch.update_cell(cell.row, 2, moi)
                    st.success("Logo đã thay đổi!")
                    time.sleep(1)
                    st.rerun()

# --- TRANG GIỎ HÀNG, THÔNG TIN GIỮ NGUYÊN ---
elif chon_menu == "Giỏ Hàng":
    st.title("🛒 Giỏ Hàng")
    if not st.session_state.gio_hang: st.info("Giỏ hàng đang trống.")
    else:
        ws_sp = ket_noi_sheet("SanPham")
        df_sp = pd.DataFrame(ws_sp.get_all_records())
        df_sp['Giá'] = pd.to_numeric(df_sp['Giá'], errors='coerce').fillna(0)
        tong_tien = 0
        ds_order = []
        for id_sp, so_luong in st.session_state.gio_hang.items():
            sp_info = df_sp[df_sp['ID'].astype(str) == id_sp].iloc[0]
            tong_tien += sp_info['Giá'] * so_luong
            ds_order.append(f"{sp_info['Sản phẩm']} x{so_luong}")
            st.write(f"🔹 {sp_info['Sản phẩm']} x{so_luong} : {sp_info['Giá']*so_luong:,} VNĐ")
        
        st.subheader(f"Tổng: {tong_tien:,} VNĐ")
        with st.form("form_order"):
            ten = st.text_input("Họ tên")
            sdt = st.text_input("SĐT")
            dia_chi = st.text_area("Địa chỉ")
            if st.form_submit_button("Xác nhận đặt hàng"):
                if ten and sdt:
                    ws_don = ket_noi_sheet("DonHang")
                    ws_don.append_row([datetime.now().strftime("%d/%m/%Y %H:%M"), ten, sdt, dia_chi, ", ".join(ds_order), sum(st.session_state.gio_hang.values()), f"{tong_tien:,} VNĐ", "Mới"])
                    for id_sp, so_luong in st.session_state.gio_hang.items():
                        cell = ws_sp.find(str(id_sp))
                        old = int(ws_sp.cell(cell.row, 6).value)
                        ws_sp.update_cell(cell.row, 6, old - so_luong)
                    st.success("Đã đặt hàng!")
                    st.session_state.gio_hang = {}
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
