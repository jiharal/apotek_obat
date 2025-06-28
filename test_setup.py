"""
Simple test script to verify the installation and basic functionality
"""

import sys
import importlib

def test_imports():
    """Test if all required modules can be imported"""
    required_modules = [
        'streamlit',
        'pandas',
        'PyPDF2',
        'pdfplumber',
        'plotly',
        'openpyxl'
    ]
    
    failed_imports = []
    
    for module in required_modules:
        try:
            importlib.import_module(module)
            print(f"✅ {module} - OK")
        except ImportError as e:
            print(f"❌ {module} - FAILED: {e}")
            failed_imports.append(module)
    
    if failed_imports:
        print(f"\n⚠️ Failed to import: {', '.join(failed_imports)}")
        print("Please install required dependencies with: pip install -r requirements.txt")
        return False
    else:
        print("\n✅ All required modules imported successfully!")
        return True

def test_local_modules():
    """Test if local modules can be imported"""
    try:
        from utils.pdf_extractor import PDFExtractor
        from utils.data_processor import DataProcessor
        from utils.visualizer import Visualizer
        import config
        
        print("✅ Local modules imported successfully!")
        
        # Test basic functionality
        processor = DataProcessor()
        extractor = PDFExtractor()
        visualizer = Visualizer()
        
        print("✅ Module instances created successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Local module import failed: {e}")
        return False

if __name__ == "__main__":
    print("Testing Medicine Price Extractor Setup...")
    print("=" * 50)
    
    # Test external dependencies
    deps_ok = test_imports()
    
    print("\n" + "=" * 50)
    
    # Test local modules
    local_ok = test_local_modules()
    
    print("\n" + "=" * 50)
    
    if deps_ok and local_ok:
        print("🎉 Setup test passed! You can run the app with: streamlit run app.py")
    else:
        print("❌ Setup test failed. Please check the errors above.")
        sys.exit(1)