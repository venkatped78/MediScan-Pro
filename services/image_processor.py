# ============================================================
# services/image_processor.py — Medical Image Processor
# Handles: JPEG, PNG, DICOM, PDF image extraction
# Preprocessing: resize, enhance, normalize for AI analysis
# ============================================================

import base64
import io
import os
from pathlib import Path
from typing import Tuple, Optional
import numpy as np


class ImageProcessor:
    """
    Processes medical images for AI analysis.
    Supports: JPG, PNG, TIFF, BMP, DICOM (.dcm), PDF
    """

    MAX_SIZE = (1024, 1024)
    QUALITY  = 90

    def load_and_encode(self, image_path: str) -> Tuple[str, str, dict]:
        """
        Load image, preprocess, and encode to base64.

        Returns:
            (base64_string, media_type, metadata)
        """
        path = Path(image_path)
        if not path.exists():
            raise FileNotFoundError(f"Image not found: {image_path}")

        suffix = path.suffix.lower().lstrip(".")

        if suffix == "dcm":
            return self._process_dicom(image_path)
        elif suffix == "pdf":
            return self._process_pdf(image_path)
        else:
            return self._process_standard(image_path)

    def _process_standard(self, path: str) -> Tuple[str, str, dict]:
        """Process standard image formats (JPG, PNG, etc.)"""
        from PIL import Image, ImageEnhance

        img = Image.open(path)
        metadata = {
            "original_size":   img.size,
            "original_mode":   img.mode,
            "format":          img.format,
            "file_size_kb":    os.path.getsize(path) // 1024,
        }

        # Convert to RGB if needed
        if img.mode in ("RGBA", "LA", "P"):
            img = img.convert("RGB")
        elif img.mode == "L":
            img = img.convert("RGB")

        # Resize if too large (preserve aspect ratio)
        img.thumbnail(self.MAX_SIZE, Image.Resampling.LANCZOS)

        # Enhance for medical clarity
        img = self._enhance_medical_image(img)

        # Encode to base64
        buffer = io.BytesIO()
        img.save(buffer, format="JPEG", quality=self.QUALITY)
        b64 = base64.standard_b64encode(buffer.getvalue()).decode("utf-8")

        metadata["processed_size"] = img.size
        return b64, "image/jpeg", metadata

    def _enhance_medical_image(self, img):
        """Apply medical image enhancements."""
        from PIL import ImageEnhance, ImageFilter

        # Slightly increase contrast for better visibility
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(1.2)

        # Slight sharpness increase
        enhancer = ImageEnhance.Sharpness(img)
        img = enhancer.enhance(1.1)

        return img

    def _process_dicom(self, path: str) -> Tuple[str, str, dict]:
        """Process DICOM medical imaging files."""
        try:
            import pydicom
            from PIL import Image

            ds = pydicom.dcmread(path)
            metadata = {
                "patient_name":   str(getattr(ds, "PatientName", "Unknown")),
                "patient_id":     str(getattr(ds, "PatientID", "")),
                "study_date":     str(getattr(ds, "StudyDate", "")),
                "modality":       str(getattr(ds, "Modality", "")),
                "body_part":      str(getattr(ds, "BodyPartExamined", "")),
                "institution":    str(getattr(ds, "InstitutionName", "")),
                "study_desc":     str(getattr(ds, "StudyDescription", "")),
                "series_desc":    str(getattr(ds, "SeriesDescription", "")),
                "format":         "DICOM",
                "file_size_kb":   os.path.getsize(path) // 1024,
            }

            # Extract pixel data
            pixel_array = ds.pixel_array

            # Normalize to 8-bit
            if pixel_array.dtype != np.uint8:
                pixel_min = pixel_array.min()
                pixel_max = pixel_array.max()
                if pixel_max > pixel_min:
                    pixel_array = ((pixel_array - pixel_min) /
                                   (pixel_max - pixel_min) * 255).astype(np.uint8)
                else:
                    pixel_array = np.zeros_like(pixel_array, dtype=np.uint8)

            # Handle different array shapes
            if len(pixel_array.shape) == 2:
                img = Image.fromarray(pixel_array, mode="L").convert("RGB")
            elif len(pixel_array.shape) == 3:
                if pixel_array.shape[2] == 3:
                    img = Image.fromarray(pixel_array, mode="RGB")
                else:
                    img = Image.fromarray(pixel_array[:,:,0], mode="L").convert("RGB")
            else:
                img = Image.fromarray(pixel_array[0], mode="L").convert("RGB")

            img.thumbnail(self.MAX_SIZE, Image.Resampling.LANCZOS)
            img = self._enhance_medical_image(img)

            buffer = io.BytesIO()
            img.save(buffer, format="JPEG", quality=self.QUALITY)
            b64 = base64.standard_b64encode(buffer.getvalue()).decode("utf-8")

            metadata["processed_size"] = img.size
            return b64, "image/jpeg", metadata

        except ImportError:
            raise ImportError("pydicom not installed. Run: pip install pydicom")
        except Exception as e:
            raise ValueError(f"DICOM processing failed: {e}")

    def _process_pdf(self, path: str) -> Tuple[str, str, dict]:
        """Extract first page image from PDF."""
        try:
            import fitz  # PyMuPDF
            doc = fitz.open(path)
            page = doc[0]
            mat  = fitz.Matrix(2, 2)  # 2x zoom for better quality
            pix  = page.get_pixmap(matrix=mat)

            from PIL import Image
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            img.thumbnail(self.MAX_SIZE, Image.Resampling.LANCZOS)

            buffer = io.BytesIO()
            img.save(buffer, format="JPEG", quality=self.QUALITY)
            b64 = base64.standard_b64encode(buffer.getvalue()).decode("utf-8")

            return b64, "image/jpeg", {
                "format": "PDF",
                "pages":  len(doc),
                "file_size_kb": os.path.getsize(path) // 1024,
                "processed_size": img.size,
            }
        except ImportError:
            # Fallback to pdf2image
            try:
                from pdf2image import convert_from_path
                images = convert_from_path(path, first_page=1, last_page=1)
                img = images[0]
                img.thumbnail(self.MAX_SIZE, Image.Resampling.LANCZOS)
                buffer = io.BytesIO()
                img.save(buffer, format="JPEG", quality=self.QUALITY)
                b64 = base64.standard_b64encode(buffer.getvalue()).decode("utf-8")
                return b64, "image/jpeg", {"format": "PDF",
                                           "file_size_kb": os.path.getsize(path) // 1024}
            except Exception as e:
                raise ValueError(f"PDF processing failed: {e}")

    def create_thumbnail(self, image_path: str, size: Tuple[int,int] = (200, 200)) -> str:
        """Create a small thumbnail for reports."""
        from PIL import Image
        img = Image.open(image_path).convert("RGB")
        img.thumbnail(size, Image.Resampling.LANCZOS)
        buffer = io.BytesIO()
        img.save(buffer, format="JPEG", quality=70)
        return base64.standard_b64encode(buffer.getvalue()).decode("utf-8")

    def get_image_stats(self, image_path: str) -> dict:
        """Get basic image statistics for quality assessment."""
        try:
            from PIL import Image
            import numpy as np
            img = Image.open(image_path).convert("L")
            arr = np.array(img)
            return {
                "mean_brightness": float(arr.mean()),
                "std_contrast":    float(arr.std()),
                "min_pixel":       int(arr.min()),
                "max_pixel":       int(arr.max()),
                "size":            img.size,
            }
        except Exception:
            return {}
