import streamlit as st
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt
import io

# Judul Aplikasi
st.markdown("<h1 style='color:#6a1b9a'>✨ Aplikasi Klusterisasi Penjualan Parfum</h1>", unsafe_allow_html=True)
st.write("📌 Upload data penjualan parfum bulanan beserta informasi harga dan diskon (jika ada) untuk analisis klaster.")

# Upload File Excel
uploaded_file = st.file_uploader("📤 Upload file Excel (data mentah, belum dikluster)", type=["xlsx"])

if uploaded_file is not None:
    df = pd.read_excel(uploaded_file)
    st.subheader("📄 Data yang Diunggah")
    st.dataframe(df)

    # --- Deteksi kolom bulan ---
    bulan_list = ['januari', 'februari', 'maret', 'april', 'mei', 'juni',
                  'juli', 'agustus', 'september', 'oktober', 'november', 'desember']
    bulan_cols = [col for col in df.columns if col.lower() in bulan_list]

    # --- Tambahan fitur numerik lain seperti harga ---
    numeric_cols = df.select_dtypes(include='number').columns.tolist()
    fitur_tambahan = [col for col in numeric_cols if col.lower() not in bulan_list]

    fitur_klaster = bulan_cols + fitur_tambahan

    if len(bulan_cols) >= 2:
        df[fitur_klaster] = df[fitur_klaster].apply(pd.to_numeric, errors='coerce').fillna(0)

        st.subheader("🔢 Pilih Jumlah Klaster")
        k = st.slider("Jumlah Klaster (K):", min_value=2, max_value=7, value=2, step=1)

        # Scaling dan clustering
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(df[fitur_klaster])

        kmeans = KMeans(n_clusters=k, random_state=42)
        df['cluster'] = kmeans.fit_predict(X_scaled)

        st.subheader("📊 Hasil Klusterisasi")
        st.dataframe(df[['Parfum'] + fitur_klaster + ['cluster']])

        # Visualisasi PCA
        st.subheader("🌀 Visualisasi Kluster (PCA 2D)")
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
        ax.set_title("Visualisasi Kluster dengan PCA")
        ax.set_xlabel("PC1")
        ax.set_ylabel("PC2")
        ax.legend()
        st.pyplot(fig)

        # Grafik tren penjualan rata-rata per kluster
        st.subheader("📈 Tren Penjualan Rata-Rata per Kluster (khusus kolom bulan)")
        mean_by_cluster = df.groupby('cluster')[bulan_cols].mean()
        fig2, ax2 = plt.subplots()
        for cluster in mean_by_cluster.index:
            ax2.plot(bulan_cols, mean_by_cluster.loc[cluster], marker='o', label=f'Cluster {cluster}')
        ax2.set_title("Rata-rata Penjualan per Bulan per Kluster")
        ax2.set_xlabel("Bulan")
        ax2.set_ylabel("Penjualan")
        ax2.legend()
        st.pyplot(fig2)

        # Interpretasi dasar (opsional)
        st.subheader("💡 Interpretasi Sederhana")
        if k == 2:
            st.markdown("- **Klaster 0**: Penjualan rendah/stabil, harga tertentu.")
            st.markdown("- **Klaster 1**: Penjualan tinggi/fluktuatif atau harga lebih tinggi.")
        elif k == 3:
            st.markdown("- **Klaster 0**: Parfum dengan penjualan rendah.")
            st.markdown("- **Klaster 1**: Penjualan musiman atau naik turun.")
            st.markdown("- **Klaster 2**: Penjualan tinggi secara konsisten.")
        else:
            st.markdown(f"- Klasterisasi terbagi menjadi **{k} klaster**. Perhatikan grafik dan data untuk analisis lebih dalam.")

        # Download hasil
        st.subheader("📥 Unduh Hasil Klusterisasi")
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            df[['Parfum'] + fitur_klaster + ['cluster']].to_excel(writer, index=False, sheet_name='Hasil Klusterisasi')
        st.download_button(
            label="Unduh Hasil Excel",
            data=buffer.getvalue(),
            file_name="hasil_kluster_parfum.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    else:
        st.error("❗Tidak ditemukan cukup kolom penjualan bulanan. Pastikan ada minimal dua kolom seperti: April, Mei, dst.")
