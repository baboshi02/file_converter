🚀 Awesome Bot Converter

A powerful, in-memory, and robust conversion tool built for Telegram, designed to handle common document and image format transformations without cluttering the filesystem.

🌟 Features
  - PDF ➡️ DOCX: Convert PDF documents into editable Word (.docx) files.

  - Word ➡️ PDF: Convert Word documents (.docx) into universally viewable PDFs.

  - Image ➡️ PDF: Transform image files (JPG, PNG, etc.) into a single PDF document.

  - In-Memory Processing: Utilizes io.BytesIO and secure temporary files (tempfile) for all conversions, ensuring data privacy and no disk clutter.

🛠️ Technology Stack

  - Language: Python 3.11+

  - Bot Framework: aiogram (v3+)

  - PDF Conversion: pdf2docx

  - Image Conversion: Pillow (PIL)

⚙️ Setup and Installation
    Prerequisites

      - Python 3.11+

      - Telegram Bot Token (Get one from @BotFather)

      - LibreOffice
Local Development Setup

  Clone the repository and install dependencies.
  ``` bash
# 1. Clone the repository
git clone https://github.com/baboshi02/file_converter/
cd awesome-bot-converter

# 2. Create and activate a virtual environment
python -m venv venv
source venv/bin/activate

# 3. Install Python requirements
pip install -r requirements.txt
# 3. Run
python main.py
# or
python3 main.py
  ```
🖥️ Usage

Start the Bot

Send the /start command to the bot on Telegram.
