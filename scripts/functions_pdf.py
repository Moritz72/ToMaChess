import os
import os.path
from typing import Sequence, cast
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.pdfbase.pdfmetrics import stringWidth
from .manager_settings import MANAGER_SETTINGS
from .manager_translation import MANAGER_TRANSLATION
from .pairing_item import get_tentative_results
from .player import Player
from .team import Team
from .tournament import Tournament

Table_Data = tuple[list[list[str]], list[str], list[str], list[float], list[str], list[str]]
FONT = "Helvetica"
FONT_BOLD = "Helvetica-Bold"
FONT_SIZE = 12
PAGE_WIDTH, PAGE_HEIGHT = A4
LEFT_MARGIN, RIGHT_MARGIN, TOP_MARGIN, BOTTOM_MARGIN = 4 * (.5 * inch,)
USABLE_WIDTH = PAGE_WIDTH - LEFT_MARGIN - RIGHT_MARGIN
USABLE_HEIGHT = PAGE_HEIGHT - TOP_MARGIN - BOTTOM_MARGIN
ROW_HEIGHT = 1.7 * FONT_SIZE
LINE_WIDTHS = (.5, 1.5, 2)


def get_path(*parts: str) -> str:
    return os.path.join(MANAGER_SETTINGS["pdf_path"], *parts)


def make_new_folder(tournament: Tournament, sub_folder: str = "") -> bool:
    if MANAGER_SETTINGS["pdf_path"] == "":
        return False
    folder_path = get_path(sub_folder)
    try:
        if sub_folder and not os.path.exists(folder_path):
            os.mkdir(folder_path)
        folder_path = os.path.join(folder_path, tournament.get_name())
        paths_parts = [
            (folder_path,), (folder_path, MANAGER_TRANSLATION.tl("Standings")),
            (folder_path, MANAGER_TRANSLATION.tl("Pairings")), (folder_path, MANAGER_TRANSLATION.tl("Results"))
        ]
        if tournament.get_category_ranges():
            name = f"{MANAGER_TRANSLATION.tl('Standings')} ({MANAGER_TRANSLATION.tl('Categories')})"
            paths_parts.append((folder_path, name))
        for parts in paths_parts:
            path = get_path(*parts)
            if not os.path.exists(path):
                os.mkdir(path)
    except:
        return False
    return True


def get_top_row_initial() -> float:
    return PAGE_HEIGHT - TOP_MARGIN - ROW_HEIGHT


def get_max_number_of_rows(top_row: float) -> int:
    return int(3 / 4 + (top_row - BOTTOM_MARGIN) / ROW_HEIGHT)


def draw_text_on_top(pdf: canvas.Canvas, top_row: float, text_on_top: Sequence[str]) -> None:
    for i, text in enumerate(text_on_top):
        pdf.drawString(LEFT_MARGIN + FONT_SIZE / 2, top_row - i * ROW_HEIGHT, text)


def draw_text(pdf: canvas.Canvas, string: str, x: float, y: float, column_width: float, align: str) -> None:
    while stringWidth(string, FONT, FONT_SIZE) > column_width - FONT_SIZE / 2:
        string = string[:-1]
    match align:
        case "CENTER":
            pdf.drawCentredString(x + column_width / 2, y, string)
        case "RIGHT":
            pdf.drawRightString(x + column_width - FONT_SIZE / 2, y, string)
        case "LEFT":
            pdf.drawString(x + FONT_SIZE / 2, y, string)


def get_vertical_header_width(vertical_header: Sequence[str]) -> float:
    if vertical_header is None:
        return 0
    max_header_len = max((len(header) for header in vertical_header))
    return FONT_SIZE * (max_header_len + .2)


def draw_header_backgrounds(
        pdf: canvas.Canvas, top_row: float, horizontal_header: Sequence[str], vertical_header: Sequence[str], n: int
) -> None:
    pdf.setFillColor(colors.lightgrey)
    top = top_row + 3 / 4 * ROW_HEIGHT
    if horizontal_header is not None:
        pdf.rect(LEFT_MARGIN, top, PAGE_WIDTH - RIGHT_MARGIN - LEFT_MARGIN, -ROW_HEIGHT, fill=True)
    if vertical_header is not None:
        bottom = top_row + (3 / 4 - n + 1) * ROW_HEIGHT
        width = get_vertical_header_width(vertical_header)
        pdf.rect(LEFT_MARGIN, top, width, bottom - top, fill=True)
    pdf.setFillColor(colors.black)


