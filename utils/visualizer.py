"""
Visualization utilities for medicine price analysis
"""

import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from typing import List, Dict, Any
import config

class Visualizer:
    """Create visualizations for medicine price analysis"""
    
    def __init__(self):
        self.color_palette = [
            '#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd',
            '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf'
        ]
    
    def create_price_distribution_chart(self, processed_data: List[Dict[str, Any]]):
        """Create price distribution chart by PBF"""
        if not processed_data:
            return go.Figure()
        
        df = pd.DataFrame(processed_data)
        
        # Create box plot
        fig = px.box(
            df, 
            x='pbf', 
            y='harga',
            title='Distribusi Harga per PBF',
            labels={'pbf': 'PBF', 'harga': 'Harga (Rp)'},
            color='pbf',
            color_discrete_sequence=self.color_palette
        )
        
        fig.update_layout(
            height=config.CHART_HEIGHT,
            showlegend=False,
            xaxis_title='PBF',
            yaxis_title='Harga (Rp)',
            yaxis=dict(tickformat=',.0f')
        )
        
        return fig
    
    def create_savings_analysis_chart(self, comparison_results: List[Dict[str, Any]]):
        """Create savings analysis chart"""
        if not comparison_results:
            return go.Figure()
        
        df = pd.DataFrame(comparison_results)
        
        # Take top 20 for better visualization
        df_top = df.head(20)
        
        fig = px.bar(
            df_top,
            x='persentase_hemat',
            y='nama_obat',
            orientation='h',
            title='Top 20 Obat dengan Penghematan Terbesar',
            labels={'persentase_hemat': 'Persentase Hemat (%)', 'nama_obat': 'Nama Obat'},
            color='persentase_hemat',
            color_continuous_scale='Viridis'
        )
        
        fig.update_layout(
            height=600,
            yaxis={'categoryorder': 'total ascending'},
            xaxis_title='Persentase Hemat (%)',
            yaxis_title='Nama Obat'
        )
        
        return fig
    
    def create_pbf_performance_chart(self, comparison_results: List[Dict[str, Any]]):
        """Create PBF performance chart"""
        if not comparison_results:
            return go.Figure()
        
        from utils.data_processor import DataProcessor
        processor = DataProcessor()
        pbf_stats = processor.get_pbf_performance(comparison_results)
        
        if not pbf_stats:
            return go.Figure()
        
        # Prepare data
        pbf_names = list(pbf_stats.keys())
        win_rates = [stats['win_rate'] for stats in pbf_stats.values()]
        best_counts = [stats['best_price_count'] for stats in pbf_stats.values()]
        total_medicines = [stats['total_medicines'] for stats in pbf_stats.values()]
        
        # Create subplot with secondary y-axis
        fig = make_subplots(
            specs=[[{"secondary_y": True}]],
            subplot_titles=("Performa PBF: Win Rate vs Jumlah Produk",)
        )
        
        # Add bar chart for win rate
        fig.add_trace(
            go.Bar(
                x=pbf_names,
                y=win_rates,
                name='Win Rate (%)',
                marker_color='lightblue',
                yaxis='y'
            ),
            secondary_y=False,
        )
        
        # Add scatter plot for total medicines
        fig.add_trace(
            go.Scatter(
                x=pbf_names,
                y=total_medicines,
                mode='markers+lines',
                name='Total Produk',
                marker=dict(size=10, color='red'),
                line=dict(color='red'),
                yaxis='y2'
            ),
            secondary_y=True,
        )
        
        # Update layout
        fig.update_xaxes(title_text="PBF")
        fig.update_yaxes(title_text="Win Rate (%)", secondary_y=False)
        fig.update_yaxes(title_text="Total Produk", secondary_y=True)
        
        fig.update_layout(
            height=config.CHART_HEIGHT,
            title_text="Performa PBF",
            showlegend=True
        )
        
        return fig
    
    def create_price_comparison_scatter(self, comparison_results: List[Dict[str, Any]]):
        """Create scatter plot comparing prices"""
        if not comparison_results:
            return go.Figure()
        
        df = pd.DataFrame(comparison_results)
        
        fig = px.scatter(
            df,
            x='harga_terbaik',
            y='harga_termahal',
            size='persentase_hemat',
            color='jumlah_pbf',
            hover_data=['nama_obat', 'pbf_terbaik', 'pbf_termahal'],
            title='Perbandingan Harga: Terbaik vs Termahal',
            labels={
                'harga_terbaik': 'Harga Terbaik (Rp)',
                'harga_termahal': 'Harga Termahal (Rp)',
                'jumlah_pbf': 'Jumlah PBF'
            }
        )
        
        # Add diagonal line (equal prices)
        max_price = max(df['harga_termahal'].max(), df['harga_terbaik'].max())
        fig.add_trace(
            go.Scatter(
                x=[0, max_price],
                y=[0, max_price],
                mode='lines',
                name='Harga Sama',
                line=dict(dash='dash', color='red'),
                showlegend=True
            )
        )
        
        fig.update_layout(
            height=config.CHART_HEIGHT,
            xaxis=dict(tickformat=',.0f'),
            yaxis=dict(tickformat=',.0f')
        )
        
        return fig
    
    def create_medicine_category_chart(self, processed_data: List[Dict[str, Any]]):
        """Create chart showing medicine categories"""
        if not processed_data:
            return go.Figure()
        
        df = pd.DataFrame(processed_data)
        
        # Extract medicine categories based on unit/form
        def categorize_medicine(row):
            satuan = str(row.get('satuan', '')).lower()
            nama = str(row.get('nama_obat', '')).lower()
            
            if 'tablet' in satuan or 'tab' in satuan:
                return 'Tablet'
            elif 'kapsul' in satuan or 'caps' in satuan:
                return 'Kapsul'
            elif 'sirup' in satuan or 'syrup' in satuan:
                return 'Sirup'
            elif 'injeksi' in satuan or 'inj' in satuan:
                return 'Injeksi'
            elif 'salep' in nama or 'cream' in nama:
                return 'Topikal'
            else:
                return 'Lainnya'
        
        df['kategori'] = df.apply(categorize_medicine, axis=1)
        
        # Count by category
        category_counts = df['kategori'].value_counts()
        
        fig = px.pie(
            values=category_counts.values,
            names=category_counts.index,
            title='Distribusi Kategori Obat',
            color_discrete_sequence=self.color_palette
        )
        
        fig.update_layout(height=config.CHART_HEIGHT)
        
        return fig
    
    def create_price_trend_chart(self, comparison_results: List[Dict[str, Any]]):
        """Create price trend analysis chart"""
        if not comparison_results:
            return go.Figure()
        
        df = pd.DataFrame(comparison_results)
        
        # Create price ranges
        df['price_range'] = pd.cut(
            df['harga_terbaik'], 
            bins=[0, 10000, 50000, 100000, 500000, float('inf')],
            labels=['<10K', '10K-50K', '50K-100K', '100K-500K', '>500K']
        )
        
        # Count medicines in each price range
        price_range_counts = df['price_range'].value_counts().sort_index()
        
        fig = px.bar(
            x=price_range_counts.index,
            y=price_range_counts.values,
            title='Distribusi Harga Obat',
            labels={'x': 'Range Harga (Rp)', 'y': 'Jumlah Obat'},
            color=price_range_counts.values,
            color_continuous_scale='Blues'
        )
        
        fig.update_layout(
            height=config.CHART_HEIGHT,
            xaxis_title='Range Harga (Rp)',
            yaxis_title='Jumlah Obat',
            showlegend=False
        )
        
        return fig
    
    def create_summary_metrics_chart(self, comparison_results: List[Dict[str, Any]]):
        """Create summary metrics visualization"""
        if not comparison_results:
            return go.Figure()
        
        df = pd.DataFrame(comparison_results)
        
        # Calculate metrics
        total_medicines = len(df)
        avg_savings = df['persentase_hemat'].mean()
        max_savings = df['persentase_hemat'].max()
        total_savings_amount = df['penghematan_rupiah'].sum()
        
        # Create gauge chart for average savings
        fig = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=avg_savings,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Rata-rata Penghematan (%)"},
            delta={'reference': 10},
            gauge={
                'axis': {'range': [None, 50]},
                'bar': {'color': "darkblue"},
                'steps': [
                    {'range': [0, 10], 'color': "lightgray"},
                    {'range': [10, 25], 'color': "gray"},
                    {'range': [25, 50], 'color': "lightgreen"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 30
                }
            }
        ))
        
        fig.update_layout(
            height=config.CHART_HEIGHT,
            title="Ringkasan Penghematan"
        )
        
        return fig
    
    def create_detailed_comparison_table(self, comparison_results: List[Dict[str, Any]], medicine_name: str):
        """Create detailed comparison for a specific medicine"""
        if not comparison_results:
            return go.Figure()
        
        # Find the medicine
        medicine_data = None
        for result in comparison_results:
            if medicine_name.lower() in result['nama_obat'].lower():
                medicine_data = result
                break
        
        if not medicine_data:
            return go.Figure()
        
        # Extract PBF prices
        pbf_prices = []
        for key, value in medicine_data.items():
            if key.startswith('harga_') and key not in ['harga_terbaik', 'harga_termahal', 'harga_rata_rata']:
                pbf_name = key.replace('harga_', '')
                pbf_prices.append({'PBF': pbf_name, 'Harga': value})
        
        if not pbf_prices:
            return go.Figure()
        
        df_prices = pd.DataFrame(pbf_prices)
        
        # Create bar chart
        fig = px.bar(
            df_prices,
            x='PBF',
            y='Harga',
            title=f'Perbandingan Harga: {medicine_data["nama_obat"]}',
            labels={'Harga': 'Harga (Rp)'},
            color='Harga',
            color_continuous_scale='RdYlGn_r'
        )
        
        # Add average line
        avg_price = df_prices['Harga'].mean()
        fig.add_hline(
            y=avg_price,
            line_dash="dash",
            line_color="red",
            annotation_text=f"Rata-rata: Rp {avg_price:,.0f}"
        )
        
        fig.update_layout(
            height=config.CHART_HEIGHT,
            yaxis=dict(tickformat=',.0f')
        )
        
        return fig