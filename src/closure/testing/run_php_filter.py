import subprocess

from ..classes.filter_part import FilterPart


class PHPFilterError(RuntimeError):
    pass


def run_php_filter(chain: str) -> bytes:
    if isinstance(chain, FilterPart):
        chain = str(chain)

    php_code = f'<?php echo file_get_contents("{chain}");'

    result = subprocess.run(
        ["php"],
        input=php_code.encode("utf-8"),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    if result.returncode != 0:
        raise PHPFilterError(
            result.stderr.decode("utf-8", errors="replace").strip()
        )

    stderr_text = result.stderr.decode("utf-8", errors="replace").strip()

    if stderr_text:
        raise PHPFilterError(stderr_text)

    return result.stdout