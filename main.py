#!env/bin/python
from PIL import Image 
from io import BytesIO
import dotenv
import asyncio
import os
import tempfile
import aiohttp
import subprocess
from pdf2docx import Converter


from aiogram import Dispatcher, Bot, Router, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.types import (
        BufferedInputFile,
        CallbackQuery,
        InlineKeyboardButton,
        InlineKeyboardMarkup,
        Message,
        )
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

def libreoffice_exec():
    return 'libreoffice' 
def convert_docx_to_pdf_linux(docx_path: str, output_dir: str) -> str:
    """
    Uses LibreOffice in headless mode via subprocess to convert DOCX to PDF.
    Returns the path to the newly created PDF file.
    """
    
    args = [
        libreoffice_exec(),
        '--headless',
        '--convert-to',
        'pdf',
        '--outdir',
        output_dir,
        docx_path
    ]
    
    
    
    result = subprocess.run(args, check=True, capture_output=True, timeout=30)
    
    
    base_name = os.path.splitext(os.path.basename(docx_path))[0]
    pdf_path = os.path.join(output_dir, f"{base_name}.pdf")
    
    if not os.path.exists(pdf_path):
        
        raise FileNotFoundError(
            f"LibreOffice conversion failed. Stderr: {result.stderr.decode()}"
        )
        
    return pdf_path

form_router = Router()
dotenv.load_dotenv()


class Form(StatesGroup):
    pdf_to_word = State()
    word_to_pdf=State()
    image_to_pdf=State()


@form_router.message(CommandStart())
async def start_handler(message: Message) -> None:
    await message.answer(f"Hello, {message.from_user.first_name}")


@form_router.message(Command("convert"))
async def help_handler(message: Message) -> None:
    await message.answer(
            "Choose the type of conversion you want",
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(text="PDF to Word", callback_data="pdfToWord"),
                        InlineKeyboardButton(text="Word to PDF", callback_data="wordToPdf"),
                        ],
                    [

                        InlineKeyboardButton(text="Image to PDF", callback_data="imageToPdf"),
                        ]


                    ]
                ),
            )


