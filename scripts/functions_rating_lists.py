import os
import os.path
from requests import get, exceptions
from zipfile import ZipFile, BadZipFile
from xml.etree.ElementTree import parse
from csv import reader
from .class_database_handler import database_handler
from .class_collection import Collection
from .functions_util import get_root_directory
from .functions_collection import add_collection, collection_exists


def get_uuid_from_numbers(n, m):
    return f"00000000-0000-0000-{str(n).zfill(4)}-{str(m).zfill(12)}"


def renew_certificate(certificate):
    try:
        response = get(
            f"https://raw.githubusercontent.com/Moritz72/ToMaChess/master/certificates/{certificate.split('/')[-1]}"
        )
        response.raise_for_status()
        with open(certificate, 'wb') as file:
            file.write(response.content)
    except exceptions.RequestException as e:
        return


def process_xml(xml_file_path, key_dict):
    tree = parse(xml_file_path)
    root = tree.getroot()
    players = [
        {key_dict[child_elem.tag]: child_elem.text for child_elem in player_elem if child_elem.tag in key_dict}
        for player_elem in root.iter("player")
    ]
    return players


def process_csv(csv_file_path, key_dict):
    with open(csv_file_path, 'r') as file:
        csv_reader = reader(file)
        header = next(csv_reader)
        indices = tuple(header.index(key) for key in key_dict)
        players = [{value: row[indices[j]] for j, value in enumerate(list(key_dict.values()))} for row in csv_reader]
    return players


def download_and_unzip(url, file_to_extract, verify=True, retry=True):
    try:
        response = get(url, verify=verify)
        response.raise_for_status()
        with open(os.path.join(get_root_directory(), "zip_file.zip"), 'wb') as file:
            file.write(response.content)
        with ZipFile(os.path.join(get_root_directory(), "zip_file.zip"), 'r') as zip_file:
            return zip_file.extract(file_to_extract)
    except exceptions.SSLError:
        renew_certificate(verify)
        if retry:
            return download_and_unzip(url, file_to_extract, verify=verify, retry=False)
    except exceptions.RequestException as e:
        return
    except BadZipFile as e:
        return
    finally:
        if os.path.exists(os.path.join(get_root_directory(), "zip_file.zip")):
            os.remove(os.path.join(get_root_directory(), "zip_file.zip"))
        if os.path.exists(os.path.join(get_root_directory(), file_to_extract)):
            os.rename(
                os.path.join(get_root_directory(), file_to_extract),
                os.path.join(get_root_directory(), "extracted_file")
            )


def update_list(name, number, get_list):
    player_list = get_list()
    if player_list is None:
        return
    collection_uuid = get_uuid_from_numbers(number, 0)
    if collection_exists("", collection_uuid):
        uuids_to_delete = set(
            tuple(entry[:-2])
            for entry in database_handler.get_entries("players", ("uuid_associate",), (collection_uuid,))
        ) - set((get_uuid_from_numbers(number, entry["id"]), collection_uuid) for entry in player_list)
    else:
        collection = add_collection("", Collection(name, "Players", collection_uuid))
        uuids_to_delete = set()
    database_handler.add_or_update_entries(
        "players", ("name", "sex", "birthday", "country", "title", "rating", "uuid", "uuid_associate"),
        tuple(
            (
                entry["name"], entry["sex"], entry["birthday"], entry["country"], entry["title"], int(entry["rating"]),
                get_uuid_from_numbers(number, entry["id"]), collection_uuid
            ) for entry in player_list
        )
    )


def get_fide_standard_list():
    unzipped_file = download_and_unzip(
        "http://ratings.fide.com/download/standard_rating_list_xml.zip", "standard_rating_list.xml"
    )
    if unzipped_file is None:
        return
    player_list = process_xml(
        os.path.join(get_root_directory(), "extracted_file"),
        {
            "name": "name", "sex": "sex", "birthday": "birthday", "country": "country", "title": "title",
            "rating": "rating", "fideid": "id"
        }
    )
    os.remove(os.path.join(get_root_directory(), "extracted_file"))
    return player_list


def get_dsb_list():
    unzipped_file = download_and_unzip(
        "https://dwz.svw.info/services/files/export/csv/LV-0-csv_v2.zip", "spieler.csv",
        verify=os.path.join(get_root_directory(), "certificates", "svw-info-certificate.pem")
    )
    if unzipped_file is None:
        return
    player_list = process_csv(
        os.path.join(get_root_directory(), "extracted_file"),
        {
            "ID": "id", "Spielername": "name", "Geschlecht": "sex", "Geburtsjahr": "birthday", "FIDE-Land": "country",
            "FIDE-Titel": "title", "DWZ": "rating"
        }
    )
    os.remove(os.path.join(get_root_directory(), "extracted_file"))
    for i in range(len(player_list)):
        player_list[i]["name"] = player_list[i]["name"].replace(",", ", ")
        if player_list[i]["rating"] == "":
            player_list[i]["rating"] = 0
    return player_list


rating_lists = {"FIDE": (1, get_fide_standard_list), "DSB": (2, get_dsb_list)}


def update_list_by_name(name):
    update_list(name, *rating_lists[name])
