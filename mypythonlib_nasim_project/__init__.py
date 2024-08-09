from .remove_pnum_hilight_title import process_directory
from .split_chapters import process_directory as split_chapters
from .clean_text import process_directory as clean_text
from .fix_lines import process_directory as fix_lines
from .replace_numbers import process_directory as replace_numbers

__all__ = [
   process_directory,
   split_chapters,
   clean_text,
   fix_lines,
   replace_numbers   
]