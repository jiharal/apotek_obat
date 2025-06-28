"""
Main Streamlit application for medicine price extraction from PDF files
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import io

from utils.pdf_extractor import PDFExtractor
from utils.data_processor import DataProcessor
from utils.visualizer import Visualizer
import config

def main():
    st.set_page_config(
        page_title=config.APP_TITLE,
        page_icon="💊",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.title(config.APP_TITLE)
    st.markdown(config.APP_DESCRIPTION)
    
    # Initialize session state
    if 'processed_data' not in st.session_state:
        st.session_state.processed_data = None
    if 'comparison_results' not in st.session_state:
        st.session_state.comparison_results = None
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Pengaturan")
        
        # File upload
        st.subheader("📁 Upload File PDF")
        
        # Information about PBF folder
        st.info("💡 **Tips**: Simpan file PDF di folder `pbf/` untuk organisasi yang lebih baik")
        
        if st.button("📂 Buka Folder PBF"):
            import os
            pbf_path = os.path.abspath("pbf")
            st.code(f"Lokasi folder: {pbf_path}")
            
            # List files in pbf folder if any
            if os.path.exists("pbf"):
                pdf_files = []
                for root, dirs, files in os.walk("pbf"):
                    for file in files:
                        if file.lower().endswith('.pdf'):
                            pdf_files.append(os.path.relpath(os.path.join(root, file)))
                
                if pdf_files:
                    st.write("📋 **File PDF yang ditemukan:**")
                    for pdf_file in pdf_files[:10]:  # Show max 10 files
                        st.write(f"- {pdf_file}")
                    if len(pdf_files) > 10:
                        st.write(f"... dan {len(pdf_files) - 10} file lainnya")
                else:
                    st.write("📂 Folder kosong - belum ada file PDF")
        
        uploaded_files = st.file_uploader(
            "Pilih file PDF dari berbagai PBF",
            type=['pdf'],
            accept_multiple_files=True,
            help="Upload file PDF yang berisi daftar harga obat dari PBF. Format kolom yang didukung: NAMA BARANG, HNA+PPN. Mendukung layout dua tabel berdampingan per halaman."
        )
        
        # Processing options
        st.subheader("🔧 Opsi Pemrosesan")
        similarity_threshold = st.slider(
            "Threshold Kesamaan Nama Obat",
            min_value=0.5,
            max_value=1.0,
            value=config.SIMILARITY_THRESHOLD,
            step=0.1,
            help="Tingkat kesamaan minimum untuk menganggap obat sebagai produk yang sama"
        )
        
        process_button = st.button("🚀 Proses File", type="primary")
    
    # Main content area
    if uploaded_files and process_button:
        process_files(uploaded_files, similarity_threshold)
    
    # Display results if available
    if st.session_state.processed_data is not None and len(st.session_state.processed_data) > 0:
        display_results()
    elif st.session_state.processed_data is not None and len(st.session_state.processed_data) == 0:
        st.warning("⚠️ Tidak ada data yang berhasil diekstrak dari file PDF yang diupload. Silakan coba dengan file PDF yang berbeda.")

def process_files(uploaded_files, similarity_threshold):
    """Process uploaded PDF files"""
    with st.spinner("Sedang memproses file PDF..."):
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        pdf_extractor = PDFExtractor()
        data_processor = DataProcessor(similarity_threshold)
        
        all_data = []
        
        for i, uploaded_file in enumerate(uploaded_files):
            status_text.text(f"Memproses {uploaded_file.name}...")
            
            try:
                # Extract data from PDF
                extracted_data = pdf_extractor.extract_from_file(uploaded_file)
                
                # Add PBF name from filename
                pbf_name = uploaded_file.name.replace('.pdf', '')
                for item in extracted_data:
                    item['pbf'] = pbf_name
                
                all_data.extend(extracted_data)
                
            except Exception as e:
                st.error(f"Error memproses {uploaded_file.name}: {str(e)}")
            
            progress_bar.progress((i + 1) / len(uploaded_files))
        
        if all_data:
            # Process and clean data
            status_text.text("Membersihkan dan memproses data...")
            processed_data = data_processor.process_data(all_data)
            
            # Generate comparison results
            status_text.text("Membandingkan harga...")
            comparison_results = data_processor.compare_prices(processed_data)
            
            st.session_state.processed_data = processed_data
            st.session_state.comparison_results = comparison_results
            
            status_text.text("✅ Pemrosesan selesai!")
            progress_bar.progress(1.0)
            
            st.success(f"Berhasil memproses {len(uploaded_files)} file PDF dengan {len(comparison_results)} obat unik")
        else:
            st.error("Tidak ada data yang berhasil diekstrak dari file PDF")

def display_results():
    """Display processing results"""
    
    # Create tabs
    tab1, tab2, tab3 = st.tabs(["💊 Data Obat", "📊 Filter & Cari", "💾 Export"])
    
    with tab1:
        display_price_comparison()
    
    with tab2:
        display_full_data()
    
    with tab3:
        display_export_options()

def display_price_comparison():
    """Display focused medicine data table"""
    st.subheader("💊 Data Obat")
    
    if st.session_state.processed_data is not None:
        # Create focused dataframe
        data = []
        for item in st.session_state.processed_data:
            data.append({
                'Nama Obat': item.get('nama_obat', ''),
                'Harga (Rp)': f"Rp {item.get('harga', 0):,.0f}",
                'PBF': item.get('pbf', ''),
                'Tabel': item.get('table_side', '')
            })
        
        df = pd.DataFrame(data)
        
        # Search functionality
        search_term = st.text_input("🔍 Cari obat:", placeholder="Masukkan nama obat...")
        
        if search_term:
            df = df[df['Nama Obat'].str.contains(search_term, case=False, na=False)]
        
        # Display summary stats
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Obat", len(df))
        with col2:
            avg_price = sum(item.get('harga', 0) for item in st.session_state.processed_data) / len(st.session_state.processed_data) if st.session_state.processed_data else 0
            st.metric("Rata-rata Harga", f"Rp {avg_price:,.0f}")
        with col3:
            total_pbf = len(set(item.get('pbf', '') for item in st.session_state.processed_data)) if st.session_state.processed_data else 0
            st.metric("Jumlah PBF", total_pbf)
        
        # Display focused table
        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True
        )

def display_analytics():
    """Display analytics and charts"""
    st.subheader("📈 Analitik Harga")
    
    if st.session_state.comparison_results is not None and len(st.session_state.comparison_results) > 0:
        visualizer = Visualizer()
        
        # Price distribution chart
        st.subheader("Distribusi Harga per PBF")
        price_dist_fig = visualizer.create_price_distribution_chart(st.session_state.processed_data)
        st.plotly_chart(price_dist_fig, use_container_width=True, key="price_distribution_chart")
        
        # Savings analysis
        st.subheader("Analisis Penghematan")
        savings_fig = visualizer.create_savings_analysis_chart(st.session_state.comparison_results)
        st.plotly_chart(savings_fig, use_container_width=True, key="savings_analysis_chart")
        
        # PBF performance
        st.subheader("Performa PBF")
        pbf_performance_fig = visualizer.create_pbf_performance_chart(st.session_state.comparison_results)
        st.plotly_chart(pbf_performance_fig, use_container_width=True, key="pbf_performance_chart")
    else:
        st.info("📊 Analitik akan tersedia setelah file PDF diproses dan data perbandingan tersedia.")

def display_full_data():
    """Display filtered data with search options"""
    st.subheader("📊 Filter & Pencarian")
    
    if st.session_state.processed_data is not None:
        # Create detailed dataframe
        data = []
        for item in st.session_state.processed_data:
            data.append({
                'Nama Obat': item.get('nama_obat', ''),
                'Harga': item.get('harga', 0),
                'PBF': item.get('pbf', ''),
                'Tabel': item.get('table_side', ''),
                'Halaman': item.get('page', 1)
            })
        
        df = pd.DataFrame(data)
        
        # Filters
        col1, col2, col3 = st.columns(3)
        with col1:
            pbf_options = df['PBF'].unique().tolist()
            pbf_filter = st.multiselect("Filter PBF:", pbf_options, default=pbf_options)
        with col2:
            if df['Harga'].max() > 0:
                price_range = st.slider(
                    "Range Harga:",
                    min_value=float(df['Harga'].min()),
                    max_value=float(df['Harga'].max()),
                    value=(float(df['Harga'].min()), float(df['Harga'].max()))
                )
            else:
                price_range = (0, 1000000)
        with col3:
            table_options = [''] + df['Tabel'].unique().tolist()
            table_filter = st.selectbox("Filter Tabel:", table_options)
        
        # Apply filters
        filtered_df = df.copy()
        if pbf_filter:
            filtered_df = filtered_df[filtered_df['PBF'].isin(pbf_filter)]
        if table_filter:
            filtered_df = filtered_df[filtered_df['Tabel'] == table_filter]
        filtered_df = filtered_df[
            (filtered_df['Harga'] >= price_range[0]) & 
            (filtered_df['Harga'] <= price_range[1])
        ]
        
        # Format price for display
        filtered_df['Harga (Rp)'] = filtered_df['Harga'].apply(lambda x: f"Rp {x:,.0f}")
        display_df = filtered_df.drop('Harga', axis=1)
        
        st.dataframe(display_df, use_container_width=True, hide_index=True)

def display_export_options():
    """Display export options"""
    st.subheader("💾 Export Data")
    
    if st.session_state.comparison_results is not None:
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Export Perbandingan Harga")
            comparison_df = pd.DataFrame(st.session_state.comparison_results)
            
            # CSV export
            csv_data = comparison_df.to_csv(index=False)
            st.download_button(
                label="📄 Download CSV",
                data=csv_data,
                file_name=f"perbandingan_harga_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
            
            # Excel export
            excel_buffer = io.BytesIO()
            with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
                comparison_df.to_excel(writer, sheet_name='Perbandingan Harga', index=False)
            
            st.download_button(
                label="📊 Download Excel",
                data=excel_buffer.getvalue(),
                file_name=f"perbandingan_harga_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        
        with col2:
            st.subheader("Export Data Lengkap")
            full_df = pd.DataFrame(st.session_state.processed_data)
            
            # CSV export
            csv_data_full = full_df.to_csv(index=False)
            st.download_button(
                label="📄 Download CSV Lengkap",
                data=csv_data_full,
                file_name=f"data_lengkap_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
            
            # Excel export
            excel_buffer_full = io.BytesIO()
            with pd.ExcelWriter(excel_buffer_full, engine='openpyxl') as writer:
                full_df.to_excel(writer, sheet_name='Data Lengkap', index=False)
            
            st.download_button(
                label="📊 Download Excel Lengkap",
                data=excel_buffer_full.getvalue(),
                file_name=f"data_lengkap_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

if __name__ == "__main__":
    main()