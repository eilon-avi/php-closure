from ..constants.operations import ROT13, B64D, B64E
from ..classes.filter_part import FilterPart


def rot13_wrap(chain: FilterPart):
    return ROT13 / chain / ROT13


def b64_wrap(chain: FilterPart):
    return B64E / chain / B64D


def iconv_multi_wrap(chain, *enc_pairs):
    out_chain = FilterPart([])
    for enc_pair in reversed(enc_pairs):
        src_enc, dst_enc = enc_pair
        out_chain = out_chain / f"convert.iconv.{dst_enc}.{src_enc}"

    out_chain = out_chain / chain

    for enc_pair in enc_pairs:
        src_enc, dst_enc = enc_pair
        out_chain = out_chain / f"convert.iconv.{src_enc}.{dst_enc}"

    return out_chain
