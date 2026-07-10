from ..classes.filter_part import FilterPart

B64E = FilterPart("convert.base64-encode")
B64D = FilterPart("convert.base64-decode")
REMOVE_EQUAL = FilterPart("convert.iconv.855.UTF7")
QPE = FilterPart("convert.quoted-printable-encode")
QPD = FilterPart("convert.quoted-printable-decode")
ROT13 = FilterPart("string.rot13")

MULT_3 = FilterPart(["convert.iconv.UTF-16LE.UTF8"])
ANTI_MULT_3 = FilterPart(["convert.iconv.UTF8.UTF-16LE"])
INFLATE_2 = "convert.iconv.UCS-2.UTF16"