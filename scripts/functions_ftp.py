import os.path
from typing import cast
from re import escape, sub
from io import BytesIO
from .manager_translation import MANAGER_TRANSLATION
from .ftp_connection import FTP_CONNECTION
from .pairing_item import get_tentative_results
from .ms_tournament import MS_Tournament
from .tournament import Tournament
from .player import Player
from .team import Team
from .category_range import Category_Range
from .functions_util import get_root_directory, read_file

PERMISSIBLE_CHARACTERS = "abcdefghijklmnopqrstuvwxyz0123456789_+-"


def get_style(filename: str) -> str:
    return read_file(os.path.join(get_root_directory(), "css", filename))


def get_file_name(name: str, sub_folder: str = "") -> str:
    pattern = f"[^{escape(PERMISSIBLE_CHARACTERS)}]"
    folder = sub(pattern, '', name.lower().replace(' ', '_').replace('.', '_'))
    while "__" in folder:
        folder = folder.replace('__', '_')
    if sub_folder:
        return f"{sub_folder}/{folder}"
    return folder


def get_file_name_category(category_range: Category_Range) -> str:
    title = category_range.get_title(False)
    if "≥ " in title:
        title += " - "
        title = title.replace("≥ ", '')
    else:
        title = title.replace("≤ ", " - ")
    return get_file_name(title.replace(" - ", '-'))


def make_folder(folder_name: str) -> None:
    nlst = FTP_CONNECTION.nlst()
    if nlst is None:
        return
    if folder_name not in nlst:
        FTP_CONNECTION.mkd(folder_name)


def make_new_folders(tournament: Tournament, sub_folder: str = "") -> None:
    if sub_folder:
        folder_path = f"{sub_folder}/{get_file_name(tournament.get_name())}"
        make_folder(sub_folder)
    else:
        folder_path = get_file_name(tournament.get_name())

    categories = tournament.get_category_ranges()
    paths_parts = [(folder_path,), (folder_path, "standings"), (folder_path, "pairings"), (folder_path, "results")]
    paths_parts.extend([
        (folder_path, "standings", get_file_name_category(category_range)) for category_range in categories
    ])
    for parts in paths_parts:
        make_folder('/'.join(parts))
    make_index_file(folder_path, tournament)


def make_index_file(folder_path: str, tournament: Tournament) -> None:
    names = tuple(tournament.get_round_name(roun) for roun in range(1, tournament.get_round()))
    names_display = tuple(MANAGER_TRANSLATION.tl(name) for name in names)
    names_file = tuple(get_file_name(''.join(name)) for name in names)
    participants_link = f"<a href=participants.html>{MANAGER_TRANSLATION.tl('Participants')}</a>"
    standings_links = [f"<a href=standings/{f}.html>{d}</a>" for d, f in zip(names_display, names_file)]
    pairings_links = [f"<a href=pairings/{f}.html>{d}</a>" for d, f in zip(names_display, names_file)]
    results_links = [f"<a href=results/{f}.html>{d}</a>" for d, f in zip(names_display, names_file)]

    pairings = tournament.get_pairings()
    if bool(pairings) and pairings.is_fixed():
        recent_name = tournament.get_round_name(tournament.get_round())
        recent_name_display = MANAGER_TRANSLATION.tl(recent_name)
        recent_name_file = get_file_name(''.join(recent_name))
        pairings_links.append(f"<a href=pairings/{recent_name_file}.html>{recent_name_display}</a>")
    categories = tournament.get_category_ranges()
    categories_links = [[
        f"<a href=standings/{get_file_name_category(category_range)}/{f}.html>{d}</a>"
        for d, f in zip(names_display, names_file)
    ] for category_range in categories]

    html = f"<!DOCTYPE html><html><head><style>{get_style('index.css')}</style></head><body>"
    html += f"<h2>{tournament}</h2><table class='table-info'>"
    for key, value in tournament.get_details().items():
        html += f"<tr><td class='bold'>{MANAGER_TRANSLATION.tl(key)}</td><td>{MANAGER_TRANSLATION.tl(value)}</td></tr>"
    if not tournament.is_valid():
        html += "</table></body></html>"
        upload_to_server(f"{folder_path}/index.html", html)
        return
    html += f"</table><br><span class='large'>{participants_link}</span><br><br><table class='table-links'>"
    html += f"<tr><th>{MANAGER_TRANSLATION.tl('Pairings')}</th><td>"
    html += "</td><td>".join(pairings_links)
    html += f"</td><tr><th>{MANAGER_TRANSLATION.tl('Results')}</th><td>"
    html += "</td><td>".join(results_links)
    html += f"</td><tr><th>{MANAGER_TRANSLATION.tl('Standings')}</th><td>"
    html += "</td><td>".join(standings_links)
    if bool(categories):
        html += "</td></table><br><table class='table-links'>"
    for category_range, category_links in zip(categories, categories_links):
        html += f"</td><tr><th>{category_range.get_title()}</th><td>"
        html += "</td><td>".join(category_links)
    html += "</td></table></body></html>"
    upload_to_server(f"{folder_path}/index.html", html)


