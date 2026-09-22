#!/usr/bin/env python3
"""Draw the replacement figures for the COMP3540 lecture decks.

The 2024 theory PowerPoints illustrate the set texts with scans and web grabs
of their figures (see scripts/deck-images.README.md). Those cannot go on a
public site, but the *models* they show are course content, so this script
redraws them as original figures: transparent SVG on the deck's dark palette,
text kept as real <text> so it stays crisp at projector scale.

    python3 scripts/make-deck-figures.py            # write src/decks/figures/*.svg
    python3 scripts/make-deck-figures.py --check    # lint them
    python3 scripts/make-deck-figures.py --sheet    # contact sheet for review

The SVGs are committed, so `pnpm build` and CI never need this script or its
dependencies. It is a regeneration tool, like scripts/convert-pptx-decks.py.

Needs: pip install -r scripts/requirements.txt, and `brew install graphviz`
for the node-and-arrow figures.

Nothing here is traced from a source figure. Each one was drawn from the
`teaches` sentence in scripts/deck-images.json and the primary literature;
see "Originality" in scripts/deck-images.README.md.
"""

from __future__ import annotations

import argparse
import json
import math
import pathlib
import re
import shutil
import subprocess
import sys

HERE = pathlib.Path(__file__).parent
OUT = HERE.parent / "src" / "decks" / "figures"

# The deck palette, mirroring src/decks/theme.css. Every colour here clears
# 4.5:1 against the deck background except DIM, which is stroke-only (3.6:1,
# above the 3:1 needed for a non-text graphic).
BG = "#1f2429"
PALETTE = {
    "text": "#f2f2f2",
    "accent": "#be830e",
    "gold": "#e9b44c",
    "muted": "#9aa3ab",
    "teal": "#5ec9c0",
    "blue": "#7fb3ea",
    "pink": "#f09ac0",
    "green": "#8fd18a",
    "red": "#f08a7a",
    "violet": "#c3a6f0",
    "sand": "#d9c9a3",
}
DIM = "#6f7a84"  # strokes and gridlines only, never text
FONT = '"Public Sans", system-ui, sans-serif'
# Graphviz takes a bare family name, so the fallback chain is patched back
# into its output in _dot() below.
FONT_DOT = "Public Sans"

_figures: dict[str, callable] = {}


def figure(name):
    def wrap(fn):
        _figures[name] = fn
        return fn
    return wrap


# ---------------------------------------------------------------- matplotlib

def _plt():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({
        "svg.fonttype": "none",       # keep <text>, do not outline
        "font.family": "sans-serif",
        "font.sans-serif": ["Public Sans", "system-ui", "sans-serif"],
        "font.size": 15,
        "text.color": PALETTE["text"],
        "axes.labelcolor": PALETTE["text"],
        "axes.edgecolor": PALETTE["muted"],
        "xtick.color": PALETTE["muted"],
        "ytick.color": PALETTE["muted"],
        "figure.figsize": (8, 4.5),
    })
    return plt


def _save(plt, fig, name):
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / f"{name}.svg"
    fig.savefig(path, format="svg", transparent=True, bbox_inches="tight",
                pad_inches=0.12)
    plt.close(fig)
    return path


def _bare(ax, xlabel=None, ylabel=None):
    """Axes with arrows for direction and no numbers -- these are conceptual
    plots, and tick values would imply data we do not have."""
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color(PALETTE["muted"])
        ax.spines[side].set_linewidth(1.4)
    ax.set_xticks([])
    ax.set_yticks([])
    if xlabel:
        ax.set_xlabel(xlabel, fontsize=15)
    if ylabel:
        ax.set_ylabel(ylabel, fontsize=15)


# ------------------------------------------------------------------ graphviz

def _dot(name, source, engine="dot"):
    if shutil.which(engine) is None:
        raise SystemExit(
            f"{engine} not found -- the node-and-arrow figures need Graphviz "
            "(brew install graphviz)."
        )
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / f"{name}.svg"
    svg = subprocess.run([engine, "-Tsvg"], input=source, text=True,
                         capture_output=True, check=True).stdout
    # Graphviz writes a white background rect even with bgcolor=transparent
    # on some builds, and an XML comment naming the source graph.
    svg = re.sub(r"<!--.*?-->", "", svg, flags=re.S)
    svg = re.sub(r'<polygon fill="#?(white|ffffff)"[^/]*/>', "", svg, flags=re.I)
    svg = svg.replace(f'font-family="{FONT_DOT}"', f'font-family={FONT!r}')
    path.write_text(svg)
    return path


def _graph(body, *, engine="dot", rankdir="TB", **gattrs):
    attrs = {
        "bgcolor": "transparent",
        "rankdir": rankdir,
        "fontname": FONT_DOT,
        "fontsize": "16",
        "nodesep": "0.45",
        "ranksep": "0.55",
        **gattrs,
    }
    ga = " ".join(f'{k}="{v}"' for k, v in attrs.items())
    return f"""digraph G {{
  graph [{ga}];
  node [shape=box style=rounded fontname="{FONT_DOT}" fontsize=16
        color="{PALETTE['muted']}" fontcolor="{PALETTE['text']}"
        penwidth=1.6 margin="0.22,0.14"];
  edge [color="{PALETTE['muted']}" fontname="{FONT_DOT}" fontsize=15
        fontcolor="{PALETTE['muted']}" penwidth=1.6 arrowsize=0.8];
{body}
}}"""


