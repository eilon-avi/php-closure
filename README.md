# php-closure

**php-closure** (the `closure` command) is a CLI tool, written in Python, that generates [PHP filter chains](https://www.php.net/manual/en/filters.php) for wrapping any file with an arbitrary prefix and suffix. A chain is a long `php://filter/...` string. When PHP reads it, the result is the file's contents with your prefix and suffix around them.

It is meant for CTF challenges and for testing PHP local file inclusion (LFI) bugs on systems you are authorized to test.

# Installation

Install **closure** directly from GitHub using `pip`:

```bash
pip install git+https://github.com/eilon-avi/php-closure.git
```

Alternatively, clone the repository and install it locally:

```bash
pip install php-closure
```

Requires Python 3.8 or newer. PHP is optional and is only needed for `--test`.

# Usage

After installation, the CLI is available from your terminal:

```bash
closure --help
```

![Output of closure --help](https://github.com/user-attachments/assets/e96a193f-4bda-43bb-8e94-afccd2e81bd6)

Use the available options to create your php filter chain:

![Example run with a JSON prefix and suffix, writing the chain to chain.txt](https://github.com/user-attachments/assets/60924d67-5ea4-454b-8b75-5e8c93f10424)

## Example

Wrap `data.txt` in a PHP opening tag and closing tag, and write the chain to `chain.txt`:

```bash
closure -p "<?php " -s "?>" -o chain.txt data.txt
```

Output:

```
Chain written to: chain.txt

Resulting chain size: 13004
```

Chains are long, so write them to a file with `-o`. Without `-o`, closure prints the chain to stdout. Add `-t` to run the chain with your local PHP install and print the result (requires PHP to be installed).

# Documentation & Research

All of the technical details about how this tool works are summarized in [this](https://eilon-avi.github.io/projects/closure/) blog post.
