import os
import os.path
from requests import get, exceptions
from zipfile import ZipFile, BadZipFile
from xml.etree.ElementTree import parse
from csv import reader
from dbfread import DBF
from .class_database_handler import DATABASE_HANDLER
from .class_collection import Collection
from .functions_util import get_app_data_directory
from .functions_collection import add_collection, collection_exists


def get_uuid_from_numbers(n, m):
    return f"00000000-0000-0000-{str(n).zfill(4)}-{str(m).zfill(12)}"


def renew_certificate(certificate):
    if not os.path.exists(os.path.dirname(certificate)):
        os.mkdir(os.path.dirname(certificate))
    try:
        response = get(
            f"https://raw.githubusercontent.com/Moritz72/ToMaChess/master/certificates/{os.path.basename(certificate)}"
        )
        response.raise_for_status()
        with open(certificate, 'wb') as file:
            file.write(response.content)
    except exceptions.RequestException as e:
        return


def process_xml(xml_file_path, key_dict):
    return [
        {key_dict[child_elem.tag]: child_elem.text for child_elem in player_elem if child_elem.tag in key_dict}
        for player_elem in parse(xml_file_path).getroot().iter("player")
    ]


def process_csv(csv_file_path, key_dict):
    with open(csv_file_path, 'r') as file:
        csv_reader = reader(file)
        header = next(csv_reader)
        indices = tuple(header.index(key) for key in key_dict)
        return [{value: row[indices[j]] for j, value in enumerate(list(key_dict.values()))} for row in csv_reader]


def download_and_unzip(url, file_to_extract, verify=True, retry=True):
    path_zip = os.path.join(get_app_data_directory(), "temp", "zip_file.zip")
    path_extract = os.path.join(get_app_data_directory(), "temp")
    try:
        response = get(url, verify=verify, headers={"User-Agent": "XY"})
        response.raise_for_status()
        with open(path_zip, 'wb') as file:
            file.write(response.content)
        with ZipFile(path_zip, 'r') as zip_file:
            return zip_file.extract(file_to_extract, path_extract)
    except (exceptions.SSLError, OSError):
        renew_certificate(verify)
        if retry:
            return download_and_unzip(url, file_to_extract, verify=verify, retry=False)
    except exceptions.RequestException as e:
        return
    except BadZipFile as e:
        return
    finally:
        if os.path.exists(path_zip):
            os.remove(path_zip)
        path_extract = os.path.join(path_extract, file_to_extract)
        if os.path.exists(path_extract):
            os.rename(path_extract, os.path.join(get_app_data_directory(), "temp", "extracted_file"))


def update_list(name, number, get_list):
    player_list = get_list()
    if player_list is None:
        return
    collection_uuid = get_uuid_from_numbers(number, 0)
    if collection_exists("", collection_uuid):
        uuids_to_delete = set(
            tuple(entry[-2:])
            for entry in DATABASE_HANDLER.get_entries("players", ("uuid_associate",), (collection_uuid,))
        ) - set((get_uuid_from_numbers(number, entry["id"]), collection_uuid) for entry in player_list)
    else:
        collection = add_collection("", Collection(name, "Players", collection_uuid))
        uuids_to_delete = set()
    DATABASE_HANDLER.add_or_update_entries(
        "players", ("name", "sex", "birthday", "country", "title", "rating", "uuid", "uuid_associate"),
        tuple(
            (
                entry["name"], entry["sex"], entry["birthday"], entry["country"], entry["title"], int(entry["rating"]),
                get_uuid_from_numbers(number, entry["id"]), collection_uuid
            ) for entry in player_list
        )
    )
    uuids_to_delete = list(uuids_to_delete)
    while uuids_to_delete:
        DATABASE_HANDLER.delete_entries_list(
            "players", ("uuid", "uuid_associate"), [list(entry) for entry in zip(*uuids_to_delete[:100])]
        )
        uuids_to_delete = uuids_to_delete[100:]


def get_fide_standard_list():
    url = "http://ratings.fide.com/download/standard_rating_list_xml.zip"
    unzipped_file = download_and_unzip(url, "standard_rating_list.xml")
    if unzipped_file is None:
        return
    player_list = process_xml(
        os.path.join(get_app_data_directory(), "temp", "extracted_file"),
        {
            "name": "name", "sex": "sex", "birthday": "birthday", "country": "country", "title": "title",
            "rating": "rating", "fideid": "id"
        }
    )
    os.remove(os.path.join(get_app_data_directory(), "temp", "extracted_file"))
    return player_list


def get_dsb_list():
    url = "https://dwz.svw.info/services/files/export/csv/LV-0-csv_v2.zip"
    certificate = os.path.join(get_app_data_directory(), "certificates", "svw-info-certificate.pem")
    unzipped_file = download_and_unzip(url, "spieler.csv", verify=certificate)
    if unzipped_file is None:
        return
    player_list = process_csv(
        os.path.join(get_app_data_directory(), "temp", "extracted_file"),
        {
            "ID": "id", "Spielername": "name", "Geschlecht": "sex", "Geburtsjahr": "birthday", "FIDE-Land": "country",
            "FIDE-Titel": "title", "DWZ": "rating"
        }
    )
    os.remove(os.path.join(get_app_data_directory(), "temp", "extracted_file"))
    for player in player_list:
        player["name"] = player["name"].replace(",", ", ")
        if player["country"] == '-':
            player["country"] = ""
        if player["rating"] == "":
            player["rating"] = 0
    return player_list


def get_uscf_list():
    url = "https://www.kingregistration.com/combineddb/db"
    unzipped_file = download_and_unzip(url, "uscffide.dbf")
    if unzipped_file is None:
        return
    player_list = []
    for record in DBF(os.path.join(get_app_data_directory(), "temp", "extracted_file")):
        player_list.append({
            "id": record["MEM_ID"], "name": record["MEM_NAME"].replace(",", ", ").title(), "sex": record["GENDER"],
            "birthday": record["BYEAR"], "country": record["FEDERATION"], "title": record["TITLE"],
            "rating": record["R_LPB_RAT"] or 0
        })
    os.remove(os.path.join(get_app_data_directory(), "temp", "extracted_file"))
    return player_list


RATING_LISTS = {"FIDE": (1, get_fide_standard_list), "DSB": (2, get_dsb_list), "USCF": (3, get_uscf_list)}


def update_list_by_name(name):
    update_list(name, *RATING_LISTS[name])
