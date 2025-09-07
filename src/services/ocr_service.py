import re
from typing import List, Dict, Optional


class OCRService:
    # Pre-compile regex patterns for better performance
    ITEMS_PATTERN = re.compile(r"^\s*(.+?)\s+([0-9][0-9,\s]*)\s*원\s*$")
    DATE_PATTERN = re.compile(r"일시:\s*([0-9]{4}-[0-9]{2}-[0-9]{2}\s+[0-9]{2}:[0-9]{2}:[0-9]{2})")

    def extract_text(self, image_path: str) -> str:
        """Extract text from a receipt image using Google Cloud Vision.

        Returns a non-empty string when OCR succeeds, or an empty string on
        failure. This function is written to be easy to mock in tests.
        """
        try:
            from google.cloud import vision
            from google.api_core import exceptions

            client = vision.ImageAnnotatorClient()
            with open(image_path, "rb") as f:
                content = f.read()

            image = vision.Image(content=content)
            response = client.text_detection(image=image)
            annotations = getattr(response, "text_annotations", [])
            if annotations:
                return annotations[0].description or ""
            return ""
        except (FileNotFoundError, exceptions.GoogleAPICallError):
            # Be forgiving in the absence of credentials or on errors.
            return ""

    def parse_store_name(self, ocr_text: str) -> Optional[str]:
        lines = ocr_text.strip().split("\n")
        for raw in lines:
            line = raw.strip()
            if not line:
                continue
            lowered = line.lower()
            if (
                "tel" in lowered
                or "총계" in line
                or "원" in line
                or lowered.startswith("일시:")
                or line[0:1].isdigit()
            ):
                continue
            # Heuristic: prefer the first non-empty, non-metadata line
            return line
        return None

    def parse_items_and_prices(self, ocr_text: str) -> List[Dict[str, int]]:
        items: List[Dict[str, int]] = []
        lines = ocr_text.strip().split("\n")

        for raw in lines:
            line = raw.strip()
            if not line or "총계" in line or line.upper().startswith("TEL"):
                continue
            if "원" not in line:
                continue

            match = self.ITEMS_PATTERN.match(line)
            if match:
                name = match.group(1).strip()
                # Remove commas and spaces inside the number
                price_str = re.sub(r"[\s,]", "", match.group(2))
                try:
                    price = int(price_str)
                except ValueError:
                    continue
                items.append({"name": name, "price": price})

        return items

    def parse_date(self, ocr_text: str) -> Optional[str]:
        lines = ocr_text.strip().split("\n")

        for raw in lines:
            line = raw.strip()
            if "일시:" in line:
                date_match = self.DATE_PATTERN.search(line)
                if date_match:
                    return date_match.group(1).strip()

        return None
