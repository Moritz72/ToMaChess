import os
import os.path
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.pdfbase.pdfmetrics import stringWidth
from .class_settings_handler import settings_handler
from .class_translation_handler import translation_handler
from .functions_categories import get_category_range_title

FONT = "Helvetica"
FONT_BOLD = "Helvetica-Bold"
FONT_SIZE = 12
PAGE_WIDTH, PAGE_HEIGHT = A4
LEFT_MARGIN, RIGHT_MARGIN, TOP_MARGIN, BOTTOM_MARGIN = 4 * (0.5 * inch,)
USABLE_WIDTH = PAGE_WIDTH - LEFT_MARGIN - RIGHT_MARGIN
USABLE_HEIGHT = PAGE_HEIGHT - TOP_MARGIN - BOTTOM_MARGIN
ROW_HEIGHT = 1.7 * FONT_SIZE
LINE_WIDTHS = (.5, 1.5, 2)


def get_path(*parts):
    return os.path.join(settings_handler.settings['pdf_path'], *parts)


def make_new_folder(tournament, sub_folder=""):
    if settings_handler.settings["pdf_path"] == "":
        return False
    folder_path = get_path(sub_folder)
    try:
        if sub_folder and not os.path.exists(folder_path):
            os.mkdir(folder_path)
        folder_path = os.path.join(folder_path, tournament.get_name())
        paths_parts = [
            (folder_path,), (folder_path, translation_handler.tl("Standings")),
            (folder_path, translation_handler.tl("Pairings")), (folder_path, translation_handler.tl("Results"))
        ]
        if "category_ranges" in tournament.get_parameters() and tournament.get_parameter("category_ranges"):
            name = f"{translation_handler.tl('Standings')} ({translation_handler.tl('Categories')})"
            paths_parts.append((folder_path, name))
        for parts in paths_parts:
            path = get_path(*parts)
            if not os.path.exists(path):
                os.mkdir(path)
    except:
        return False
    return True


def get_top_row_initial():
    return PAGE_HEIGHT - TOP_MARGIN - ROW_HEIGHT


def get_max_number_of_rows(top_row):
    return int(3 / 4 + (top_row - BOTTOM_MARGIN) / ROW_HEIGHT)


def draw_text_on_top(pdf, top_row, text_on_top):
    for i, text in enumerate(text_on_top):
        pdf.drawString(LEFT_MARGIN + FONT_SIZE / 2, top_row - i * ROW_HEIGHT, text)


def draw_text(pdf, value, x, y, column_width, align):
    if value is None:
        string = ""
    else:
        string = str(value)
    while stringWidth(string, FONT, FONT_SIZE) > column_width - FONT_SIZE / 2:
        string = string[:-1]
    if align == "CENTER":
        pdf.drawCentredString(x + column_width / 2, y, string)
    elif align == "RIGHT":
        pdf.drawRightString(x + column_width - FONT_SIZE / 2, y, string)
    elif align == "LEFT":
        pdf.drawString(x + FONT_SIZE / 2, y, string)


def get_vertical_header_width(vertical_header):
    if vertical_header is None:
        return 0
    max_header_len = max((len(header) for header in vertical_header))
    return FONT_SIZE * (max_header_len + .2)


def draw_header_backgrounds(pdf, top_row, horizontal_header, vertical_header, n):
    pdf.setFillColor(colors.lightgrey)
    top = top_row + 3 / 4 * ROW_HEIGHT
    if horizontal_header is not None:
        pdf.rect(LEFT_MARGIN, top, PAGE_WIDTH - RIGHT_MARGIN - LEFT_MARGIN, -ROW_HEIGHT, fill=True)
    if vertical_header is not None:
        bottom = top_row + (3 / 4 - n + 1) * ROW_HEIGHT
        width = get_vertical_header_width(vertical_header)
        pdf.rect(LEFT_MARGIN, top, width, bottom - top, fill=True)
    pdf.setFillColor(colors.black)


def draw_horizontal_lines(pdf, top_row, horizontal_header, n):
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


def draw_vertical_lines(pdf, top_row, vertical_header, column_widths, n):
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


def draw_horizontal_header(pdf, top_row, horizontal_header, column_widths, shift_x):
    pdf.setFont(FONT_BOLD, FONT_SIZE)
    x = LEFT_MARGIN + shift_x
    y = top_row
    for header, column_width in zip(horizontal_header, column_widths):
        draw_text(pdf, header, x, y, column_width, "CENTER")
        x += column_width


