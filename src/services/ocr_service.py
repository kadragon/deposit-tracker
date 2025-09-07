import re


class OCRService:
    def extract_text(self, image_path):
        return "Sample extracted text"
    
    def parse_store_name(self, ocr_text):
        lines = ocr_text.strip().split('\n')
        for line in lines:
            line = line.strip()
            if line and not line.startswith('서울') and not line.startswith('TEL:') and '원' not in line and '총계' not in line:
                return line
        return None
    
    def parse_items_and_prices(self, ocr_text):
        items = []
        lines = ocr_text.strip().split('\n')
        
        for line in lines:
            line = line.strip()
            # 상품명과 가격이 포함된 라인을 찾음 (총계 제외)
            if '원' in line and '총계' not in line and not line.startswith('TEL:'):
                # 정규식을 사용해 상품명과 가격을 추출
                match = re.match(r'(.+?)\s+([0-9,]+)원', line)
                if match:
                    name = match.group(1).strip()
                    price_str = match.group(2).replace(',', '')
                    price = int(price_str)
                    items.append({"name": name, "price": price})
        
        return items
    
    def parse_date(self, ocr_text):
        lines = ocr_text.strip().split('\n')
        
        for line in lines:
            line = line.strip()
            # 날짜가 포함된 라인을 찾음
            if '일시:' in line:
                # "일시: YYYY-MM-DD HH:MM:SS" 형태에서 날짜 부분을 추출
                date_match = re.search(r'일시:\s*(.+)', line)
                if date_match:
                    return date_match.group(1).strip()
        
        return None