import subprocess
import os
import tempfile
import aiohttp
from aiogram.types import Message, BufferedInputFile

# NOTE: The LibreOffice executable name is 'libreoffice' or 'soffice' on Linux
# We'll use a function to find the right one or default to 'libreoffice'
def libreoffice_exec():
    return 'libreoffice' # Standard name in many Linux distros
def convert_docx_to_pdf_linux(docx_path: str, output_dir: str) -> str:
    """
    Uses LibreOffice in headless mode via subprocess to convert DOCX to PDF.
    Returns the path to the newly created PDF file.
    """
    # The command: <exec> --headless --convert-to pdf --outdir <output_dir> <input_file>
    args = [
        libreoffice_exec(),
        '--headless',
        '--convert-to',
        'pdf',
        '--outdir',
        output_dir,
        docx_path
    ]
    
    # Run the command and wait for it to complete
    # The 'check=True' will raise an error if the command fails
    result = subprocess.run(args, check=True, capture_output=True, timeout=30)
    
    # LibreOffice creates the file with the same base name in the outdir
    base_name = os.path.splitext(os.path.basename(docx_path))[0]
    pdf_path = os.path.join(output_dir, f"{base_name}.pdf")
    
    if not os.path.exists(pdf_path):
        # Fallback error handling if the file wasn't created
        raise FileNotFoundError(
            f"LibreOffice conversion failed. Stderr: {result.stderr.decode()}"
        )
        
    return pdf_path
