import os
import fitz
from paddleocr import PaddleOCR

ocr = PaddleOCR(lang='en')


class PDFController:
    def __init__(self, pdf_file=None):
        self.pdf_file = pdf_file
        self.text_result = []

    def get_pdf_text(self):
        temp_dir = "temp_files"
        file_path = os.path.join(temp_dir, self.pdf_file.name)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        with open(file_path, "wb+") as f:
            for chunk in self.pdf_file.chunks():
                f.write(chunk)
        
        # OCR Process
        transform_pdf = fitz.open(file_path)
        for page_number, page in enumerate(transform_pdf):
            pix = page.get_pixmap()
            img_path = os.path.join(temp_dir, f"{self.pdf_file.name}_page_{page_number}.png")
            pix.save(img_path)
            try:
                result = ocr.predict(img_path)
                for page_result in result:
                    rec_texts = page_result.get('rec_texts', [])
                    self.text_result.extend(rec_texts)
            except Exception as e:
                self.text_result.append(f"Error processing page {page_number}: {e}")
        return self.text_result