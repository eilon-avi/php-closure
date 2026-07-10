from dataclasses import dataclass

from classes.filter_part import FilterPart
from utils.chain_functions import iconv_multi_wrap


@dataclass
class Appender:
    chain: FilterPart
    bytes: bytes
    required_padding: int

    def extend(self, iconv_encodings, new_bytes):
        return Appender(
            iconv_multi_wrap(self.chain, *iconv_encodings),
            new_bytes,
            self.required_padding,
        )