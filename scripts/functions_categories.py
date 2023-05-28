from math import inf

integer_categories = ("Rating", "Birth")
type_to_categories = {"player": ("Rating", "Birth", "Sex"), "team": tuple()}
category_to_method_string = {"Rating": "get_rating", "Birth": "get_birthday", "Sex": "get_sex"}


def get_category_range_string(category, bottom, top):
    if bottom == top:
        return f"{category} {bottom}"
    if bottom in (-inf, ""):
        return f"{category} ≤ {top}"
    if top in (inf, ""):
        return f"{category} ≥ {bottom}"
    return f"{category} {bottom} - {top}"


def object_in_category_range(obj, category, bottom, top):
    method_string = category_to_method_string[category]
    if hasattr(obj, method_string):
        method = getattr(obj, method_string)
        if callable(method):
            value = method() or (0 if category in integer_categories else "")
            return bottom <= value <= top
    return False


def filter_list_by_category_range(obj_list, category, bottom, top):
    return [obj for obj in obj_list if object_in_category_range(obj, category, bottom, top)]
