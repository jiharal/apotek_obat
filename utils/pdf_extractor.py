"""
PDF extraction utilities for medicine price data
"""

import re
import pandas as pd
import pdfplumber
import PyPDF2
import tabula
from io import BytesIO
from typing import List, Dict, Any
import streamlit as st


class PDFExtractor:
    """Extract medicine price data from PDF files"""

    def __init__(self):
        self.price_patterns = [
            r"Rp\s*[\d,\.]+",
            r"IDR\s*[\d,\.]+",
            r"[\d,\.]+\s*rupiah",
            r"\b\d{1,3}(?:[,\.]\d{3})*(?:[,\.]\d{2})?\b",
            r"\b\d{3,}\b",  # Simple number pattern for prices
            r"[\d,\.]{3,}",  # Numbers with commas/dots
        ]

        self.medicine_indicators = [
            "tablet",
            "kapsul",
            "sirup",
            "injeksi",
            "mg",
            "ml",
            "gram",
            "strip",
            "botol",
            "ampul",
        ]

        # Common column names for medicine names
        self.medicine_name_columns = [
            "nama brg",
            "nama barang",
            "nama obat",
            "barang",
            "obat",
            "produk",
            "product",
            "item",
            "medicine",
            "drug",
            "nama_barang",
            "nama_obat",
            "nama_brg",
        ]

        # Common column names for prices
        self.price_columns = [
            "hna+ppn",
            "hna + ppn",
            "hrg+ppn",
            "hrg + ppn",
            "harga jadi",
            "harga_jadi",
            "hna ppn",
            "hrg ppn",
            "harga",
            "price",
            "hna",
            "hrg",
            "harga + ppn",
            "harga+ppn",
            "harga ppn",
            "total",
            "amount",
            "hna_ppn",
            "harga_ppn",
            "hrg_ppn",
        ]
        


    def extract_from_file(self, uploaded_file) -> List[Dict[str, Any]]:
        """Extract data from uploaded PDF file - Focus on table extraction only"""
        try:
            # Focus only on table extraction methods
            data = []

            # Method 1: Try pdfplumber for table extraction
            try:
                data.extend(self._extract_with_pdfplumber(uploaded_file))
                if data:
                    st.success(
                        f"✅ Berhasil mengekstrak {len(data)} item dari {uploaded_file.name} menggunakan pdfplumber"
                    )
            except Exception as e:
                st.warning(f"pdfplumber extraction failed: {str(e)}")

            # Method 2: Try tabula for table extraction if pdfplumber failed
            if not data:
                try:
                    data.extend(self._extract_with_tabula(uploaded_file))
                    if data:
                        st.success(
                            f"✅ Berhasil mengekstrak {len(data)} item dari {uploaded_file.name} menggunakan tabula"
                        )
                except Exception as e:
                    st.warning(f"tabula extraction failed: {str(e)}")

            # Skip text-based extraction - focus only on tables
            if not data:
                st.error(
                    f"❌ Tidak dapat menemukan tabel di {uploaded_file.name}. Pastikan PDF berisi tabel harga yang terstruktur."
                )

            return self._validate_and_clean_data(data)

        except Exception as e:
            st.error(f"Failed to extract data from {uploaded_file.name}: {str(e)}")
            return []

    def _extract_with_pdfplumber(self, uploaded_file) -> List[Dict[str, Any]]:
        """Extract data using pdfplumber - Focus on tables only"""
        data = []

        with pdfplumber.open(uploaded_file) as pdf:
            for page_num, page in enumerate(pdf.pages):
                # Extract tables only
                tables = page.extract_tables()

                for table_index, table in enumerate(tables):
                    if (
                        table and len(table) > 1
                    ):  # Must have header and at least one data row
                        # Convert table to dataframe
                        try:
                            # Use first row as header if it looks like a header
                            header_row = table[0] if table[0] else None
                            data_rows = table[1:]

                            # Create dataframe
                            if header_row:
                                df = pd.DataFrame(data_rows, columns=header_row)
                                # Identify column mappings
                                column_mapping = self._identify_columns(header_row)

                                # Debug: Show identified columns
                                if any(
                                    col is not None for col in column_mapping.values()
                                ):
                                    name_header = (
                                        header_row[column_mapping["name_col"]]
                                        if column_mapping["name_col"] is not None
                                        else "❌"
                                    )
                                    price_header = (
                                        header_row[column_mapping["price_col"]]
                                        if column_mapping["price_col"] is not None
                                        else "❌"
                                    )
                                    st.info(
                                        f"📋 Kolom terdeteksi - Nama: '{name_header}' | Harga: '{price_header}'"
                                    )
                            else:
                                df = pd.DataFrame(data_rows)
                                column_mapping = None

                            # Process each row for medicine data
                            for row_index, row in df.iterrows():
                                if column_mapping:
                                    medicine_data = self._extract_medicine_info_from_row_with_mapping(
                                        row, column_mapping
                                    )
                                else:
                                    medicine_data = (
                                        self._extract_medicine_info_from_row(
                                            row.tolist()
                                        )
                                    )

                                if medicine_data:
                                    medicine_data["page"] = page_num + 1
                                    medicine_data["table_index"] = table_index
                                    medicine_data["row_index"] = row_index
                                    data.append(medicine_data)
                        except Exception as e:
                            st.warning(
                                f"Error processing table {table_index} on page {page_num + 1}: {str(e)}"
                            )
                            continue

        return data

    def _extract_with_tabula(self, uploaded_file) -> List[Dict[str, Any]]:
        """Extract data using tabula - Focus on structured tables"""
        data = []

        # Save uploaded file temporarily
        temp_file = BytesIO(uploaded_file.read())
        uploaded_file.seek(0)  # Reset file pointer

        try:
            # Extract tables from all pages with better options
            dfs = tabula.read_pdf(
                temp_file,
                pages="all",
                multiple_tables=True,
                pandas_options={"header": 0},  # Use first row as header
                silent=True,
            )

            for table_num, df in enumerate(dfs):
                if not df.empty and len(df) > 0:
                    # Clean column names
                    original_columns = list(df.columns)
                    df.columns = [
                        str(col).strip() if col else f"Col_{i}"
                        for i, col in enumerate(df.columns)
                    ]

                    # Identify column mappings from headers
                    column_mapping = self._identify_columns(original_columns)

                    # Process each row
                    for row_index, row in df.iterrows():
                        if column_mapping and (
                            column_mapping["name_col"] is not None
                            and column_mapping["price_col"] is not None
                        ):
                            medicine_data = (
                                self._extract_medicine_info_from_row_with_mapping(
                                    row, column_mapping
                                )
                            )
                        else:
                            medicine_data = self._extract_medicine_info_from_row(
                                row.tolist()
                            )

                        if medicine_data:
                            medicine_data["table_num"] = table_num
                            medicine_data["row_index"] = row_index
                            data.append(medicine_data)

        except Exception as e:
            raise Exception(f"Tabula extraction failed: {str(e)}")

        return data

    def _extract_text_based(self, uploaded_file) -> List[Dict[str, Any]]:
        """Extract data from text content"""
        data = []

        # Read PDF with PyPDF2
        pdf_reader = PyPDF2.PdfReader(uploaded_file)

        for page_num, page in enumerate(pdf_reader.pages):
            text = page.extract_text()
            if text:
                page_data = self._extract_from_text(text, page_num + 1)
                data.extend(page_data)

        return data

    def _extract_from_text(self, text: str, page_num: int) -> List[Dict[str, Any]]:
        """Extract medicine data from text"""
        data = []
        lines = text.split("\n")

        for i, line in enumerate(lines):
            line = line.strip()

            # Check if line contains medicine indicators
            if any(
                indicator.lower() in line.lower()
                for indicator in self.medicine_indicators
            ):
                # Look for price in current line or nearby lines
                price = self._extract_price_from_text(line)

                if not price and i + 1 < len(lines):
                    price = self._extract_price_from_text(lines[i + 1])

                if not price and i > 0:
                    price = self._extract_price_from_text(lines[i - 1])

                if price:
                    medicine_name = self._clean_medicine_name(line)
                    if medicine_name:
                        data.append(
                            {
                                "nama_obat": medicine_name,
                                "harga": price,
                                # "satuan": self._extract_unit(line),
                                "page": page_num,
                            }
                        )

        return data

    def _identify_columns(self, header_row: List) -> Dict[str, int]:
        """Identify columns for medicine names and prices only"""
        column_mapping = {
            "name_col": None,
            "price_col": None,
        }

        for i, header in enumerate(header_row):
            if not header:
                continue

            header_clean = str(header).lower().strip()

            # Check for medicine name columns
            if column_mapping["name_col"] is None:
                for name_pattern in self.medicine_name_columns:
                    if name_pattern.lower() in header_clean:
                        column_mapping["name_col"] = i
                        break

            # Check for price columns
            if column_mapping["price_col"] is None:
                for price_pattern in self.price_columns:
                    if price_pattern.lower() in header_clean:
                        column_mapping["price_col"] = i
                        break

        return column_mapping

    def _extract_medicine_info_from_row_with_mapping(
        self, row, column_mapping: Dict[str, int]
    ) -> Dict[str, Any]:
        """Extract medicine information using identified column mapping"""
        if not column_mapping or column_mapping["name_col"] is None:
            return self._extract_medicine_info_from_row(row.tolist())

        try:
            # Get values from mapped columns
            name_col = column_mapping["name_col"]
            price_col = column_mapping["price_col"]

            # Extract name (required)
            medicine_name = ""
            if name_col < len(row):
                medicine_name = str(
                    row.iloc[name_col] if hasattr(row, "iloc") else row[name_col]
                )
                medicine_name = self._clean_medicine_name(medicine_name)

            # Extract price (optional but preferred)
            price_value = None
            if price_col is not None and price_col < len(row):
                price_text = str(
                    row.iloc[price_col] if hasattr(row, "iloc") else row[price_col]
                )
                price_value = self._extract_price_from_text(price_text)

            # Validate and return (only name is required)
            if medicine_name and len(medicine_name) > 2:
                return {
                    "nama_obat": medicine_name,
                    "harga": price_value if price_value else 0,
                    "extraction_method": "column_mapping",
                }

        except Exception as e:
            # Fallback to row-based extraction
            return self._extract_medicine_info_from_row(row.tolist())

        return None

    def _extract_medicine_info_from_row(self, row: List) -> Dict[str, Any]:
        """Extract medicine information from table row - Improved for structured data"""
        if not row or len(row) < 2:
            return None

        medicine_data = {}
        potential_names = []
        potential_prices = []

        # First pass: identify all potential names and prices
        for i, cell in enumerate(row):
            cell_str = str(cell).strip() if cell else ""

            if not cell_str or cell_str.lower() in ["nan", "none", "", "null"]:
                continue

            # Check if cell contains price
            price = self._extract_price_from_text(cell_str)
            if price:
                potential_prices.append((i, price, cell_str))

            # Check if cell contains medicine name (prioritize cells with medicine indicators)
            if any(
                indicator.lower() in cell_str.lower()
                for indicator in self.medicine_indicators
            ):
                potential_names.append(
                    (i, cell_str, True)
                )  # True = has medicine indicator
            elif (
                len(cell_str) > 3 and not price
            ):  # Potential name if no price and reasonable length
                potential_names.append(
                    (i, cell_str, False)
                )  # False = no medicine indicator

        # Second pass: assign best candidates
        # Prioritize medicine names with indicators
        best_name = None
        for _, name, has_indicator in sorted(
            potential_names, key=lambda x: x[2], reverse=True
        ):
            cleaned_name = self._clean_medicine_name(name)
            if cleaned_name and len(cleaned_name) > 2:
                best_name = (name, cleaned_name)
                break

        # Get the best price (usually the largest reasonable price)
        best_price = None
        if potential_prices:
            # Sort by price value and take the most reasonable one
            valid_prices = [
                (i, price, orig)
                for i, price, orig in potential_prices
                if 100 <= price <= 10000000
            ]
            if valid_prices:
                best_price = sorted(valid_prices, key=lambda x: x[1])[-1][
                    1
                ]  # Take highest valid price

        # Build result
        if best_name and best_price:
            medicine_data = {
                "nama_obat": best_name[1],  # cleaned name
                "harga": best_price,
                "kemasan": "",
                "raw_row": row,  # Keep original row for debugging
            }
            return medicine_data

        return None

    def _extract_price_from_text(self, text: str) -> float:
        """Extract price from text - Enhanced for Indonesian formats"""
        if not text:
            return None

        # Remove common currency symbols and whitespace
        text_clean = re.sub(r"[Rp\s]+", "", str(text), flags=re.IGNORECASE)
        text_clean = re.sub(r"IDR\s*", "", text_clean, flags=re.IGNORECASE)
        text_clean = re.sub(r"\s*rupiah\s*", "", text_clean, flags=re.IGNORECASE)
        text_clean = text_clean.strip()

        # Enhanced price patterns for better detection
        enhanced_patterns = [
            r"\b\d{1,3}(?:\.\d{3})*(?:,\d{1,2})?\b",  # Indonesian: 1.500.000,50
            r"\b\d{1,3}(?:,\d{3})*(?:\.\d{1,2})?\b",  # US/International: 1,500,000.50
            r"\b\d{4,}\b",  # Simple numbers: 1500000
            r"\b\d{1,3}(?:[,\.]\d{3})+\b",  # Numbers with separators
            r"\d+[,\.]\d+",  # Any number with decimal
            r"\d{3,}",  # Any number 3+ digits
        ]

        for pattern in enhanced_patterns:
            matches = re.findall(pattern, text_clean)
            for match in matches:
                try:
                    price = self._parse_indonesian_price(match)
                    if price and 100 <= price <= 100000000:  # Reasonable price range
                        # Debug info for price parsing (remove in production)
                        # st.write(f"✅ Parsed price: '{match}' → {price:,.0f}")
                        return price
                except (ValueError, TypeError) as e:
                    # Debug info for failed parsing (remove in production)
                    # st.write(f"❌ Failed to parse: '{match}' - {str(e)}")
                    continue

        return None
    
    def _parse_indonesian_price(self, price_str: str) -> float:
        """Parse Indonesian price format with improved logic"""
        if not price_str:
            return None
            
        # Remove any remaining non-numeric characters except dots and commas
        price_str = re.sub(r"[^\d,\.]", "", price_str)
        
        if not price_str:
            return None
            
        # Case 1: No separators - simple number
        if ',' not in price_str and '.' not in price_str:
            return float(price_str)
        
        # Case 2: Only dots (Indonesian thousands separator)
        if ',' not in price_str and '.' in price_str:
            # Check if it's decimal (only one dot with 1-2 digits after)
            if price_str.count('.') == 1 and len(price_str.split('.')[1]) <= 2:
                return float(price_str)  # Decimal format
            else:
                # Thousands separator - remove all dots
                return float(price_str.replace('.', ''))
        
        # Case 3: Only commas 
        if '.' not in price_str and ',' in price_str:
            # Check if it's decimal (only one comma with 1-2 digits after)
            if price_str.count(',') == 1 and len(price_str.split(',')[1]) <= 2:
                return float(price_str.replace(',', '.'))  # Convert to decimal
            else:
                # Thousands separator - remove all commas
                return float(price_str.replace(',', ''))
        
        # Case 4: Both dots and commas - determine format
        if ',' in price_str and '.' in price_str:
            # Split by all separators to analyze
            parts = re.split(r'[,\.]', price_str)
            
            # Indonesian format: 1.500.000,50 (dots=thousands, comma=decimal)
            if price_str.rfind(',') > price_str.rfind('.'):
                # Last separator is comma - Indonesian format
                if len(parts[-1]) <= 2:  # Last part is decimal
                    integer_part = ''.join(parts[:-1])
                    decimal_part = parts[-1]
                    return float(f"{integer_part}.{decimal_part}")
                else:
                    # All separators are thousands
                    return float(''.join(parts))
            
            # US format: 1,500,000.50 (commas=thousands, dot=decimal)
            else:
                # Last separator is dot
                if len(parts[-1]) <= 2:  # Last part is decimal
                    integer_part = ''.join(parts[:-1])
                    decimal_part = parts[-1]
                    return float(f"{integer_part}.{decimal_part}")
                else:
                    # All separators are thousands
                    return float(''.join(parts))
        
        # Fallback - try direct conversion
        try:
            return float(price_str)
        except ValueError:
            return None

        
    def _extract_dual_tables_from_page(self, page, page_num: int) -> List[Dict[str, Any]]:
        """Extract data from dual side-by-side tables on a page"""
        data = []
        
        try:
            # Get page dimensions
            page_width = page.width
            page_height = page.height
            
            # Define boundaries for left and right tables
            # Adjust these values based on your PDF layout
            left_table_bbox = (0, 0, page_width * 0.48, page_height)  # Left 48% of page
            right_table_bbox = (page_width * 0.52, 0, page_width, page_height)  # Right 48% of page
            
            # Extract left table
            left_crop = page.crop(left_table_bbox)
            left_tables = left_crop.extract_tables()
            
            # Extract right table  
            right_crop = page.crop(right_table_bbox)
            right_tables = right_crop.extract_tables()
            
            # Process left tables
            for table_index, table in enumerate(left_tables):
                if table and len(table) > 1:
                    table_data = self._process_single_table(table, page_num, f"left_{table_index}")
                    if table_data:
                        # Mark as left table
                        for item in table_data:
                            item["table_side"] = "left"
                        data.extend(table_data)
                        st.success(f"✅ Extracted {len(table_data)} items from left table on page {page_num + 1}")
            
            # Process right tables
            for table_index, table in enumerate(right_tables):
                if table and len(table) > 1:
                    table_data = self._process_single_table(table, page_num, f"right_{table_index}")
                    if table_data:
                        # Mark as right table
                        for item in table_data:
                            item["table_side"] = "right"
                        data.extend(table_data)
                        st.success(f"✅ Extracted {len(table_data)} items from right table on page {page_num + 1}")
                        
            return data if data else None
            
        except Exception as e:
            st.warning(f"Dual table extraction failed on page {page_num + 1}: {str(e)}")
            return None
    
    def _process_single_table(self, table, page_num: int, table_id: str) -> List[Dict[str, Any]]:
        """Process a single table and extract medicine data"""
        data = []
        
        try:
            # Use first row as header if it looks like a header
            header_row = table[0] if table[0] else None
            data_rows = table[1:]
            
            if not header_row:
                return data
                
            # Create dataframe
            df = pd.DataFrame(data_rows, columns=header_row)
            
            # Identify column mappings
            column_mapping = self._identify_columns(header_row)
            
            # Debug: Show identified columns
            if any(col is not None for col in column_mapping.values()):
                name_header = (
                    header_row[column_mapping["name_col"]]
                    if column_mapping["name_col"] is not None
                    else "❌"
                )
                price_header = (
                    header_row[column_mapping["price_col"]]
                    if column_mapping["price_col"] is not None
                    else "❌"
                )
                st.info(
                    f"📋 [{table_id}] Kolom terdeteksi - Nama: '{name_header}' | Harga: '{price_header}'"
                )
            
            # Process each row for medicine data
            for row_index, row in df.iterrows():
                medicine_data = self._extract_medicine_info_from_row_with_mapping(
                    row, column_mapping
                )
                
                if medicine_data:
                    medicine_data["page"] = page_num + 1
                    medicine_data["table_id"] = table_id
                    medicine_data["row_index"] = row_index
                    data.append(medicine_data)
                    
        except Exception as e:
            st.warning(f"Error processing table {table_id} on page {page_num + 1}: {str(e)}")
            
        return data


    def _clean_medicine_name(self, text: str) -> str:
        """Minimal cleaning to preserve original medicine names from each PBF"""
        if not text:
            return ""

        # Convert to string and basic cleanup
        name = str(text).strip()
        
        # Skip if it's clearly not a medicine name (common headers)
        skip_patterns = [
            r"^no\.?\s*$",
            r"^nama\s*(obat|barang|brg)?\s*$",
            r"^barang\s*$",
            r"^harga\s*$",
            r"^hna\s*$",
            r"^hrg\s*$",
            r"^hna\s*\+\s*ppn\s*$",
            r"^price\s*$",
            r"^item\s*$",
            r"^kode\s*$",
            r"^product\s*$",
            r"^\d+\s*$",  # Just numbers
            r"^total\s*$",
            r"^subtotal\s*$",
        ]
        
        for pattern in skip_patterns:
            if re.match(pattern, name.lower()):
                return ""
        
        # Minimal cleaning - only remove obvious table artifacts
        # Remove leading item numbers (e.g., "1. ", "001 ")
        name = re.sub(r"^\d+\.?\s+", "", name)
        
        # Remove trailing dots and extra spaces
        name = re.sub(r"\s*\.+\s*$", "", name)
        
        # Normalize whitespace but preserve original casing and formatting
        name = " ".join(name.split())
        
        # Only return if it has reasonable length
        if len(name) >= 3:
            return name
        
        return ""

    def _extract_unit(self, text: str) -> str:
        """Extract unit/packaging information"""
        if not text:
            return ""

        # Common medicine units
        units = [
            "tablet",
            "kapsul",
            "sirup",
            "injeksi",
            "ml",
            "mg",
            "gram",
            "strip",
            "botol",
            "ampul",
            "vial",
        ]

        text_lower = text.lower()
        for unit in units:
            if unit in text_lower:
                # Try to extract number + unit
                pattern = rf"\d+\s*{unit}"
                match = re.search(pattern, text_lower)
                if match:
                    return match.group()
                return unit

        return ""

    def _validate_and_clean_data(
        self, data: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Validate and clean extracted data - Enhanced for table data"""
        cleaned_data = []
        seen_combinations = set()  # To avoid duplicates

        for item in data:
            # Skip if missing essential data
            if not item.get("nama_obat") or not item.get("harga"):
                continue

            # Skip if medicine name is too short or looks like header/garbage
            nama_obat = str(item["nama_obat"]).strip()
            if len(nama_obat) < 3:
                continue

            # Skip common table headers or non-medicine entries
            skip_patterns = [
                r"^no\.?\s*$",
                r"^nama\s*obat\s*$",
                r"^nama\s*barang\s*$",
                r"^nama\s*brg\s*$",
                r"^barang\s*$",
                r"^harga\s*$",
                r"^hna\s*$",
                r"^hrg\s*$",
                r"^hna\s*\+\s*ppn\s*$",
                r"^hna\+ppn\s*$",
                r"^hrg\s*\+\s*ppn\s*$",
                r"^hrg\+ppn\s*$",
                r"^harga\s*jadi\s*$",
                r"^satuan\s*$",
                r"^kode\s*$",
                r"^item\s*$",
                r"^product\s*$",
                r"^price\s*$",
                r"^\d+\s*$",
                r"^total\s*$",
                r"^subtotal\s*$",
                r"^kemasan\s*$",
            ]

            if any(re.match(pattern, nama_obat.lower()) for pattern in skip_patterns):
                continue

            # Skip if price is unreasonable (expanded range)
            harga = item["harga"]
            if harga < 100 or harga > 50000000:
                continue

            # Create unique key to avoid duplicates
            unique_key = f"{nama_obat.lower()}_{harga}_{item.get('page', 1)}"
            if unique_key in seen_combinations:
                continue
            seen_combinations.add(unique_key)

            # Ensure all required fields exist
            cleaned_item = {
                "nama_obat": nama_obat,
                "harga": float(harga) if harga else 0,
                "page": item.get("page", 1),
                "pbf": item.get("pbf", ""),
                "table_index": item.get("table_index", 0),
                "table_id": item.get("table_id", ""),
                "table_side": item.get("table_side", ""),
                "row_index": item.get("row_index", 0),
            }

            cleaned_data.append(cleaned_item)

        return cleaned_data
