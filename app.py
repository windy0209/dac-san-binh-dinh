import streamlit as st
from streamlit_option_menu import option_menu
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import pandas as pd

# --- CẤU HÌNH TRANG ---
st.set_page_config(page_title="Đặc Sản Bình Định - Xứ Nẫu Quán", layout="wide", page_icon="🍱")

# --- KẾT NỐI GOOGLE SHEETS ---
def connect_to_gsheet():
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        # Lấy thông tin từ Streamlit Secrets
        creds_info = st.secrets["gcp_service_account"]
        creds = Credentials.from_service_account_info(creds_info, scopes=scope)
        client = gspread.authorize(creds)
        
        # THAY 'DonHangBinhDinh' BẰNG TÊN FILE GOOGLE SHEETS CỦA BẠN
        sheet = client.open("DonHangBinhDinh").sheet1
        return sheet
    except Exception as e:
        st.error(f"Lỗi kết nối Google Sheets: {e}")
        return None

# --- CSS TÙY CHỈNH (Giao diện chuyên nghiệp) ---
st.markdown("""
    <style>
    .main { background-color: #f9f9f9; }
    .product-card {
        background-color: white; padding: 15px; border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05); text-align: center;
        border: 1px solid #eee; margin-bottom: 20px;
    }
    .price-text { color: #d32f2f; font-weight: bold; font-size: 20px; }
    .zalo-sidebar {
        background-color: #0068ff; color: white !important;
        padding: 12px; border-radius: 10px; text-align: center;
        display: block; text-decoration: none; font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR & ZALO ---
with st.sidebar:
    st.markdown("<h2 style='text-align: center; color: #d32f2f;'>ĐẶC SẢN BÌNH ĐỊNH</h2>", unsafe_allow_html=True)
    selected = option_menu(
        menu_title=None,
        options=["Trang Chủ", "Sản Phẩm", "Đặt Hàng", "Thông Tin Shop", "Quản Lý"],
        icons=["house", "grid", "cart-check", "info-circle", "table"],
        default_index=0,
    )
    
    st.write("---")
    sdt_zalo = "0901234567"  # THAY SỐ ZALO CỦA BẠN
    st.markdown(f'<a href="https://zalo.me/{sdt_zalo}" target="_blank" class="zalo-sidebar">💬 Nhắn Zalo Tư Vấn</a>', unsafe_allow_html=True)
    st.caption("Hỗ trợ trực tiếp 24/7")

# --- TRANG CHỦ ---
if selected == "Trang Chủ":
    st.title("🏯 Tinh Hoa Ẩm Thực Đất Võ")
    st.image("https://vcdn1-dulich.vnecdn.net/2022/06/03/7-1654247844-3323-1654247920.jpg", use_container_width=True)
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Sản phẩm", "50+")
    col2.metric("Khách hàng", "1.000+")
    col3.metric("Đánh giá", "4.9/5 ⭐")
    
    st.info("📍 Shop chuyên cung cấp sỉ & lẻ Nem Chợ Huyện, Tré Bó Rơm, Rượu Bàu Đá chính gốc.")

# --- SẢN PHẨM ---
elif selected == "Sản Phẩm":
    st.title("🍱 Danh sách sản phẩm")
    products = [
        {"name": "Nem Chợ Huyện", "price": "50.000đ/vỉ", "img": "https://mia.vn/media/uploads/blog-du-lich/nem-cho-huyen-dac-san-binh-dinh-lam-say-long-bao-thuc-khach-1-1652173169.jpg"},
        {"name": "Tré Bó Rơm", "price": "40.000đ/cây", "img": "https://dacsanbinhdinhonline.com/wp-content/uploads/2020/03/tre-bo-rom-binh-dinh.jpg"},
        {"name": "Bánh Ít Lá Gai", "price": "5.000đ/cái", "img": "https://Dacsanbinhdinh.vn/wp-content/uploads/2021/05/banh-it-la-gai.jpg"},
        {"name": "Rượu Bàu Đá", "price": "120.000đ/lít", "img": "https://ruoubaudachinhhieu.com/wp-content/uploads/2018/12/ruou-bau-da-binh-dinh.jpg"}
    ]
    
    cols = st.columns(2)
    for i, p in enumerate(products):
        with cols[i % 2]:
            st.markdown(f"""
                <div class="product-card">
                    <img src="{p['img']}" width="100%" style="height:250px; object-fit:cover; border-radius:10px;">
                    <h3>{p['name']}</h3>
                    <p class="price-text">{p['price']}</p>
                </div>
            """, unsafe_allow_html=True)
            if st.button(f"Chọn mua {p['name']}", key=i):
                st.toast(f"Đã thêm {p['name']} vào danh sách chọn!")

# --- ĐẶT HÀNG (Kết nối Google Sheets) ---
elif selected == "Đặt Hàng":
    st.title("🛒 Thông tin đặt hàng")
    st.write("Vui lòng điền thông tin, đơn hàng sẽ được gửi trực tiếp đến hệ thống quản lý của shop.")
    
    with st.form("order_form", clear_on_submit=True):
        col_in1, col_in2 = st.columns(2)
        with col_in1:
            name = st.text_input("Họ và tên *")
            phone = st.text_input("Số điện thoại *")
        with col_in2:
            address = st.text_area("Địa chỉ nhận hàng *")
        
        items = st.multiselect("Sản phẩm muốn đặt", ["Nem Chợ Huyện", "Tré Bó Rơm", "Bánh Ít Lá Gai", "Rượu Bàu Đá", "Bún Song Thằn"])
        note = st.text_input("Ghi chú thêm (Số lượng, yêu cầu khác...)")
        
        submitted = st.form_submit_button("XÁC NHẬN ĐẶT HÀNG")
        
        if submitted:
            if name and phone and address and items:
                with st.spinner('Đang gửi đơn hàng...'):
                    sheet = connect_to_gsheet()
                    if sheet:
                        new_row = [
                            datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                            name, phone, address, 
                            ", ".join(items), 
                            note, 
                            "Chờ xử lý"
                        ]
                        sheet.append_row(new_row)
                        st.success("🎉 Đơn hàng đã gửi thành công! Shop sẽ gọi xác nhận ngay.")
                        st.balloons()
            else:
                st.warning("Vui lòng điền đầy đủ các mục có dấu (*)")

# --- QUẢN LÝ (Xem trực tiếp từ Sheets) ---
elif selected == "Quản Lý":
    st.title("📊 Quản lý đơn hàng (Admin)")
    password = st.text_input("Mật khẩu truy cập", type="password")
    
    if password == "binhdinh123": # Thay mật khẩu của bạn
        sheet = connect_to_gsheet()
        if sheet:
            data = sheet.get_all_records()
            if data:
                df = pd.DataFrame(data)
                st.dataframe(df, use_container_width=True)
                
                # Nút tải file Excel
                csv = df.to_csv(index=False).encode('utf-8-sig')
                st.download_button("📥 Tải danh sách đơn hàng (.csv)", csv, "don_hang.csv", "text/csv")
            else:
                st.info("Chưa có dữ liệu đơn hàng trên Google Sheets.")
    elif password != "":
        st.error("Mật khẩu không đúng!")

# --- THÔNG TIN SHOP ---
elif selected == "Thông Tin Shop":
    st.title("🏠 Thông tin Xứ Nẫu Quán")
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("""
        **Địa chỉ gốc:** Thị trấn Tuy Phước, Huyện Tuy Phước, Tỉnh Bình Định.  
        **Văn phòng đại diện:** TP. Quy Nhơn, Bình Định.  
        **Hotline:** 0901.234.567  
        **Email:** thinhbinhdinh@gmail.com
        """)
    with col_b:
        st.info("Chúng tôi cam kết mang đến sản phẩm sạch, không chất bảo quản, giữ nguyên hương vị truyền thống quê hương.")
