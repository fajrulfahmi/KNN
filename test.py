import mysql.connector
import streamlit as st

# Mengambil kredensial dari secrets
mysql_config = st.secrets["mysql"]

# Koneksi ke MySQL
connection = mysql.connector.connect(
    host=mysql_config["host"],
    port=mysql_config["port"],
    user=mysql_config["user"],
    password=mysql_config["password"],
    database=mysql_config["database"]
)

# Membuat cursor dan menjalankan query
cursor = connection.cursor()
cursor.execute("SELECT * FROM admin")
result = cursor.fetchall()

# Tampilkan hasil
for row in result:
    st.write(row)

# Tutup koneksi
cursor.close()
connection.close()
