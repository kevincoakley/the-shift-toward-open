#!/usr/bin/env python3
"""
Extract text from academic PDF papers using PyMuPDF (fitz) library.
Processes all PDFs in the pdf/ directory and saves results to results/ directory.
"""

import os
import re
from pathlib import Path
import fitz  # PyMuPDF


def clean_non_latin_chars(text: str) -> str:
    """Remove non-Latin characters and symbols while preserving letters, numbers, punctuation, and useful symbols."""
    # Keep Latin letters, numbers, standard punctuation, and useful symbols:
    # - Email/web: @ # / \ . _
    # - Math: + - * = % < > 
    # - Other useful: & $ | ~
    cleaned = re.sub(r'[^\w\s.,;:!?()[\]{}"\'-@#/\\._+\-*=%<>&$|~]', ' ', text)
    
    # Clean up multiple spaces created by character removal
    cleaned = re.sub(r'\s+', ' ', cleaned)
    
    return cleaned.strip()


def clean_text(text: str) -> str:
    """Clean and fix common PDF extraction issues in academic papers."""
    # Enhanced hyphen handling for academic papers
    text = re.sub(r'(\w)-\s+(\w)', r'\1\2', text)  # Fix "word- word" -> "wordword"
    text = re.sub(r'(\w)-\s*\n\s*(\w)', r'\1\2', text)  # Fix hyphenated across lines
    text = re.sub(r'(\w)-\n(\w)', r'\1\2', text)  # Handle line break hyphens
    
    # Remove common footer patterns
    text = re.sub(r'\n\s*\d+\s*$', '', text)  # Remove trailing page numbers
    text = re.sub(r'\n\s*[\d\-–—]+\s*$', '', text)  # Remove footer separators
    
    # Fix common PDF extraction issues
    text = re.sub(r'([a-z])([A-Z])', r'\1 \2', text)  # Fix merged words like "wordWord"
    text = re.sub(r'\s+', ' ', text)  # Normalize whitespace (after hyphen fixes)
        
    # Preserve academic formatting
    text = re.sub(r'\n\s*•\s*', '\n• ', text)  # Fix bullet points
    text = re.sub(r'\n\s*(\d+\.)\s*', r'\n\1 ', text)  # Fix numbered lists
    
    # Clean up multiple spaces
    text = re.sub(r'\s{2,}', ' ', text)  # Multiple spaces to single space
    
    return text.strip()


def extract_text_blocks(doc):
    """Extract text blocks from PDF document, filtering and cleaning as needed."""
    text_blocks = []
    
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        
        # Get text blocks with positioning info
        blocks = page.get_text("dict")
        
        for block in blocks["blocks"]:
            if "lines" in block:  # Text block
                block_text = ""
                for line in block["lines"]:
                    line_text = ""
                    for span in line["spans"]:
                        line_text += span["text"]
                    block_text += line_text + " "
                
                # Clean the block text
                block_text = block_text.strip()
                if block_text:
                    # Apply character cleaning
                    cleaned_block = clean_non_latin_chars(block_text)
                    
                    # Skip if cleaning removed all meaningful content
                    if cleaned_block and len(cleaned_block.strip()) > 3:
                        text_blocks.append(cleaned_block)
    
    return text_blocks


def process_pdf(pdf_path: Path, output_dir: Path) -> None:
    """Process a single PDF file and extract text using PyMuPDF."""
    print(f"Processing: {pdf_path.name}")
    
    try:
        # Open PDF with PyMuPDF
        doc = fitz.open(str(pdf_path))
        
        # Extract text blocks
        text_blocks = extract_text_blocks(doc)
        
        # Close the document
        doc.close()
        
        # Save plain text output
        text_output_file = output_dir / f"{pdf_path.stem}.txt"
        with open(text_output_file, 'w', encoding='utf-8') as f:
            f.write(f"# {pdf_path.name}\n\n")
            for block in text_blocks:
                cleaned_text = clean_text(block)
                # Skip if too short after cleaning
                if cleaned_text and len(cleaned_text) > 10:
                    f.write(cleaned_text + "\n\n")
        
        print(f"✓ Completed: {pdf_path.name} -> {text_output_file.name}")
        
    except Exception as e:
        print(f"✗ Error processing {pdf_path.name}: {str(e)}")


def main():
    """Main function to process all PDFs in the pdf directory using PyMuPDF."""
    # Set up directories
    pdf_dir = Path("pdf")
    output_dir = Path("results")
    
    # Create output directory if it doesn't exist
    output_dir.mkdir(exist_ok=True)
    
    # Check if pdf directory exists
    if not pdf_dir.exists():
        print(f"Error: {pdf_dir} directory does not exist!")
        return
    
    # Find all PDF files
    pdf_files = list(pdf_dir.glob("*.pdf"))
    
    if not pdf_files:
        print(f"No PDF files found in {pdf_dir}")
        return
    
    print(f"Found {len(pdf_files)} PDF files to process")
    print(f"Output will be saved to: {output_dir.absolute()}")
    print("-" * 60)
    
    # Process each PDF with error handling
    success_count = 0
    error_count = 0
    
    for pdf_file in sorted(pdf_files):
        try:
            process_pdf(pdf_file, output_dir)
            success_count += 1
        except Exception as e:
            print(f"✗ Failed to process {pdf_file.name}: {str(e)}")
            error_count += 1
            continue
    
    print("-" * 60)
    print(f"Processing complete! Results saved in {output_dir.absolute()}")
    print(f"Successfully processed: {success_count} files")
    print(f"Failed to process: {error_count} files")


if __name__ == "__main__":
    main()