# --------------------------------------------------------------- the figures
# Each figure is drawn from the `teaches` sentence in deck-images.json and the
# primary source named in its `credit`, never traced from the slide scan.

@figure("flow-channel")
def flow_channel():
    """Csikszentmihalyi's flow channel. Drawn as a band between two labelled
    regions -- no walk of balls and arrows, which is Schell's rendering."""
    plt = _plt()
    fig, ax = plt.subplots(figsize=(7.2, 4.6))
    ax.fill_between([0, 10], [-1.4, 8.6], [1.4, 11.4], color=PALETTE["gold"],
                    alpha=0.20, linewidth=0)
    ax.plot([0, 10], [-1.4, 8.6], color=PALETTE["gold"], lw=2)
    ax.plot([0, 10], [1.4, 11.4], color=PALETTE["gold"], lw=2)
    ax.text(6.4, 9.2, "Anxiety", color=PALETTE["red"], fontsize=17, ha="center")
    ax.text(5.0, 5.1, "Flow channel", color=PALETTE["gold"], fontsize=17,
            ha="center", rotation=39, rotation_mode="anchor")
    ax.text(3.4, 0.7, "Boredom", color=PALETTE["blue"], fontsize=17, ha="center")
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 11.4)
    _bare(ax, "Player skill →", "Challenge →")
    return _save(plt, fig, "flow-channel")


@figure("flow-octants")
def flow_octants():
    """Massimini & Carli's eight channels. Flat two-tint palette and every
    wedge labelled, so nothing depends on colour alone."""
    plt = _plt()
    fig, ax = plt.subplots(figsize=(6.4, 6.4))
    names = ["Control", "Flow", "Arousal", "Anxiety",
             "Worry", "Apathy", "Boredom", "Relaxation"]
    tints = [PALETTE["gold"], PALETTE["teal"]]
    for k, label in enumerate(names):
        a0, a1 = k * 45, (k + 1) * 45
        ax.add_patch(plt.matplotlib.patches.Wedge(
            (0, 0), 1.0, a0, a1, facecolor=tints[k % 2], alpha=0.22,
            edgecolor=PALETTE["muted"], linewidth=1.2))
        mid = math.radians((a0 + a1) / 2)
        r = 0.58 if k % 2 else 0.80
        ax.text(r * math.cos(mid), r * math.sin(mid), label,
                color=PALETTE["text"], fontsize=15, ha="center", va="center")
    ax.annotate("", (0, 1.22), (0, -1.05),
                arrowprops=dict(arrowstyle="->", color=PALETTE["muted"], lw=1.4))
    ax.annotate("", (1.22, 0), (-1.05, 0),
                arrowprops=dict(arrowstyle="->", color=PALETTE["muted"], lw=1.4))
    ax.text(0, 1.30, "Challenge →", color=PALETTE["text"], fontsize=15,
            ha="center")
    ax.text(1.28, 0, "Skill →", color=PALETTE["text"], fontsize=15,
            va="center")
    ax.set_xlim(-1.35, 1.55)
    ax.set_ylim(-1.2, 1.45)
    ax.set_aspect("equal")
    ax.axis("off")
    return _save(plt, fig, "flow-octants")


@figure("maslow-hierarchy")
def maslow_hierarchy():
    """Maslow's five needs. Maslow never drew a pyramid -- that is a later
    management-textbook device -- but the decks teach it that way, so keep the
    shape and add the game example per level, which is the course's point."""
    plt = _plt()
    fig, ax = plt.subplots(figsize=(8.4, 5.0))
    bands = [
        ("Physiological", "food, warmth, rest", PALETTE["red"]),
        ("Safety", "security, predictable rules", PALETTE["sand"]),
        ("Belonging", "guilds, co-op play, a team", PALETTE["green"]),
        ("Esteem", "mastery, rank, recognition", PALETTE["teal"]),
        ("Self-actualisation", "creative play, self-expression", PALETTE["violet"]),
    ]
    n, apex, halfw, tip = len(bands), 4.4, 4.2, 0.30
    for k, (name, gloss, colour) in enumerate(bands):
        y0, y1 = k * apex / n, (k + 1) * apex / n
        w0 = halfw * (1 - (1 - tip) * y0 / apex)
        w1 = halfw * (1 - (1 - tip) * y1 / apex)
        ax.add_patch(plt.matplotlib.patches.Polygon(
            [(-w0, y0), (w0, y0), (w1, y1), (-w1, y1)], closed=True,
            facecolor=colour, alpha=0.22, edgecolor=PALETTE["muted"],
            linewidth=1.2))
        ax.text(0, (y0 + y1) / 2 + 0.10, name, color=PALETTE["text"],
                fontsize=16, ha="center", va="center")
        ax.text(0, (y0 + y1) / 2 - 0.26, gloss, color=PALETTE["muted"],
                fontsize=12, ha="center", va="center")
    ax.annotate("", (-4.55, apex), (-4.55, 0),
                arrowprops=dict(arrowstyle="->", color=PALETTE["muted"], lw=1.4))
    ax.text(-4.75, apex / 2, "Lower needs met first", color=PALETTE["muted"],
            fontsize=13, rotation=90, ha="center", va="center")
    ax.set_xlim(-5.4, 4.4)
    ax.set_ylim(-0.25, apex + 0.25)
    ax.axis("off")
    return _save(plt, fig, "maslow-hierarchy")


