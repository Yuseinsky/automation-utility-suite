# core/__init__.py
# Legacy Archive Digitization Pipeline - Core Modules
"""
This package contains the three core processing modules:
  - ImageMapper:   Maps raw images to page numbers and renames them.
  - LayoutSorter:  Sorts page blocks by physical book order.
  - TextCleaner:   Applies regex-based cleaning rules to remove noise.
"""

from .image_mapper import ImageMapper
from .layout_sorter import LayoutSorter
from .text_cleaner import TextCleaner

__all__ = ["ImageMapper", "LayoutSorter", "TextCleaner"]
