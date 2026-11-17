#!/usr/bin/env python3
"""board_svg.py: draws the workshop board as an SVG document for Miro's canvas tools.

Two uses:
  board_svg.py template [--row design|diagnosis|both] [--lang en|es|both]   an empty template board
  board_svg.py from-log <log.json> [--lang en|es|both] [--color blue|purple|orange] [--x N --y N] [--title "..."]
                                                                            a board filled from a decision log

The output goes to stdout. Send it with the Miro connector's create call, on a board of your own.
Every frame carries its number, its title, its status stamp, the question for the person and one
labeled box per field of TEMPLATE.md. Text is XML-escaped here, so a stray "&" cannot break the call.

Standard library only. Python 3.9+.
"""
import argparse
import json
import math
import sys
from xml.sax.saxutils import escape

# (id, EN title, ES title, EN question, ES question, [(field, EN label, ES label)])
DESIGN = [
    ("0", "Start here", "Empezá acá", "", "", [
        ("decision", "What we are deciding", "Qué se decide"),
        ("how_to_read", "How to read this board", "Cómo se lee este tablero"),
        ("asks_table", "What the AI drafted, and what it asks you", "Qué escribió la IA y qué te pregunta"),
    ]),
    ("1", "Goal", "Objetivo", "Is this the goal, or is there one above it?", "¿Es este el objetivo o hay uno más arriba?", [
        ("business_goal", "Business goal", "Objetivo de negocio"),
        ("user_problem", "The problem it solves for the user", "Qué problema le resuelve al usuario"),
        ("metric", "How the business keeps score", "Métrica del negocio"),
        ("why_now", "Why now", "Por qué ahora"),
        ("brief_and_givens", "The brief and what is fixed", "Consigna y lo que viene fijo"),
    ]),
    ("2", "Customer", "El cliente", "Why this one and not the other?", "¿Por qué este y no el otro?", [
        ("segments", "Segments: who pays, uses or lives with it", "Segmentos: ¿paga, usa o convive?"),
        ("chosen", "The one we pick", "El elegido"),
        ("chosen_why", "Why, with a sized assumption or a source", "Por qué, con un número de supuesto o una fuente"),
    ]),
    ("3", "Their moment", "Su momento y para qué lo usa", "Is this scene real?", "¿La escena es real?", [
        ("persona", "A person with a name", "Una persona con nombre"),
        ("moment", "When, and what is happening", "Cuándo y qué le pasa"),
        ("deeper_want", "What they want underneath", "Lo que quiere de fondo"),
        ("use_cases", "Use cases, one marked as the priority", "Casos de uso, uno marcado"),
    ]),
    ("4", "Where it fails today", "Dónde falla hoy", "These, or is one missing?", "¿Estas o falta una?", [
        ("failures", "Weak point, cause, and how they solve it today", "Punto débil, causa y cómo lo resuelve hoy"),
        ("ranking_criterion", "The criterion, said before ranking", "El criterio, dicho antes de ordenar"),
        ("top", "The top ones", "Las primeras"),
    ]),
    ("5", "Ideas", "Ideas", "Which one would you add?", "¿Cuál agregarías?", [
        ("ideas", "Small, habit-changing and bold, each tied to a failure", "Chica, que cambia un hábito y ambiciosa; cada una ataca una falla"),
        ("scoring", "Optional scoring, 1 to 5", "Puntaje del 1 al 5, opcional"),
    ]),
    ("6", "Choose, hypothesis and metrics", "Elegir, hipótesis y métricas",
     "Is it the one that moves the goal most, and is this how we would know?",
     "¿Es la que más mueve el objetivo, y es así como lo sabríamos?", [
        ("chosen_idea+why_vs_goal", "The pick, against the goal", "La elegida, contra el objetivo"),
        ("hypothesis", "Hypothesis: statement, baseline, target, timeframe", "Hipótesis: la frase, base, meta y plazo"),
        ("metrics", "Metrics: north star, primary, secondary, guardrails", "Métricas: norte, primaria, secundarias, lo que no se puede romper"),
        ("cheap_test", "How I test it cheaply", "Cómo lo pruebo barato"),
        ("weak_spot", "What is weak about it", "Qué tiene de flojo"),
    ]),
    ("7", "Growth and vision", "Crecer y visión", "What is left out?", "¿Qué queda afuera?", [
        ("growth", "How it brings more users", "Cómo trae más usuarios"),
        ("phases", "Phases", "Fases"),
        ("company_strategy_fit", "How it fits the company's strategy", "Cómo encaja en la estrategia de la empresa"),
        ("dilemma_principle", "The principle that settles trade-offs", "El principio que decide los dilemas"),
        ("one_sentence_summary", "The whole case in one sentence", "Resumen en una frase"),
    ]),
    ("A", "Assumptions", "Franja de supuestos", "Which one worries you most?", "¿Cuál te preocupa más?", [
        ("assumptions", "Everything we do not know, in sight", "Todo lo que no se sabe, a la vista"),
        ("most_worrying", "The one that worries most", "El que más preocupa"),
    ]),
    ("E", "Evidence", "Evidencia", "", "", [
        ("items", "Screenshots, quotes and numbers, each with its source", "Capturas, citas y números, cada uno con su fuente"),
    ]),
]
DIAGNOSIS = [
    ("D1", "Isolate", "Aislar", "Is this the branch, or is it upstream?", "¿Es esta la rama o viene de más arriba?", [
        ("metric", "The metric that moved", "La métrica que se movió"),
        ("tree", "The metric tree", "El árbol de la métrica"),
        ("branch_that_moved", "The branch that moved", "La rama que se movió"),
    ]),
    ("D2", "Diagnose", "Diagnosticar", "Which cut would you add before believing this?", "¿Qué corte sumarías antes de creerlo?", [
        ("cuts", "Cuts, each with what it showed", "Cortes, cada uno con lo que mostró"),
        ("cause_hypothesis", "Our hypothesis of the cause", "La hipótesis de la causa"),
    ]),
    ("D3", "Resolve", "Resolver", "Does this fix the cause or the symptom?", "¿Arregla la causa o el síntoma?", [
        ("goal", "The goal we resolve against", "El objetivo contra el que se resuelve"),
        ("options", "Options", "Opciones"),
        ("chosen", "The pick", "La elegida"),
        ("how_measured", "How we will know", "Cómo se mide"),
    ]),
]

