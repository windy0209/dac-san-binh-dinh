import streamlit as st
from streamlit_option_menu import option_menu
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import pandas as pd
import time
import re

# =============================
# 1. CẤU HÌNH & CSS (TỐI ƯU GIAO DIỆN)
# =============================
st.set_page_config(page_title="Xứ Nẫu Store", layout="wide", page_icon="🌿")

st.markdown("""
<style>
    /* Tổng thể */
    .stApp { background-color: #f4f7f4; }
    .block-container { padding: 1rem 0.5rem !important; }
    
    /* Menu ngang cuộn mượt trên Mobile */
    div[data-testid="stHorizontalBlock"] {
        display: flex !important; flex-wrap: nowrap !important;
        overflow-x: auto !important; -webkit-overflow-scrolling: touch;
        gap: 8px; padding: 10px 0;
    }
    div[data-testid="stHorizontalBlock"]::-webkit-scrollbar { display: none; }
    
    /* Card sản phẩm đổ bóng */
    .product-box {
        background: white; padding: 12px; border-radius: 15px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05); text-align: center;
        border: 1px solid #eee; margin-bottom: 15px;
    }
    .product-img { width: 100%; height: 130px; object-fit: cover; border-radius: 10px; }
    
    /* Badge giỏ hàng */
    .cart-badge {
        background-color: #d32f2f; color: white; padding: 2px 6px;
        border-radius: 50%; font-size: 10px; position: relative; top: -10px;
    }
</style>
""", unsafe_allow_html=True)

# =============================
# 2. KẾT NỐI DỮ LIỆU
# =============================
@st.cache_resource
def connect_gsheet(sheet_name):
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        if "gcp_service_account" in st.secrets:
            creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scope)
        else:
            creds = Credentials.from_service_account_file("credentials.json", scopes=scope)
        return gspread.authorize(creds).open("DonHangDacSanBinhDinh").worksheet(sheet_name)
    except: return None

# Khởi tạo giỏ hàng
if "gio_hang" not in st.session_state: st.session_state.gio_hang = {}
if "logged_in" not in st.session_state: st.session_state.logged_in = False

# =============================
# 3. HEADER & MENU BỔ SUNG ICON
# =============================
total_items = sum(st.session_state.gio_hang.values())
cart_label = f"Giỏ Hàng ({total_items})" if total_items > 0 else "Giỏ Hàng"

with st.container():
    menu = option_menu(
        menu_title=None,
        options=["Trang Chủ", "Cửa Hàng", "Giỏ Hàng", "Thông Tin", "Quản Trị"],
        icons=["house-door", "bag-heart", "cart3", "info-circle", "person-badge"],
        menu_icon="cast", default_index=0, orientation="horizontal",
        styles={
            "container": {"padding": "0!important", "background-color": "white", "border-radius": "12px"},
            "nav-link": {"font-size": "0.85rem", "padding": "10px", "white-space": "nowrap"},
            "nav-link-selected": {"background-color": "#2e7d32"},
        }
    )

# =============================
# 4. CHI TIẾT CÁC TAB
# =============================

if menu == "Trang Chủ":
    st.markdown("<h2 style='text-align:center;color:#2e7d32;'>🌿 ĐẶC SẢN BÌNH ĐỊNH</h2>", unsafe_allow_html=True)
    st.image("https://raw.githubusercontent.com/windy0209/dac-san-binh-dinh/main/banner.png", use_container_width=True) # Thay link banner của bạn
    
    col_feat1, col_feat2, col_feat3 = st.columns(3)
    col_feat1.metric("Chất lượng", "100% Sạch")
    col_feat2.metric("Giao hàng", "Toàn quốc")
    col_feat3.metric("Hỗ trợ", "24/7")

