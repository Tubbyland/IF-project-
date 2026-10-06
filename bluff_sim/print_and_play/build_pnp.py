"""Build the print-and-play PDF from a rule file.

Every number on the cards, tracks, aids and in the rules text comes from the
rule file, so a rules change only needs a rebuild:

    cd bluff_sim
    python print_and_play/build_pnp.py --config configs/candidates/C.yaml \
        --version 1.0 --out print_and_play/rules_v1.0_print_and_play.pdf

Paper: A4. The card grid (3 x 3 cards of 63 x 88 mm) also fits US Letter
printed at 100%.
"""
from __future__ import annotations

import argparse
import io
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pypdf import PdfReader, PdfWriter  # noqa: E402
from reportlab.lib import colors  # noqa: E402
from reportlab.lib.enums import TA_CENTER  # noqa: E402
from reportlab.lib.pagesizes import A4, landscape  # noqa: E402
from reportlab.lib.styles import ParagraphStyle  # noqa: E402
from reportlab.lib.units import mm  # noqa: E402
from reportlab.pdfbase import pdfmetrics  # noqa: E402
from reportlab.pdfbase.ttfonts import TTFont  # noqa: E402
from reportlab.pdfgen import canvas  # noqa: E402
from reportlab.platypus import (KeepTogether, ListFlowable, ListItem,  # noqa: E402
                                PageBreak, Paragraph, SimpleDocTemplate,
                                Spacer, Table, TableStyle)

from bluffsim.config import GameConfig, load_config  # noqa: E402

FONT_DIR = "/usr/share/fonts/truetype/dejavu"
pdfmetrics.registerFont(TTFont("Sans", f"{FONT_DIR}/DejaVuSans.ttf"))
pdfmetrics.registerFont(TTFont("Sans-Bold", f"{FONT_DIR}/DejaVuSans-Bold.ttf"))
pdfmetrics.registerFontFamily("Sans", normal="Sans", bold="Sans-Bold")

INK = colors.HexColor("#1d1d1b")
QUIET = colors.HexColor("#5b5a56")
RULE = colors.HexColor("#c9c7c0")
CUT = colors.HexColor("#9a9893")
# One colour per deck, light enough to print well on any printer.
HAND = colors.HexColor("#3a6ea5")
PERSONAL = colors.HexColor("#2e8b57")
COLLECTIVE = colors.HexColor("#c0661c")
PLAYERS = [colors.HexColor(h) for h in
           ("#b23a48", "#3a6ea5", "#2e8b57", "#8a5a9e")]
PLAYER_NAMES = ["Red", "Blue", "Green", "Purple"]
SOLO_TINT = colors.HexColor("#dfeadf")
BUST_TINT = colors.HexColor("#f4dccb")

CARD_W, CARD_H = 63 * mm, 88 * mm
PAGE_W, PAGE_H = A4


def tint(c, amount):
    """Mix a colour with white: amount 0 = white, 1 = the colour."""
    return colors.Color(1 - (1 - c.red) * amount, 1 - (1 - c.green) * amount,
                        1 - (1 - c.blue) * amount)


# ---------------------------------------------------------------------------
# Rules (platypus)
# ---------------------------------------------------------------------------

def styles():
    base = dict(fontName="Sans", textColor=INK, leading=13.5, fontSize=9.6)
    return {
        "title": ParagraphStyle("title", fontName="Sans-Bold", fontSize=22,
                                leading=27, textColor=INK, spaceAfter=4),
        "subtitle": ParagraphStyle("subtitle", fontName="Sans", fontSize=11,
                                   leading=15, textColor=QUIET,
                                   spaceAfter=14),
        "h2": ParagraphStyle("h2", fontName="Sans-Bold", fontSize=13,
                             leading=17, textColor=INK, spaceBefore=12,
                             spaceAfter=5),
        "h3": ParagraphStyle("h3", fontName="Sans-Bold", fontSize=10.5,
                             leading=14, textColor=INK, spaceBefore=6,
                             spaceAfter=3),
        "body": ParagraphStyle("body", spaceAfter=5, **base),
        "cell": ParagraphStyle("cell", fontName="Sans", fontSize=8.8,
                               leading=11.5, textColor=INK),
        "cellb": ParagraphStyle("cellb", fontName="Sans-Bold", fontSize=8.8,
                                leading=11.5, textColor=INK),
        "small": ParagraphStyle("small", fontName="Sans", fontSize=8.4,
                                leading=11, textColor=QUIET),
    }