W, H, PAD, GAP = 1400, 1000, 64, 320
INK, BODY = "#1a1a1a", "#595959"
STAMPS = {"draft": ("Draft", "Borrador"), "open": ("Open", "Abierto"), "kept": ("Decided", "Decidido"),
          "changed": ("Changed", "Cambiado")}


def pick(en, es, lang):
    if lang == "en" or not es or en == es:
        return en
    if lang == "es":
        return es
    return en + " · " + es


def attr(text):
    """Escaped for an XML attribute, on one line."""
    return escape(" ".join(str(text).split()), {'"': "&quot;"})


def flat(value):
    """A field value as short board text."""
    if value is None or value == "" or value == [] or value == {}:
        return ""
    if isinstance(value, str):
        return escape(value)  # the box body is read as HTML, so the person's text is escaped once more
    if isinstance(value, list):
        return "<br>".join("· " + inline(v) for v in value)
    if isinstance(value, dict):
        return "<br>".join("%s: %s" % (k.replace("_", " "), inline(v)) for k, v in value.items() if inline(v))
    return escape(str(value))


def inline(value):
    """A nested value on one line: 'name: Daily commuter; role: uses'."""
    if isinstance(value, list):
        return ", ".join(inline(v) for v in value)
    if isinstance(value, dict):
        rest = [(k, inline(v)) for k, v in value.items() if k != "name" and inline(v)]
        if "name" in value:  # 'Daily commuter (uses)', 'No visible slots (cause: ...; alternative today: ...)'
            if not rest:
                return inline(value["name"])
            detail = rest[0][1] if len(rest) == 1 else "; ".join("%s: %s" % (k.replace("_", " "), v) for k, v in rest)
            return "%s (%s)" % (inline(value["name"]), detail)
        return "; ".join("%s: %s" % (k.replace("_", " "), v) for k, v in rest)
    if value is None:
        return ""
    return escape(str(value)).replace("_", " ") if isinstance(value, str) and " " not in value else escape(str(value))


