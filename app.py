import streamlit as st
from streamlit_option_menu import option_menu
import sqlite3
from datetime import datetime

# --- KHỞI TẠO DATABASE ---
def init_db():
    conn = sqlite3.connect('don_hang.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            phone TEXT,
            address TEXT,
            products TEXT,
            payment TEXT,
            order_date TEXT
        )
    ''')
    conn.commit()
    conn.close()

def save_order(name, phone, address, products, payment):
    conn = sqlite3.connect('don_hang.db')
    c = conn.cursor()
    # Chuyển list sản phẩm thành chuỗi để lưu vào DB
    products_str = ", ".join(products)
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute('''
        INSERT INTO orders (name, phone, address, products, payment, order_date)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (name, phone, address, products_str, payment, now))
    conn.commit()
    conn.close()

# Gọi hàm khởi tạo DB khi chạy app
init_db()

# --- CẤU HÌNH GIAO DIỆN (Giữ nguyên phần CSS từ file trước) ---
st.set_page_config(page_title="Đặc Sản Bình Định - Admin", layout="wide")

with st.sidebar:
    selected = option_menu(
        "Menu Hệ Thống",
        ["Trang Chủ", "Sản Phẩm", "Đặt Hàng", "Quản Lý Đơn (Admin)"], 
        icons=["house", "bag", "cart-check", "database-lock"],
        menu_icon="cast", default_index=0
    )

# --- PHẦN ĐẶT HÀNG (CẬP NHẬT) ---
if selected == "Đặt Hàng":
    st.title("🛒 Xác Nhận Đặt Hàng")
    with st.form("order_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Họ và tên *")
            phone = st.text_input("Số điện thoại *")
        with col2:
            address = st.text_area("Địa chỉ chi tiết *")
        
        items = st.multiselect("Chọn đặc sản", ["Nem Chợ Huyện", "Tré Bó Rơm", "Bánh Ít Lá Gai", "Rượu Bàu Đá"])
        payment = st.selectbox("Thanh toán", ["Tiền mặt (COD)", "Chuyển khoản"])
        
        submitted = st.form_submit_button("Gửi Đơn Hàng")
        
        if submitted:
            if name and phone and address and items:
                save_order(name, phone, address, items, payment)
                st.success(f"Cảm ơn {name}! Đơn hàng đã được lưu vào hệ thống.")
                st.balloons()
            else:
                st.error("Vui lòng điền đầy đủ thông tin có dấu (*)")

# --- PHẦN QUẢN LÝ ĐƠN HÀNG (DÀNH CHO CHỦ SHOP) ---
elif selected == "Quản Lý Đơn (Admin)":
    st.title("📊 Danh Sách Đơn Hàng Mới")
    
    # Đọc dữ liệu từ SQLite
    conn = sqlite3.connect('don_hang.db')
    import pandas as pd
    df = pd.read_sql_query("SELECT * FROM orders ORDER BY id DESC", conn)
    conn.close()

    if not df.empty:
        # Hiển thị bảng dữ liệu chuyên nghiệp bằng dataframe
        st.dataframe(df, use_container_width=True)
        
        # Nút xuất file Excel (tùy chọn)
        csv = df.to_csv(index=False).encode('utf-8-sig')
        st.download_button("Tải danh sách đơn hàng (.csv)", csv, "don_hang.csv", "text/csv")
    else:
        st.info("Chưa có đơn hàng nào được đặt.")

# (Các phần Trang Chủ, Sản Phẩm bạn giữ nguyên code từ bài trước nhé)