def draw_vertical_header(pdf, top_row, vertical_header, from_index, to_index, shift_y):
    pdf.setFont(FONT_BOLD, FONT_SIZE)
    x = LEFT_MARGIN
    y = top_row - shift_y
    width = get_vertical_header_width(vertical_header)
    for header in vertical_header[from_index:to_index]:
        draw_text(pdf, header, x, y, width, "CENTER")
        y -= ROW_HEIGHT


def draw_row(pdf, top_row, row, values, column_widths, aligns, shift_x, shift_y):
    pdf.setFont(FONT, FONT_SIZE)
    x = LEFT_MARGIN + shift_x
    y = top_row - row * ROW_HEIGHT - shift_y
    for value, column_width, align in zip(values, column_widths, aligns):
        draw_text(pdf, value, x, y, column_width, align)
        x += column_width


def add_table_to_pdf(
        pdf, top_row, table, horizontal_header=None, vertical_header=None, column_widths=None, aligns=None,
        text_on_top=[]
):
    if len(table) == 0 or len(table[0]) == 0:
        return top_row - 2 * ROW_HEIGHT

    if horizontal_header is not None:
        horizontal_header = translation_handler.tl_list(horizontal_header, short=True)
    if vertical_header is not None:
        vertical_header = translation_handler.tl_list(vertical_header, short=True)
    vertical_header_width = get_vertical_header_width(vertical_header)
    if column_widths is None:
        column_widths = len(table[0]) * ((USABLE_WIDTH - vertical_header_width) / len(table[0]))
    else:
        column_widths = tuple((USABLE_WIDTH - vertical_header_width) * width for width in column_widths)
    aligns = aligns or len(table[0]) * ("LEFT",)
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


def make_pdf_from_tables(filename, tables_data):
    pdf = canvas.Canvas(filename, pagesize=A4)
    top_row = get_top_row_initial()
    for table, horizontal_header, vertical_header, column_widths, aligns, text_on_top in tables_data:
        top_row = add_table_to_pdf(
            pdf, top_row, table, horizontal_header, vertical_header, column_widths, aligns, text_on_top
        )
        top_row -= 2 * ROW_HEIGHT
    pdf.save()


def tournament_participants_to_pdf(tournament, sub_folder=""):
    if not make_new_folder(tournament, sub_folder):
        return
    filename = get_path(sub_folder, tournament.get_name(), f"{translation_handler.tl('Participants')}.pdf")
    header_horizontal = ("Name", "Sex", "Birth", "Federation", "Title", "Rating")
    column_widths = (.6, .07, .08, .08, .08, .09)
    aligns = ["LEFT"] + 5 * ["CENTER"]

    if tournament.is_team_tournament():
        tables_data = tuple(
            (
                [player.get_data()[:6] for player in team.get_members()], header_horizontal,
                tuple(str(i + 1) for i in range(len(team.get_members()))), column_widths, aligns,
                [translation_handler.tl("Participants"), "", team.get_name()] if i == 0 else [team.get_name()]
            )
            for i, team in enumerate(tournament.get_participants())
        )
    else:
        header_vertical = tuple(str(i + 1) for i in range(len(tournament.get_participants())))
        table = [participant.get_data()[:6] for participant in tournament.get_participants()]
        tables_data = ((
            table, header_horizontal, header_vertical, column_widths, aligns, [translation_handler.tl("Participants")]
        ),)

    make_pdf_from_tables(filename, tables_data)


