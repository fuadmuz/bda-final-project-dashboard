# Dashboard Analitik Kecelakaan Lalu Lintas AS (2016–2023)

Final Project — **COMP8035041 Big Data Analytics**, BINUS University Graduate Program.

**Fuad Maulana Muzaddiq** — 2602687343 — MTI 2422
Dosen: Dr. Maria Susan Anggreainy, S.Kom., M.Kom.

---

## Tentang dashboard ini

Dashboard menyajikan hasil analisis 7.721.570 catatan kecelakaan lalu lintas di 49 negara bagian
Amerika Serikat, dalam empat halaman:

| Halaman | Isi |
|---|---|
| **Ringkasan** | Angka kunci dan tiga insight utama |
| **Kapan & Di Mana** | Peta titik rawan interaktif, pola per jam, per hari, dan per kondisi cuaca |
| **Model Risiko** | Performa model prediksi + **simulator**: atur kondisi kejadian, lihat peluang berdampak besar |
| **Jaringan Koridor** | Hasil graph analytics: PageRank ruas jalan, peta ruas kritis, dan koridor terbesar |

## Cara menjalankan secara lokal

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Struktur berkas

```
├── app.py              aplikasi Streamlit
├── requirements.txt    daftar pustaka
└── data/               artefak hasil pengolahan Spark (agregat, model, data graph)
```

Seluruh perhitungan berat — pembersihan 7,7 juta baris, pelatihan model, dan algoritma graph —
dilakukan lebih dahulu menggunakan **Apache Spark** dan **GraphFrames** di Google Colab. Dashboard
hanya memuat hasil ringkasnya agar dapat berjalan seketika.

Model pada simulator adalah `HistGradientBoostingClassifier` yang dilatih atas fitur dan target yang
sama dengan model Spark MLlib pada Assignment II (target: Severity ≥ 3). Pendekatan *train big,
serve small* ini dipakai karena lingkungan hosting dashboard tidak menyediakan klaster Spark.

## Sumber data

Moosavi, S., Samavatian, M. H., Parthasarathy, S., & Ramnath, R. (2019).
*A Countrywide Traffic Accident Dataset.* arXiv:1906.05409.
Dataset: [US Accidents (2016–2023) di Kaggle](https://www.kaggle.com/datasets/sobhanmoosavi/us-accidents),
lisensi **CC BY-NC-SA 4.0** — digunakan untuk keperluan akademik non-komersial.