elif menu == "Cửa Hàng":
    ws = connect_gsheet("SanPham")
    if ws:
        df = pd.DataFrame(ws.get_all_records())
        
        # Bộ lọc cải tiến
        c_search, c_cat = st.columns([2, 1])
        search_query = c_search.text_input("🔍 Tìm tên sản phẩm...", key="search")
        categories = ["Tất cả"] + sorted(df["Loại"].unique().tolist()) if "Loại" in df.columns else ["Tất cả"]
        selected_cat = c_cat.selectbox("📂 Danh mục", categories)
        
        # Lọc dữ liệu
        df_display = df[df["Sản phẩm"].str.contains(search_query, case=False)]
        if selected_cat != "Tất cả":
            df_display = df_display[df_display["Loại"] == selected_cat]
            
        cols = st.columns(2)
        for i, (_, row) in enumerate(df_display.iterrows()):
            with cols[i % 2]:
                st.markdown(f"""
                <div class="product-box">
                    <img src="{row['Hình ảnh']}" class="product-img">
                    <div style="font-weight:bold; margin-top:8px; height:40px; overflow:hidden;">{row['Sản phẩm']}</div>
                    <div style="color:#f39c12; font-size:1.1rem; font-weight:700;">{row['Giá']:,}đ</div>
                    <div style="color:gray; font-size:0.7rem;">Kho: {row['Tồn kho']}</div>
                </div>
                """, unsafe_allow_html=True)
                if int(row["Tồn kho"]) > 0:
                    if st.button(f"THÊM 🛒", key=f"add_{row['ID']}"):
                        st.session_state.gio_hang[str(row["ID"])] = st.session_state.gio_hang.get(str(row["ID"]), 0) + 1
                        st.toast(f"Đã thêm {row['Sản phẩm']} vào giỏ!")
                        time.sleep(0.5); st.rerun()
                else: st.button("HẾT HÀNG", disabled=True, key=f"sold_{row['ID']}")

elif menu == "Giỏ Hàng":
    st.subheader("🛒 Chi tiết đơn hàng")
    if not st.session_state.gio_hang:
        st.info("Giỏ hàng của bạn đang trống. Hãy chọn món ngon nhé!")
    else:
        ws_sp = connect_gsheet("SanPham")
        df_sp = pd.DataFrame(ws_sp.get_all_records())
        total_price = 0
        order_details = []
        
        for sp_id, qty in list(st.session_state.gio_hang.items()):
            item = df_sp[df_sp['ID'].astype(str) == sp_id].iloc[0]
            subtotal = item['Giá'] * qty
            total_price += subtotal
            order_details.append(f"{item['Sản phẩm']} x{qty}")
            
            c_name, c_qty, c_del = st.columns([3, 1, 1])
            c_name.write(f"**{item['Sản phẩm']}**\n{item['Giá']:,}đ")
            c_qty.write(f"x{qty}")
            if c_del.button("❌", key=f"del_{sp_id}"):
                del st.session_state.gio_hang[sp_id]; st.rerun()
        
        st.divider()
        st.write(f"### Tổng cộng: :red[{total_price:,} VNĐ]")
        
        with st.expander("🚚 Thông tin nhận hàng", expanded=True):
            with st.form("checkout_form"):
                u_name = st.text_input("Họ và Tên *")
                u_phone = st.text_input("Số điện thoại *")
                u_address = st.text_area("Địa chỉ giao hàng *")
                u_note = st.text_input("Ghi chú (Ví dụ: Giao giờ hành chính)")
                
                if st.form_submit_button("XÁC NHẬN ĐẶT HÀNG"):
                    if u_name and u_phone and u_address:
                        ws_don = connect_gsheet("DonHang")
                        ws_don.append_row([
                            datetime.now().strftime("%d/%m/%Y %H:%M"), u_name, u_phone, u_address, 
                            ", ".join(order_details), sum(st.session_state.gio_hang.values()), 
                            f"{total_price:,} VNĐ", "Mới", u_note
                        ])
                        # Cập nhật tồn kho thực tế
                        for sp_id, qty in st.session_state.gio_hang.items():
                            cell = ws_sp.find(df_sp[df_sp['ID'].astype(str) == sp_id].iloc[0]['Sản phẩm'])
                            old_stock = int(ws_sp.cell(cell.row, 6).value)
                            ws_sp.update_cell(cell.row, 6, old_stock - qty)
                        
                        st.session_state.gio_hang = {}
                        st.success("Đơn hàng đã được gửi đi! Chúng tôi sẽ gọi xác nhận sớm."); st.balloons()
                        time.sleep(2); st.rerun()
                    else: st.error("Vui lòng điền đủ thông tin dấu (*)")