def draw_horizontal_lines(pdf: canvas.Canvas, top_row: float, horizontal_header: Sequence[str], n: int) -> None:
    left = LEFT_MARGIN
    right = PAGE_WIDTH - RIGHT_MARGIN
    y = top_row + 3 / 4 * ROW_HEIGHT
    for i in range(n):
        if i == n - 1 or y - ROW_HEIGHT < BOTTOM_MARGIN or i == 0:
            pdf.setLineWidth(LINE_WIDTHS[2])
        elif i == 1 and horizontal_header is not None:
            pdf.setLineWidth(LINE_WIDTHS[1])
        else:
            pdf.setLineWidth(LINE_WIDTHS[0])
        pdf.line(left, y, right, y)
        y -= ROW_HEIGHT


def draw_vertical_lines(
        pdf: canvas.Canvas, top_row: float, vertical_header: Sequence[str], column_widths: Sequence[float], n: int
) -> None:
    top = top_row + 3 / 4 * ROW_HEIGHT
    bottom = top_row + (3 / 4 - n + 1) * ROW_HEIGHT
    x = LEFT_MARGIN
    if vertical_header is not None:
        pdf.setLineWidth(LINE_WIDTHS[2])
        pdf.line(x, top, x, bottom)
        x += get_vertical_header_width(vertical_header)
    for i in range(len(column_widths) + 1):
        if i == len(column_widths) or (i == 0 and vertical_header is None):
            pdf.setLineWidth(LINE_WIDTHS[2])
        elif i == 0 and vertical_header is not None:
            pdf.setLineWidth(LINE_WIDTHS[1])
        else:
            pdf.setLineWidth(LINE_WIDTHS[0])
        pdf.line(x, top, x, bottom)
        if i < len(column_widths):
            x += column_widths[i]


def draw_horizontal_header(
        pdf: canvas.Canvas, top_row: float, horizontal_header: Sequence[str],
        column_widths: Sequence[float], shift_x: float
) -> None:
    pdf.setFont(FONT_BOLD, FONT_SIZE)
    x = LEFT_MARGIN + shift_x
    y = top_row
    for header, column_width in zip(horizontal_header, column_widths):
        draw_text(pdf, header, x, y, column_width, "CENTER")
        x += column_width


def draw_vertical_header(
        pdf: canvas.Canvas, top_row: float, vertical_header: Sequence[str],
        from_index: int, to_index: int, shift_y: float
) -> None:
    pdf.setFont(FONT_BOLD, FONT_SIZE)
    x = LEFT_MARGIN
    y = top_row - shift_y
    width = get_vertical_header_width(vertical_header)
    for header in vertical_header[from_index:to_index]:
        draw_text(pdf, header, x, y, width, "CENTER")
        y -= ROW_HEIGHT


def draw_row(
        pdf: canvas.Canvas, top_row: float, row: int, strings: Sequence[str], column_widths: Sequence[float],
        aligns: Sequence[str], shift_x: float, shift_y: float
) -> None:
    pdf.setFont(FONT, FONT_SIZE)
    x = LEFT_MARGIN + shift_x
    y = top_row - row * ROW_HEIGHT - shift_y
    for string, column_width, align in zip(strings, column_widths, aligns):
        draw_text(pdf, string, x, y, column_width, align)
        x += column_width