@figure("bartle-taxonomy")
def bartle_taxonomy():
    """Bartle's four player types on acting/interacting x players/world.
    Text labels only -- the card suits are Bartle's decorative device."""
    plt = _plt()
    fig, ax = plt.subplots(figsize=(7.0, 5.4))
    quads = [(1, 1, "Achievers", "act on the world"),
             (-1, 1, "Killers", "act on players"),
             (-1, -1, "Socialisers", "interact with players"),
             (1, -1, "Explorers", "interact with the world")]
    for sx, sy, name, gloss in quads:
        ax.text(sx * 0.55, sy * 0.62, name, color=PALETTE["gold"], fontsize=18,
                ha="center", va="center")
        ax.text(sx * 0.55, sy * 0.62 - 0.13, gloss, color=PALETTE["muted"],
                fontsize=13, ha="center", va="center")
    ax.annotate("", (0, 1.05), (0, -1.05),
                arrowprops=dict(arrowstyle="<->", color=PALETTE["muted"], lw=1.4))
    ax.annotate("", (1.05, 0), (-1.05, 0),
                arrowprops=dict(arrowstyle="<->", color=PALETTE["muted"], lw=1.4))
    for x, y, t, ha, va in [(0, 1.12, "Acting", "center", "bottom"),
                            (0, -1.12, "Interacting", "center", "top"),
                            (-1.10, 0, "Players", "right", "center"),
                            (1.10, 0, "World", "left", "center")]:
        ax.text(x, y, t, color=PALETTE["text"], fontsize=15, ha=ha, va=va)
    ax.set_xlim(-1.45, 1.45)
    ax.set_ylim(-1.3, 1.3)
    ax.axis("off")
    return _save(plt, fig, "bartle-taxonomy")


@figure("dramatic-arc")
def dramatic_arc():
    """Freytag's arc (1863): a single curve with the five stage names."""
    plt = _plt()
    import numpy as np
    fig, ax = plt.subplots(figsize=(8.0, 4.0))
    x = np.linspace(0, 10, 400)
    y = 0.6 + 5.0 * np.exp(-((x - 5.8) ** 2) / 5.2) * (1 / (1 + np.exp(-(x - 2.2))))
    ax.plot(x, y, color=PALETTE["gold"], lw=2.6)
    for xx, label in [(1.0, "Exposition"), (3.7, "Rising\naction"),
                      (5.8, "Climax"), (7.9, "Falling\naction"),
                      (9.6, "Denouement")]:
        yy = float(np.interp(xx, x, y))
        ax.plot([xx], [yy], "o", color=PALETTE["gold"], ms=7)
        ax.annotate(label, (xx, yy), textcoords="offset points",
                    xytext=(0, 14), ha="center", color=PALETTE["text"],
                    fontsize=14)
    ax.set_xlim(0, 10.6)
    ax.set_ylim(0, 7.4)
    _bare(ax, "Time →", "Tension →")
    return _save(plt, fig, "dramatic-arc")


@figure("interest-curve")
def interest_curve():
    """Schell's interest curve. Our own beat sequence and our own vocabulary
    -- Schell's specific A-H walk is his expression, the idea is not."""
    plt = _plt()
    import numpy as np
    fig, ax = plt.subplots(figsize=(8.4, 4.2))
    beats = [(0.0, 1.2, "Start"), (0.9, 4.1, "Hook"), (1.8, 2.5, ""),
             (3.0, 4.4, ""), (4.1, 3.2, ""), (5.4, 5.4, ""),
             (6.4, 4.0, ""), (7.6, 6.3, ""), (8.6, 4.6, ""),
             (9.5, 8.4, "Climax"), (10.0, 3.0, "Release")]
    xs = [b[0] for b in beats]
    ys = [b[1] for b in beats]
    ax.plot(xs, ys, color=PALETTE["gold"], lw=2.4, marker="o", ms=6)
    ax.axhline(1.2, color=DIM, lw=1.2, ls=":")
    ax.text(10.15, 1.2, "Interest\nthreshold", color=PALETTE["muted"],
            fontsize=12, va="center")
    for xx, yy, label in beats:
        if label:
            ax.annotate(label, (xx, yy), textcoords="offset points",
                        xytext=(0, 13), ha="center", color=PALETTE["text"],
                        fontsize=14)
    ax.set_xlim(-0.3, 12.0)
    ax.set_ylim(0, 10.2)
    _bare(ax, "Time in the experience →", "Interest →")
    return _save(plt, fig, "interest-curve")


@figure("interest-curve-nested")
def interest_curve_nested():
    """The same shape at three scales: a session, a level, an encounter."""
    plt = _plt()
    import numpy as np
    fig, axes = plt.subplots(1, 3, figsize=(10.5, 3.2))
    base_x = np.array([0, 0.9, 1.8, 3.0, 4.1, 5.4, 6.4, 7.6, 8.6, 9.5, 10.0])
    base_y = np.array([1.2, 4.1, 2.5, 4.4, 3.2, 5.4, 4.0, 6.3, 4.6, 8.4, 3.0])
    for ax, title in zip(axes, ["Whole game", "One level", "One encounter"]):
        ax.plot(base_x, base_y, color=PALETTE["gold"], lw=2.2)
        ax.set_title(title, color=PALETTE["text"], fontsize=15, pad=10)
        ax.set_xlim(-0.3, 10.6)
        ax.set_ylim(0, 9.6)
        _bare(ax)
    axes[0].set_ylabel("Interest →", fontsize=14)
    for ax in axes:
        ax.set_xlabel("Time →", fontsize=14)
    fig.tight_layout()
    return _save(plt, fig, "interest-curve-nested")