def bullets(items, st, numbered=False):
    return ListFlowable(
        [ListItem(Paragraph(t, st["body"]), leftIndent=14) for t in items],
        bulletType="1" if numbered else "bullet", start="1" if numbered
        else None, leftIndent=14, bulletFontName="Sans", bulletFontSize=9,
        bulletColor=INK)


def table(rows, st, widths, header=True):
    data = [[Paragraph(c, st["cellb"] if (header and i == 0) else st["cell"])
             for c in row] for i, row in enumerate(rows)]
    t = Table(data, colWidths=widths, repeatRows=1 if header else 0)
    t.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LINEBELOW", (0, 0), (-1, -1), 0.4, RULE),
        ("LINEBELOW", (0, 0), (-1, 0), 0.8, INK) if header else
        ("LINEBELOW", (0, 0), (-1, 0), 0.4, RULE),
        ("TOPPADDING", (0, 0), (-1, -1), 3.5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3.5),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
    ]))
    return t


def rules_pdf(cfg: GameConfig, version: str) -> bytes:
    st = styles()
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, leftMargin=20 * mm,
                            rightMargin=20 * mm, topMargin=18 * mm,
                            bottomMargin=18 * mm,
                            title=f"Rules v{version} print and play",
                            author="")
    n_hand = len(cfg.hand_deck())
    n_pers = len(cfg.personal_deck())
    n_coll = len(cfg.collective_deck())
    lo_c, hi_c = cfg.collective_continuous
    bust_at = cfg.bust_limit + 1
    W = cfg.win_threshold
    tw = PAGE_W - 40 * mm
    s = []

    # --- Cover and assembly ------------------------------------------------
    s += [Paragraph(f"Rules v{version}", st["title"]),
          Paragraph("A semi-cooperative bluffing card game for 4 players · "
                    "print and play", st["subtitle"])]
    s.append(Paragraph(
        f"Four players play {cfg.rounds} rounds of cards against hidden "
        "targets. The game ends one of three ways: one player wins alone, "
        "the player closest to zero wins when the group fails, or everyone "
        "wins together.", st["body"]))
    s.append(Paragraph("What to print", st["h2"]))
    s.append(table([
        ["Section", "Pages", "Notes"],
        ["Rules and player aids", "this section", "Print once. Cut the 4 "
         "player aids apart."],
        ["Track board", "1 (landscape)", f"4 Drift Tracks and the Group "
         f"Tally. Shaded zones: solo win at {W}+, bust at {bust_at}+."],
        ["Hand cards", f"{-(-n_hand // 9)}", f"{n_hand} cards: "
         f"{cfg.hand_lo} to {cfg.hand_hi}, "
         f"{cfg.effective_hand_copies()} of each."],
        ["Personal Target cards", f"{-(-n_pers // 9)}", f"{n_pers} cards: "
         f"{cfg.personal_lo} to {cfg.personal_hi}, "
         f"{cfg.effective_personal_copies()} of each."],
        ["Collective Target cards", f"{-(-n_coll // 9)}", f"{n_coll} cards: "
         f"{lo_c} to {hi_c}, one of each."],
        ["Clue cards (optional)", "3", "5 per player in 4 colours, plus a "
         "first-player card."],
        ["Card backs (optional)", "4", "One page per deck, for double-sided "
         "printing."],
    ], st, [42 * mm, 26 * mm, tw - 68 * mm]))
    s.append(Paragraph("Assembly", st["h2"]))
    s.append(bullets([
        "Print at <b>100% / actual size</b>, not \"fit to page\". Cards are "
        "63 × 88 mm, a standard playing-card size.",
        "Cut along the thin grey lines. The short marks in the margins line "
        "up with every cut.",
        "Card backs: either print each deck's back page on the reverse of "
        "its front pages (double-sided, flip on the long edge), or put each "
        "card in a sleeve with an old playing card behind it.",
        "You also need <b>5 small markers</b> (coins, cubes or paper clips): "
        "one per player for their Drift Track and one for the Group Tally.",
        "Clue cards are optional. Placed face up beside your pocket, they "
        "keep everyone's claim on the table until the reveal, so it is easy "
        "to see who lied.",
    ], st))
    s.append(PageBreak())

    # --- Rules ---------------------------------------------------------------
    s.append(Paragraph("Rules", st["title"]))
    s.append(Paragraph("Goal", st["h2"]))
    s.append(Paragraph(
        "Each round, every player has a private aim (their <b>Personal "
        "Target</b>) and the table shares one (the <b>Collective Target</b>). "
        "Players lay cards face down, describe their total with a clue that "
        "may be a lie, and can veto each other. When the cards are revealed, "
        "how far each player missed their own target moves them along their "
        "<b>Drift Track</b>, and how far the table missed the shared target "
        "moves the <b>Group Tally</b>.", st["body"]))
    s.append(bullets([
        f"<b>Solo win:</b> push your own track {W} or more away from zero.",
        f"<b>Bust win:</b> if the Group Tally goes more than "
        f"{cfg.bust_limit} from zero, the group loses and the player closest "
        "to zero wins.",
        f"<b>Shared win:</b> survive all {cfg.rounds} rounds without either "
        "happening, and everyone wins.",
    ], st))

    s.append(Paragraph("Setup", st["h2"]))
    s.append(bullets([
        "Shuffle the Hand, Personal Target and Collective Target decks "
        "separately and place them face down. No deck is ever reshuffled.",
        f"Deal {cfg.hand_size} hand cards to each player. Hands are hidden; "
        "the number of cards each player holds is public.",
        "Put every Drift Track marker and the Group Tally marker on 0.",
        "Choose a first player and give them the first-player card. It moves "
        "one seat to the left each round.",
    ], st, numbered=True))

    s.append(Paragraph("Each round", st["h2"]))
    s.append(Paragraph(
        f"The game lasts {cfg.rounds} rounds. Each round has five steps; "
        "after every round, check the end of the game.", st["body"]))
    clue_rows = [
        ["Clue", "Pocket total compared with your Personal Target"],
        ["Much lower", f"{cfg.clue_much} or more below"],
        ["Lower", f"{cfg.clue_close + 1} to {cfg.clue_much - 1} below"],
        ["Close", f"within {cfg.clue_close} either way"],
        ["Higher", f"{cfg.clue_close + 1} to {cfg.clue_much - 1} above"],
        ["Much higher", f"{cfg.clue_much} or more above"],
    ]
    steps = [
        ("1. Reveal targets.", "Each player draws a Personal Target face up. "
         "Draw one Collective Target face up. The <b>gap</b> is the "
         "Collective Target minus the sum of the four Personal Targets: how "
         "far the table must drift together."),
        ("2. Play and clue.", f"In turn order, starting with the first "
         f"player, each player places <b>{cfg.min_cards} to "
         f"{cfg.max_cards} cards</b> face down as their pocket, then gives "
         "one clue about their pocket total. Clues may be true or false."),
    ]
    for head, text in steps:
        s.append(Paragraph(f"<b>{head}</b> {text}", st["body"]))
    s.append(table(clue_rows, st, [32 * mm, tw - 32 * mm]))
    s.append(Spacer(1, 6))
    more = [
        ("3. Veto.", f"The <b>leader</b> is the player furthest from zero; "
         "everyone tied for furthest is a leader. A player is <b>eligible</b> "
         f"if they are not a leader and are at least <b>{cfg.veto_gap}</b> "
         "closer to zero than the leader. All eligible players declare at "
         "once (for example, point on a count of three; a fist means pass): "
         "each vetoes one other player or passes."),
        ("4. Reveal and resolve.", "Reveal every pocket. Each player's "
         "<b>drift</b> is their pocket total minus their Personal Target, "
         "with its sign."),
    ]
    head, text = more[0]
    s.append(Paragraph(f"<b>{head}</b> {text}", st["body"]))
    head, text = more[1]
    step4 = [Paragraph(f"<b>{head}</b> {text}", st["body"])]
    s.append(KeepTogether(step4 + [bullets([
        "<b>Not vetoed:</b> move your own marker by your drift.",
        "<b>Vetoed once or more:</b> your drift does not move your marker. "
        "Instead, <b>each</b> player who vetoed you moves their own marker "
        "by your full drift.",
        f"<b>Vetoed {cfg.double_veto_at} or more times:</b> in addition, "
        "your contribution to the group counts as exactly your Personal "
        "Target.",
        f"<b>Final round (round {cfg.rounds}):</b> all drift on tracks counts "
        "double, including drift taken by a veto.",
        "<b>Group Tally:</b> move it by the sum of all contributions minus "
        "the Collective Target. A contribution is the pocket total, except "
        "under a double veto.",
    ], st)]))
    s.append(Paragraph(
        f"<b>5. Cleanup.</b> Revealed pocket cards go to the discard pile, "
        f"face up and sorted by value. Each player draws "
        f"<b>{cfg.draw_per_round}</b> card.", st["body"]))

    s.append(Paragraph("End of the game", st["h2"]))
    s.append(Paragraph("After each round, check these in order; the first "
                       "that applies ends the game.", st["body"]))
    s.append(bullets([
        f"<b>Bust.</b> If the Group Tally is {bust_at} or more away from "
        "zero, the group has failed. The player closest to zero wins; ties "
        "share the win. A bust overrides a solo win in the same round.",
        f"<b>Solo win.</b> If any track is {W} or more away from zero, the "
        "player furthest from zero wins; ties share the win.",
        f"<b>Shared win.</b> If round {cfg.rounds} ends with neither, all "
        "players win together.",
    ], st, numbered=True))

    rulings = [
        ["Situation", "Ruling"],
        [f"A track passes {W}", "It keeps counting; tracks have no cap. "
         "Note the number if it runs off the board."],
        ["Several players tie for furthest from zero", "All are leaders and "
         "none may veto. In round 1 everyone is at 0, so nobody can veto."],
        ["When eligibility is checked", "On the tracks at the start of the "
         "veto step."],
        ["A vetoes B while B vetoes C", "A takes only B's own drift, never "
         "what B took from C."],
        ["Vetoed exactly once", "The contribution is still the real pocket "
         "total."],
        ["Final-round doubling", "Tracks only. The Group Tally is never "
         "doubled."],
        [f"Group Tally at exactly {cfg.bust_limit} or −{cfg.bust_limit}",
         "Not a bust; play on."],
        ["Lying", "Any clue may be false. There is no penalty except what "
         "the others remember."],
    ]
    s.append(KeepTogether([Paragraph("Rulings", st["h2"]),
                           table(rulings, st, [62 * mm, tw - 62 * mm])]))
    s.append(Spacer(1, 10))
    s.append(Paragraph(f"Rules version {version}. Rule file: "
                       "bluff_sim/configs/candidates/C.yaml.", st["small"]))
    s.append(PageBreak())
    s.append(Spacer(1, 1))   # page for the player aids (drawn by canvas)

    doc.build(s)
    return buf.getvalue()


