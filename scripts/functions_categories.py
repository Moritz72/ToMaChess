from math import inf
from .class_translation_handler import translation_handler

integer_categories = ("Rating", "Birth")
type_to_categories = {"player": ("Rating", "Birth", "Sex", "Federation"), "team": tuple()}
category_to_method_string = {
    "Rating": "get_rating", "Birth": "get_birthday", "Sex": "get_sex", "Federation": "get_country"
}


def get_range_string(bottom, top):
    if bottom == top:
        return f"{bottom}"
    if bottom in (-inf, ""):
        return f"≤ {top}"
    if top in (inf, ""):
        return f"≥ {bottom}"
    return f"{bottom} - {top}"


def get_category_range_title(category, bottom, top):
    return f"{translation_handler.tl(category)} {get_range_string(bottom, top)}"


def object_in_category_range(obj, category, bottom, top):
    method_string = category_to_method_string[category]
    if hasattr(obj, method_string):
        method = getattr(obj, method_string)
        if callable(method):
            value = method()
            if value is None:
                return False
            return bottom <= value <= top
    return False


def filter_list_by_category_range(obj_list, category, bottom, top):
    return [obj for obj in obj_list if object_in_category_range(obj, category, bottom, top)]