@figure("production-funnel")
def production_funnel():
    """Fullerton's production funnel, redesigned as a timeline: the same
    lesson (iterations get shorter and cheaper as launch approaches) with a
    different visual argument, so it is not a redraw of her figure."""
    plt = _plt()
    fig, ax = plt.subplots(figsize=(9.6, 3.8))
    phases = [("Concept", 0.0, 2.4, 3), ("Pre-production", 2.4, 5.2, 4),
              ("Production", 5.2, 8.4, 6), ("QA", 8.4, 10.0, 5)]
    colours = [PALETTE["violet"], PALETTE["blue"], PALETTE["teal"], PALETTE["gold"]]
    for (name, x0, x1, loops), colour in zip(phases, colours):
        ax.add_patch(plt.matplotlib.patches.Rectangle(
            (x0, 0.55), x1 - x0, 1.5, facecolor=colour, alpha=0.18,
            edgecolor=PALETTE["muted"], linewidth=1.2))
        ax.text((x0 + x1) / 2, 2.22, name, color=PALETTE["text"], fontsize=15,
                ha="center")
        r = 0.34 * (1 - 0.62 * (x0 / 10.0))
        for k in range(loops):
            cx = x0 + (x1 - x0) * (k + 0.5) / loops
            ax.add_patch(plt.matplotlib.patches.Circle(
                (cx, 1.3), r, fill=False, edgecolor=colour, linewidth=1.8))
    ax.annotate("", (10.35, 0.18), (0, 0.18),
                arrowprops=dict(arrowstyle="->", color=PALETTE["muted"], lw=1.6))
    ax.text(0, -0.12, "Each circle is one design iteration: more of them, "
            "shorter and cheaper, as launch approaches",
            color=PALETTE["muted"], fontsize=13, va="top")
    ax.text(10.45, 0.18, "Launch", color=PALETTE["gold"], fontsize=15,
            va="center")
    ax.set_xlim(-0.2, 12.3)
    ax.set_ylim(-0.7, 2.6)
    ax.axis("off")
    return _save(plt, fig, "production-funnel")


@figure("interaction-patterns")
def interaction_patterns():
    """Fullerton's player interaction patterns. A different pictogram
    vocabulary from hers: a filled dot is a player, a ring is the game,
    arrows carry the direction of competition or cooperation."""
    plt = _plt()
    fig, axes = plt.subplots(2, 4, figsize=(11.0, 5.2))
    P, G = PALETTE["gold"], PALETTE["teal"]

    def player(ax, x, y):
        ax.plot([x], [y], "o", color=P, ms=11)

    def game(ax, x, y):
        ax.add_patch(plt.matplotlib.patches.Circle(
            (x, y), 0.20, fill=False, edgecolor=G, lw=2.2))

    def arrow(ax, a, b, both=False):
        ax.annotate("", b, a, arrowprops=dict(
            arrowstyle="<->" if both else "->", color=PALETTE["muted"], lw=1.5,
            shrinkA=9, shrinkB=11))

    specs = [
        ("Single player\nvs game", lambda ax: (
            player(ax, -0.5, 0), game(ax, 0.5, 0), arrow(ax, (-0.5, 0), (0.5, 0)))),
        ("Multiple players\nvs game", lambda ax: (
            [player(ax, -0.6, y) for y in (0.45, 0, -0.45)], game(ax, 0.6, 0),
            [arrow(ax, (-0.6, y), (0.6, 0)) for y in (0.45, 0, -0.45)])),
        ("Player vs player", lambda ax: (
            player(ax, -0.5, 0), player(ax, 0.5, 0),
            arrow(ax, (-0.5, 0), (0.5, 0), both=True))),
        ("Unilateral\ncompetition", lambda ax: (
            player(ax, 0, 0.5), player(ax, -0.55, -0.4), player(ax, 0.55, -0.4),
            arrow(ax, (-0.55, -0.4), (0, 0.5)), arrow(ax, (0.55, -0.4), (0, 0.5)))),
        ("Multilateral\ncompetition", lambda ax: (
            [player(ax, 0.62 * math.cos(math.radians(a)),
                    0.62 * math.sin(math.radians(a))) for a in (90, 210, 330)],
            [arrow(ax, (0.62 * math.cos(math.radians(a)),
                        0.62 * math.sin(math.radians(a))),
                   (0.62 * math.cos(math.radians(b)),
                    0.62 * math.sin(math.radians(b))), both=True)
             for a, b in ((90, 210), (210, 330), (330, 90))])),
        ("Cooperative play", lambda ax: (
            player(ax, -0.62, 0.25), player(ax, 0, 0.25),
            game(ax, 0.62, -0.25),
            arrow(ax, (-0.62, 0.25), (0.62, -0.25)),
            arrow(ax, (0, 0.25), (0.62, -0.25)))),
        ("Team competition", lambda ax: (
            [player(ax, -0.72, y) for y in (0.3, -0.3)],
            [player(ax, 0.72, y) for y in (0.3, -0.3)],
            arrow(ax, (-0.72, 0), (0.72, 0), both=True))),
    ]
    for ax, (title, draw) in zip(axes.flat, specs):
        draw(ax)
        ax.set_title(title, color=PALETTE["text"], fontsize=13.5, pad=6)
        ax.set_xlim(-1.1, 1.1)
        ax.set_ylim(-0.95, 0.95)
        ax.set_aspect("equal")
        ax.axis("off")
    axes.flat[-1].axis("off")
    axes.flat[-1].text(0, 0, "●  player\n○  the game",
                       color=PALETTE["muted"], fontsize=14, ha="center",
                       va="center")
    axes.flat[-1].set_xlim(-1.1, 1.1)
    axes.flat[-1].set_ylim(-0.95, 0.95)
    fig.tight_layout()
    return _save(plt, fig, "interaction-patterns")