# ---------------------------------------------------------------------------
# Canvas pages
# ---------------------------------------------------------------------------

def crop_marks(c, x0, y0, cols, rows, w, h, page_w, page_h):
    """Thin cut lines between cards and short marks in the margins."""
    c.setStrokeColor(CUT)
    c.setLineWidth(0.3)
    xs = [x0 + i * w for i in range(cols + 1)]
    ys = [y0 + j * h for j in range(rows + 1)]
    for x in xs:
        c.line(x, y0 - 6 * mm, x, y0 - 1.5 * mm)
        c.line(x, ys[-1] + 1.5 * mm, x, ys[-1] + 6 * mm)
    for y in ys:
        c.line(x0 - 6 * mm, y, x0 - 1.5 * mm, y)
        c.line(xs[-1] + 1.5 * mm, y, xs[-1] + 6 * mm, y)
    c.setStrokeColor(RULE)
    c.setLineWidth(0.25)
    for x in xs:
        c.line(x, y0, x, ys[-1])
    for y in ys:
        c.line(x0, y, xs[-1], y)


def footer(c, text, page_w):
    c.setFont("Sans", 7)
    c.setFillColor(QUIET)
    c.drawCentredString(page_w / 2, 7 * mm, text)


def player_aids(c, cfg: GameConfig, version: str):
    """Four A6 player aids on one A4 page."""
    w, h = PAGE_W / 2, PAGE_H / 2
    bust_at = cfg.bust_limit + 1
    for k in range(4):
        x0 = (k % 2) * w
        y0 = PAGE_H - (k // 2 + 1) * h
        col = PLAYERS[k]
        pad = 9 * mm
        c.setFillColor(tint(col, 0.15))
        c.rect(x0 + pad - 3 * mm, y0 + h - pad - 9 * mm, w - 2 * pad + 6 * mm,
               9 * mm, fill=1, stroke=0)
        c.setFillColor(INK)
        c.setFont("Sans-Bold", 11)
        c.drawString(x0 + pad, y0 + h - pad - 6.2 * mm,
                     f"Player aid · {PLAYER_NAMES[k]}")
        y = y0 + h - pad - 16 * mm
        lines = [
            ("b", "Each round"),
            ("", "1  Draw targets. Gap = collective − sum of personals."),
            ("", f"2  Play {cfg.min_cards}–{cfg.max_cards} cards face down, "
                 "then give a clue."),
            ("", f"3  Veto: if ≥ {cfg.veto_gap} closer to zero than the"),
            ("", "    leader, veto one player or pass (all at once)."),
            ("", "4  Drift = pocket − personal target."),
            ("", "    Vetoed: each vetoer takes your drift."),
            ("", f"    Vetoed {cfg.double_veto_at}+: your contribution = "
                 "your target."),
            ("", f"    Round {cfg.rounds}: track moves ×"
                 f"{cfg.final_multiplier}."),
            ("", "    Tally += contributions − collective."),
            ("", f"5  Discard pockets, draw {cfg.draw_per_round}."),
            ("gap", ""),
            ("b", "Clues (pocket vs your target)"),
            ("", f"Close: within {cfg.clue_close}"),
            ("", f"Lower / Higher: {cfg.clue_close + 1}–"
                 f"{cfg.clue_much - 1} away"),
            ("", f"Much lower / higher: {cfg.clue_much}+ away"),
            ("gap", ""),
            ("b", "Game ends, checked in this order"),
            ("", f"Bust: tally {bust_at}+ from 0 → closest to 0 wins"),
            ("", f"Solo: a track {cfg.win_threshold}+ from 0 → furthest "
                 "wins"),
            ("", f"End of round {cfg.rounds}: everyone wins"),
        ]
        for kind, text in lines:
            if kind == "gap":
                y -= 2.5 * mm
                continue
            c.setFont("Sans-Bold" if kind == "b" else "Sans",
                      9 if kind == "b" else 8.2)
            c.setFillColor(INK)
            c.drawString(x0 + pad, y, text)
            y -= 4.6 * mm
        c.setFont("Sans", 6.5)
        c.setFillColor(QUIET)
        c.drawString(x0 + pad, y0 + 6 * mm, f"Rules v{version}")
    c.setStrokeColor(CUT)
    c.setLineWidth(0.3)
    c.setDash(3, 3)
    c.line(PAGE_W / 2, 0, PAGE_W / 2, PAGE_H)
    c.line(0, PAGE_H / 2, PAGE_W, PAGE_H / 2)
    c.setDash()
    c.showPage()


def track_board(c, cfg: GameConfig, version: str):
    """Landscape page: 4 Drift Tracks and the Group Tally, each in two rows
    (0 to +25 above, 0 to -25 below) so cells are big enough for a marker."""
    pw, ph = landscape(A4)
    c.setPageSize((pw, ph))
    span = 25
    cell = 9.4 * mm
    row_h = 12 * mm
    label_w = 31 * mm
    x0 = (pw - label_w - (span + 1) * cell) / 2 + label_w
    W, bust_at = cfg.win_threshold, cfg.bust_limit + 1
    c.setFont("Sans-Bold", 13)
    c.setFillColor(INK)
    c.drawString(x0 - label_w, ph - 14 * mm, "Track board")
    c.setFont("Sans", 8)
    c.setFillColor(QUIET)
    c.drawString(x0 - label_w + 34 * mm, ph - 14 * mm,
                 f"Green cells: solo win at {W} or more from zero.  "
                 f"Orange cells: bust at {bust_at} or more from zero.  "
                 "Past 25? Note the number.")
    tracks = [(PLAYER_NAMES[i], PLAYERS[i], "solo") for i in range(4)]
    tracks.append(("Group Tally", INK, "bust"))
    band = 2 * row_h + 9 * mm
    top = ph - 24 * mm
    for k, (name, col, kind) in enumerate(tracks):
        yt = top - k * band - row_h          # upper row (positive)
        yb = yt - row_h                      # lower row (negative)
        c.setFillColor(tint(col, 0.18) if kind == "solo"
                       else tint(INK, 0.08))
        c.roundRect(x0 - label_w, yb, label_w - 3 * mm, 2 * row_h, 2 * mm,
                    fill=1, stroke=0)
        c.setFillColor(INK)
        c.setFont("Sans-Bold", 10)
        c.drawString(x0 - label_w + 3 * mm, yb + row_h + 1.5 * mm, name)
        c.setFont("Sans", 7)
        c.setFillColor(QUIET)
        c.drawString(x0 - label_w + 3 * mm, yb + row_h - 4 * mm,
                     "Drift Track" if kind == "solo" else "shared")
        for row, sign in ((yt, 1), (yb, -1)):
            for v in range(span + 1):
                x = x0 + v * cell
                if v == 0 and sign < 0:
                    continue                 # zero is drawn once, spanning
                hot = (v >= W) if kind == "solo" else (v >= bust_at)
                fill = (SOLO_TINT if kind == "solo" else BUST_TINT) \
                    if hot else colors.white
                c.setFillColor(fill)
                c.setStrokeColor(RULE)
                c.setLineWidth(0.5)
                if v == 0:
                    c.rect(x, yb, cell, 2 * row_h, fill=1, stroke=1)
                    c.setFillColor(INK)
                    c.setFont("Sans-Bold", 10)
                    c.drawCentredString(x + cell / 2, yb + row_h - 1.3 * mm,
                                        "0")
                    continue
                c.rect(x, row, cell, row_h, fill=1, stroke=1)
                c.setFillColor(INK if hot else QUIET)
                c.setFont("Sans-Bold" if v % 5 == 0 else "Sans",
                          8 if v % 5 == 0 else 7)
                label = f"+{v}" if sign > 0 else f"−{v}"
                c.drawCentredString(x + cell / 2, row + row_h / 2 - 1 * mm,
                                    label)
    footer(c, f"Rules v{version} · print at 100% (A4 landscape)", pw)
    c.showPage()
    c.setPageSize(A4)


def card_grid_origin():
    return ((PAGE_W - 3 * CARD_W) / 2, (PAGE_H - 3 * CARD_H) / 2)


def number(c, x, y, value, font, size, centred=False):
    """Draw a number; underline 6 and 9 so they read the same either way
    up."""
    text = str(value)
    c.setFont(font, size)
    w = pdfmetrics.stringWidth(text, font, size)
    left = x - w / 2 if centred else x
    c.drawString(left, y, text)
    if value in (6, 9):
        c.saveState()
        c.setLineWidth(max(0.6, size / 14))
        c.setStrokeColor(c._fillColorObj)
        c.line(left, y - size * 0.14, left + w, y - size * 0.14)
        c.restoreState()


def draw_number_card(c, x, y, value, title, col, sub=""):
    """Big number, corner indices, a coloured band naming the deck."""
    c.saveState()
    c.setFillColor(colors.white)
    c.rect(x, y, CARD_W, CARD_H, fill=1, stroke=0)
    inset = 3.2 * mm
    c.setStrokeColor(col)
    c.setLineWidth(1.1)
    c.roundRect(x + inset, y + inset, CARD_W - 2 * inset,
                CARD_H - 2 * inset, 3 * mm, fill=0, stroke=1)
    band_h = 8.5 * mm
    c.setFillColor(tint(col, 0.9))
    c.roundRect(x + inset, y + CARD_H - inset - band_h, CARD_W - 2 * inset,
                band_h, 3 * mm, fill=1, stroke=0)
    c.rect(x + inset, y + CARD_H - inset - band_h, CARD_W - 2 * inset,
           band_h / 2, fill=1, stroke=0)
    c.setFillColor(colors.white)
    c.setFont("Sans-Bold", 7.5)
    c.drawCentredString(x + CARD_W / 2, y + CARD_H - inset - band_h + 3 * mm,
                        title.upper())
    c.setFillColor(INK)
    number(c, x + CARD_W / 2, y + CARD_H / 2 - 9 * mm, value, "Sans-Bold",
           40 if value < 100 else 34, centred=True)
    if sub:
        c.setFont("Sans", 7)
        c.setFillColor(QUIET)
        c.drawCentredString(x + CARD_W / 2, y + 12 * mm, sub)
    c.setFillColor(col)
    number(c, x + inset + 2.2 * mm, y + CARD_H - inset - band_h - 5.5 * mm,
           value, "Sans-Bold", 10)
    c.translate(x + CARD_W - inset - 2.2 * mm, y + inset + 5.5 * mm)
    c.rotate(180)
    number(c, 0, 0, value, "Sans-Bold", 10)
    c.restoreState()


def draw_clue_card(c, x, y, clue, rng, player):
    col = PLAYERS[player]
    c.saveState()
    inset = 3.2 * mm
    c.setFillColor(tint(col, 0.12))
    c.roundRect(x + inset, y + inset, CARD_W - 2 * inset,
                CARD_H - 2 * inset, 3 * mm, fill=1, stroke=0)
    c.setStrokeColor(col)
    c.setLineWidth(1.1)
    c.roundRect(x + inset, y + inset, CARD_W - 2 * inset,
                CARD_H - 2 * inset, 3 * mm, fill=0, stroke=1)
    arrows = {"Much lower": "↓↓", "Lower": "↓", "Close": "=",
              "Higher": "↑", "Much higher": "↑↑"}[clue]
    c.setFillColor(col)
    c.setFont("Sans-Bold", 34)
    c.drawCentredString(x + CARD_W / 2, y + CARD_H / 2 + 4 * mm, arrows)
    c.setFillColor(INK)
    c.setFont("Sans-Bold", 13)
    c.drawCentredString(x + CARD_W / 2, y + CARD_H / 2 - 9 * mm,
                        clue.upper())
    c.setFont("Sans", 7.5)
    c.setFillColor(QUIET)
    c.drawCentredString(x + CARD_W / 2, y + CARD_H / 2 - 15 * mm, rng)
    c.setFont("Sans", 7)
    c.drawCentredString(x + CARD_W / 2, y + 9 * mm,
                        f"Clue · {PLAYER_NAMES[player]}")
    c.restoreState()


def draw_first_player(c, x, y):
    c.saveState()
    inset = 3.2 * mm
    c.setStrokeColor(INK)
    c.setLineWidth(1.1)
    c.roundRect(x + inset, y + inset, CARD_W - 2 * inset,
                CARD_H - 2 * inset, 3 * mm, fill=0, stroke=1)
    c.setFillColor(INK)
    c.setFont("Sans-Bold", 14)
    c.drawCentredString(x + CARD_W / 2, y + CARD_H / 2 + 2 * mm, "FIRST")
    c.drawCentredString(x + CARD_W / 2, y + CARD_H / 2 - 5 * mm, "PLAYER")
    c.setFont("Sans", 7)
    c.setFillColor(QUIET)
    c.drawCentredString(x + CARD_W / 2, y + 12 * mm,
                        "Passes one seat left each round")
    c.restoreState()


def card_pages(c, draws, label, version):
    """draws: list of callables f(c, x, y), 9 per page."""
    x0, y0 = card_grid_origin()
    for p in range(0, len(draws), 9):
        chunk = draws[p:p + 9]
        for i, f in enumerate(chunk):
            col, row = i % 3, 2 - i // 3
            f(c, x0 + col * CARD_W, y0 + row * CARD_H)
        crop_marks(c, x0, y0, 3, 3, CARD_W, CARD_H, PAGE_W, PAGE_H)
        footer(c, f"{label} · page {p // 9 + 1} of {-(-len(draws) // 9)} · "
                  f"Rules v{version} · print at 100%", PAGE_W)
        c.showPage()


def back_page(c, title, col, version):
    x0, y0 = card_grid_origin()
    for i in range(9):
        x, y = x0 + (i % 3) * CARD_W, y0 + (2 - i // 3) * CARD_H
        inset = 3.2 * mm
        c.setFillColor(tint(col, 0.85))
        c.roundRect(x + inset, y + inset, CARD_W - 2 * inset,
                    CARD_H - 2 * inset, 3 * mm, fill=1, stroke=0)
        c.setStrokeColor(colors.white)
        c.setLineWidth(1.2)
        c.roundRect(x + 6 * mm, y + 6 * mm, CARD_W - 12 * mm,
                    CARD_H - 12 * mm, 2.5 * mm, fill=0, stroke=1)
        c.setFillColor(colors.white)
        c.setFont("Sans-Bold", 11)
        for k, word in enumerate(title.upper().split()):
            c.drawCentredString(x + CARD_W / 2,
                                y + CARD_H / 2 + (len(title.split()) / 2
                                                  - k - 0.7) * 5 * mm, word)
    crop_marks(c, x0, y0, 3, 3, CARD_W, CARD_H, PAGE_W, PAGE_H)
    footer(c, f"Back: {title} · print on the reverse of its fronts "
              f"(flip on long edge) · Rules v{version}", PAGE_W)
    c.showPage()


def components_pdf(cfg: GameConfig, version: str) -> bytes:
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    c.setTitle(f"Rules v{version} print and play")
    player_aids(c, cfg, version)
    track_board(c, cfg, version)

    hand = sorted(cfg.hand_deck())
    card_pages(c, [lambda c, x, y, v=v: draw_number_card(
        c, x, y, v, "Hand", HAND) for v in hand], "Hand cards", version)
    pers = sorted(cfg.personal_deck())
    card_pages(c, [lambda c, x, y, v=v: draw_number_card(
        c, x, y, v, "Personal Target", PERSONAL, "your aim this round")
        for v in pers], "Personal Target cards", version)
    coll = sorted(cfg.collective_deck())
    card_pages(c, [lambda c, x, y, v=v: draw_number_card(
        c, x, y, v, "Collective Target", COLLECTIVE, "the table's aim")
        for v in coll], "Collective Target cards", version)

    lo, mid = cfg.clue_close, cfg.clue_much
    clues = [("Much lower", f"{mid} or more below target"),
             ("Lower", f"{lo + 1} to {mid - 1} below target"),
             ("Close", f"within {lo} of target"),
             ("Higher", f"{lo + 1} to {mid - 1} above target"),
             ("Much higher", f"{mid} or more above target")]
    clue_draws = [lambda c, x, y, n=n, r=r, p=p: draw_clue_card(c, x, y, n, r,
                                                                p)
                  for p in range(4) for n, r in clues]
    clue_draws.append(lambda c, x, y: draw_first_player(c, x, y))
    card_pages(c, clue_draws, "Clue cards and first-player card", version)

    for title, col in (("Hand", HAND), ("Personal Target", PERSONAL),
                       ("Collective Target", COLLECTIVE), ("Clue", QUIET)):
        back_page(c, title, col, version)
    c.save()
    return buf.getvalue()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="configs/candidates/C.yaml")
    ap.add_argument("--version", default="1.0")
    ap.add_argument("--out",
                    default="print_and_play/rules_v1.0_print_and_play.pdf")
    args = ap.parse_args()
    cfg = load_config(args.config)
    if cfg.n_players != 4:
        sys.exit("the player aids and track board are drawn for 4 players")
    writer = PdfWriter()
    rules = PdfReader(io.BytesIO(rules_pdf(cfg, args.version)))
    comps = PdfReader(io.BytesIO(components_pdf(cfg, args.version)))
    # The rules end with a blank page reserved for the player aids; replace
    # it with the canvas-drawn aids page.
    for page in rules.pages[:-1]:
        writer.add_page(page)
    for page in comps.pages:
        writer.add_page(page)
    writer.add_metadata({"/Title": f"Rules v{args.version} print and play"})
    with open(args.out, "wb") as f:
        writer.write(f)
    print(f"{args.out}: {len(writer.pages)} pages")


if __name__ == "__main__":
    main()
