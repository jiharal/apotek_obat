"""
Data processing and price comparison utilities
"""

import pandas as pd
import numpy as np
from difflib import SequenceMatcher
from typing import List, Dict, Any
import re
from datetime import datetime


class DataProcessor:
    """Process and analyze medicine price data"""

    def __init__(self, similarity_threshold: float = 0.8):
        self.similarity_threshold = similarity_threshold
        self.common_medicine_variations = {
            "paracetamol": ["paracetamol", "parasetamol", "acetaminophen"],
            "amoxicillin": ["amoxicillin", "amoksisilin", "amoxicilin"],
            "ibuprofen": ["ibuprofen", "ibuprophen"],
            "aspirin": ["aspirin", "asam asetilsalisilat", "asetosal"],
        }

    def process_data(self, raw_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process and clean raw extracted data"""
        if not raw_data:
            return []

        # Convert to DataFrame for easier processing
        df = pd.DataFrame(raw_data)

        # Clean medicine names
        df["nama_obat_cleaned"] = df["nama_obat"].apply(self._clean_medicine_name)


        # Add derived fields
        df["nama_obat_standardized"] = df["nama_obat_cleaned"].apply(
            self._standardize_medicine_name
        )
        df["timestamp"] = datetime.now()

        # Ensure harga column exists
        if "harga" not in df.columns:
            df["harga"] = 0

        # Remove duplicates within same PBF and table side
        df = df.drop_duplicates(subset=["nama_obat_standardized", "pbf", "table_side"], keep="first")

        # Convert back to list of dicts
        return df.to_dict("records")

    def compare_prices(
        self, processed_data: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Compare prices across PBFs and find best deals"""
        if not processed_data:
            return []

        df = pd.DataFrame(processed_data)

        # Group by standardized medicine name
        grouped = df.groupby("nama_obat_standardized")

        comparison_results = []

        for medicine_name, group in grouped:
            if len(group) < 2:  # Skip if only one PBF has this medicine
                continue

            # Find best price
            best_price_row = group.loc[group["harga"].idxmin()]
            worst_price_row = group.loc[group["harga"].idxmax()]

            # Calculate savings
            savings_amount = worst_price_row["harga"] - best_price_row["harga"]
            savings_percentage = (
                (savings_amount / worst_price_row["harga"]) * 100
                if worst_price_row["harga"] > 0
                else 0
            )

            # Create price comparison data
            price_data = {}
            for _, row in group.iterrows():
                pbf_name = row["pbf"]
                price_data[f"harga_{pbf_name}"] = row["harga"]

            comparison_result = {
                "nama_obat": best_price_row["nama_obat_cleaned"],
                "nama_obat_standardized": medicine_name,
                "harga_terbaik": best_price_row["harga"],
                "pbf_terbaik": best_price_row["pbf"],
                "harga_termahal": worst_price_row["harga"],
                "pbf_termahal": worst_price_row["pbf"],
                "penghematan_rupiah": savings_amount,
                "persentase_hemat": savings_percentage,
                "jumlah_pbf": len(group),
                # "satuan": best_price_row["satuan_normalized"],
                "harga_rata_rata": group["harga"].mean(),
                "selisih_harga": group["harga"].max() - group["harga"].min(),
                **price_data,
            }

            comparison_results.append(comparison_result)

        # Sort by savings percentage (highest first)
        comparison_results.sort(key=lambda x: x["persentase_hemat"], reverse=True)

        return comparison_results

    def _clean_medicine_name(self, name: str) -> str:
        """Minimal cleaning to preserve original PBF medicine names"""
        if not name or pd.isna(name):
            return ""

        # Preserve original name with minimal cleaning
        name = str(name).strip()
        
        # Only normalize whitespace
        name = " ".join(name.split())

        return name

    def _standardize_medicine_name(self, name: str) -> str:
        """Standardize medicine name using known variations"""
        if not name:
            return ""

        name_lower = name.lower()

        # Check against known variations
        for standard_name, variations in self.common_medicine_variations.items():
            for variation in variations:
                if variation in name_lower:
                    return standard_name.title()

        return name

    def _normalize_unit(self, unit: str) -> str:
        """Normalize unit information"""
        if not unit or pd.isna(unit):
            return ""

        unit = str(unit).lower().strip()

        # Standardize common units
        unit_mappings = {
            "tab": "tablet",
            "caps": "kapsul",
            "cap": "kapsul",
            "inj": "injeksi",
            "syr": "sirup",
            "susp": "suspensi",
            "bot": "botol",
            "btl": "botol",
            "amp": "ampul",
            "vl": "vial",
        }

        for abbrev, full_form in unit_mappings.items():
            if abbrev in unit:
                unit = unit.replace(abbrev, full_form)

        return unit.strip()

    def find_similar_medicines(
        self, target_name: str, medicine_list: List[str]
    ) -> List[Dict[str, Any]]:
        """Find medicines with similar names"""
        similar_medicines = []

        target_clean = self._clean_medicine_name(target_name)

        for medicine in medicine_list:
            medicine_clean = self._clean_medicine_name(medicine)

            # Calculate similarity
            similarity = SequenceMatcher(
                None, target_clean.lower(), medicine_clean.lower()
            ).ratio()

            if (
                similarity >= self.similarity_threshold
                and target_clean.lower() != medicine_clean.lower()
            ):
                similar_medicines.append(
                    {"nama_obat": medicine, "similarity_score": similarity}
                )

        # Sort by similarity score
        similar_medicines.sort(key=lambda x: x["similarity_score"], reverse=True)

        return similar_medicines

    def get_price_statistics(
        self, processed_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Calculate price statistics"""
        if not processed_data:
            return {}

        df = pd.DataFrame(processed_data)

        stats = {
            "total_medicines": len(df),
            "total_pbfs": df["pbf"].nunique(),
            "average_price": df["harga"].mean(),
            "median_price": df["harga"].median(),
            "min_price": df["harga"].min(),
            "max_price": df["harga"].max(),
            "price_std": df["harga"].std(),
            "medicines_per_pbf": df.groupby("pbf").size().to_dict(),
            "avg_price_per_pbf": df.groupby("pbf")["harga"].mean().to_dict(),
        }

        return stats

    def get_best_deals(
        self, comparison_results: List[Dict[str, Any]], top_n: int = 10
    ) -> List[Dict[str, Any]]:
        """Get top N best deals by savings percentage"""
        if not comparison_results:
            return []

        # Sort by savings percentage and return top N
        sorted_deals = sorted(
            comparison_results, key=lambda x: x["persentase_hemat"], reverse=True
        )

        return sorted_deals[:top_n]

    def get_pbf_performance(
        self, comparison_results: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze PBF performance in terms of best prices"""
        if not comparison_results:
            return {}

        pbf_stats = {}

        for result in comparison_results:
            best_pbf = result["pbf_terbaik"]

            if best_pbf not in pbf_stats:
                pbf_stats[best_pbf] = {
                    "best_price_count": 0,
                    "total_medicines": 0,
                    "total_savings": 0,
                    "win_rate": 0,
                }

            pbf_stats[best_pbf]["best_price_count"] += 1
            pbf_stats[best_pbf]["total_savings"] += result["penghematan_rupiah"]

        # Calculate win rates and total medicines per PBF
        all_pbfs = set()
        for result in comparison_results:
            all_pbfs.add(result["pbf_terbaik"])
            all_pbfs.add(result["pbf_termahal"])

            # Count all PBF prices mentioned in each result
            for key in result.keys():
                if (
                    key.startswith("harga_")
                    and key != "harga_terbaik"
                    and key != "harga_termahal"
                    and key != "harga_rata_rata"
                ):
                    pbf_name = key.replace("harga_", "")
                    all_pbfs.add(pbf_name)

        # Count total medicines per PBF
        for pbf in all_pbfs:
            if pbf not in pbf_stats:
                pbf_stats[pbf] = {
                    "best_price_count": 0,
                    "total_medicines": 0,
                    "total_savings": 0,
                    "win_rate": 0,
                }

            # Count how many medicines this PBF has
            for result in comparison_results:
                pbf_price_key = f"harga_{pbf}"
                if pbf_price_key in result:
                    pbf_stats[pbf]["total_medicines"] += 1

        # Calculate win rates
        for pbf, stats in pbf_stats.items():
            if stats["total_medicines"] > 0:
                stats["win_rate"] = (
                    stats["best_price_count"] / stats["total_medicines"]
                ) * 100

        return pbf_stats