# ---------------------------------------------------------- node-and-arrow

@figure("iterative-design-cycle")
def iterative_design_cycle():
    """Fullerton's iterative loop. Laid out by circo from an edge list, so it
    cannot be a trace; the 'problems found' back-edge is the teaching point."""
    return _dot("iterative-design-cycle", _graph(f"""
  gen  [label="Generate\\nideas"];
  form [label="Formalise\\nideas"];
  test [label="Test\\nideas"];
  eval [label="Evaluate\\nresults"];
  gen -> form -> test -> eval;
  eval -> gen [label="problems found", color="{PALETTE['gold']}",
               fontcolor="{PALETTE['gold']}"];
""", engine="circo", mindist="1.5"), engine="circo")


@figure("design-loop")
def design_loop():
    """Cook's loop (Lostgarden, 2012) -- the slides credit Fullerton for this,
    which is wrong; the credit in deck-images.json fixes it. Text nodes only:
    the lightbulb/hand/gear/eye icons are Cook's device."""
    return _dot("design-loop", _graph(f"""
  model    [label="Mental model"];
  action   [label="Action"];
  rules    [label="Rules"];
  feedback [label="Feedback"];
  model -> action -> rules -> feedback -> model;
""", engine="circo", mindist="1.4"), engine="circo")


@figure("design-arc")
def design_arc():
    """Cook's arc: the same four stages as an open chain that terminates,
    which is exactly how it differs from the loop."""
    return _dot("design-arc", _graph(f"""
  model    [label="Mental model"];
  action   [label="Action"];
  rules    [label="Rules"];
  feedback [label="Feedback"];
  done     [label="Exhausted", color="{PALETTE['gold']}",
            fontcolor="{PALETTE['gold']}"];
  model -> action -> rules -> feedback -> done;
""", rankdir="LR"))


@figure("interface-model")
def interface_model():
    """Schell's interface model: the player never touches the world directly.
    Plain boxes -- the gamepad, TV and cityscape clip art are his."""
    return _dot("interface-model", _graph(f"""
  player [label="Player", color="{PALETTE['gold']}",
          fontcolor="{PALETTE['gold']}"];
  pin    [label="Physical\\ninput"];
  pout   [label="Physical\\noutput"];
  vif    [label="Virtual\\ninterface"];
  world  [label="Game world", color="{PALETTE['teal']}",
          fontcolor="{PALETTE['teal']}"];
  player -> pin    [label="1"];
  pin    -> vif    [label="2"];
  vif    -> world  [label="3"];
  world  -> vif    [label="4"];
  vif    -> pout   [label="5"];
  pout   -> player [label="6"];
  {{ rank=same; pin; pout; }}
""", rankdir="LR"))


@figure("rules-taxonomy")
def rules_taxonomy():
    """Parlett's three kinds of rule, via Salen & Zimmerman. Sublabels are
    paraphrased and the layout is top-down rather than the source's ring."""
    return _dot("rules-taxonomy", _graph(f"""
  found [label="Foundational rules\\nthe abstract system underneath"];
  oper  [label="Operational rules\\nwhat the players actually do"];
  behav [label="Behavioural rules\\nthe unwritten etiquette of play"];
  play  [label="Play", color="{PALETTE['gold']}", fontcolor="{PALETTE['gold']}"];
  found -> oper  [label="expressed as"];
  oper  -> play  [label="performed as"];
  behav -> play  [label="shapes how"];
  play  -> oper  [label="players renegotiate", color="{PALETTE['gold']}",
                  fontcolor="{PALETTE['gold']}", constraint=false];
  {{ rank=same; oper; behav; }}
""", ranksep="1.1", nodesep="0.9"))


@figure("pacman-ghost-fsm")
def pacman_ghost_fsm():
    """The ghost state machine. This is the observable behaviour of a 1980
    arcade game, not anyone's drawing of it."""
    return _dot("pacman-ghost-fsm", _graph(f"""
  node [fontsize=18];
  edge [fontsize=17];
  base  [label="In base"];
  chase [label="Chasing", color="{PALETTE['gold']}",
         fontcolor="{PALETTE['gold']}"];
  flee  [label="Fleeing", color="{PALETTE['blue']}",
         fontcolor="{PALETTE['blue']}"];
  blink [label="Flashing"];
  eyes  [label="Eyes to base"];
  base  -> chase [label="timer up"];
  chase -> flee  [label="power pill"];
  flee  -> blink [label="fading"];
  blink -> chase [label="pill ends"];
  flee  -> eyes  [label="eaten"];
  blink -> eyes  [label="eaten"];
  eyes  -> base  [label="arrives"];
""", engine="circo", mindist="1.45"), engine="circo")


