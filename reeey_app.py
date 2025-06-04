import streamlit as st
from io import BytesIO
from fpdf import FPDF
import pandas as pd
from datetime import datetime
import base64
import qrcode
from PIL import Image
import os

st.set_page_config(page_title="Reyy's Bakery", layout="wide")

menu_harga = {
    "Choco Cookies": {"harga": 15000, "gambar": "https://joyfoodsunshine.com/wp-content/uploads/2018/02/best-chocolate-chip-cookies-recipe-4.jpg"},
    "Choco Bread": {"harga": 10000, "gambar": "https://kirbiecravings.com/wp-content/uploads/2022/09/2-ingredient-chocolate-bread-6a-700x741.jpg"},
    "Choco Cake": {"harga": 20000, "gambar": "https://stephaniessweets.com/wp-content/uploads/2020/05/IMG_0243.jpg"},
    "Choco Crepe": {"harga": 15000, "gambar": "https://emmaduckworthbakes.com/wp-content/uploads/2023/02/Chocolate-Crepes-with-strawberries.jpg"},
    "Choco Chiffon": {"harga": 20000, "gambar": "https://www.nordicware.com/wp-content/uploads/2021/04/51122_Formed_Bundt_02_1K__95956.1719496681.1280.1280-960x960.jpg"},
    "Choco Ice Cream": {"harga": 5000, "gambar": "https://joyfoodsunshine.com/wp-content/uploads/2020/06/homemade-chocolate-ice-cream-recipe-11.jpg"},
    "Choco Milkshake": {"harga": 15000, "gambar": "https://www.mrishtanna.com/wp-content/uploads/2018/04/vegan-chocolate-milkshake-recipe.jpg"},
    "Choco Ice": {"harga": 10000, "gambar": "https://coffeeatthree.com/wp-content/uploads/iced-chocolate-almondmilk-shaken-espresso-featured.jpg"},
    "Choco Hot": {"harga": 10000, "gambar": "https://www.bunsenburnerbakery.com/wp-content/uploads/2017/11/decadently-thick-hot-chocolate-square-31-735x735.jpg"}
}

if "pesanan" not in st.session_state:
    st.session_state.pesanan = {}

st.title("`~` REYY'S BAKERY `~` 🍫")
st.subheader(">>> CHOCO EDITION <<<")

menu = ["Tentang Toko", "Menu", "Tambah Pesanan", "Lihat Pesanan", "Total & Bayar"]
pilihan = st.sidebar.radio("Menu Utama", menu)

if pilihan == "Tentang Toko":
    st.markdown("""
    ## 🫑 Tentang Reyy's Bakery
    Kami menyajikan berbagai makanan dan minuman yang serba cokelat.  
    Mulai dari cookies, kue, roti, hingga minuman segar dan hangat.  
    Terima kasih sudah berkunjung! 🍫
    """)

elif pilihan == "Menu":
    st.header("📜 Daftar Menu")
    cols = st.columns(3)
    for idx, (item, data) in enumerate(menu_harga.items()):
        with cols[idx % 3]:
            st.image(data["gambar"], width=150)
            st.write(f"**{item}**\nRp{data['harga']:,}")

elif pilihan == "Tambah Pesanan":
    st.header("📝 Tambah Pesanan")
    pilihan_menu = st.selectbox("Pilih Menu", list(menu_harga.keys()))
    jumlah = st.number_input("Jumlah", min_value=1, step=1)
    if st.button("Tambahkan"):
        st.session_state.pesanan[pilihan_menu] = st.session_state.pesanan.get(pilihan_menu, 0) + jumlah
        st.success(f"{jumlah} x {pilihan_menu} ditambahkan.")

elif pilihan == "Lihat Pesanan":
    st.header("📦 Pesanan Anda")
    if not st.session_state.pesanan:
        st.info("Belum ada pesanan.")
    else:
        for item, jumlah in st.session_state.pesanan.items():
            harga = menu_harga[item]["harga"]
            st.write(f"{item} x{jumlah} = Rp{harga * jumlah:,}")

