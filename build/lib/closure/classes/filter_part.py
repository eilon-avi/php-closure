class FilterPart:
    def __init__(self, filter_steps):
        if isinstance(filter_steps, str):
            self.filter_steps = [filter_steps]
        else:
            self.filter_steps = list(filter_steps)

    def __reversed__(self):
        steps = self.filter_steps[::-1].copy()

        iconv_prefix = "convert.iconv."
        base64_prefix = "convert.base64-"

        for i in range(len(steps)):
            if steps[i].startswith(iconv_prefix):
                parts = steps[i][len(iconv_prefix):].split(".")
                x, y = parts
                steps[i] = f"{iconv_prefix}{y}.{x}"
            elif steps[i].startswith(base64_prefix):
                operation = steps[i][len(base64_prefix):]
                rev_operation = "decode" if operation == "encode" else "encode"
                steps[i] = f"{base64_prefix}{rev_operation}"

        return FilterPart(steps)

    def __truediv__(self, other):
        """
        Overloads the / operator:
        FilterPart / FilterPart -> merged FilterPart
        FilterPart / str        -> wrapped + merged
        """
        if isinstance(other, str):
            other = FilterPart([other])
        elif not isinstance(other, FilterPart):
            raise TypeError("Can only divide FilterPart by FilterPart or str")

        return FilterPart(self.filter_steps + other.filter_steps)

    def __mul__(self, other):
        if not isinstance(other, int):
            raise TypeError("Can only multiply FilterPart by int")

        return FilterPart(self.filter_steps * other)

    def __str__(self):
        return "/".join(self.filter_steps)

    def __repr__(self):
        return f"FilterPart({self.filter_steps})"
