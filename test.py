import mysql.connector
import streamlit as st

try:
    mysql_config = st.secrets["mysql"]
    connection = mysql.connector.connect(
        host=mysql_config["host"],
        port=mysql_config["port"],
        user=mysql_config["user"],
        password=mysql_config["password"],
        database=mysql_config["database"]
    )
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM admin")
    result = cursor.fetchall()

    for row in result:
        st.write(row)
    
except mysql.connector.Error as err:
    st.error(f"Error: {err}")
except Exception as e:
    st.error(f"An unexpected error occurred: {e}")
