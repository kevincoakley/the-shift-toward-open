# PDF to Text Extractor

A high-quality Python tool for extracting clean text from academic PDF papers using the `PyMuPDF` (fitz) library. Optimized for academic papers with advanced text processing that removes non-Latin characters and symbols while preserving document structure for LLM analysis.

## Features

- **High-Quality Text Extraction**: Uses PyMuPDF's block-based extraction for accurate text recovery
- **LLM-Optimized Output**: Removes non-Latin characters and symbols while preserving meaningful content
- **Clean Text Processing**: Fixes common PDF extraction issues like hyphenation and spacing
- **Document Structure**: Preserves titles, sections, and paragraph organization
- **Character Filtering**: Keeps only letters, numbers, and standard punctuation for better LLM analysis
- **Batch Processing**: Processes all PDFs in the `pdf/` directory automatically
- **Robust Error Handling**: Continues processing even if individual files fail
- **Academic Paper Optimized**: Specifically tuned for conference papers and academic documents

## Dependencies

This project uses the following key dependencies:

- **PyMuPDF** - High-performance PDF text extraction library
- **Python 3.9+** - Required for PyMuPDF compatibility

## System Requirements

- **Python**: 3.9 or higher
- **PyMuPDF**: Installed automatically via uv

## Installation

### Install Python Dependencies

Using the UV package manager (recommended):

```bash
# Install UV if you haven't already
pip install uv

# Install project dependencies
uv sync
```

Alternatively, using pip:

```bash
pip install -e .
```

## Usage

### Basic Usage

1. **Place PDF files** in the `pdf/` directory
2. **Run the extraction script**:

```bash
uv run python extract_pdf_text.py
```

### Output

The script processes all PDF files in the `pdf/` directory and saves results to the `results/` directory. For each PDF file, one output file is generated:

- **`filename.txt`** - Clean text output organized by document sections

### Example Output Structure

**TXT Output** provides clean, readable text:
```
# paper.pdf

Research Paper Title

Authors: John Doe, Jane Smith

Abstract
This paper presents...

Introduction
The field of research...
```

## Configuration

The extraction is configured for LLM-optimized academic paper processing with these settings:

- **Block-based Extraction**: Uses PyMuPDF's text block structure for better organization
- **Character Filtering**: Removes non-Latin characters and symbols while preserving content
- **Text Cleaning**: Fixes hyphenation, spacing, and common PDF extraction issues
- **Document Structure**: Maintains titles, sections, and paragraph breaks

## Performance

- **Processing Speed**: Fast - PyMuPDF is significantly faster than other libraries
- **Quality**: Optimized for academic papers with clean, LLM-ready output
- **Memory Usage**: Low - efficient processing suitable for large batches
- **Error Handling**: Robust - continues processing if individual files fail

## Troubleshooting

### Common Issues

1. **Import errors with PyMuPDF**
   ```bash
   uv sync  # Reinstall dependencies
   ```

2. **Processing very large PDFs**
   - PyMuPDF handles large files efficiently
   - No special configuration needed

### Logs and Output

The script provides real-time progress updates:
```
Found 400 PDF files to process
Output will be saved to: /path/to/results
------------------------------------------------------------
Processing: paper1.pdf
✓ Completed: paper1.pdf -> paper1.txt
Processing: paper2.pdf
✓ Completed: paper2.pdf -> paper2.txt
------------------------------------------------------------
Processing complete! Results saved in /path/to/results
Successfully processed: 398 files
Failed to process: 2 files
```

## Directory Structure

```
pdf_to_text/
├── README.md
├── pyproject.toml          # UV package configuration
├── extract_pdf_text.py     # Main extraction script
├── pdf/                    # Input PDF files
│   ├── paper1.pdf
│   ├── paper2.pdf
│   └── ...
└── results/                # Output directory
    ├── paper1.txt          # Clean text output
    ├── paper2.txt          # Clean text output
    └── ...
```

## License

This project is open source and available under the MIT License.