@form_router.callback_query(F.data == "imageToPdf")
async def image_to_pdf(query: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(Form.image_to_pdf)
    await query.answer("You have chosen image to pdf")
    await query.message.bot.send_message(
            text="You have chosen image to pdf", chat_id=query.from_user.id
            )
    await query.message.bot.send_message(
            text="Send image file you want to convert to pdf",
            chat_id=query.from_user.id,
            )
@form_router.callback_query(F.data == "wordToPdf")
async def word_to_pdf(query: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(Form.word_to_pdf)
    await query.answer("You have chosen word to pdf")
    await query.message.bot.send_message(
            text="You have chosen word to pdf", chat_id=query.from_user.id
            )
    await query.message.bot.send_message(
            text="Send the word file that you want to convert to pdf",
            chat_id=query.from_user.id,
            )
@form_router.callback_query(F.data == "pdfToWord")
async def pdf_to_word(query: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(Form.pdf_to_word)
    await query.answer("You have chosen pdf to word")
    await query.message.bot.send_message(
            text="You have chosen pdf to word", chat_id=query.from_user.id
            )
    await query.message.bot.send_message(
            text="Send the pdf file that you want to convert to word",
            chat_id=query.from_user.id,
            )


@form_router.message(Form.word_to_pdf)



async def convert_word_to_pdf_final(message: Message, state: FSMContext) -> None:
    document = message.document
    await message.answer("✅ Word DOCX received. Starting conversion to PDF...")
    
    file = await message.bot.get_file(document.file_id)
    download_url = f"https://api.telegram.org/file/bot{message.bot.token}/{file.file_path}"
    
    pdf_content = None
    docx_filepath = None
    pdf_filepath = None

    try:
        
        with tempfile.NamedTemporaryFile(suffix=".docx", delete=False) as tmp_docx:
            docx_filepath = tmp_docx.name
            async with aiohttp.ClientSession() as session:
                async with session.get(download_url) as resp:
                    if resp.status == 200:
                        tmp_docx.write(await resp.read())
                    else:
                        await message.answer(f"❌ Failed to download file. Status: {resp.status}")
                        return

        
        await message.answer("Processing conversion with LibreOffice...")
        
        
        output_dir = os.path.dirname(docx_filepath)
        pdf_filepath = convert_docx_to_pdf_linux(docx_filepath, output_dir)

        
        with open(pdf_filepath, 'rb') as f:
            pdf_content = f.read()

        
        base_name = os.path.splitext(document.file_name)[0]
        new_filename = f"{base_name}.pdf"

        await message.bot.send_document(
            chat_id=message.from_user.id,
            document=BufferedInputFile(pdf_content, new_filename),
            caption="🎉 Your Word file has been converted to PDF!"
        )

    except subprocess.CalledProcessError as e:
        await message.answer("❌ Conversion failed. LibreOffice command failed to execute. Check your Dockerfile/installation.")
        print(f"Subprocess Error: {e.stderr.decode()}")
    except Exception as e:
        await message.answer(f"❌ An unexpected error occurred: {e}")
        print(f"General Error: {e}")
        
    finally:
        
        if docx_filepath and os.path.exists(docx_filepath):
            os.unlink(docx_filepath)
        if pdf_filepath and os.path.exists(pdf_filepath):
            os.unlink(pdf_filepath)
            
    await state.clear()

@form_router.message(Form.image_to_pdf)
async def convert_image_to_pdf(message: Message,state:FSMContext) -> None:
    document = message.document or message.photo[-1] 
    await message.answer("✅ Image received. Starting conversion to PDF...")
    file = await message.bot.get_file(document.file_id)
    download_url = f"https://api.telegram.org/file/bot{message.bot.token}/{file.file_path}"
    pdf_content = None 
    try:
        image_buffer = BytesIO()
        async with aiohttp.ClientSession() as session:
            async with session.get(download_url) as resp:
                if resp.status == 200:
                    image_buffer.write(await resp.read())
                    image_buffer.seek(0)
                else:
                    await message.answer(f"❌ Failed to download file. Status: {resp.status}")
                    return

        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp_pdf:
            pdf_filepath = tmp_pdf.name
            img = Image.open(image_buffer)
            img.save(pdf_filepath, "PDF", resolution=100.0)
        with open(pdf_filepath, 'rb') as f:
            pdf_content = f.read()
        os.unlink(pdf_filepath) 
        base_name = getattr(document, 'file_name', 'image') 
        base_name = os.path.splitext(base_name)[0]
        new_filename = f"{base_name}.pdf"
        await message.bot.send_document(
                chat_id=message.from_user.id,
                document=BufferedInputFile(pdf_content, new_filename),
                caption="🎉 Your image has been converted to PDF!"
                )
        await state.clear()
    except Exception as e:
        
        if 'pdf_filepath' in locals() and os.path.exists(pdf_filepath):
            os.unlink(pdf_filepath)
        await message.answer(f"❌ An error occurred: {e}")

@form_router.message(Form.pdf_to_word)
@form_router.message(F.document.file_name.endswith(".pdf"))
async def convert_pdf_to_word_robust(message: Message, state: FSMContext) -> None:
    document = message.document
    await message.answer("✅ PDF received. Starting conversion...")
    file = await message.bot.get_file(document.file_id)
    pdf_file_path_tg: str = file.file_path
    download_url = (
            f"https://api.telegram.org/file/bot{message.bot.token}/{pdf_file_path_tg}"
            )
    try:
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp_pdf:
            pdf_filepath = tmp_pdf.name
            async with aiohttp.ClientSession() as session:
                async with session.get(download_url) as resp:
                    if resp.status == 200:
                        tmp_pdf.write(await resp.read())
                    else:
                        await message.answer(
                                f"❌ Failed to download file. Status: {resp.status}"
                                )
                        return

        with tempfile.NamedTemporaryFile(suffix=".docx", delete=False) as tmp_docx:
            docx_filepath = tmp_docx.name
            await message.answer("Processing conversion...")
            cv = Converter(pdf_filepath)
            cv.convert(docx_filepath)
            cv.close()
        with open(docx_filepath, "rb") as f:
            docx_content = f.read()
        os.unlink(pdf_filepath)
        os.unlink(docx_filepath)
        base_name = os.path.splitext(document.file_name)[0]
        new_filename = f"{base_name}.docx"
        await message.bot.send_document(
                chat_id=message.from_user.id,
                document=BufferedInputFile(docx_content, new_filename),
                caption="🎉 Your PDF has been converted to DOCX!",
                )
        await state.clear()

    except Exception as e:
        if "pdf_filepath" in locals() and os.path.exists(pdf_filepath):
            os.unlink(pdf_filepath)
        if "docx_filepath" in locals() and os.path.exists(docx_filepath):
            os.unlink(docx_filepath)

        print(f"Conversion Error: {e}")
        await message.answer(
                "❌ An unexpected error occurred during conversion or file handling."
                )

    await state.clear()


@form_router.message()
async def fallback(message: Message) -> None:
    await message.answer("Please enter valid command")


async def main() -> None:
    bot_api_key = os.getenv("BOT_API")
    if not bot_api_key:
        raise BaseException("Provid valid api key as env BOT_API:'1234'")
    bot = Bot(
            token=bot_api_key, default=DefaultBotProperties(parse_mode=ParseMode.HTML)
            )
    print("Polling...")
    dp = Dispatcher()
    dp.include_router(form_router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())