elif menu == "Quản Trị":
    if not st.session_state.logged_in:
        c_l, c_m, c_r = st.columns([1,2,1])
        with c_m:
            st.markdown("### 🔐 Hệ thống Admin")
            user = st.text_input("Tài khoản")
            pw = st.text_input("Mật khẩu", type="password")
            if st.button("Đăng nhập"):
                if user == "admin" and pw == "binhdinh0209":
                    st.session_state.logged_in = True; st.rerun()
                else: st.error("Sai thông tin!")
    else:
        st.sidebar.button("Đăng xuất", on_click=lambda: st.session_state.update({"logged_in": False}))
        tab_k, tab_d, tab_bc = st.tabs(["📦 Kho Hàng", "📜 Đơn Hàng", "📈 Báo Cáo"])
        
        ws_sp = connect_gsheet("SanPham")
        ws_don = connect_gsheet("DonHang")
        
        with tab_k:
            df_k = pd.DataFrame(ws_sp.get_all_records())
            df_k_edit = st.data_editor(df_k, num_rows="dynamic", use_container_width=True)
            if st.button("💾 Cập nhật kho"):
                ws_sp.clear(); ws_sp.update([df_k_edit.columns.values.tolist()] + df_k_edit.values.tolist())
                st.success("Kho đã lưu!")

        with tab_d:
            df_d_old = pd.DataFrame(ws_don.get_all_records())
            # Tính năng Dropdown trạng thái trong bảng
            df_d_new = st.data_editor(df_d_old, column_config={
                "Trạng thái": st.column_config.SelectboxColumn(
                    "Trạng thái", options=["Mới", "Đang giao", "Hoàn thành", "Hủy"], required=True
                )
            }, use_container_width=True)
            
            if st.button("🚀 Cập nhật & Hoàn kho"):
                for idx in range(len(df_d_old)):
                    old_s = df_d_old.iloc[idx]['Trạng thái']
                    new_s = df_d_new.iloc[idx]['Trạng thái']
                    
                    if old_s != "Hủy" and new_s == "Hủy":
                        items = str(df_d_new.iloc[idx]['Sản phẩm']).split(", ")
                        for it in items:
                            m = re.search(r"(.+)\s+x(\d+)", it)
                            if m:
                                name, q = m.group(1).strip(), int(m.group(2))
                                try:
                                    c = ws_sp.find(name)
                                    ws_sp.update_cell(c.row, 6, int(ws_sp.cell(c.row, 6).value) + q)
                                    st.toast(f"Đã hoàn {q} {name} vào kho")
                                except: pass
                
                ws_don.clear(); ws_don.update([df_d_new.columns.values.tolist()] + df_d_new.values.tolist())
                st.success("Đã cập nhật tất cả đơn hàng!"); st.rerun()

        with tab_bc:
            df_bc = pd.DataFrame(ws_don.get_all_records())
            st.metric("Tổng đơn hàng", len(df_bc))
            st.metric("Đơn mới", len(df_bc[df_bc["Trạng thái"] == "Mới"]))
            st.write("Dữ liệu chi tiết:")
            st.dataframe(df_bc)

elif menu == "Thông Tin":
    st.markdown("""
    <div style="background:white; padding:25px; border-radius:15px; border-left: 5px solid #2e7d32;">
        <h3>🏡 XỨ NẪU STORE</h3>
        <p><b>📍 Địa chỉ:</b> 96 Ngô Đức Đệ, Bình Định, An Nhơn, Bình Định</p>
        <p><b>📞 Hotline:</b> 0932.642.376</p>
        <p><b>📧 Email:</b> miendatvo86@gmail.com</p>
        <hr>
        <p>🚚 <i>Chuyên cung cấp Nem Chả, Tré, Bánh Ít lá gai và các loại đặc sản Bình Định chính gốc.</i></p>
    </div>
    """, unsafe_allow_html=True)
    st.map(pd.DataFrame({'lat': [13.8930], 'lon': [109.1002]}))