# One color family per row, so two examples on the same board are told apart at a glance.
# (faint surface, light badge, dark badge text). Assumptions stay red and questions yellow in every family.
FAMILIES = {
    "blue": ("#f0f5fd", "#c6dcff", "#305bab"),
    "purple": ("#f4f2fd", "#dedaff", "#6631d7"),
    "orange": ("#fff5ed", "#f8d3af", "#9b4a08"),
}


def frame_svg(spec, x, y, lang, state=None, family="blue"):
    faint, light, dark = FAMILIES[family]
    fid, en, es, q_en, q_es, boxes = spec
    state = state or {}
    fields = state.get("fields") or {}
    stamp = STAMPS[state.get("stamp", "draft")]
    out = []
    out.append('<g id="f%s" transform="translate(%d,%d)" data-frame="%s">' % (fid, x, y, attr(fid + " · " + pick(en, es, lang))))
    out.append('<rect data-type="frame" x="0" y="0" width="%d" height="%d" fill="#ffffff" data-title="%s" />'
               % (W, H, attr(fid + " · " + pick(en, es, lang))))
    out.append('<circle cx="%d" cy="%d" r="44" fill="%s" stroke="none" data-content="%s" data-text-color="%s" '
               'data-font-size="33" data-font-weight="bold" />' % (PAD + 44, PAD + 44, light, attr(fid), dark))
    out.append('<text x="%d" y="%d" font-family="noto_sans" font-size="33" font-weight="bold" fill="%s">%s</text>'
               % (PAD + 112, PAD + 40, INK, escape(en if lang != "es" else es)))
    if lang == "both" and es != en:
        out.append('<text x="%d" y="%d" font-family="noto_sans" font-size="22" fill="%s">%s</text>'
                   % (PAD + 112, PAD + 78, BODY, escape(es)))
    changed = state.get("stamp") == "changed"  # the one stamp that has to stand out
    out.append('<rect x="%d" y="%d" width="176" height="48" rx="62" fill="%s" stroke="none" data-content="%s" '
               'data-text-color="%s" data-font-size="18" data-font-weight="bold" />'
               % (W - PAD - 176, PAD + 20, "#ffdc4a" if changed else "#f7f7f7", attr(pick(stamp[0], stamp[1], lang)),
                  INK if changed else BODY))
    top = PAD + 120
    if q_en:
        question = escape(state["question"]) if state.get("question") else pick(q_en, q_es, lang)
        out.append('<rect x="%d" y="%d" width="%d" height="96" rx="12" fill="#fff6b6" stroke="none" data-content="%s" '
                   'data-text-color="%s" data-font-size="22" data-font-weight="bold" data-text-align="left" />'
                   % (PAD, top, W - 2 * PAD, attr(question), INK))
        top += 96 + 32
    n = len(boxes)
    rows = int(math.ceil(n / 2.0)) if n > 1 else 1
    inner_w, inner_h = W - 2 * PAD, H - PAD - top
    box_h = (inner_h - 32 * (rows - 1)) // rows
    half = (inner_w - 32) // 2
    fill = "#fff0f0" if fid == "A" else faint
    for i, (field, l_en, l_es) in enumerate(boxes):
        row, col = divmod(i, 2)
        full = n == 1 or (i == n - 1 and n % 2 == 1)
        bx = PAD + (0 if full else col * (half + 32))
        bw = inner_w if full else half
        by = top + row * (box_h + 32)
        label = "<b>%s</b>" % pick(l_en, l_es, lang)
        body = "<br>".join(t for t in (flat(fields.get(name)) for name in field.split("+")) if t)  # a box can hold two fields
        content = label + ("<br>" + body if body else "")
        out.append('<rect x="%d" y="%d" width="%d" height="%d" rx="12" fill="%s" stroke="none" data-content="%s" '
                   'data-text-color="%s" data-font-size="18" data-text-align="left" data-text-align-vertical="top" />'
                   % (bx, by, bw, box_h, fill, attr(content), BODY))
    out.append("</g>")
    return "\n".join(out)


