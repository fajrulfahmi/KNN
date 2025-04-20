import streamlit as st

# Data Dummy
data_training_count = 50
kepuasan_pelanggan_count = 120
history_count = 30

st.set_page_config(page_title="Full Page Dashboard", page_icon="📊", layout="wide")
# Gunakan CDN Tailwind
st.markdown("""
    <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.0.3/dist/tailwind.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css" rel="stylesheet">

    """, unsafe_allow_html=True)


# # Menampilkan card dengan Tailwind CSS dan data
col1, col2, col3 = st.columns(3)
with col1:
            st.markdown(f"""
                <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css" rel="stylesheet">
                <div class="rounded-lg overflow-hidden shadow-md p-6 bg-indigo-500 text-white flex items-center space-x-4">
                    <span class="w-16 h-16 text-white">
                        <i class="fas fa-database text-6xl"></i> <!-- Ganti ikon menggunakan Font Awesome -->
                    </span>
                    <div>
                        <h2 style="font-size: 1.5rem; font-weight: bold;">Data Training</h2>
                        <p class="mt-1" style="font-size: 2rem; font-weight: bold;">{data_training_count}</p>
                    </div>
                </div>
            """, unsafe_allow_html=True)

with col2:
            st.markdown(f"""
                <div class="rounded-lg overflow-hidden shadow-md p-6 bg-green-600 text-white flex items-center space-x-4">
                    <span class="w-16 h-16 text-white">
                        <i class="fas fa-thumbs-up text-6xl"></i> <!-- Ikon untuk Kepuasan Pelanggan -->
                    </span>
                    <div>
                        <h2 style="font-size: 1.5rem; font-weight: bold;">Kepuasan Pelanggan</h2>
                        <p class="mt-1" style="font-size: 2rem; font-weight: bold;">{kepuasan_pelanggan_count}</p>
                    </div>
                </div>
            """, unsafe_allow_html=True)

with col3:
            st.markdown(f"""
                <div class="rounded-lg overflow-hidden shadow-md p-6 bg-red-600 text-white flex items-center space-x-4">
                    <span class="w-16 h-16 text-white">
                        <i class="fas fa-history text-6xl"></i> <!-- Ikon untuk Riwayat Klasifikasi -->
                    </span>
                    <div>
                        <h2 style="font-size: 1.5rem; font-weight: bold;">Riwayat Klasifikasi</h2>
                        <p class="mt-1" style="font-size: 2rem; font-weight: bold;">{history_count}</p>
                    </div>
                </div>
            """, unsafe_allow_html=True)
