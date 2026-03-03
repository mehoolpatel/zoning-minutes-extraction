import os
import pdfplumber
import glob

# 1. Get the absolute path of the directory containing this script
# This works whether you run it from the root or inside the folder
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# 2. Define the PDF folder relative to the SCRIPT_DIR
# Assuming your script is in project/scripts/ and PDFs are in project/data/pdfs/
PDF_FOLDER = os.path.join(SCRIPT_DIR, "..", "data", "pdfs")

# 3. Create a unique path for the output
OUTPUT_DIR = os.path.join(SCRIPT_DIR, "..", "data", "extracted_pages")
os.makedirs(OUTPUT_DIR, exist_ok=True)

def process_files():
    # Verify the directory actually exists
    if not os.path.exists(PDF_FOLDER):
        print(f"Error: Directory not found at {PDF_FOLDER}")
        return

    print(f"Looking for PDFs in: {PDF_FOLDER}")
    
    # Find all PDFs in the folder
    pdf_files = glob.glob(os.path.join(PDF_FOLDER, "*.pdf"))
    
    if not pdf_files:
        print("No PDF files found.")
        return

    for file_path in pdf_files:
        print(f"--- Processing: {os.path.basename(file_path)} ---")
        
        try:
            with pdfplumber.open(file_path) as pdf:
                for i, page in enumerate(pdf.pages):
                    text = page.extract_text(layout=True)
                    
                    filename = os.path.join(
                        OUTPUT_DIR, 
                        f"{os.path.basename(file_path)}_page_{i+1}.txt"
                    )
                    
                    with open(filename, "w", encoding="utf-8") as f:
                        f.write(text)
                    
                    print(f"Saved: {filename}")
                    
        except Exception as e:
            print(f"Error processing {file_path}: {e}")

if __name__ == "__main__":
    process_files()