@figure("rock-paper-scissors-lizard-spock")
def rpsls():
    """A five-way intransitive balance. Text nodes on a circo ring -- the
    scissors/lizard/rock photographs are the source figure's expression."""
    beats = [("Scissors", "Paper"), ("Paper", "Rock"), ("Rock", "Lizard"),
             ("Lizard", "Spock"), ("Spock", "Scissors"), ("Scissors", "Lizard"),
             ("Lizard", "Paper"), ("Paper", "Spock"), ("Spock", "Rock"),
             ("Rock", "Scissors")]
    order = ["Rock", "Spock", "Paper", "Lizard", "Scissors"]
    pins = "\n".join(
        f'  "{n}" [pos="{2.4 * math.sin(2 * math.pi * k / 5):.3f},'
        f'{2.4 * math.cos(2 * math.pi * k / 5):.3f}!"]'
        for k, n in enumerate(order))
    edges = "\n".join(f'  "{a}" -> "{b}";' for a, b in beats)
    return _dot("rock-paper-scissors-lizard-spock", _graph(
        f'  node [shape=ellipse];\n{pins}\n{edges}\n', engine="neato"),
        engine="neato")


# --- figures for slides that never had a picture (scripts/deck-extras.json).
# These are not redrawings: nothing on the slide was dropped. They are drawn
# from the bullets the slide already carries and the pages it cites.

@figure("narrowing-the-list")
def narrowing_the_list():
    """Fullerton's funnel from a brainstorm to one game. Counts are the ones
    the slide gives; the second pass back into the funnel is the point."""
    plt = _plt()
    fig, ax = plt.subplots(figsize=(8.0, 4.4))
    bands = [
        ("Everything you brainstormed", 5.0, PALETTE["muted"]),
        ("Shortlist: 5-10 ideas", 3.4, PALETTE["gold"]),
        ("Three ideas", 2.0, PALETTE["teal"]),
        ("One game to prototype", 0.9, PALETTE["accent"]),
    ]
    h = 1.0
    for k, (label, w, colour) in enumerate(bands):
        y1 = -k * h
        y0 = y1 - h
        w1 = w / 2
        w0 = (bands[k + 1][1] if k + 1 < len(bands) else w) / 2
        ax.add_patch(plt.matplotlib.patches.Polygon(
            [(-w1, y1), (w1, y1), (w0, y0), (-w0, y0)], closed=True,
            facecolor=colour, alpha=0.20, edgecolor=PALETTE["muted"],
            linewidth=1.2))
        ax.text(0, y1 - h / 2, label, color=PALETTE["text"], fontsize=16,
                ha="center", va="center")
    ax.annotate("", (-3.5, -3.6), (-3.5, -1.1),
                arrowprops=dict(arrowstyle="->", color=PALETTE["gold"], lw=1.6,
                                connectionstyle="arc3,rad=0.4"))
    ax.text(-4.8, -2.35, "Brainstorm\nagain on each", color=PALETTE["gold"],
            fontsize=14, ha="center", va="center")
    ax.set_xlim(-6.1, 2.9)
    ax.set_ylim(-4.15, 0.15)
    ax.axis("off")
    return _save(plt, fig, "narrowing-the-list")


@figure("idea-filters")
def idea_filters():
    """The four questions Fullerton edits a brainstormed list with. Drawn as
    gates rather than a checklist: an idea has to pass all four."""
    return _dot("idea-filters", _graph("""
  long  [label="A long list\nof ideas" color="%(muted)s"];
  tech  [label="Can you\nbuild it?"];
  market[label="Will people\nplay it?"];
  love  [label="Do you\nlove it?"];
  cost  [label="Can you\nafford it?"];
  short [label="The list\nworth testing" color="%(accent)s"];
  long -> tech -> market -> love -> cost -> short;
""" % PALETTE, rankdir="LR", ranksep="0.35"))


@figure("sprint-cycle")
def sprint_cycle():
    """The sprint loop the Agile slides describe in prose: plan, build, show,
    reflect, reprioritise. Two to four weeks, then round again."""
    return _dot("sprint-cycle", _graph("""
  node [fontsize=20];
  backlog [label="Prioritised backlog"];
  plan    [label="Sprint planning"];
  build   [label="Build (2-4 weeks)"];
  demo    [label="Demo day"];
  retro   [label="Retrospective"];
  backlog -> plan -> build -> demo -> retro -> backlog;
""", engine="circo", mindist="1.5"), engine="circo")


@figure("burndown")
def burndown():
    """A burndown chart. Conceptual, not data: the point is that the real
    line is above the ideal one and that new work pushes it back up."""
    plt = _plt()
    fig, ax = plt.subplots(figsize=(8.0, 4.3))
    ideal_x = [0, 10]
    ideal_y = [10, 0]
    real_x = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    real_y = [10, 9.6, 9.0, 8.8, 9.9, 9.0, 7.4, 6.2, 4.4, 2.4, 0.6]
    ax.plot(ideal_x, ideal_y, color=DIM, lw=2, ls="--")
    ax.plot(real_x, real_y, color=PALETTE["gold"], lw=2.6, marker="o", ms=5)
    ax.annotate("Scope added", (4, 9.9), textcoords="offset points",
                xytext=(6, 14), color=PALETTE["red"], fontsize=15)
    ax.plot([4], [9.9], marker="o", ms=9, color=PALETTE["red"])
    ax.text(8.3, 1.6, "Ideal", color=PALETTE["muted"], fontsize=15)
    ax.text(6.2, 7.2, "Actual", color=PALETTE["gold"], fontsize=15)
    ax.set_xlim(0, 10.6)
    ax.set_ylim(0, 11)
    _bare(ax, "Days in the sprint \u2192", "Work remaining \u2192")
    return _save(plt, fig, "burndown")