def tournament_standings_to_pdf(tournament, sub_folder=""):
    if not make_new_folder(tournament, sub_folder):
        return
    round_name = translation_handler.tl(tournament.get_round_name(tournament.get_round() - 1))
    top_line = translation_handler.tl("Standings after {}", insert=round_name)
    filename = get_path(sub_folder, tournament.get_name(), translation_handler.tl("Standings"), f"{round_name}.pdf")
    header_horizontal, header_vertical, table = tournament.get_standings()
    column_widths = [1 - .1 * (len(header_horizontal) - 1)] + (len(header_horizontal) - 1) * [.1]
    aligns = ["LEFT"] + (len(header_horizontal) - 1) * ["CENTER"]
    table_data = (table, header_horizontal, header_vertical, column_widths, aligns, [top_line])

    make_pdf_from_tables(filename, (table_data,))

    if "category_ranges" not in tournament.get_parameters() or not tournament.get_parameter("category_ranges"):
        return
    filename = get_path(
        sub_folder, tournament.get_name(),
        f"{translation_handler.tl('Standings')} ({translation_handler.tl('Categories')})", f"{round_name}.pdf"
    )
    tables_data = tuple(
        (
            tournament.get_standings(category_range)[2], header_horizontal, tournament.get_standings(category_range)[1],
            column_widths, aligns, [top_line + f" ({get_category_range_title(*category_range)})"]
        )
        for category_range in tournament.get_parameter("category_ranges")
    )

    make_pdf_from_tables(filename, tables_data)


def tournament_pairings_to_pdf(tournament, sub_folder=""):
    if not make_new_folder(tournament, sub_folder):
        return
    pairings = tournament.get_pairings()
    if pairings is None:
        return
    round_name = translation_handler.tl(tournament.get_round_name(tournament.get_round()))
    top_line = translation_handler.tl("Pairings for {}", insert=round_name)
    filename = get_path(sub_folder, tournament.get_name(), translation_handler.tl("Pairings"), f"{round_name}.pdf")
    uuid_to_participant_dict = tournament.get_uuid_to_participant_dict() | {None: "bye"}
    header_horizontal = ("", "", "")
    header_vertical = tuple(str(i + 1) for i in range(len(pairings)))
    table = [[uuid_to_participant_dict[uuid_1], ":", uuid_to_participant_dict[uuid_2]] for uuid_1, uuid_2 in pairings]
    table_data = (table, header_horizontal, header_vertical, (.45, .1, .45), ("LEFT", "CENTER", "RIGHT"), [top_line])

    make_pdf_from_tables(filename, (table_data,))


def tournament_results_to_pdf(tournament, sub_folder=""):
    if not make_new_folder(tournament, sub_folder):
        return
    if tournament.get_round() == 1:
        return
    round_name = translation_handler.tl(tournament.get_round_name(tournament.get_round() - 1))
    top_line = translation_handler.tl("Results of {}", insert=round_name)
    filename = get_path(sub_folder, tournament.get_name(), translation_handler.tl("Results"), f"{round_name}.pdf")
    uuid_to_participant_dict = tournament.get_uuid_to_participant_dict() | {None: "bye"}
    results = tournament.get_results()[-1]
    column_widths = (.45, .1, .45)
    aligns = ("LEFT", "CENTER", "RIGHT")

    if tournament.is_team_tournament():
        tables_data = []
        uuid_to_individual_dict = tournament.get_uuid_to_individual_dict() | {None: "bye"}
        results_individual = tournament.get_results_individual()[-1]
        score_dict_game = tournament.get_score_dict_game()
        for ((uuid_1, _), (uuid_2, _)), individual in zip(results, results_individual):
            team_score_1, team_score_2 = (
                sum(score_dict_game[score_1] for (_, score_1), _ in individual),
                sum(score_dict_game[score_2] for _, (_, score_2) in individual)
            )
            header_horizontal = (
                uuid_to_participant_dict[uuid_1], f"{team_score_1} : {team_score_2}", uuid_to_participant_dict[uuid_2]
            )
            header_vertical = tuple(str(i + 1) for i in range(len(individual)))
            table = [
                [uuid_to_individual_dict[uuid_1], f"{score_1} : {score_2}", uuid_to_individual_dict[uuid_2]]
                for (uuid_1, score_1), (uuid_2, score_2) in individual
            ]
            tables_data.append((
                table, header_horizontal, header_vertical, column_widths, aligns,
                [top_line] if len(tables_data) == 0 else []
            ))
    else:
        header_horizontal = ("", "", "")
        header_vertical = tuple(str(i + 1) for i in range(len(results)))
        table = [
            [uuid_to_participant_dict[uuid_1], f"{score_1} : {score_2}", uuid_to_participant_dict[uuid_2]]
            for (uuid_1, score_1), (uuid_2, score_2) in results
        ]
        tables_data = ((table, header_horizontal, header_vertical, column_widths, aligns, [top_line]),)

    make_pdf_from_tables(filename, tables_data)
