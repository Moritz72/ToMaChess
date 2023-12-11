import os
import os.path
from typing import Sequence, Callable, cast
from requests import get, exceptions
from zipfile import ZipFile, BadZipFile
from xml.etree.ElementTree import parse
from csv import reader
from dbfread import DBF
from .collection import Collection
from .player import Player
from .functions_util import get_app_data_directory
from .db_collection import DB_COLLECTION, collection_exists
from .db_player import DB_PLAYER


def get_uuid_from_numbers(n: int, m: int) -> str:
    return f"00000000-0000-0000-{str(n).zfill(4)}-{str(m).zfill(12)}"


def renew_certificate(certificate: str) -> None:
    if not os.path.exists(os.path.dirname(certificate)):
        os.mkdir(os.path.dirname(certificate))
    url = f"https://raw.githubusercontent.com/Moritz72/ToMaChess/master/certificates/{os.path.basename(certificate)}"
    try:
        response = get(url)
        response.raise_for_status()
        with open(certificate, 'wb') as file:
            file.write(response.content)
    except exceptions.RequestException:
        return


def process_xml(xml_file_path: str, keys: Sequence[str]) -> list[tuple[str, ...]]:
    return [
        tuple(cast(str, child_elem.text) for child_elem in player_elem if child_elem.tag in keys)
        for player_elem in parse(xml_file_path).getroot().iter("player")
    ]


def process_csv(csv_file_path: str, keys: Sequence[str]) -> list[tuple[str, ...]]:
    with open(csv_file_path, 'r') as file:
        csv_reader = reader(file)
        header = next(csv_reader)
        indices = tuple(header.index(key) for key in keys)
        return [tuple(row[indices[j]] for j, value in enumerate(keys)) for row in csv_reader]


def download_and_unzip(url: str, file_to_extract: str, verify: bool | str = True, retry: bool = True) -> str | None:
    path_zip = os.path.join(get_app_data_directory(), "temp", "zip_file.zip")
    path_extract = os.path.join(get_app_data_directory(), "temp")
    try:
        response = get(url, verify=verify, headers={"User-Agent": "XY"})
        response.raise_for_status()
        with open(path_zip, 'wb') as file:
            file.write(response.content)
        with ZipFile(path_zip) as zip_file:
            return zip_file.extract(file_to_extract, path_extract)
    except (exceptions.SSLError, OSError):
        if isinstance(verify, str):
            renew_certificate(verify)
        if retry:
            return download_and_unzip(url, file_to_extract, verify=verify, retry=False)
        return None
    except exceptions.RequestException:
        return None
    except BadZipFile:
        return None
    finally:
        if os.path.exists(path_zip):
            os.remove(path_zip)
        path_extract = os.path.join(path_extract, file_to_extract)
        if os.path.exists(path_extract):
            os.rename(path_extract, os.path.join(get_app_data_directory(), "temp", "extracted_file"))


def update_list(name: str, get_list: Callable[[], list[Player] | None]) -> None:
    players_new = get_list()
    if players_new is None:
        return
    collection_uuid = players_new[0].get_uuid_associate()
    if collection_exists("", collection_uuid):
        players = DB_PLAYER.load_all("", collection_uuid)
    else:
        players = []
        DB_COLLECTION.add_list("", [Collection(name, "Players", collection_uuid)])
    DB_PLAYER.add_list("", list(set(players_new) - set(players)))
    DB_PLAYER.update_list("", list(set(players) & set(players_new)))
    DB_PLAYER.remove_list("", list(set(players) - set(players_new)))


def get_fide_standard_list() -> list[Player] | None:
    url = "http://ratings.fide.com/download/standard_rating_list_xml.zip"
    unzipped_file = download_and_unzip(url, "standard_rating_list.xml")
    if unzipped_file is None:
        return None
    data = process_xml(
        os.path.join(get_app_data_directory(), "temp", "extracted_file"),
        ("name", "sex", "birthday", "country", "title", "rating", "fideid")
    )
    os.remove(os.path.join(get_app_data_directory(), "temp", "extracted_file"))
    return [Player(
        entry[1], entry[3], entry[6], entry[2], entry[4], entry[5],
        get_uuid_from_numbers(1, int(entry[0])), get_uuid_from_numbers(1, 0)
    ) for entry in data]


def get_dsb_list() -> list[Player] | None:
    url = "https://dwz.svw.info/services/files/export/csv/LV-0-csv_v2.zip"
    certificate = os.path.join(get_app_data_directory(), "certificates", "svw-info-certificate.pem")
    unzipped_file = download_and_unzip(url, "spieler.csv", verify=certificate)
    if unzipped_file is None:
        return None
    data = process_csv(
        os.path.join(get_app_data_directory(), "temp", "extracted_file"),
        ("Spielername", "Geschlecht", "Geburtsjahr", "FIDE-Land", "FIDE-Titel", "DWZ", "ID")
    )
    os.remove(os.path.join(get_app_data_directory(), "temp", "extracted_file"))
    return [Player(
        entry[0].replace(",", ", "), entry[1], entry[2], entry[3], None if entry[4] == '-' else entry[4], entry[5],
        get_uuid_from_numbers(2, int(entry[6])), get_uuid_from_numbers(2, 0)
    ) for entry in data]


def get_uscf_list() -> list[Player] | None:
    url = "https://www.kingregistration.com/combineddb/db"
    unzipped_file = download_and_unzip(url, "uscffide.dbf")
    if unzipped_file is None:
        return None
    data: list[tuple[str, ...]] = [(
        record["MEM_NAME"], record["GENDER"], record["BYEAR"], record["FEDERATION"],
        record["TITLE"], record["R_LPB_RAT"], record["MEM_ID"]
    ) for record in DBF(os.path.join(get_app_data_directory(), "temp", "extracted_file"))]
    os.remove(os.path.join(get_app_data_directory(), "temp", "extracted_file"))
    return [Player(
        entry[0].replace(",", ", ").title(), entry[1], entry[2], entry[3], entry[4], entry[5],
        get_uuid_from_numbers(3, int(entry[6])), get_uuid_from_numbers(3, 0)
    ) for entry in data]


RATING_LISTS: dict[str, Callable[[], list[Player] | None]] = {
    "FIDE": get_fide_standard_list, "DSB": get_dsb_list, "USCF": get_uscf_list
}


def update_list_by_name(name: str) -> None:
    update_list(name, RATING_LISTS[name])
