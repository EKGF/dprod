# Regenerate with: python spec-generator/contracts_diagram.py  (run from the repository root)
"""Generate assets/dprod-contracts-overview.svg after the ASCII overview in
dprod-contracts/docs/contracts-guide.md: a DataOffer box, an "accept" arrow and a
DataContract box, with the computed duty-state lifecycle underneath. Drawn in the
style of dprod-model.svg: Arial, black-bordered boxes with bold titles, a
blue-bordered DPROD panel, blue arrows. Each row names the ODRL/DPROD property
that carries it.
"""
from xml.sax.saxutils import escape

FONT = "Arial"
TITLE_H = 54
ROW_H = 34
PAD = 10
BLUE = "#0044CC"
LINK = "#0055FF"
GREY = "#666666"
K = "#000000"

out = []


def text(x, y, s, size=15, color=K, weight="normal", anchor="start", style="normal"):
    out.append(f'<text x="{x}" y="{y}" font-family="{FONT}" font-size="{size}px" font-weight="{weight}" '
               f'font-style="{style}" fill="{color}" text-anchor="{anchor}" dominant-baseline="central">'
               f'{escape(s)}</text>')


def panel(title, x, y, w, h):
    out.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="#ffffff" stroke="{BLUE}"/>')
    out.append(f'<rect x="{x}" y="{y}" width="{w}" height="40" fill="#ffffff" stroke="{BLUE}"/>')
    text(x + w / 2, y + 20, title, size=24, weight="bold", anchor="middle")


def policy_box(x, y, w, name, superclass, rows):
    """A class box whose rows read 'what it holds' on the left, 'carried by' on the right."""
    h = TITLE_H + ROW_H * len(rows) + PAD
    out.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="#ffffff" stroke="{K}"/>')
    out.append(f'<line x1="{x}" y1="{y + TITLE_H}" x2="{x + w}" y2="{y + TITLE_H}" stroke="{K}"/>')
    text(x + w / 2, y + 20, name, size=19, weight="bold", color=BLUE, anchor="middle")
    text(x + w / 2, y + 40, f"a kind of {superclass}", size=14, color=GREY, anchor="middle", style="italic")
    for i, (label, prop) in enumerate(rows):
        yy = y + TITLE_H + PAD / 2 + ROW_H * i + ROW_H / 2
        text(x + 12, yy, label, size=16)
        text(x + w - 12, yy, prop, size=14, color=BLUE if prop.startswith("dprod:") else GREY, anchor="end")
    return h


def state(cx, cy, label, w=150, h=46):
    out.append(f'<rect x="{cx - w / 2}" y="{cy - h / 2}" width="{w}" height="{h}" rx="23" ry="23" '
               f'fill="#ffffff" stroke="{K}"/>')
    text(cx, cy, label, size=17, weight="bold", anchor="middle")


def arrow(points, width=1.5):
    d = "M " + " L ".join(f"{x} {y}" for x, y in points)
    out.append(f'<path d="{d}" fill="none" stroke="{LINK}" stroke-width="{width}" marker-end="url(#arrow)"/>')


W, H = 1180, 720

# ---- Offer and contract
panel("Data offer and data contract", 10, 10, W - 20, 390)
BOX_W, BOX_Y = 430, 80
OFFER_X, CONTRACT_X = 60, W - 60 - BOX_W
offer_h = policy_box(OFFER_X, BOX_Y, BOX_W, "DataOffer", "odrl:Offer", [
    ("Provider duties", "odrl:obligation"),
    ("Consumer rights", "odrl:permission"),
    ("Prohibitions", "odrl:prohibition"),
    ("Recurrence rules", "dprod:recurrence"),
    ("Offer status", "dprod:offerLifecycleStatus"),
])
contract_h = policy_box(CONTRACT_X, BOX_Y, BOX_W, "DataContract", "odrl:Agreement", [
    ("Provider duties", "odrl:obligation"),
    ("Consumer rights", "odrl:permission"),
    ("Consumer duties", "odrl:obligation"),
    ("Prohibitions", "odrl:prohibition"),
    ("Contract status", "dprod:contractLifecycleStatus"),
    ("Duty state", "dprod:dutyState"),
])

# accept: the consumer accepts the offer, and the contract records which offer it accepted
ay = BOX_Y + TITLE_H + 40
arrow([(OFFER_X + BOX_W, ay), (CONTRACT_X, ay)], width=2.5)
text((OFFER_X + BOX_W + CONTRACT_X) / 2, ay - 20, "accept", size=18, weight="bold", anchor="middle")
by = ay + 60
arrow([(CONTRACT_X, by), (OFFER_X + BOX_W, by)])
text((OFFER_X + BOX_W + CONTRACT_X) / 2, by + 18, "dprod:acceptsOffer", size=14, color=BLUE, anchor="middle")

text(OFFER_X + BOX_W / 2, BOX_Y + offer_h + 24, "published by the provider (odrl:assigner)",
     size=14, color=GREY, anchor="middle", style="italic")
text(CONTRACT_X + BOX_W / 2, BOX_Y + contract_h + 24, "binds provider and consumer (odrl:assignee)",
     size=14, color=GREY, anchor="middle", style="italic")

# ---- Duty state
SY = 420
panel("Duty state, computed by the evaluator", 10, SY, W - 20, H - SY - 10)
row1, row2 = SY + 100, SY + 220
pend_x, act_x = 380, 760
state(pend_x, row1, "Pending")
state(act_x, row1, "Active")
arrow([(pend_x + 75, row1), (act_x - 75, row1)], width=2)
text((pend_x + act_x) / 2, row1 - 18, "condition true", size=15, anchor="middle")

ful_x, vio_x = act_x - 130, act_x + 130
state(ful_x, row2, "Fulfilled")
state(vio_x, row2, "Violated")
arrow([(act_x - 20, row1 + 23), (act_x - 20, row1 + 60), (ful_x, row1 + 60), (ful_x, row2 - 23)])
arrow([(act_x + 20, row1 + 23), (act_x + 20, row1 + 60), (vio_x, row1 + 60), (vio_x, row2 - 23)])
text(ful_x - 12, row1 + 60, "action done", size=15, anchor="end")
text(vio_x + 12, row1 + 60, "deadline passed", size=15, anchor="start")

text(60, row2 - 10, "Authored offer and contract status", size=14, color=GREY, style="italic")
text(60, row2 + 10, "and computed duty state are separate.", size=14, color=GREY, style="italic")

svg = [f'<svg version="1.1" xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
       '<defs><marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto-start-reverse">'
       f'<path d="M 0 0 L 10 5 L 0 10" fill="none" stroke="{LINK}" stroke-width="1.5"/></marker></defs>',
       f'<rect x="0" y="0" width="{W}" height="{H}" fill="#ffffff"/>'] + out + ['</svg>']
open('assets/dprod-contracts-overview.svg', 'w').write("\n".join(svg) + "\n")
print("svg written")
