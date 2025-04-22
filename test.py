import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd
import mysql.connector
from sklearn.neighbors import KNeighborsClassifier
import pickle
import os
import uuid
import plotly.express as px
import streamlit.components.v1 as components

# Set halaman menjadi wide (lebar)
st.set_page_config(page_title="KNN", page_icon="📊", layout="wide")

with open("style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

st.markdown(
    """
    <head>
        <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css" rel="stylesheet">
    </head>
""",
    unsafe_allow_html=True,
)


# ------------------------ Koneksi ke Database ------------------------
def get_connection():
    return mysql.connector.connect(
        host="localhost", user="root", password="root", database="mydb"
    )


# ------------------------ Cek Login ------------------------
def check_login(username, password):
    db = get_connection()
    cursor = db.cursor()
    cursor.execute(
        "SELECT * FROM admin WHERE username=%s AND password=%s", (username, password)
    )
    user = cursor.fetchone()
    cursor.close()
    db.close()
    return user


# ------------------------ Dapatkan ID Admin ------------------------
def get_admin_id(username):
    db = get_connection()
    cursor = db.cursor()
    cursor.execute("SELECT idAdmin FROM admin WHERE username=%s", (username,))
    result = cursor.fetchone()
    cursor.close()
    db.close()
    return result[0] if result else None


# ------------------------ Load Data Training ------------------------
def load_data():
    db = get_connection()
    query = "SELECT * FROM dataTraining"
    df = pd.read_sql(query, db)
    db.close()
    return df


# Fungsi untuk mengambil informasi update terakhir
def get_last_update_info():
    db = get_connection()
    cursor = db.cursor(dictionary=True)
    query = """
        SELECT update_at, Admin_idAdmin 
        FROM dataTraining 
        ORDER BY update_at DESC 
        LIMIT 1;
    """
    cursor.execute(query)
    result = cursor.fetchone()
    db.close()

    return result


def get_info_pembaruan_terakhir():
    data = get_last_update_info()

    if data:
        last_update = data["update_at"].strftime("%d/%m/%Y %H:%M:%S")
        admin_id = data["Admin_idAdmin"]

        # Ambil username dari ID admin
        db = get_connection()
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT username FROM admin WHERE idAdmin = %s", (admin_id,))
        user = cursor.fetchone()
        cursor.close()
        db.close()

        username = user["username"] if user else f"Admin ID: {admin_id}"
        return f"Diperbarui oleh {username} pada {last_update}"
    else:
        return "Belum ada data pembaruan."


# ------------------------ Simpan dan Load Model ------------------------
def save_model(model):
    with open("model_knn.pkl", "wb") as f:
        pickle.dump(model, f)


def load_model():
    if os.path.exists("model_knn.pkl"):
        with open("model_knn.pkl", "rb") as f:
            return pickle.load(f)
    return None


# ------------------------ Melatih Model Secara Otomatis ------------------------
def train_model():
    df = load_data()
    if not df.empty:
        X = df[["q1", "q2", "q3", "q4", "q5", "q6", "q7", "q8", "q9"]]
        y = df["q10"]
        knn = KNeighborsClassifier(n_neighbors=3)
        knn.fit(X, y)
        save_model(knn)


# ------------------------ Halaman Login ------------------------
def login_page():
    st.markdown(
        """
        <style>
        /* Memastikan form ditengah dengan padding yang dinamis */
        .st-emotion-cache-yw8pof {
            padding: 10rem 35rem 0 35rem;  /* Padding default untuk layar besar */
        }

        /* Responsif: mengurangi padding pada layar yang lebih kecil */
        @media (max-width: 1500px) {
            .st-emotion-cache-yw8pof {
                padding: 6rem 30rem 0 30rem;  /* Menyesuaikan padding di layar medium */
            }
        }

        @media (max-width: 1200px) {
            .st-emotion-cache-yw8pof {
                padding: 4rem 25rem 0 25rem;  /* Menyesuaikan padding di layar kecil */
            }
        }
                
        @media (max-width: 1000px) {
            .st-emotion-cache-yw8pof {
                padding: 4rem 20rem 0 20rem;  /* Menyesuaikan padding di layar kecil */
            }
        }

        @media (max-width: 900px) {
            .st-emotion-cache-yw8pof {
                padding: 2rem 5rem 0 5rem;  /* Menyesuaikan padding di layar ponsel */
            }
        }

        /* CSS untuk menempatkan judul login di tengah */
        .login-title {
            text-align: center;
            font-size: 2rem;
        }
        
        </style>
    """,
        unsafe_allow_html=True,
    )

    # Kontainer untuk menempatkan form di tengah
    with st.container():
        with st.form(key="login_form", clear_on_submit=True):
            # Menambahkan div dengan class untuk mengatur form
            st.markdown('<div class="login-container">', unsafe_allow_html=True)

            # Judul login yang diposisikan di tengah
            st.markdown('<h1 class="login-title">Login</h1>', unsafe_allow_html=True)

            # Input username dan password
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")

            # Tombol submit untuk login
            if st.form_submit_button("Login"):
                if check_login(username, password):
                    # Menyimpan informasi login dalam session state
                    st.session_state["login"] = True
                    st.session_state["username"] = username
                    st.success("Login berhasil!")
                    st.rerun()
                else:
                    st.error("Username atau password salah")

            st.markdown("</div>", unsafe_allow_html=True)


# ------------------------ Halaman Utama Aplikasi ------------------------
def main_app():
    with st.sidebar:
        selected = option_menu(
            menu_title="Menu",
            options=[
                "Dashboard",
                "Data Training",
                "Kepuasan Pelanggan",
                "History",
                "Logout",
            ],
            icons=[
                "speedometer",
                "database",
                "person",
                "clock-history",
                "box-arrow-right",
            ],
            menu_icon="cast",
            default_index=0,
            styles={
                "icon": {"font-size": "18px"},  # Ukuran font ikon
                "nav-link": {"font-size": "16px"},  # Ukuran font untuk teks menu
                "nav-link-selected": {
                    "background-color": "#4e5d91",
                    "color": "white",
                    "font-size": "16px",  # Ukuran font tetap sama ketika dipilih
                    "font-weight": "bold",  # Menambah efek bold pada teks yang dipilih
                },
            },
        )

    if selected == "Dashboard":
        st.markdown(
            """
            <div style="display: flex; align-items: center; gap: 1rem;">
                <div style="background-color: #4e5d91; border-radius: 20px; width: 60px; height: 40px; display: flex; justify-content: center; align-items: center;">
                    <i class="fas fa-tachometer-alt" style="color: white; font-size: 20px;"></i>
                </div>  
                <h1 style="margin: 0;">Dashboard</h1>
            </div>
        """,
            unsafe_allow_html=True,
        )

        db = get_connection()

        # Jumlah Data Training
        cursor = db.cursor()
        cursor.execute("SELECT COUNT(*) FROM dataTraining")
        data_training_count = cursor.fetchone()[0]

        # Total Data Kepuasan Pelanggan
        cursor.execute("SELECT COUNT(*) FROM kepuasanPelanggan")
        kepuasan_pelanggan_count = cursor.fetchone()[0]

        # Jumlah Riwayat Klasifikasi
        cursor.execute("SELECT COUNT(*) FROM history")
        history_count = cursor.fetchone()[0]

        cursor.close()
        db.close()

        # Menampilkan card dengan Tailwind CSS dan data
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(
                f"""
                <div class="rounded-lg overflow-hidden shadow-md p-6 bg-gray-200 text-black flex items-center justify-center space-x-4">
                    <span class="w-20 h-20 bg-yellow-500 text-indigo-500 flex items-center justify-center rounded-full">
                        <i class="fas fa-database text-5xl text-white"></i>
                    </span>
                    <div class="text-black">
                        <h2 style="font-size: 1rem; font-weight: bold; margin-bottom: -2rem;">Data Training</h2>
                        <p style="font-size: 4rem; font-weight: bold;">{data_training_count}</p>
                    </div>
                </div>
            """,
                unsafe_allow_html=True,
            )

        with col2:
            st.markdown(
                f"""
                <div class="rounded-lg overflow-hidden shadow-md p-6 bg-gray-200 text-black flex items-center justify-center space-x-4">
                    <span class="w-20 h-20 bg-green-600 text-green-600 flex items-center justify-center rounded-full">
                        <i class="fas fa-user text-5xl text-white"></i>
                    </span>
                    <div class="text-black">
                        <h2 style="font-size: 1rem; font-weight: bold; margin-bottom: -2rem;"> Data Pelanggan</h2>
                        <p style="font-size: 4rem; font-weight: bold;">{kepuasan_pelanggan_count}</p>
                    </div>
                </div>
            """,
                unsafe_allow_html=True,
            )

        with col3:
            st.markdown(
                f"""
                <div class="rounded-lg overflow-hidden shadow-md p-6 bg-gray-200 text-black flex items-center justify-center space-x-4">
                    <span class="w-20 h-20 bg-red-600 text-red-600 flex items-center justify-center rounded-full">
                        <i class="fas fa-history text-5xl text-white"></i>
                    </span>
                    <div class="text-black">
                        <h2 style="font-size: 1rem; font-weight: bold; margin-bottom: -2rem;">Riwayat Klasifikasi</h2>
                        <p style="font-size: 4rem; font-weight: bold;">{history_count}</p>
                    </div>
                </div>
            """,
                unsafe_allow_html=True,
            )

        st.markdown(
            """
            <style>
                .st-ae {
                    box-shadow: 
                        0 4px 6px -1px rgba(0, 0, 0, 0.1),
                        0 2px 4px -2px rgba(0, 0, 0, 0.1) !important;
                    border-radius: 8px !important; /* Opsional: bisa disesuaikan */
                }
                .st-emotion-cache-ue6h4q {
                min-height:0;    
                }
            </style>
        """,
            unsafe_allow_html=True,
        )

        # Ambil data dari tabel history
        query = "SELECT updated_at, q10 FROM history"
        conn = get_connection()  # Fix: define conn here
        df = pd.read_sql(query, conn)

        # Tutup koneksi setelah ambil data
        conn.close()

        # Konversi kolom timestamp ke hanya tanggal
        df["tanggal"] = pd.to_datetime(df["updated_at"]).dt.date

        # Kelompokkan berdasarkan tanggal dan nilai q10
        summary = df.groupby(["tanggal", "q10"]).size().unstack(fill_value=0)

        # Ubah nama kolom untuk keterbacaan
        summary.columns = ["Kurang Puas", "Puas", "Sangat Puas"]

        # Reset index agar tanggal jadi kolom biasa
        summary_reset = summary.reset_index()

        # Format kolom tanggal menjadi 'dd-mm-yyyy'
        summary_reset["tanggal"] = summary_reset["tanggal"].apply(
            lambda x: x.strftime("%d-%m-%Y")
        )

        col1, col2 = st.columns(2)
        with col1:
            # Siapkan kolom layout untuk grafik
            fig_line = px.line(
                summary_reset,
                x="tanggal",
                y=summary.columns,
                # title="Kepuasan per Tanggal",
                labels={"value": "Jumlah Responden", "tanggal": "Tanggal"},
                color_discrete_map={
                    "Sangat Puas": "#059669",
                    "Puas": "#f59e0b",
                    "Kurang Puas": "#d62728",
                },
            )
            fig_line.update_layout(
                xaxis=dict(tickformat="%Y-%m-%d"),
                xaxis_title="Tanggal",
                yaxis_title="Jumlah Responden",
                plot_bgcolor="#e5e7eb",
                paper_bgcolor="#e5e7eb",
                font_color="black",
            )

            html_chart = fig_line.to_html(full_html=False)

            # Menampilkan grafik di atas
            components.html(
                f"""
                <div style="
                    background-color: #e5e7eb;
                    border-radius: 16px;
                    padding: 10px;
                    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1),
                    0 2px 4px -2px rgba(0, 0, 0, 0.1);
                ">
                    {html_chart}
                </div>
            """,
                height=500,
            )

        with col2:

            # # Tampilkan dropdown
            # selected_date = st.selectbox("", summary_reset['tanggal'].astype(str).tolist())

            # # Filter data untuk tanggal yang dipilih
            # bar_data = summary_reset[summary_reset['tanggal'].astype(str) == selected_date]

            # Hitung total jumlah per kategori untuk semua tanggal
            total_summary = summary.sum().reset_index()
            total_summary.columns = ["Kategori", "Jumlah"]

            # Chart total keseluruhan
            fig_total = px.bar(
                total_summary,
                x="Kategori",
                y="Jumlah",
                color="Kategori",
                # title='Jumlah Keseluruhan Responden per Kategori',
                color_discrete_map={
                    "Sangat Puas": "#059669",
                    "Puas": "#f59e0b",
                    "Kurang Puas": "#d62728",
                },
            )

            # Update layout dengan menambahkan efek rounded corners pada batang
            fig_total.update_traces(marker=dict(cornerradius=10))  # Efek rounded corner

            fig_total.update_layout(
                plot_bgcolor="#e5e7eb",
                paper_bgcolor="#e5e7eb",
                font_color="black",
            )

            html_bar = fig_total.to_html(full_html=False)
            # Tampilkan chart-nya
            components.html(
                f"""
                <div style="
                    background-color: #e5e7eb;
                    border-radius: 16px;
                    padding: 10px;
                    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1),
                    0 2px 4px -2px rgba(0, 0, 0, 0.1);
                ">
                    {html_bar}
                </div>
            """,
                height=500,
            )

        # # Siapkan kolom layout: kiri dan kanan (batang & lingkaran)
        # col1, col2 = st.columns(2)

        # # Kolom kiri: diagram batang
        # with col1:
        #     bar_data_long = bar_data.melt(
        #         id_vars='tanggal',
        #         value_vars=summary.columns,
        #         var_name='Kategori',
        #         value_name='Jumlah'
        #     )

        #     fig_bar = px.bar(
        #         bar_data_long,
        #         x='Kategori',
        #         y='Jumlah',
        #         color='Kategori',
        #         color_discrete_map={
        #             'Sangat Puas': '#059669',
        #             'Puas': '#f59e0b',
        #             'Kurang Puas': '#d62728'
        #         }
        #     )

        #     fig_bar.update_layout(
        #         plot_bgcolor='#e5e7eb',
        #         paper_bgcolor='#e5e7eb',
        #         font_color='black'
        #     )

        #     html_bar = fig_bar.to_html(full_html=False)

        #     components.html(f"""
        #         <div style="
        #             background-color: #e5e7eb;
        #             border-radius: 16px;
        #             padding: 10px;
        #             box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1),
        #             0 2px 4px -2px rgba(0, 0, 0, 0.1);
        #         ">
        #             {html_bar}
        #         </div>
        #     """, height=500)

        # # Kolom kanan: diagram lingkaran
        # with col2:
        #     pie_data = bar_data_long.groupby('Kategori')['Jumlah'].sum().reset_index()

        #     fig_pie = px.pie(
        #         pie_data,
        #         names='Kategori',
        #         values='Jumlah',
        #         color='Kategori',
        #         color_discrete_map={
        #             'Sangat Puas': '#059669',
        #             'Puas': '#f59e0b',
        #             'Kurang Puas': '#d62728'
        #         }
        #     )

        #     fig_pie.update_layout(
        #         plot_bgcolor='#e5e7eb',
        #         paper_bgcolor='#e5e7eb',
        #         font_color='black'
        #     )

        #     html_pie = fig_pie.to_html(full_html=False)

        #     components.html(f"""
        #         <div style="
        #             background-color: #e5e7eb;
        #             border-radius: 16px;
        #             padding: 10px;
        #             box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1),
        #             0 2px 4px -2px rgba(0, 0, 0, 0.1);
        #         ">
        #             {html_pie}
        #         </div>
        #     """, height=500)

        # # Kolom bawah: grafik garis
        # fig_line = px.line(
        #     summary_reset,
        #     x='tanggal',
        #     y=summary.columns,
        #     title="Kepuasan per Tanggal",
        #     labels={'value': 'Jumlah Responden', 'tanggal': 'Tanggal'},
        #     color_discrete_map={
        #         'Sangat Puas': '#059669',
        #         'Puas': '#f59e0b',
        #         'Kurang Puas': '#d62728'
        #     }
        # )
        # fig_line.update_layout(
        #     xaxis=dict(tickformat="%Y-%m-%d"),
        #     xaxis_title="Tanggal",
        #     yaxis_title="Jumlah Responden",
        #     plot_bgcolor='#e5e7eb',
        #     paper_bgcolor='#e5e7eb',
        #     font_color='black'
        # )

        # html_chart = fig_line.to_html(full_html=False)

        # components.html(f"""
        #         <div style="
        #             background-color: #e5e7eb;
        #             border-radius: 16px;
        #             padding: 10px;
        #             box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1),
        #             0 2px 4px -2px rgba(0, 0, 0, 0.1);
        #         ">
        #             {html_chart}
        #         </div>
        #     """, height=500)

    elif selected == "Data Training":
        st.markdown(
            """
            <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css" rel="stylesheet">
            <div style="display: flex; align-items: center; gap: 1rem;">
                <div style="background-color: #4e5d91; border-radius: 20px; width: 60px; height: 40px; display: flex; justify-content: center; align-items: center;">
                    <i class="fas fa-database" style="color: white; font-size: 20px;"></i>
                </div>  
                <h1 style="margin: 0;">Data Training</h1>
            </div>
        """,
            unsafe_allow_html=True,
        )

        st.markdown(
            """
            <style>
                .stFileUploader {
                    display: flex;
                    flex-direction:column;
                    justify-content: center;
                    align-items: center;
                    padding: 20px;
                    border: 2px dashed #4e5d91;
                    border-radius: 10px;
                    background-color: #f0f2f6;
                    text-align: center;
                    font-size: 14px;
                    color: #4e5d91;
                }
                .st-emotion-cache-ue6h4q {
                    min-height: 0;
                }             
                .stFileUploaderDropzone{
                    border: 2px dashed #4e5d91;
                }
                .stFileUploader .stFileUploader__message {
                    font-size: 16px;
                }
                .stFileUploader .stFileUploader__message p {
                    font-weight: bold;
                }
                .st-emotion-cache-u8hs99 {
                    flex-direction: column;   
                }
                .st-emotion-cache-nwtri {
                    margin-right: 0;    
                }
                .st-emotion-cache-9g466w{
                    flex-direction: column; 
                }
                .st-emotion-cache-hvk9mj{
                    margin-top: 0.5rem;
                    border-radius: 50px;
                }
            </style>
        """,
            unsafe_allow_html=True,
        )

        # Custom file uploader with additional message
        file = st.file_uploader("", type=["csv", "xlsx"])

        # Jika ada file yang diupload
        if file is not None:
            try:
                # Membaca file
                df = (
                    pd.read_csv(file)
                    if file.name.endswith(".csv")
                    else pd.read_excel(file)
                )
                required_columns = {
                    "id",
                    "Q1",
                    "Q2",
                    "Q3",
                    "Q4",
                    "Q5",
                    "Q6",
                    "Q7",
                    "Q8",
                    "Q9",
                    "Q10",
                }
                if not required_columns.issubset(df.columns):
                    st.error("File tidak memiliki kolom yang sesuai: id, Q1-Q10")
                    return

                # Menampilkan dua kolom: data upload dan data di database
                col1, col2 = st.columns([1, 1])

                # with col1:
                #     st.markdown("### Preview Data yang Diupload")
                #     with st.expander("Lihat Data Training yang Diunggah"):
                #         selected_columns = st.multiselect(
                #             "Pilih Kolom untuk Ditampilkan",
                #             df.columns.tolist(),
                #             default=df.columns.tolist(),
                #             key="multiselect_upload_preview",
                #         )
                #         st.dataframe(df[selected_columns], use_container_width=True)

                with col1:
                    # st.markdown("### Data Training Saat Ini")
                    try:
                        current_data = load_data()

                        # Hapus kolom tidak perlu
                        drop_cols = ["update_at", "Admin_idAdmin"]
                        for col in drop_cols:
                            if col in current_data.columns:
                                current_data = current_data.drop(columns=col)

                        # Ubah nama kolom
                        current_data = current_data.rename(
                            columns={
                                "iddataTraining": "id",
                                "q1": "Q1",
                                "q2": "Q2",
                                "q3": "Q3",
                                "q4": "Q4",
                                "q5": "Q5",
                                "q6": "Q6",
                                "q7": "Q7",
                                "q8": "Q8",
                                "q9": "Q9",
                                "q10": "Q10",
                            }
                        )

                        with st.expander("Data Training yang Digunakan"):
                            show_columns = st.multiselect(
                                get_info_pembaruan_terakhir(),
                                current_data.columns.tolist(),
                                default=current_data.columns.tolist(),
                                key="multiselect_database_view",
                            )
                            st.dataframe(
                                current_data[show_columns], use_container_width=True
                            )

                    except Exception as e:
                        st.error(f"❌ Gagal memuat data: {e}")

                with col2:
                    # st.markdown("### Preview Data Upload")
                    with st.expander("Data Kepuasan yang Diunggah"):
                        selected_columns = st.multiselect(
                            "Preview sebelum disimpan",
                            df.columns.tolist(),
                            default=df.columns.tolist(),
                            key="preview_kepuasan",
                        )
                        st.dataframe(df[selected_columns], use_container_width=True)

                col1, col2 = st.columns([2, 5])  # Atur rasio lebar kolom

                with col1:
                    # Checkbox konfirmasi
                    setuju = st.checkbox("Yakin ingin menyimpan Data Training")

                    # Tombol hanya aktif jika checkbox dicentang
                    if setuju:
                        if st.button("Simpan Data Training"):
                            admin_id = get_admin_id(st.session_state["username"])
                            db = get_connection()
                            cursor = db.cursor()

                            # Hapus data lama
                            cursor.execute("DELETE FROM dataTraining")

                            # Simpan data baru
                            for _, row in df.iterrows():
                                sql = """
                                INSERT INTO dataTraining 
                                (iddataTraining, Admin_idAdmin, q1, q2, q3, q4, q5, q6, q7, q8, q9, q10) 
                                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                                """
                                values = (
                                    row["id"],
                                    admin_id,
                                    row["Q1"],
                                    row["Q2"],
                                    row["Q3"],
                                    row["Q4"],
                                    row["Q5"],
                                    row["Q6"],
                                    row["Q7"],
                                    row["Q8"],
                                    row["Q9"],
                                    row["Q10"],
                                )
                                cursor.execute(sql, values)

                            db.commit()
                            cursor.close()
                            db.close()

                            # Tampilkan sukses di kolom 2 (kanan)
                            with col2:
                                st.success("✅ Data Training Berhasil Disimpan")

                            # Latih ulang model
                            train_model()
                    else:
                        st.warning(
                            "Silakan centang kotak konfirmasi terlebih dahulu sebelum menyimpan."
                        )

            except Exception as e:
                st.error(f"❌ Gagal upload data: {e}")

        else:
            # Jika tidak ada file diupload, tampilkan data dari database
            # st.markdown("### Data Training yang Digunakan")

            try:
                current_data = load_data()

                # Hapus kolom tidak perlu
                drop_cols = ["update_at", "Admin_idAdmin"]
                for col in drop_cols:
                    if col in current_data.columns:
                        current_data = current_data.drop(columns=col)

                # Ubah nama kolom
                current_data = current_data.rename(
                    columns={
                        "iddataTraining": "id",
                        "q1": "Q1",
                        "q2": "Q2",
                        "q3": "Q3",
                        "q4": "Q4",
                        "q5": "Q5",
                        "q6": "Q6",
                        "q7": "Q7",
                        "q8": "Q8",
                        "q9": "Q9",
                        "q10": "Q10",
                    }
                )

                with st.expander("Data Training yang Digunakan"):
                    show_columns = st.multiselect(
                        get_info_pembaruan_terakhir(),
                        current_data.columns.tolist(),
                        default=current_data.columns.tolist(),
                        key="multiselect_database_only",
                    )
                    st.dataframe(current_data[show_columns], use_container_width=True)

            except Exception as e:
                st.error(f"❌ Gagal memuat data: {e}")

    # ------------------------
    elif selected == "Kepuasan Pelanggan":
        st.title("Kepuasan Pelanggan")
        file = st.file_uploader(
            "Upload file CSV atau Excel", type=["csv", "xlsx"], key="pelanggan"
        )

        if file is not None:
            try:
                df = (
                    pd.read_csv(file)
                    if file.name.endswith(".csv")
                    else pd.read_excel(file)
                )
                required_columns = {
                    "id_pelanggan",
                    "Q1",
                    "Q2",
                    "Q3",
                    "Q4",
                    "Q5",
                    "Q6",
                    "Q7",
                    "Q8",
                    "Q9",
                }
                if not required_columns.issubset(df.columns):
                    st.error("File harus memiliki kolom: id_pelanggan, Q1 - Q9")
                    return

                col1, col2 = st.columns([1, 1])

                with col1:
                    st.markdown("### Preview Data Upload")
                    with st.expander("Lihat Data Kepuasan yang Diunggah"):
                        selected_columns = st.multiselect(
                            "Pilih Kolom untuk Ditampilkan",
                            df.columns.tolist(),
                            default=df.columns.tolist(),
                            key="preview_kepuasan",
                        )
                        st.dataframe(df[selected_columns], use_container_width=True)

                with col2:
                    st.markdown("### Data Kepuasan Pelanggan Saat Ini")
                    try:
                        db = get_connection()
                        df_db = pd.read_sql("SELECT * FROM kepuasanPelanggan", db)
                        db.close()

                        if "Admin_idAdmin" in df_db.columns:
                            df_db = df_db.drop(columns=["Admin_idAdmin"])

                        df_db = df_db.rename(
                            columns={
                                "idkepuasanPelanggan": "id_pelanggan",
                                "q1": "Q1",
                                "q2": "Q2",
                                "q3": "Q3",
                                "q4": "Q4",
                                "q5": "Q5",
                                "q6": "Q6",
                                "q7": "Q7",
                                "q8": "Q8",
                                "q9": "Q9",
                            }
                        )

                        with st.expander("Lihat Data Kepuasan dari Database"):
                            selected_cols = st.multiselect(
                                "Pilih Kolom untuk Ditampilkan",
                                df_db.columns.tolist(),
                                default=df_db.columns.tolist(),
                                key="db_kepuasan",
                            )
                            st.dataframe(df_db[selected_cols], use_container_width=True)

                    except Exception as e:
                        st.error(f"Gagal memuat data: {e}")

                if st.button("Prediksi dengan KNN"):
                    model = load_model()
                    if model is None:
                        st.error(
                            "Model belum tersedia. Harap upload data training terlebih dahulu."
                        )
                    else:
                        # Ubah kolom menjadi huruf kecil agar sesuai model
                        df.columns = df.columns.str.lower()

                        # Lakukan prediksi
                        try:
                            X_pred = df[
                                ["q1", "q2", "q3", "q4", "q5", "q6", "q7", "q8", "q9"]
                            ]
                            df["Kelas"] = model.predict(X_pred)
                            st.success("Prediksi berhasil dilakukan!")

                            with st.expander("Hasil Prediksi"):
                                st.dataframe(df, use_container_width=True)

                            # Simpan ke history
                            admin_id = get_admin_id(st.session_state["username"])
                            db = get_connection()
                            cursor = db.cursor()
                            for _, row in df.iterrows():
                                sql = """
                                INSERT INTO history (idhistory, Admin_idAdmin, q1, q2, q3, q4, q5, q6, q7, q8, q9, q10)
                                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                                """
                                idhistory = str(uuid.uuid4())[:5]
                                values = (
                                    idhistory,
                                    admin_id,
                                    row["q1"],
                                    row["q2"],
                                    row["q3"],
                                    row["q4"],
                                    row["q5"],
                                    row["q6"],
                                    row["q7"],
                                    row["q8"],
                                    row["q9"],
                                    row["Kelas"],
                                )
                                cursor.execute(sql, values)
                            db.commit()
                            cursor.close()
                            db.close()
                            st.success(
                                "Hasil prediksi berhasil disimpan ke tabel history!"
                            )

                            # Diagram distribusi prediksi
                            st.markdown(
                                "### Diagram Lingkaran Distribusi Kelas Prediksi"
                            )
                            chart_data = df["Kelas"].value_counts().reset_index()
                            chart_data.columns = ["Kelas", "Jumlah"]

                            st.plotly_chart(
                                {
                                    "data": [
                                        {
                                            "labels": chart_data["Kelas"],
                                            "values": chart_data["Jumlah"],
                                            "type": "pie",
                                            "hole": 0.3,
                                        }
                                    ],
                                    "layout": {
                                        "margin": {"l": 0, "r": 0, "b": 0, "t": 30},
                                        "title": "Distribusi Kelas Prediksi",
                                    },
                                }
                            )

                        except Exception as e:
                            st.error(f"❌ Gagal menyimpan data: {e}")

            except Exception as e:
                st.error(f"❌ Gagal membaca file: {e}")

        else:
            # Jika tidak ada file diupload
            st.markdown("### Data Kepuasan Pelanggan Saat Ini di Database")
            try:
                db = get_connection()
                df_db = pd.read_sql("SELECT * FROM kepuasanPelanggan", db)
                db.close()

                if "Admin_idAdmin" in df_db.columns:
                    df_db = df_db.drop(columns=["Admin_idAdmin"])

                df_db = df_db.rename(
                    columns={
                        "idkepuasanPelanggan": "id_pelanggan",
                        "q1": "Q1",
                        "q2": "Q2",
                        "q3": "Q3",
                        "q4": "Q4",
                        "q5": "Q5",
                        "q6": "Q6",
                        "q7": "Q7",
                        "q8": "Q8",
                        "q9": "Q9",
                    }
                )

                with st.expander("Lihat Data Kepuasan dari Database"):
                    selected_cols = st.multiselect(
                        "Pilih Kolom untuk Ditampilkan",
                        df_db.columns.tolist(),
                        default=df_db.columns.tolist(),
                        key="db_kepuasan",
                    )
                    st.dataframe(df_db[selected_cols], use_container_width=True)

            except Exception as e:
                st.error(f"❌ Gagal memuat data: {e}")
    # ------------------------

    elif selected == "History":
        st.title("History Prediksi Kepuasan Pelanggan")

        try:
            db = get_connection()
            query = "SELECT * FROM history ORDER BY updated_at DESC"
            df_history = pd.read_sql(query, db)
            db.close()

            if "updated_at" in df_history.columns:
                df_history["updated_at"] = pd.to_datetime(df_history["updated_at"])

                # Tambahkan kolom Tanggal dan Jam
                df_history["Tanggal"] = df_history["updated_at"].dt.strftime("%d/%m/%Y")
                df_history["Jam"] = df_history["updated_at"].dt.strftime("%H:%M:%S")

                # Simpan data kolom untuk ditampilkan (exclude kolom idhistory, updated_at)
                display_df = df_history.drop(columns=["idhistory", "updated_at"])

                # Ganti nama kolom
                rename_dict = {
                    "admin_idAdmin": "Diedit Oleh",
                    "q1": "Q1",
                    "q2": "Q2",
                    "q3": "Q3",
                    "q4": "Q4",
                    "q5": "Q5",
                    "q6": "Q6",
                    "q7": "Q7",
                    "q8": "Q8",
                    "q9": "Q9",
                    "q10": "Kelas",
                }
                display_df.rename(columns=rename_dict, inplace=True)

                # Tambahkan kolom Keterangan Kelas berdasarkan nilai Q10 (Kelas)
                def map_keterangan(value):
                    if value == "0":
                        return "Kurang Puas"
                    elif value == "1":
                        return "Puas"
                    elif value == "2":
                        return "Sangat Puas"
                    else:
                        return "Nilai Tidak Valid"

                # Terapkan fungsi map_keterangan ke kolom Q10 (Kelas)
                display_df["Hasil Prediksi"] = display_df["Kelas"].apply(map_keterangan)

                # Letakkan kolom Q10 (Kelas) dan Keterangan Kelas setelah Q9
                cols = [
                    "Tanggal",
                    "Jam",
                    "Diedit Oleh",
                    "Q1",
                    "Q2",
                    "Q3",
                    "Q4",
                    "Q5",
                    "Q6",
                    "Q7",
                    "Q8",
                    "Q9",
                    "Kelas",
                    "Hasil Prediksi",
                ]
                display_df = display_df[cols]

                # Filter tanggal
                min_date = df_history["updated_at"].min().date()
                max_date = df_history["updated_at"].max().date()

                col1, col2 = st.columns(2)
                with col1:
                    start_date = st.date_input(
                        "📅 Tanggal Mulai",
                        min_value=min_date,
                        max_value=max_date,
                        value=min_date,
                    )
                with col2:
                    end_date = st.date_input(
                        "📅 Tanggal Akhir",
                        min_value=min_date,
                        max_value=max_date,
                        value=max_date,
                    )

                if start_date > end_date:
                    st.warning(
                        "❗ Tanggal mulai tidak boleh lebih besar dari tanggal akhir."
                    )
                else:
                    filtered_df = display_df[
                        (df_history["updated_at"].dt.date >= start_date)
                        & (df_history["updated_at"].dt.date <= end_date)
                    ]

                    with st.expander("📄 Lihat Data History"):
                        show_columns = st.multiselect(
                            "🧩 Pilih Kolom yang Ditampilkan:",
                            options=filtered_df.columns.tolist(),
                            default=filtered_df.columns.tolist(),
                        )
                        st.dataframe(
                            filtered_df[show_columns], use_container_width=True
                        )

                    # Tombol hapus
                    col1, col2 = st.columns([5, 1])
                    with col1:
                        if st.button("🗑️ Hapus Data Berdasarkan Tanggal"):
                            try:
                                db = get_connection()
                                cursor = db.cursor()
                                delete_query = """
                                    DELETE FROM history
                                    WHERE DATE(updated_at) BETWEEN %s AND %s
                                """
                                cursor.execute(delete_query, (start_date, end_date))
                                db.commit()
                                cursor.close()
                                db.close()
                                st.success(
                                    f"✅ Data history dari tanggal {start_date.strftime('%d/%m/%Y')} sampai {end_date.strftime('%d/%m/%Y')} berhasil dihapus!"
                                )
                            except Exception as e:
                                st.error(f"❌ Gagal menghapus data: {e}")
                    with col2:
                        if st.button("❌ Hapus Semua History"):
                            try:
                                db = get_connection()
                                cursor = db.cursor()
                                cursor.execute("DELETE FROM history")
                                db.commit()
                                cursor.close()
                                db.close()
                                st.success("✅ Semua data history telah dihapus!")
                            except Exception as e:
                                st.error(f"❌ Gagal menghapus semua data: {e}")
            else:
                st.warning("Kolom `updated_at` tidak ditemukan dalam tabel history.")
                st.dataframe(df_history)

        except Exception as e:
            st.error(f"❌ Gagal memuat data history: {e}")

    elif selected == "Logout":
        st.session_state.clear()
        st.success("👋 Berhasil logout.")
        st.rerun()


# ------------------------ Routing ------------------------
if "login" not in st.session_state or not st.session_state["login"]:
    login_page()
    # main_app()
else:
    main_app()
