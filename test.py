import streamlit as st
from streamlit_option_menu import option_menu
from streamlit_extras.metric_cards import style_metric_cards
import pandas as pd
import mysql.connector
from sklearn.neighbors import KNeighborsClassifier
import pickle
import os
import uuid

with open('style.css')as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html = True)

# ------------------------ Koneksi ke Database ------------------------
def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="root",
        database="mydb"
    )

# ------------------------ Cek Login ------------------------
def check_login(username, password):
    db = get_connection()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM admin WHERE username=%s AND password=%s", (username, password))
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
        X = df[['q1', 'q2', 'q3', 'q4', 'q5', 'q6', 'q7', 'q8', 'q9']]
        y = df['q10']
        knn = KNeighborsClassifier(n_neighbors=3)
        knn.fit(X, y)
        save_model(knn)

# ------------------------ Halaman Login ------------------------
def login_page():
    st.title("🔐 Login Admin")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if check_login(username, password):
            st.session_state["login"] = True
            st.session_state["username"] = username
            st.success("Login berhasil!")
            st.rerun()
        else:
            st.error("Username atau password salah")

# ------------------------ Halaman Utama Aplikasi ------------------------
def main_app():
    with st.sidebar:
        selected = option_menu(
            menu_title="Main Menu",
            options=["Dashboard",  "Data Training", "Kepuasan Pelanggan", "History","Logout"],
            icons=["bar-chart", "clock-history", "box-arrow-right", "box-arrow-right", "box-arrow-right"],
            menu_icon="cast",
            default_index=0
        )

    if selected == "Dashboard":
        st.title("Dashboard")
        
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
        
        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown(f"""
                <div style="background-color:#e0f7fa; padding:20px; border-radius:15px; 
                            box-shadow:2px 2px 10px rgba(0,0,0,0.1); 
                            border:1px solid #00acc1; display:flex; align-items:center;">
                    <div style="font-size:48px; margin-right:15px;">📊</div>
                    <div style="width:100%; text-align:center;">
                        <h4 style="color:#007c91; margin:0 0 4px 0;">Data Training</h4>
                        <h2 style="color:#004d40; margin-top:-1.5rem;">{data_training_count}</h2>
                    </div>
                </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown(f"""
                <div style="background-color:#f1f8e9; padding:20px; border-radius:15px; 
                            box-shadow:2px 2px 10px rgba(0,0,0,0.1); 
                            border:1px solid #8bc34a; display:flex; align-items:center;">
                    <div style="font-size:48px; margin-right:15px;">📋</div>
                    <div style="width:100%; text-align:center;">
                        <h4 style="color:#558b2f; margin:0 0 4px 0;">Kepuasan Pelanggan</h4>
                        <h2 style="color:#33691e; margin-top:-1.5rem;">{kepuasan_pelanggan_count}</h2>
                    </div>
                </div>
            """, unsafe_allow_html=True)

        with col3:
            st.markdown(f"""
                <div style="background-color:#fce4ec; padding:20px; border-radius:15px; 
                            box-shadow:1px 2px 10px rgba(0,0,0,0.1); 
                            border:1px solid #f06292; display:flex; align-items:center;">
                    <div style="font-size:48px; margin-right:15px;">📁</div>
                    <div style="width:100%; text-align:center;">
                        <h4 style="color:#ad1457; margin:0 0 4px 0;">Riwayat Klasifikasi</h4>
                        <h2 style="color:#880e4f; margin-top:-1.5rem;">{history_count}</h2>
                    </div>
                </div>
            """, unsafe_allow_html=True)




    elif selected == "Data Training":
        st.title("Data Training")
        file = st.file_uploader("Upload file CSV atau Excel", type=["csv", "xlsx"])

        if file is not None:
            try:
                df = pd.read_csv(file) if file.name.endswith('.csv') else pd.read_excel(file)
                required_columns = {'id', 'Q1', 'Q2', 'Q3', 'Q4', 'Q5', 'Q6', 'Q7', 'Q8', 'Q9', 'Q10'}
                if not required_columns.issubset(df.columns):
                    st.error("File tidak memiliki kolom yang sesuai: id, Q1-Q10")
                    return

                st.markdown("### 📋 Preview Data Sebelum Disimpan")
                st.dataframe(df)

                if st.button("🚀 Simpan ke Database"):
                    admin_id = get_admin_id(st.session_state["username"])
                    db = get_connection()
                    cursor = db.cursor()
                    cursor.execute("DELETE FROM dataTraining")

                    for _, row in df.iterrows():
                        sql = """
                        INSERT INTO dataTraining 
                        (iddataTraining, Admin_idAdmin, q1, q2, q3, q4, q5, q6, q7, q8, q9, q10) 
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """
                        values = (
                            row['id'], admin_id, row['Q1'], row['Q2'], row['Q3'], row['Q4'],
                            row['Q5'], row['Q6'], row['Q7'], row['Q8'], row['Q9'], row['Q10']
                        )
                        cursor.execute(sql, values)
                    db.commit()
                    cursor.close()
                    db.close()
                    st.success("✅ Data berhasil diupload ke database dan data lama dihapus!")
                    train_model()
                    st.info("🤖 Model berhasil dilatih ulang secara otomatis!")
            except Exception as e:
                st.error(f"❌ Gagal upload data: {e}")

        st.markdown("### 📊 Data Training Saat Ini di Database")
        st.dataframe(load_data())

    elif selected == "Kepuasan Pelanggan":
        st.subheader("📥 Upload Data Kepuasan Pelanggan (.csv / .xlsx)")
        file = st.file_uploader("Upload file CSV atau Excel", type=["csv", "xlsx"], key="pelanggan")

        if file is not None:
            try:
                df = pd.read_csv(file) if file.name.endswith('.csv') else pd.read_excel(file)
                required_columns = {'id_pelanggan', 'Q1', 'Q2', 'Q3', 'Q4', 'Q5', 'Q6', 'Q7', 'Q8', 'Q9'}
                if not required_columns.issubset(df.columns):
                    st.error("File harus memiliki kolom: id_pelanggan, Q1 - Q9")
                    return

                st.markdown("### 👀 Preview Data Upload")
                st.dataframe(df)

                if st.button("🚀 Simpan ke Database"):
                    admin_id = get_admin_id(st.session_state["username"])
                    db = get_connection()
                    cursor = db.cursor()

                    cursor.execute("DELETE FROM kepuasanPelanggan")

                    for _, row in df.iterrows():
                        sql = """
                        INSERT INTO kepuasanPelanggan
                        (idkepuasanPelanggan, Admin_idAdmin, q1, q2, q3, q4, q5, q6, q7, q8, q9)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """
                        values = (
                            row['id_pelanggan'], admin_id, row['Q1'], row['Q2'], row['Q3'],
                            row['Q4'], row['Q5'], row['Q6'], row['Q7'], row['Q8'], row['Q9']
                        )
                        cursor.execute(sql, values)

                    db.commit()
                    cursor.close()
                    db.close()
                    st.success("✅ Data baru berhasil disimpan. Semua data lama telah dihapus!")

            except Exception as e:
                st.error(f"❌ Gagal menyimpan data: {e}")

        st.markdown("### 📊 Data Kepuasan Pelanggan Saat Ini di Database")
        try:
            db = get_connection()
            df = pd.read_sql("SELECT * FROM kepuasanPelanggan", db)
            db.close()
            st.dataframe(df)

            if st.button("🔍 Prediksi dengan KNN"):
                model = load_model()
                if model is None:
                    st.error("Model belum tersedia. Harap upload data training terlebih dahulu.")
                else:
                    X_pred = df[['q1', 'q2', 'q3', 'q4', 'q5', 'q6', 'q7', 'q8', 'q9']]
                    df['Prediksi_Kepuasan'] = model.predict(X_pred)
                    st.success("Prediksi berhasil dilakukan!")
                    st.dataframe(df)

                    # Simpan hasil ke tabel history
                    admin_id = get_admin_id(st.session_state["username"])
                    db = get_connection()
                    cursor = db.cursor()
                    for _, row in df.iterrows():
                        sql = """
                        INSERT INTO history (idhistory, Admin_idAdmin, q1, q2, q3, q4, q5, q6, q7, q8, q9, q10)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """
                        idhistory = str(uuid.uuid4())[:10]  # id unik
                        values = (
                            idhistory, admin_id, row['q1'], row['q2'], row['q3'], row['q4'],
                            row['q5'], row['q6'], row['q7'], row['q8'], row['q9'], row['Prediksi_Kepuasan']
                        )
                        cursor.execute(sql, values)
                    db.commit()
                    cursor.close()
                    db.close()
                    st.success("📦 Hasil prediksi berhasil disimpan ke tabel history!")

                    st.markdown("### 🥧 Diagram Lingkaran Distribusi Kelas Prediksi")
                    chart_data = df['Prediksi_Kepuasan'].value_counts().reset_index()
                    chart_data.columns = ['Kelas', 'Jumlah']

                    st.plotly_chart({
                        "data": [
                            {
                                "labels": chart_data['Kelas'],
                                "values": chart_data['Jumlah'],
                                "type": "pie",
                                "hole": 0.3
                            }
                        ],
                        "layout": {
                            "margin": {"l": 0, "r": 0, "b": 0, "t": 30},
                            "title": "Distribusi Kelas Prediksi"
                        }
                    })
        except Exception as e:
            st.error(f"Gagal memuat data: {e}")

    elif selected == "History":
        st.subheader("🗂️ Tabel History Prediksi Kepuasan Pelanggan")
        db = get_connection()
        query = "SELECT * FROM history"
        df_history = pd.read_sql(query, db)
        db.close()
        st.dataframe(df_history)

        if st.button("❌ Clear History"):
            db = get_connection()
            cursor = db.cursor()
            cursor.execute("DELETE FROM history")
            db.commit()
            cursor.close()
            db.close()
            st.success("✅ Semua data history telah dihapus!")

    elif selected == "Logout":
        st.session_state.clear()
        st.success("👋 Berhasil logout.")
        st.rerun()

# ------------------------ Routing ------------------------
if "login" not in st.session_state or not st.session_state["login"]:
    # login_page()
     main_app()
else:
    main_app()