@figure("playtest-session")
def playtest_session():
    """The test script Fullerton asks for, as a timeline. The play session is
    the short part: most of the hour is framing it and talking afterwards."""
    plt = _plt()
    fig, ax = plt.subplots(figsize=(9.0, 3.0))
    parts = [
        ("Introduction", 3, PALETTE["muted"]),
        ("Warm-up", 5, PALETTE["teal"]),
        ("Play session", 20, PALETTE["gold"]),
        ("Discussion", 20, PALETTE["accent"]),
        ("Wrap-up", 5, PALETTE["violet"]),
    ]
    x = 0
    for k, (label, mins, colour) in enumerate(parts):
        ax.add_patch(plt.matplotlib.patches.Rectangle(
            (x, 0), mins, 1, facecolor=colour, alpha=0.22,
            edgecolor=PALETTE["muted"], linewidth=1.2))
        # The three-minute block is too narrow for its own name, so the
        # labels step up and down on a leader rather than colliding.
        top = 1.9 if k % 2 else 1.3
        ax.plot([x + mins / 2, x + mins / 2], [1.05, top - 0.08], color=DIM,
                lw=1.1)
        ax.text(x + mins / 2, top, label, color=PALETTE["text"], fontsize=15,
                ha="center", va="bottom")
        ax.text(x + mins / 2, 0.5, f"{mins} min", color=PALETTE["muted"],
                fontsize=13, ha="center", va="center")
        x += mins
    ax.annotate("", (0, -0.5), (x, -0.5),
                arrowprops=dict(arrowstyle="<->", color=PALETTE["muted"], lw=1.4))
    ax.text(x / 2, -1.05, "About an hour per playtester", color=PALETTE["muted"],
            fontsize=14, ha="center")
    ax.set_xlim(-2.5, x + 2.5)
    ax.set_ylim(-1.5, 2.6)
    ax.axis("off")
    return _save(plt, fig, "playtest-session")


@figure("playtest-notes")
def playtest_notes():
    """The three parts of Fullerton's note-taking form. Her own form is a
    full page of her questions, so this is the structure, not the content."""
    plt = _plt()
    fig, ax = plt.subplots(figsize=(9.0, 3.6))
    cols = [
        ("In-game observations", "what they did, chose,\nfound, got stuck on",
         PALETTE["teal"], "while they play"),
        ("Post-game questions", "appeal, challenge,\nunderstanding, changes",
         PALETTE["gold"], "after they play"),
        ("Revision ideas", "yours, written while\nit is still fresh",
         PALETTE["accent"], "after they leave"),
    ]
    for k, (title, body, colour, when) in enumerate(cols):
        x = k * 3.8
        ax.add_patch(plt.matplotlib.patches.FancyBboxPatch(
            (x, 0), 3.0, 2.4, boxstyle="round,pad=0.06,rounding_size=0.12",
            facecolor=colour, alpha=0.16, edgecolor=PALETTE["muted"],
            linewidth=1.3))
        ax.text(x + 1.5, 1.92, title, color=PALETTE["text"], fontsize=15,
                ha="center", va="center")
        ax.text(x + 1.5, 1.15, body, color=PALETTE["muted"], fontsize=13,
                ha="center", va="center", linespacing=1.4)
        ax.text(x + 1.5, 0.35, when, color=colour, fontsize=13, ha="center",
                va="center")
    ax.set_xlim(-0.3, 10.9)
    ax.set_ylim(-0.3, 2.7)
    ax.axis("off")
    return _save(plt, fig, "playtest-notes")


@figure("playtest-observation")
def playtest_observation():
    """Where everyone sits. The slide's advice -- run it yourself or watch
    from a distance -- is a diagram, and it is easier to follow as one."""
    return _dot("playtest-observation", _graph("""
  tester [label="Playtester" color="%(gold)s"];
  game   [label="The game,\nunexplained"];
  aloud  [label="Thinking aloud" shape=plaintext color="%(bg)s"];
  you    [label="You: watching,\nnot helping" color="%(accent)s"];
  notes  [label="Notes and\nrecording"];
  tester -> game [label="plays"];
  tester -> aloud;
  aloud -> you;
  you -> notes;
  { rank=same; tester; game; }
""" % dict(PALETTE, bg=BG), rankdir="LR", ranksep="0.5"))

# --------------------------------------------------------------------- lint

def _luminance(hex_colour: str) -> float:
    h = hex_colour.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    ch = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    ch = [c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4 for c in ch]
    return 0.2126 * ch[0] + 0.7152 * ch[1] + 0.0722 * ch[2]


def contrast(a: str, b: str) -> float:
    l1, l2 = sorted((_luminance(a), _luminance(b)), reverse=True)
    return (l1 + 0.05) / (l2 + 0.05)


# The space a figure gets on a 1280x720 slide, in css px.
FIG_W, FIG_H = 1100, 432

ALLOWED_COLOURS = {c.lower() for c in PALETTE.values()} | {DIM.lower()}
TEXT_SAFE = {c.lower() for c in PALETTE.values()}