def make_index_file_ms_tournament(ms_tournament: MS_Tournament) -> None:
    folder_path = get_file_name(ms_tournament.get_name())
    make_folder(folder_path)
    html = f"<!DOCTYPE html><html><head><style>{get_style('index_ms.css')}</style></head><body>"
    html += f"<h2>{ms_tournament}</h2><br><br>"
    for stage in range(ms_tournament.get_stages()):
        for tournament in ms_tournament.get_stage_tournaments(stage):
            name = tournament.get_name()
            make_folder(get_file_name(name, folder_path))
            make_index_file(get_file_name(name, folder_path), tournament)
            html += f"<span class='tournament'><a href={get_file_name(name)}/index.html>{name}</a></span>"
        html += "<br><br><br><br>"
    html += "</td></body></html>"
    upload_to_server(f"{folder_path}/index.html", html)


def get_player_entry(player: Player, i: int) -> str:
    return f"""
    <tr>
        <td class="placement">{i + 1}</td>
        <td class="name">{player.get_name() or ""}</td>
        <td class="sex">{player.get_sex() or ""}</td>
        <td class="birth">{player.get_birthday() or ""}</td>
        <td class="federation">{player.get_country() or ""}</td>
        <td class="title">{player.get_title() or ""}</td>
        <td class="rating">{player.get_rating() or ""}</td>
    </tr>
    """


def get_results_entry(item_1: str, item_2: str, score_1: str, score_2: str, i: int, name_dict: dict[str, str]) -> str:
    score = "" if score_1 == 'b' else f"{score_1} : {score_2}"
    return f"""
    <tr>
        <td class="board">{i + 1}</td>
        <td class="player_1">{name_dict[item_1]}</td>
        <td class="result">{score}</td>
        <td class="player_2">{name_dict[item_2]}</td>
        </tr>
    """


def get_html_participants(tournament: Tournament) -> str:
    participants = cast(list[Player], tournament.get_participants())
    caption = MANAGER_TRANSLATION.tl("Participants")
    header_horizontal = ("Name", "Sex", "Birth", "Federation", "Title", "Rating")
    html = f"<!DOCTYPE html><html><head><style>{get_style('participants.css')}</style></head><body>"
    html += f"<h2>{tournament}</h2>"
    html += f"<table><caption>{caption}</caption>"
    piece = '</th><th>'.join(MANAGER_TRANSLATION.tl(item, short=True) for item in header_horizontal)
    html += f"<tr><th></th><th>{piece}</th></tr>"
    for i, player in enumerate(sorted(participants, key=lambda participant: participant.get_name())):
        html += get_player_entry(player, i)
    html += "</table></body></html>"
    return html


