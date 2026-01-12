from typing import List, Dict
from transformers import LayoutLMv3Processor, LayoutLMv3ForTokenClassification
import torch

class LayoutExtractor:
    def __init__(self, model_path: str):
        self.processor = LayoutLMv3Processor.from_pretrained(model_path)
        self.model = LayoutLMv3ForTokenClassification.from_pretrained(model_path)
        self.model.eval()

    def extract(self, image, ocr_tokens) -> Dict[str, str]:
        ...
