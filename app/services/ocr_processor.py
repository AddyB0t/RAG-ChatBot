"""
OCR Processing for scanned PDFs and images
Uses pytesseract with advanced image preprocessing
"""
import io
import logging
from typing import List, Optional
from PIL import Image, ImageOps, ImageFilter
import cv2
import numpy as np
import pytesseract

logger = logging.getLogger(__name__)

class OCRProcessor:
    """Advanced OCR processor with image preprocessing"""

    def __init__(self):
        """Initialize OCR processor"""
        self.tesseract_available = self._check_tesseract()

    def _check_tesseract(self) -> bool:
        """Check if Tesseract is available"""
        try:
            pytesseract.get_tesseract_version()
            return True
        except Exception as e:
            logger.warning(f"Tesseract not available: {e}")
            return False

    def preprocess_for_ocr(self, image: Image.Image) -> Image.Image:
        """
        Advanced image preprocessing for better OCR results

        Steps:
        1. Convert to OpenCV format
        2. Resize (2x upscaling)
        3. Convert to grayscale
        4. Apply denoising
        5. Apply adaptive thresholding
        """
        try:
            open_cv_image = np.array(image)

            if len(open_cv_image.shape) > 2:
                open_cv_image = cv2.cvtColor(open_cv_image, cv2.COLOR_RGB2BGR)

            open_cv_image = cv2.resize(
                open_cv_image,
                None,
                fx=2,
                fy=2,
                interpolation=cv2.INTER_LANCZOS4
            )

            if len(open_cv_image.shape) > 2:
                gray = cv2.cvtColor(open_cv_image, cv2.COLOR_BGR2GRAY)
            else:
                gray = open_cv_image

            denoised = cv2.medianBlur(gray, 3)

            binary = cv2.adaptiveThreshold(
                denoised,
                255,
                cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                cv2.THRESH_BINARY,
                11,
                2
            )

            return Image.fromarray(binary)

        except Exception as e:
            logger.error(f"Error preprocessing image: {e}")
            return image

    def extract_text_from_image(
        self,
        image: Image.Image,
        lang: str = 'eng',
        preprocess: bool = True
    ) -> str:
        """
        Extract text from image using OCR

        Args:
            image: PIL Image object
            lang: Language for OCR (default: 'eng')
            preprocess: Apply preprocessing (default: True)

        Returns:
            Extracted text
        """
        if not self.tesseract_available:
            logger.warning("Tesseract not available, cannot perform OCR")
            return ""

        try:
            if preprocess:
                processed_image = self.preprocess_for_ocr(image)
            else:
                processed_image = image

            text = pytesseract.image_to_string(
                processed_image,
                lang=lang,
                config='--psm 6'
            )

            return text.strip()

        except Exception as e:
            logger.error(f"Error extracting text from image: {e}")
            return ""

    def extract_text_from_pdf_images(
        self,
        pdf_path: str,
        lang: str = 'eng'
    ) -> List[str]:
        """
        Extract text from scanned PDF using OCR
        Converts PDF pages to images and applies OCR

        Args:
            pdf_path: Path to PDF file
            lang: Language for OCR

        Returns:
            List of extracted text per page
        """
        if not self.tesseract_available:
            logger.warning("Tesseract not available, cannot perform OCR on PDF")
            return []

        try:
            try:
                from pdf2image import convert_from_path
            except ImportError:
                logger.error("pdf2image not installed. Install with: pip install pdf2image")
                return []

            images = convert_from_path(pdf_path, dpi=300)

            texts = []
            for i, image in enumerate(images):
                logger.info(f"Processing page {i + 1}/{len(images)} with OCR")
                text = self.extract_text_from_image(image, lang=lang)
                texts.append(text)

            return texts

        except Exception as e:
            logger.error(f"Error extracting text from PDF with OCR: {e}")
            return []

    def is_scanned_pdf(self, pdf_path: str) -> bool:
        """
        Detect if PDF is scanned (image-based) or text-based

        Args:
            pdf_path: Path to PDF file

        Returns:
            True if scanned (needs OCR), False if text-based
        """
        try:
            import PyPDF2

            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)

                pages_to_check = min(3, len(pdf_reader.pages))

                for i in range(pages_to_check):
                    page = pdf_reader.pages[i]
                    text = page.extract_text()

                    if text and len(text.strip()) > 50:
                        return False

                return True

        except Exception as e:
            logger.error(f"Error checking if PDF is scanned: {e}")
            return False

_ocr_processor_instance = None

def get_ocr_processor() -> OCRProcessor:
    """Get or create OCR processor instance (singleton)"""
    global _ocr_processor_instance
    if _ocr_processor_instance is None:
        _ocr_processor_instance = OCRProcessor()
    return _ocr_processor_instance