def get_html_participants_team(tournament: Tournament) -> str:
    participants = cast(list[Team], tournament.get_participants())
    header_horizontal = ("Name", "Sex", "Birth", "Federation", "Title", "Rating")
    html = f"<!DOCTYPE html><html><head><style>{get_style('participants.css')}</style></head><body>"
    html += f"<h2>{tournament}</h2>"
    for team in participants:
        html += f"<table><caption>{team.get_name()}</caption>"
        piece = '</th><th>'.join(MANAGER_TRANSLATION.tl(item, short=True) for item in header_horizontal)
        html += f"<tr><th></th><th>{piece}</th></tr>"
        for i, player in enumerate(team.get_members()):
            html += get_player_entry(player, i)
        html += "</table><br>"
    html += "</body></html>"
    return html


def get_html_latest_standings(tournament: Tournament, category_range: Category_Range | None = None) -> str:
    round_name = MANAGER_TRANSLATION.tl(tournament.get_round_name(tournament.get_round() - 1))
    caption = MANAGER_TRANSLATION.tl("Standings after {}", insert=round_name)
    if category_range is not None:
        caption += f" ({category_range.get_title()})"
    table = tournament.get_standings(category_range)
    html = f"<!DOCTYPE html><html><head><style>{get_style('standings.css')}</style></head><body>"
    html += f"<h2>{tournament}</h2>"
    html += f"<table><caption>{caption}</caption>"
    piece = '</th><th>'.join(MANAGER_TRANSLATION.tl(item, short=True) for item in table.headers)
    html += f"<tr><th></th><th>{piece}</th></tr>"
    for row, vertical_item in zip(table.get_strings(), table.get_header_vertical()):
        html += f"<tr><td class='placement'>{vertical_item}</td>"
        for i, item in enumerate(row):
            if i == 0:
                html += f"<td class='name'>{item}</td>"
            else:
                html += f"<td class='score'>{item}</td>"
        html += "</tr>"
    html += "</table></body></html>"
    return html


def get_html_pairings(tournament: Tournament) -> str:
    pairings = tournament.get_pairings()
    if not bool(pairings):
        return ""
    name_dict = tournament.get_uuid_to_name_dict() | {"bye": "bye", "": ""}
    round_name = MANAGER_TRANSLATION.tl(tournament.get_round_name(tournament.get_round()))
    caption = MANAGER_TRANSLATION.tl('Pairings for {}', insert=round_name)
    html = f"<!DOCTYPE html><html><head><style>{get_style('pairings.css')}</style></head><body>"
    html += f"<h2>{tournament}</h2>"
    html += f"<table><caption>{caption}</caption>"
    html += "<tr><th></th><th></th><th></th><th></th></tr>"
    for i, (item_1, item_2) in enumerate(pairings):
        assert(not isinstance(item_1, list) and not isinstance(item_2, list))
        score_1, score_2 = get_tentative_results(item_1, item_2) or ("", "")
        html += get_results_entry(item_1, item_2, score_1, score_2, i, name_dict)
    html += "</table></body></html>"
    return html


def get_html_results_round(tournament: Tournament, roun: int) -> str:
    if roun >= tournament.get_round():
        return ""
    results = tournament.get_results()[roun - 1]
    name_dict = tournament.get_uuid_to_name_dict() | {"bye": "bye", "": ""}
    round_name = MANAGER_TRANSLATION.tl(tournament.get_round_name(roun))
    caption = MANAGER_TRANSLATION.tl('Results of {}', insert=round_name)
    html = f"<!DOCTYPE html><html><head><style>{get_style('results.css')}</style></head><body>"
    html += f"<h2>{tournament}</h2>"
    html += f"<table><caption>{caption}</caption>"
    html += "<tr><th></th><th></th><th></th><th></th></tr>"
    for i, ((item_1, score_1), (item_2, score_2)) in enumerate(results):
        html += get_results_entry(item_1, item_2, score_1, score_2, i, name_dict)
    html += "</table></body></html>"
    return html


