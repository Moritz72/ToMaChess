from os import pardir, remove
from os.path import dirname, abspath, join, exists
from codecs import open
from itertools import groupby


def read_file(path):
    f = open(path, 'r', "utf-8")
    res = f.read()
    f.close()
    return res


def write_file(path, content):
    f = open(path, 'w', "utf-8")
    f.write(content)
    f.close()


def get_root_directory():
    return abspath(join(dirname(abspath(__file__)), pardir))


def get_image(name):
    return f"{get_root_directory()}/images/{name}"


def remove_temporary_files():
    for file in ("zip_file.zip", "extracted_file"):
        if exists(f"{get_root_directory()}/{file}"):
            remove(f"{get_root_directory()}/{file}")


def recursive_buckets(lis, functions, reverse=True):
    if len(functions) == 0:
        return lis
    dic = functions[0]([e[0] for e in lis])
    lis = sorted(lis, key=lambda e: dic[e[0]], reverse=reverse)
    temp = [(list(group), key) for key, group in groupby(lis, lambda x: dic[x[0]])]
    return [
        [element[0], key]+element[1:] for group, key in temp
        for element in recursive_buckets(group, functions[1:], reverse)
    ]


def shorten_float(value):
    return int(value) if float(value).is_integer() else float(str(value).rstrip('0').rstrip('.'))
