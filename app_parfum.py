# Kodingan ini hanya untuk menampilkan hasil klusterisasi, jadi kalau kodingan ini dijalankan, file excel yang diunggah itu hanya file excel hasil klusterisasi yang sudah dibuat sebelumnya.

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA

# Judul Aplikasi
st.title("Analisis Kluster Penjualan Parfum")
st.write("Aplikasi ini mengelompokkan parfum berdasarkan pola penjualan dari April - September 2024")

# Mengunggah File Excel
uploaded_file = st.file_uploader("Unggah file Excel hasil klastering", type=["xlsx"])
if uploaded_file is not None:
    df = pd.read_excel(uploaded_file)

    st.subheader("Data Hasil Kluster")
    st.dataframe(df)

    # Visualisasi Kluster dengan PCA 
    if {'April', 'Mei', 'Juni', 'Juli', 'Agustus', 'September'}.issubset(df.columns):
        pca = PCA(n_components=2)
        features = df[['April', 'Mei', 'Juni', 'Juli', 'Agustus', 'September']]
        components = pca.fit_transform(features)
        df['PC1'] = components[:, 0]
        df['PC2'] = components[:, 1]

        fig, ax = plt.subplots()
        for cluster in df['Cluster'].unique():
            cluster_data = df[df['Cluster'] == cluster]
            ax.scatter(cluster_data['PC1'], cluster_data['PC2'], label=f'Cluster {cluster}')
            for i, row in cluster_data.iterrows():
                ax.text(row['PC1']+0.1, row['PC2'], row['Parfum'], fontsize=8)

        ax.set_title("Visualisasi Kluster (PCA)")
        ax.set_xlabel("Principal Component 1")
        ax.set_ylabel("Principal Component 2")
        ax.legend()
        st.pyplot(fig)