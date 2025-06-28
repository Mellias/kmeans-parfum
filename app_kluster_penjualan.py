import streamlit as st
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt
import io

# ========================
# Tampilan Header Cantik
# ========================
st.markdown("""
    <h1 style='text-align: center; color: #4B8BBE;'>📊 Aplikasi Klusterisasi Penjualan Parfum</h1>
    <p style='text-align: center; color: gray;'>Analisis pola penjualan parfum berdasarkan data bulanan</p>
    <hr>
    """, unsafe_allow_html=True)

st.markdown("""
#### 📝 Cara Menggunakan:
1. Upload file Excel berisi data penjualan parfum (kolom bulan).
2. Pilih jumlah klaster.
3. Lihat hasil klusterisasi, visualisasi PCA, tren per klaster.
4. Unduh hasil dalam bentuk Excel.
""")

# ========================
# Upload File Excel
# ========================
st.subheader("📤 Upload File Data Penjualan")
uploaded_file = st.file_uploader("Upload file Excel (data mentah, belum dikluster)", type=["xlsx"])

if uploaded_file is not None:
    df = pd.read_excel(uploaded_file)

    st.subheader("📋 Data yang Diunggah")
    st.dataframe(df)

    # Deteksi kolom bulan secara otomatis
    bulan_list = ['januari', 'februari', 'maret', 'april', 'mei', 'juni',
                  'juli', 'agustus', 'september', 'oktober', 'november', 'desember']
    bulan_cols = [col for col in df.columns if col.lower() in bulan_list]

    if len(bulan_cols) >= 2:
        # Konversi nilai bulan ke numerik
        df[bulan_cols] = df[bulan_cols].apply(pd.to_numeric, errors='coerce').fillna(0)

        # Slider jumlah klaster
        st.subheader("🔢 Pilih Jumlah Klaster")
        k = st.slider("Jumlah Klaster (K):", min_value=2, max_value=7, value=2, step=1)

        # Skala data
        features = df[bulan_cols]
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(features)

        # KMeans clustering
        kmeans = KMeans(n_clusters=k, random_state=42)
        df['cluster'] = kmeans.fit_predict(X_scaled)

        # Info jumlah data dan klaster
        col1, col2 = st.columns(2)
        col1.metric("Jumlah Parfum", len(df))
        col2.metric("Jumlah Klaster", k)

        # Hasil klusterisasi
        st.subheader("🧴 Hasil Klusterisasi")
        st.dataframe(df[['Parfum'] + bulan_cols + ['cluster']])

        # Visualisasi PCA
        st.subheader("🧭 Visualisasi Kluster (PCA 2D)")
        pca = PCA(n_components=2)
        pca_result = pca.fit_transform(X_scaled)
        df['PC1'] = pca_result[:, 0]
        df['PC2'] = pca_result[:, 1]

        fig, ax = plt.subplots()
        for cluster in df['cluster'].unique():
            cluster_data = df[df['cluster'] == cluster]
            ax.scatter(cluster_data['PC1'], cluster_data['PC2'], label=f'Cluster {cluster}')
            for i, row in cluster_data.iterrows():
                ax.text(row['PC1'] + 0.1, row['PC2'], row['Parfum'], fontsize=8)
        ax.set_xlabel("PC1")
        ax.set_ylabel("PC2")
        ax.set_title("Hasil Klusterisasi dengan PCA")
        ax.legend()
        st.pyplot(fig)

        # Grafik tren per klaster
        st.subheader("📈 Tren Rata-rata Penjualan per Klaster")
        mean_by_cluster = df.groupby('cluster')[bulan_cols].mean()

        fig2, ax2 = plt.subplots()
        for cluster in mean_by_cluster.index:
            ax2.plot(bulan_cols, mean_by_cluster.loc[cluster], marker='o', label=f'Cluster {cluster}')
        ax2.set_title("Rata-rata Penjualan per Bulan per Klaster")
        ax2.set_xlabel("Bulan")
        ax2.set_ylabel("Penjualan")
        ax2.legend()
        st.pyplot(fig2)

        # Interpretasi Klaster
        st.subheader("💡 Interpretasi Klaster")
        if k == 2:
            st.markdown("""
            - **Cluster 0**: Parfum dengan pola penjualan rendah/stabil.
            - **Cluster 1**: Parfum dengan peningkatan penjualan di bulan-bulan tertentu.
            """)
        elif k == 3:
            st.markdown("""
            - **Cluster 0**: Parfum dengan penjualan rendah dan konsisten.
            - **Cluster 1**: Parfum musiman dengan lonjakan pada waktu tertentu.
            - **Cluster 2**: Parfum dengan penjualan tinggi secara konsisten.
            """)
        else:
            st.markdown(f"Terdapat **{k} klaster**. Silakan eksplorasi tren tiap klaster pada grafik di atas.")

        # Unduh hasil klasterisasi
        st.subheader("📥 Unduh Hasil Klusterisasi")
        to_download = df[['Parfum'] + bulan_cols + ['cluster']]
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            to_download.to_excel(writer, index=False, sheet_name='Hasil Klusterisasi')
        st.download_button(
            label="📄 Unduh Hasil Excel",
            data=buffer.getvalue(),
            file_name="hasil_kluster_parfum.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.error("Tidak ditemukan cukup kolom penjualan bulanan. Pastikan file memiliki minimal dua kolom bulan seperti: Januari, Februari, Maret, dst.")
