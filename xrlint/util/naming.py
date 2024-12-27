def to_kebab_case(name: str) -> str:
    return _to_lc_case(name, "-")


def to_snake_case(name: str) -> str:
    return _to_lc_case(name, "_")


# noinspection SpellCheckingInspection
def _to_lc_case(name: str, sep: str) -> str:
    lc_case = []
    pl = False  # (p)revious character is (l)owercase
    pu = False  # (p)revious character is (u)ppercase
    ppu = False  # (p)pre-(p)revious character is (u)ppercase
    for cc in name:
        cl = cc.islower()  # (c)urrent character is (l)owercase
        cu = cc.isupper()  # (c)urrent character is (u)ppercase
        if not cc.isalnum():
            _append_sep(lc_case, sep)
        else:
            if pl and not cl:
                _append_sep(lc_case, sep)
            elif ppu and pu and cl:
                _insert_sep(lc_case, sep)
            lc_case.append(cc.lower() if not cl else cc)
        ppu = pu
        pu = cu
        pl = cl
    return "".join(lc_case)


def _append_sep(sc_name, sep):
    n = len(sc_name)
    if n > 0 and sc_name[-1] != sep:
        sc_name.append(sep)


def _insert_sep(sc_name, sep):
    n = len(sc_name)
    if n > 1 and sc_name[-2] != sep:
        sc_name.append(sc_name[-1])
        sc_name[-2] = sep
