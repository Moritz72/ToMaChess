import os
import os.path
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
    return os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir))


def get_image(name):
    return os.path.join(get_root_directory(), "images", name)


def remove_temporary_files():
    for file in ("zip_file.zip", "extracted_file"):
        path = os.path.join(get_root_directory(), file)
        if os.path.exists(path):
            os.remove(path)


def recursive_buckets(lis, functions, reverse=True):
    if len(functions) == 0:
        return lis
    dic = functions[0]([e[0] for e in lis])
    lis = sorted(lis, key=lambda e: dic[e[0]], reverse=reverse)
    temp = [(list(group), key) for key, group in groupby(lis, lambda x: dic[x[0]])]
    return [[el[0], key]+el[1:] for group, key in temp for el in recursive_buckets(group, functions[1:], reverse)]


def shorten_float(value):
    return int(value) if float(value).is_integer() else float(str(value).rstrip('0').rstrip('.'))


def remove_duplicates(list_of_hashables):
    return list({hashable: None for hashable in list_of_hashables}.keys())


def remove_uuid_duplicates(object_list):
    return list({obj.get_uuid(): obj for obj in object_list}.values())
