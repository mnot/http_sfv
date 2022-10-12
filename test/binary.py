import cProfile
import io
from pstats import Stats
import timeit

from decimal import Decimal
from http_sfv import parse_binary, parse_text, ser_binary, ser_text, Token
from harfile import read_har_file



def perf(filename):
    req_hdrs, res_hdrs = read_har_file(filename)
    t = []
    b = []
    m = []
    e = []
    for header_section in res_hdrs:
        for name, value in header_section.items():
            try:
                v = value.encode('ascii').replace(b'\x00', b', ')
                b.append(ser_binary(parse_text(v, name=name)))
                t.append((name, v))
            except KeyError:
                m.append((name, value))
            except ValueError:
                e.append((name, value))
    print(f"{len(b)} structured headers")
    print(f"{len(m)} unrecognised headers")
    print(f"{len(e)} error headers")
    return
    for name, value in t:
        obj1 = parse_text(value, name=name)
        str1 = ser_text(obj1)
        bin1 = ser_binary(obj1)
        _, obj2 = parse_binary(bin1)
        str2 = ser_text(obj2)
        assert str1 == str2, f"text for {name}: '{str1}' != binary '{str2}'"


    n = 1000
    pr = cProfile.Profile()
    pr.enable()
    text_result = timeit.timeit(lambda: [parse_text(value, name=name) for (name, value) in t], number=n)
    pr.disable()
    text_size = sum([len(v) for (n, v) in t])
    st = io.StringIO()
    ps = Stats(pr, stream=st).sort_stats("time")
    ps.print_stats(20)
    print(f"text: {text_size} bytes")
    print(f"text: {text_result:.2} seconds")
    print(f"text: {st.getvalue()}\n")

    pr = cProfile.Profile()
    pr.enable()
    bin_result = timeit.timeit(lambda: [parse_binary(value) for value in b], number=n)
    pr.disable()
    bin_size = sum([len(v) for v in b])
    st = io.StringIO()
    ps = Stats(pr, stream=st).sort_stats("time")
    ps.print_stats(20)
    print(f"binary: {bin_size} bytes")
    print(f"binary: {bin_result:.2} seconds")
    print(f"binary: {st.getvalue()}\n")
    print(f"binary {int(((text_result - bin_result) / text_result) * 100)}% faster")
    print(f"binary {int(((text_size - bin_size) / text_size) * 100)}% smaller")


if __name__ == "__main__":
    import sys
    for filename in sys.argv[1:]:
        perf(filename)

