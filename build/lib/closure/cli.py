import argparse

from .classes.chain_builder import ChainBuilder
from .testing.run_php_filter import run_php_filter
from .utils.string_functions import right_pad, prepare_injection_data, left_pad


def generate_wrap_chain(file, prefix=None, suffix=None, pad_char=" "):
    if prefix is None and suffix is None:
        raise ValueError("Either 'prefix', 'suffix' or both must be specified.")

    cb = ChainBuilder()

    if suffix is not None:
        suffix = left_pad(suffix, 4, pad_char)
        append_seq = prepare_injection_data(suffix)
        cb.append_seq(append_seq)

    if prefix is not None:
        prefix = right_pad(prefix, 4, pad_char)
        prepend_seq = prepare_injection_data(prefix)
        cb.prepend_seq(prepend_seq)

    cb.finalize()

    return cb.construct_chain(file)


def test_chain(chain: str):
    print("\nResulting chain size:", len(chain))
    result = run_php_filter(chain)
    print("---- RESULT ----")
    print(result.decode())
    print("---- END ----")


def output_result(chain: str, output_path: str):
    if output_path is not None:
        with open(output_path, "w") as f:
            f.write(chain)
        print("Chain written to:", output_path)
    else:
        print(chain)
    print("\nResulting chain size:", len(chain))


def main():
    parser = argparse.ArgumentParser(description="Closure - generate php filter chains to wrap file contents")

    parser.add_argument("file", help="File to wrap")

    parser.add_argument(
        "-p",
        "--prefix",
        default=None,
        help="Prefix to be prepended to the file contents",
    )

    parser.add_argument(
        "-s",
        "--suffix",
        default=None,
        help="Suffix to be appended to the file contents",
    )

    parser.add_argument(
        "-c",
        "--pad-char",
        default=" ",
        help="A character that will be used for padding after the prefix or before the suffix",
    )

    parser.add_argument(
        "-o",
        "--output",
        default=None,
        help="File path to write the chain to, if none specified, chain is written to stdout",
    )

    parser.add_argument(
        "-t", "--test",
        action="store_true",
        help="Run the php filter chain in the local system to see the results (requires php to be installed)",
    )

    args = parser.parse_args()

    chain = generate_wrap_chain(args.file, args.prefix, args.suffix, args.pad_char)

    if args.test:
        test_chain(chain)
    else:
        output_result(chain, args.output)


if __name__ == "__main__":
    main()