def row_svg(specs, x0, y0, lang, title, states=None, family="blue"):
    out = ['<text x="%d" y="%d" font-family="noto_sans" font-size="67" font-weight="bold" fill="%s">%s</text>'
           % (x0, y0 - 96, INK, escape(title))]
    for i, spec in enumerate(specs):
        out.append(frame_svg(spec, x0 + i * (W + GAP), y0, lang, (states or {}).get(spec[0]), family))
    return "\n".join(out)


def template(row="both", lang="both"):
    parts = []
    if row in ("design", "both"):
        parts.append(row_svg(DESIGN, 0, 0, lang, pick("Design row: build or improve a product",
                                                       "Fila de diseño: construir o mejorar un producto", lang)))
    if row in ("diagnosis", "both"):
        y = H + GAP + 200 if row == "both" else 0
        x = W + GAP if row == "both" else 0
        parts.append(row_svg(DIAGNOSIS, x, y, lang, pick("Diagnosis row: a metric moved, why?",
                                                          "Fila de diagnóstico: se movió una métrica, ¿por qué?", lang)))
    return "<svg>\n" + "\n".join(parts) + "\n</svg>\n"


def from_log(log, lang="en", x0=0, y0=0, title=None, family="blue"):
    """The board of one workshop. x0 and y0 place the row, for example under a template on the same board."""
    by_id = {fr["id"]: fr for fr in log["frames"]}
    states = {}
    for fid, fr in by_id.items():
        draft = fr.get("draft") or {}
        fields = fr["final"] if fr.get("final") is not None else (draft.get("fields") or {})
        stamp = fr.get("outcome") or ("open" if fr.get("opened_at") and fr.get("has_question") else "draft")
        states[fid] = {"fields": fields, "stamp": stamp, "question": draft.get("question") or None}
    if log.get("type") == "diagnosis":
        specs = [DESIGN[0]] + DIAGNOSIS + DESIGN[-2:]
    else:
        specs = DESIGN
    return "<svg>\n" + row_svg(specs, x0, y0, lang, title or log.get("case", "Workshop"), states, family) + "\n</svg>\n"


def main(argv=None):
    p = argparse.ArgumentParser(description="Draws the workshop board as SVG for Miro's canvas tools.")
    sub = p.add_subparsers(dest="cmd")
    s = sub.add_parser("template")
    s.add_argument("--row", choices=["design", "diagnosis", "both"], default="both")
    s.add_argument("--lang", choices=["en", "es", "both"], default="both")
    s = sub.add_parser("from-log")
    s.add_argument("log")
    s.add_argument("--lang", choices=["en", "es", "both"], default="en")
    s.add_argument("--x", type=int, default=0)
    s.add_argument("--y", type=int, default=0)
    s.add_argument("--title", default=None)
    s.add_argument("--color", choices=sorted(FAMILIES), default="blue")
    args = p.parse_args(argv)
    if args.cmd == "template":
        sys.stdout.write(template(args.row, args.lang))
    elif args.cmd == "from-log":
        with open(args.log, encoding="utf-8") as f:
            sys.stdout.write(from_log(json.load(f), args.lang, args.x, args.y, args.title, args.color))
    else:
        p.print_help()
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