def check_svg(path: pathlib.Path, spec: dict | None) -> list[str]:
    """The rules from the figure review checklist that a machine can apply.
    Everything else -- does it teach the same thing, is it legible from the
    back of a theatre -- is in scripts/deck-images.README.md for a human."""
    svg = path.read_text()
    bad: list[str] = []

    m = re.search(r'viewBox="[\d.]+ [\d.]+ ([\d.]+) ([\d.]+)"', svg)
    if not m:
        return [f"{path.name}: no viewBox"]
    vb_w, vb_h = float(m.group(1)), float(m.group(2))
    # A figure slide gives about 1100 x 432 css px, and the image fits itself
    # into that box, so whichever dimension binds decides how big the type is.
    scale = min(FIG_W / vb_w, FIG_H / vb_h)

    # A background rect would show as a light card on the dark slide.
    if re.search(r'<rect[^>]*\bfill="(?!none)(#fff|#ffffff|white)', svg, re.I):
        bad.append(f"{path.name}: opaque white background rect")

    texts = re.findall(r"<text[^>]*>(.*?)</text>", svg, re.S)
    plain = [re.sub(r"<[^>]+>", "", t).strip() for t in texts]
    plain = [t for t in plain if t]
    if len(plain) > 14:
        bad.append(f"{path.name}: {len(plain)} text labels (budget 14)")

    sizes = [float(s) for s in re.findall(r'font-size[:=]"?\s*([\d.]+)', svg)]
    if sizes and min(sizes) * scale < 16:
        bad.append(f"{path.name}: smallest text {min(sizes) * scale:.1f} "
                   "css px when rendered (need >= 16)")

    for colour in {c.lower() for c in re.findall(r'(?:fill|stroke)="(#[0-9a-fA-F]{3,6})"', svg)}:
        if colour in ("#none",):
            continue
        if colour not in ALLOWED_COLOURS:
            bad.append(f"{path.name}: colour {colour} is not in the palette")
        elif contrast(colour, BG) < 4.5 and colour not in (DIM.lower(),):
            bad.append(f"{path.name}: {colour} is {contrast(colour, BG):.1f}:1 "
                       "on the deck background (need 4.5:1)")

    if spec:
        alt = spec.get("alt", "")
        if not alt:
            bad.append(f"{path.name}: no alt text in deck-images.json "
                       "or deck-extras.json")
        elif len(alt) > 160:
            bad.append(f"{path.name}: alt text is {len(alt)} chars (keep under 160)")
        if not spec.get("credit"):
            bad.append(f"{path.name}: no credit line")
        elif not re.search(r"\b(redrawn after|after|from)\b", spec["credit"], re.I):
            bad.append(f"{path.name}: credit should say 'redrawn after' or "
                       "'after' so it is not mistaken for a scan")
        missing = [t for t in spec.get("terms", [])
                   if not any(t.lower() in p.lower() for p in plain)]
        if missing:
            bad.append(f"{path.name}: taught terms missing from the figure: "
                       + ", ".join(missing))
    return bad


def contact_sheet(dest: pathlib.Path) -> pathlib.Path:
    """Render every figure over the deck background and montage them, so a
    reviewer can see the whole set the way a student will."""
    if shutil.which("rsvg-convert") is None or shutil.which("magick") is None:
        raise SystemExit("need rsvg-convert and magick for --sheet")
    dest.mkdir(parents=True, exist_ok=True)
    pngs = []
    for svg in sorted(OUT.glob("*.svg")):
        png = dest / f"{svg.stem}.png"
        subprocess.run(["rsvg-convert", "-h", "432", "-b", BG, "-o", str(png),
                        str(svg)], check=True)
        pngs.append(str(png))
    sheet = dest / "figures-sheet.png"
    subprocess.run(["magick", "montage", "-label", "%f", *pngs, "-tile", "3x",
                    "-geometry", "520x360+8+8", "-background", BG,
                    "-fill", PALETTE["text"], "-pointsize", "15", str(sheet)],
                   check=True)
    return sheet


# ---------------------------------------------------------------------- cli

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true",
                    help="lint the figures instead of redrawing them")
    ap.add_argument("--sheet", metavar="DIR", type=pathlib.Path,
                    help="render a contact sheet into DIR for review")
    ap.add_argument("only", nargs="*", help="figure names (default: all)")
    args = ap.parse_args()

    # A figure that replaces a source picture is described in
    # deck-images.json; one drawn for a slide that never had a picture is
    # described in deck-extras.json. Both carry the alt, credit and taught
    # terms this lints against.
    specs = {}
    images = HERE / "deck-images.json"
    if images.exists():
        for entry in json.loads(images.read_text()).values():
            if entry.get("kind") == "figure" and entry.get("file"):
                specs[pathlib.Path(entry["file"]).stem] = entry
    extras = HERE / "deck-extras.json"
    if extras.exists():
        for entries in json.loads(extras.read_text()).values():
            for entry in entries:
                f = entry.get("file", "")
                if f.startswith("figures/"):
                    specs[pathlib.Path(f).stem] = entry

    names = args.only or sorted(_figures)
    unknown = [n for n in names if n not in _figures]
    if unknown:
        print("unknown figure(s):", ", ".join(unknown), file=sys.stderr)
        print("known:", ", ".join(sorted(_figures)), file=sys.stderr)
        return 2

    if args.check:
        problems = []
        for name in names:
            path = OUT / f"{name}.svg"
            if not path.exists():
                problems.append(f"{name}.svg: missing -- run without --check")
                continue
            problems += check_svg(path, specs.get(name))
        orphan = {p.stem for p in OUT.glob("*.svg")} - set(_figures)
        problems += [f"{n}.svg: no longer drawn by this script" for n in sorted(orphan)]
        for p in problems:
            print(p)
        print(f"\n{len(names)} figure(s) checked, {len(problems)} problem(s)")
        return 1 if problems else 0

    for name in names:
        path = _figures[name]()
        print(f"  {path.relative_to(HERE.parent)}")
    print(f"\n{len(names)} figure(s) written to {OUT.relative_to(HERE.parent)}")

    if args.sheet:
        print("contact sheet:", contact_sheet(args.sheet))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