elif pilihan == "Total & Bayar":
    st.header("💳 Total Pembayaran")
    if not st.session_state.pesanan:
        st.info("Belum ada pesanan.")
    else:
        nama_pembeli = st.text_input("🢍 Nama Pembeli", max_chars=50)
        total = sum(menu_harga[item]["harga"] * jml for item, jml in st.session_state.pesanan.items())
        for item, jumlah in st.session_state.pesanan.items():
            st.write(f"{item} x{jumlah} = Rp{menu_harga[item]['harga'] * jumlah:,}")
        st.markdown(f"### 💰 TOTAL: Rp{total:,}")

        metode = st.selectbox("Metode Pembayaran", ["Tunai", "Non-tunai"])

        if metode == "Non-tunai" and nama_pembeli:
            qr_data = f"Pembeli: {nama_pembeli}\nTotal: Rp{total:,}\nWaktu: {datetime.now()}"
            qr = qrcode.make(qr_data)
            qr_path = "/tmp/qr_code.png"
            qr.save(qr_path)
            st.image(qr_path, caption="QR Code Pembayaran", width=250)

        if st.button("Bayar"):
            if not nama_pembeli.strip():
                st.warning("Mohon isi nama pembeli terlebih dahulu.")
                st.stop()

            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            st.success("Pembayaran berhasil. Terima kasih! 🫓")

            # Simpan ke Excel (riwayat)
            riwayat_file = "riwayat_pesanan.xlsx"
            new_data = [
                {
                    "Waktu": now,
                    "Nama": nama_pembeli,
                    "Item": item,
                    "Jumlah": jml,
                    "Subtotal": menu_harga[item]["harga"] * jml,
                    "Metode": metode
                }
                for item, jml in st.session_state.pesanan.items()
            ]
            df_new = pd.DataFrame(new_data)
            if os.path.exists(riwayat_file):
                df_existing = pd.read_excel(riwayat_file)
                df_all = pd.concat([df_existing, df_new], ignore_index=True)
            else:
                df_all = df_new
            df_all.to_excel(riwayat_file, index=False)

            # PDF
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", "B", 16)
            pdf.cell(0, 10, "Reyy's Bakery - Struk Pembelian", ln=True, align="C")
            pdf.set_font("Arial", size=12)
            pdf.cell(0, 10, f"Nama: {nama_pembeli}", ln=True)
            pdf.cell(0, 10, f"Tanggal: {now}", ln=True)
            pdf.cell(0, 10, "-"*40, ln=True)
            for item, jml in st.session_state.pesanan.items():
                subtotal = menu_harga[item]["harga"] * jml
                pdf.cell(0, 10, f"{item} x{jml} = Rp{subtotal:,}", ln=True)
            pdf.cell(0, 10, "-"*40, ln=True)
            pdf.cell(0, 10, f"TOTAL = Rp{total:,}", ln=True)
            pdf.cell(0, 10, f"Metode: {metode}", ln=True)

            # FIXED: langsung tulis ke BytesIO, bukan encode ke bytes manual
            pdf_output = BytesIO()
            pdf.output(pdf_output)
            pdf_output.seek(0)

            # Download Buttons
            col1, col2 = st.columns(2)
            with col1:
                st.download_button(
                    "📅 Unduh Riwayat Excel",
                    data=df_all.to_excel(index=False),
                    file_name="riwayat_pesanan.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            with col2:
                st.download_button(
                    "🫒 Unduh Struk PDF",
                    data=pdf_output.getvalue(),
                    file_name="struk.pdf",
                    mime="application/pdf"
                )

            # Gunakan untuk preview
            encoded_pdf = base64.b64encode(pdf_output.getvalue()).decode('utf-8')
            st.markdown(
                f'<iframe src="data:application/pdf;base64,{encoded_pdf}" width="100%" height="500px" type="application/pdf"></iframe>',
                unsafe_allow_html=True
            )

            st.balloons()
            st.session_state.pesanan.clear()
