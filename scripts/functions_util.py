from os import pardir
from os.path import dirname, abspath, join
from codecs import open
from itertools import groupby


def read_file(directory):
    r = open(directory, 'r', 'utf-8')
    f = r.read()
    r.close()
    return f


def write_file(directory, content):
    w = open(directory, 'w', "utf-8")
    w.write(content)
    w.close()


def get_root_directory():
    return abspath(join(dirname(abspath(__file__)), pardir))


def get_directory_by_uuid(directory, uuid):
    return f"{get_root_directory()}/{directory}/{uuid}"


def recursive_buckets(lis, functions, reverse=True):
    if len(functions) == 0:
        return lis
    dic = functions[0]([e[0] for e in lis])
    lis = sorted(lis, key=lambda e: dic[e[0]], reverse=reverse)
    temp = [(list(group), key) for key, group in groupby(lis, lambda x: dic[x[0]])]
    return [[element[0], key]+element[1:] for group, key in temp
            for element in recursive_buckets(group, functions[1:], reverse)]


def shorten_float(value):
    return int(value) if float(value).is_integer() else float(str(value).rstrip('0').rstrip('.'))