def add_table_to_pdf(
        pdf: canvas.Canvas, top_row: float, table: list[list[str]], horizontal_header: Sequence[str] | None = None,
        vertical_header: Sequence[str] | None = None, column_widths: Sequence[float] | None = None,
        aligns: Sequence[str] | None = None, text_on_top: Sequence[str] | None = None, translate: bool = True
) -> float:
    if horizontal_header is None:
        horizontal_header = []
    if vertical_header is None:
        vertical_header = []
    if text_on_top is None:
        text_on_top = []
    if len(table) == 0 or len(table[0]) == 0:
        return top_row - 2 * ROW_HEIGHT

    if translate:
        horizontal_header = MANAGER_TRANSLATION.tl_list(horizontal_header, short=True)
    if translate:
        vertical_header = MANAGER_TRANSLATION.tl_list(vertical_header, short=True)
    vertical_header_width = get_vertical_header_width(vertical_header)
    if column_widths is None:
        column_widths = len(table[0]) * ((USABLE_WIDTH - vertical_header_width) / len(table[0]))
    else:
        column_widths = [(USABLE_WIDTH - vertical_header_width) * width for width in column_widths]
    aligns = aligns or len(table[0]) * ["LEFT"]
    shift_x = vertical_header_width
    shift_y = 0 if horizontal_header is None else ROW_HEIGHT
    shift_n = 1 + (horizontal_header is not None)

    required = len(text_on_top) + len(table) + 1
    max_current_page = get_max_number_of_rows(top_row)
    if top_row < get_top_row_initial() and required > max_current_page:
        pdf.showPage()
        top_row = get_top_row_initial()

    i = 0
    while i < len(table):
        if i > 0:
            pdf.showPage()
            top_row = get_top_row_initial()
        draw_text_on_top(pdf, top_row, text_on_top)
        top_row -= len(text_on_top) * ROW_HEIGHT
        n = min(len(table) - i + shift_n, get_max_number_of_rows(top_row) + 1)
        draw_header_backgrounds(pdf, top_row, horizontal_header, vertical_header, n)
        draw_horizontal_lines(pdf, top_row, horizontal_header, n)
        draw_vertical_lines(pdf, top_row, vertical_header, column_widths, n)
        if horizontal_header is not None:
            draw_horizontal_header(pdf, top_row, horizontal_header, column_widths, shift_x)
        draw_vertical_lines(pdf, top_row, vertical_header, column_widths, n)
        if vertical_header is not None:
            draw_vertical_header(pdf, top_row, vertical_header, i, i + n - shift_n, shift_y)
        for j in range(n - shift_n):
            draw_row(pdf, top_row, j, table[i+j], column_widths, aligns, shift_x, shift_y)
        top_row -= (n - shift_n) * ROW_HEIGHT
        i += n - shift_n
    return top_row


def make_pdf_from_tables(filename: str, tables_data: Sequence[Table_Data], translate: bool = True) -> None:
    pdf = canvas.Canvas(filename, pagesize=A4)
    top_row = get_top_row_initial()
    for table, horizontal_header, vertical_header, column_widths, aligns, text_on_top in tables_data:
        top_row = add_table_to_pdf(
            pdf, top_row, table, horizontal_header, vertical_header, column_widths, aligns, text_on_top, translate
        )
        top_row -= 2 * ROW_HEIGHT
    pdf.save()


def get_player_row(player: Player) -> list[str]:
    return [
        player.get_name(), player.get_sex() or "", str(player.get_birthday() or ""),
        player.get_country() or "", player.get_title() or "", str(player.get_rating() or "")
    ]


def get_result_row(item_1: str, item_2: str, score_1: str, score_2: str, name_dict: dict[str, str]) -> list[str]:
    score = "" if score_1 == 'b' else f"{score_1} : {score_2}"
    return [name_dict[item_1], score, name_dict[item_2]]


def tournament_participants_to_pdf(tournament: Tournament, sub_folder: str = "") -> None:
    if not make_new_folder(tournament, sub_folder):
        return

    filename = get_path(sub_folder, tournament.get_name(), f"{MANAGER_TRANSLATION.tl('Participants')}.pdf")
    header_horizontal = ["Name", "Sex", "Birth", "Federation", "Title", "Rating"]
    column_widths = [.6, .07, .08, .08, .08, .09]
    aligns = ["LEFT"] + 5 * ["CENTER"]

    if tournament.is_team_tournament():
        teams = cast(list[Team], tournament.get_participants())
        tables_data = [
            (
                [get_player_row(player) for player in team.get_members()], header_horizontal,
                [str(i + 1) for i in range(len(team.get_members()))], column_widths, aligns,
                [MANAGER_TRANSLATION.tl("Participants"), "", team.get_name()] if i == 0 else [team.get_name()]
            )
            for i, team in enumerate(teams)
        ]
    else:
        players = cast(list[Player], tournament.get_participants())
        header_vertical = [str(i + 1) for i in range(len(players))]
        top_lines = [MANAGER_TRANSLATION.tl("Participants")]
        table = [get_player_row(player) for player in players]
        tables_data = [(table, header_horizontal, header_vertical, column_widths, aligns, top_lines)]

    make_pdf_from_tables(filename, tables_data)