def get_html_results_round_team(tournament: Tournament, roun: int) -> str:
    if roun >= tournament.get_round():
        return ""
    results = tournament.get_results()[roun - 1]
    results_individual = tournament.get_results_team()[roun - 1]
    name_dict = tournament.get_uuid_to_name_dict() | {"bye": "bye", "": ""}
    name_dict_individual = tournament.get_uuid_to_name_dict_individual() | {"bye": "bye", "": ""}
    round_name = MANAGER_TRANSLATION.tl(tournament.get_round_name(roun))
    caption = MANAGER_TRANSLATION.tl('Results of {}', insert=round_name)
    html = f"<!DOCTYPE html><html><head><style>{get_style('results.css')}</style></head><body>"
    html += f"<h2>{tournament}</h2>"
    for i, (((team_item_1, _), (team_item_2, _)), individual) in enumerate(zip(results, results_individual)):
        team_1, team_2 = name_dict[team_item_1], name_dict[team_item_2]
        if i == 0:
            html += f"<table><caption>{caption}</caption>"
        else:
            html += f"<table>"
        html += f"<tr><th></th><th>{team_1}</th><th></th><th>{team_2}</th></tr>"
        for j, ((item_1, score_1), (item_2, score_2)) in enumerate(individual):
            html += get_results_entry(item_1, item_2, score_1, score_2, j, name_dict_individual)
        html += "</table><br>"
    html += "</body></html>"
    return html


def upload_to_server(file_path: str, html: str) -> None:
    FTP_CONNECTION.storbinary(f"STOR {file_path}", cast(str, BytesIO(html.encode("utf-8"))))


def upload_participants(tournament: Tournament, sub_folder: str = "") -> None:
    make_new_folders(tournament, sub_folder)
    file_name = f"{get_file_name(tournament.get_name(), sub_folder)}/participants.html"
    if tournament.is_team_tournament():
        upload_to_server(file_name, get_html_participants_team(tournament))
    else:
        upload_to_server(file_name, get_html_participants(tournament))


def upload_latest_standings(tournament: Tournament, sub_folder: str = "") -> None:
    make_new_folders(tournament, sub_folder)
    folder_name = f"{get_file_name(tournament.get_name(), sub_folder)}/standings"
    round_name = ''.join(tournament.get_round_name(tournament.get_round() - 1))
    file_name = f"{get_file_name(round_name, folder_name)}.html"
    upload_to_server(file_name, get_html_latest_standings(tournament))
    categories = tournament.get_category_ranges()
    if not categories:
        return
    for category_range in categories:
        file_name = f"{folder_name}/{get_file_name_category(category_range)}/{get_file_name(round_name)}.html"
        upload_to_server(file_name, get_html_latest_standings(tournament, category_range))


def upload_latest_pairings(tournament: Tournament, sub_folder: str = "") -> None:
    make_new_folders(tournament, sub_folder)
    folder_name = f"{get_file_name(tournament.get_name(), sub_folder)}/pairings"
    round_name = ''.join(tournament.get_round_name(tournament.get_round()))
    file_name = f"{get_file_name(round_name, folder_name)}.html"
    upload_to_server(file_name, get_html_pairings(tournament))


def upload_latest_results(tournament: Tournament, sub_folder: str = "") -> None:
    make_new_folders(tournament, sub_folder)
    folder_name = f"{get_file_name(tournament.get_name(), sub_folder)}/results"
    round_name = ''.join(tournament.get_round_name(tournament.get_round() - 1))
    file_name = f"{get_file_name(round_name, folder_name)}.html"
    if tournament.is_team_tournament():
        upload_to_server(file_name, get_html_results_round_team(tournament, tournament.get_round() - 1))
    else:
        upload_to_server(file_name, get_html_results_round(tournament, tournament.get_round() - 1))