def tournament_standings_to_pdf(tournament: Tournament, sub_folder: str = "") -> None:
    if not make_new_folder(tournament, sub_folder):
        return
    round_name = MANAGER_TRANSLATION.tl(tournament.get_round_name(tournament.get_round() - 1))
    top_line = MANAGER_TRANSLATION.tl("Standings after {}", insert=round_name)
    filename = get_path(sub_folder, tournament.get_name(), MANAGER_TRANSLATION.tl("Standings"), f"{round_name}.pdf")
    table = tournament.get_standings()
    column_widths = [1 - .1 * (len(table.headers) - 1)] + (len(table.headers) - 1) * [.1]
    aligns = ["LEFT"] + (len(table.headers) - 1) * ["CENTER"]
    table_data = (table.get_strings(), table.headers, table.get_header_vertical(), column_widths, aligns, [top_line])

    make_pdf_from_tables(filename, [table_data])

    if not tournament.get_category_ranges():
        return
    filename = get_path(
        sub_folder, tournament.get_name(),
        f"{MANAGER_TRANSLATION.tl('Standings')} ({MANAGER_TRANSLATION.tl('Categories')})", f"{round_name}.pdf"
    )
    tables_data = []
    for category_range in tournament.get_category_ranges():
        table_cat = tournament.get_standings(category_range)
        tables_data.append((
            table_cat.get_strings(), table.headers, table_cat.get_header_vertical(),
            column_widths, aligns, [top_line + f" ({category_range.get_title()})"]
        ))

    make_pdf_from_tables(filename, tables_data)


def tournament_pairings_to_pdf(tournament: Tournament, sub_folder: str = "") -> None:
    if not make_new_folder(tournament, sub_folder):
        return
    pairings = tournament.get_pairings()
    if not bool(pairings):
        return

    round_name = MANAGER_TRANSLATION.tl(tournament.get_round_name(tournament.get_round()))
    top_line = MANAGER_TRANSLATION.tl("Pairings for {}", insert=round_name)
    filename = get_path(sub_folder, tournament.get_name(), MANAGER_TRANSLATION.tl("Pairings"), f"{round_name}.pdf")
    name_dict = tournament.get_uuid_to_name_dict() | {"bye": "bye", "": ""}
    header_horizontal = ["", "", ""]
    header_vertical = [str(i + 1) for i in range(len(pairings))]

    table = []
    for item_1, item_2 in pairings:
        assert(not isinstance(item_1, list) and not isinstance(item_2, list))
        score_1, score_2 = get_tentative_results(item_1, item_2) or ("", "")
        table.append(get_result_row(item_1, item_2, score_1, score_2, name_dict))
    table_data = (table, header_horizontal, header_vertical, [.45, .1, .45], ["LEFT", "CENTER", "RIGHT"], [top_line])

    make_pdf_from_tables(filename, [table_data])


def tournament_results_to_pdf(tournament: Tournament, sub_folder: str = "") -> None:
    if not make_new_folder(tournament, sub_folder):
        return
    if tournament.get_round() == 1:
        return
    round_name = MANAGER_TRANSLATION.tl(tournament.get_round_name(tournament.get_round() - 1))
    top_line = MANAGER_TRANSLATION.tl("Results of {}", insert=round_name)
    filename = get_path(sub_folder, tournament.get_name(), MANAGER_TRANSLATION.tl("Results"), f"{round_name}.pdf")
    name_dict = tournament.get_uuid_to_name_dict() | {"bye": "bye", "": ""}
    results = tournament.get_results()[-1]
    column_widths = [.45, .1, .45]
    aligns = ["LEFT", "CENTER", "RIGHT"]

    if tournament.is_team_tournament():
        tables_data: list[Table_Data] = []
        name_dict_individual = tournament.get_uuid_to_name_dict_individual() | {"bye": "bye", "": ""}
        results_individual = tournament.get_results_team()[-1]
        score_dict_game = tournament.get_score_dict_game()
        for ((item_1, _), (item_2, _)), individual in zip(results, results_individual):
            team_score_1 = sum(score_dict_game[score_1] for (_, score_1), _ in individual)
            team_score_2 = sum(score_dict_game[score_2] for _, (_, score_2) in individual)
            header_horizontal = get_result_row(item_1, item_2, str(team_score_1), str(team_score_2), name_dict)
            header_vertical = [str(i + 1) for i in range(len(individual))]
            top_lines = [top_line] if len(tables_data) == 0 else []
            table = [
                get_result_row(item_1, item_2, score_1, score_2, name_dict_individual)
                for (item_1, score_1), (item_2, score_2) in individual
            ]
            tables_data.append((table, header_horizontal, header_vertical, column_widths, aligns, top_lines))
    else:
        header_horizontal = ["", "", ""]
        header_vertical = [str(i + 1) for i in range(len(results))]
        table = [
            get_result_row(item_1, item_2, score_1, score_2, name_dict)
            for (item_1, score_1), (item_2, score_2) in results
        ]
        tables_data = [(table, header_horizontal, header_vertical, column_widths, aligns, [top_line])]

    make_pdf_from_tables(filename, tables_data, translate=not tournament.is_team_tournament())
