# Regenerate with: python spec-generator/contracts_diagram.py  (run from the repository root)
"""Generate assets/dprod-contracts-model.svg in the style of dprod-model.svg:
UML class boxes (Arial, bold title, '+prefix: property' lines), a black-bordered
ODRL swimlane and a blue-bordered DPROD swimlane, green generalisation arrows and
blue association arrows. DPROD additions to ODRL classes are drawn in blue.
"""
from xml.sax.saxutils import escape

FONT = "Arial"
TITLE_H = 30
LINE_H = 22
PAD = 8
BLUE = "#0044CC"
LINK = "#0055FF"
GREEN = "#00D369"

boxes = {}
out = []

def box(name, x, y, w, lines, title_color="#000000"):
    h = TITLE_H + LINE_H * len(lines) + PAD
    boxes[name] = (x, y, w, h)
    out.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="#ffffff" stroke="#000000"/>')
    out.append(f'<line x1="{x}" y1="{y+TITLE_H}" x2="{x+w}" y2="{y+TITLE_H}" stroke="#000000"/>')
    out.append(f'<text x="{x+w/2}" y="{y+TITLE_H/2}" font-family="{FONT}" font-size="17px" font-weight="bold" '
               f'fill="{title_color}" text-anchor="middle" dominant-baseline="central">{escape(name)}</text>')
    for i, (text, color) in enumerate(lines):
        yy = y + TITLE_H + PAD/2 + LINE_H * i + LINE_H/2
        out.append(f'<text x="{x+8}" y="{yy}" font-family="{FONT}" font-size="15px" fill="{color}" '
                   f'dominant-baseline="central">{escape(text)}</text>')

def lane(title, x, y, w, h, color):
    out.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="#ffffff" stroke="{color}"/>')
    out.append(f'<rect x="{x}" y="{y}" width="{w}" height="40" fill="#ffffff" stroke="{color}"/>')
    out.append(f'<text x="{x+w/2}" y="{y+20}" font-family="{FONT}" font-size="26px" font-weight="bold" '
               f'text-anchor="middle" dominant-baseline="central">{escape(title)}</text>')

def top(name):    x,y,w,h = boxes[name]; return (x+w/2, y)
def bottom(name): x,y,w,h = boxes[name]; return (x+w/2, y+h)
def left(name):   x,y,w,h = boxes[name]; return (x, y+h/2)
def right(name):  x,y,w,h = boxes[name]; return (x+w, y+h/2)

def generalise(child, parent, via_y=None):
    """Open-triangle arrow from child (bottom box) up to parent."""
    cx, cy = top(child); px, py = bottom(parent)
    if via_y is None:
        via_y = (cy + py) / 2
    path = f"M {cx} {cy} L {cx} {via_y} L {px} {via_y} L {px} {py+12}"
    out.append(f'<path d="{path}" fill="none" stroke="{GREEN}" stroke-width="1.5"/>')
    out.append(f'<path d="M {px-8} {py+12} L {px+8} {py+12} L {px} {py} Z" fill="#ffffff" stroke="{GREEN}" stroke-width="1.5"/>')

def associate(points, label, lx, ly, color=LINK, anchor="start"):
    d = "M " + " L ".join(f"{x} {y}" for x, y in points)
    out.append(f'<path d="{d}" fill="none" stroke="{color}" stroke-width="1.5" marker-end="url(#arrow)"/>')
    out.append(f'<text x="{lx}" y="{ly}" font-family="{FONT}" font-size="14px" fill="#000000" '
               f'text-anchor="{anchor}" dominant-baseline="central">{escape(label)}</text>')

W, H = 1480, 900
# ---- lanes
lane("ODRL 2.2", 10, 10, W-20, 560, "#000000")
lane("DPROD", 10, 620, W-20, 270, BLUE)

K = "#000000"
# ---- ODRL lane
box("Policy", 60, 80, 250, [
    ("+odrl: profile", K), ("+odrl: assigner", K), ("+odrl: assignee", K), ("+odrl: target", K),
    ("+odrl: permission", K), ("+odrl: prohibition", K), ("+odrl: obligation", K)])
box("Offer", 60, 360, 110, [])
box("Agreement", 200, 360, 130, [])
box("Rule", 440, 80, 230, [
    ("+odrl: action", K), ("+odrl: target", K), ("+odrl: assignee", K), ("+odrl: constraint", K)])
box("Permission", 380, 360, 130, [])
box("Prohibition", 530, 360, 130, [])
box("Duty", 690, 300, 230, [
    ("+dprod: subjectOfDuty", BLUE), ("+dprod: objectOfDuty", BLUE),
    ("+dprod: deadline", BLUE), ("+dprod: recurrence", BLUE), ("+dprod: dutyState", BLUE)])
box("Constraint", 980, 80, 220, [
    ("+odrl: leftOperand", K), ("+odrl: operator", K), ("+odrl: rightOperand", K)])
box("LogicalConstraint", 1240, 80, 210, [
    ("+odrl: and", K), ("+odrl: or", K), ("+dprod: not", BLUE)])
box("LeftOperand", 980, 300, 240, [
    ("+dprod: operandSource", BLUE), ("+dprod: operandProperty", BLUE)])
box("Asset", 1260, 300, 190, [("+odrl: partOf", K)])
box("Party", 1000, 450, 190, [("+odrl: partOf", K)])

# ---- DPROD lane
box("DataOffer", 60, 700, 250, [
    ("+dprod: offerLifecycleStatus", BLUE), ("+dprod: effectiveDate", BLUE), ("+dprod: expirationDate", BLUE)])
box("DataContract", 380, 700, 270, [
    ("+dprod: acceptsOffer", BLUE), ("+dprod: contractLifecycleStatus", BLUE),
    ("+dprod: effectiveDate", BLUE), ("+dprod: expirationDate", BLUE)])
box("EvaluationContext", 980, 700, 240, [
    ("+dprod: request", BLUE), ("+dprod: state", BLUE), ("+dprod: agent", BLUE), ("+dprod: clock", BLUE)])
box("DataProduct", 1260, 700, 190, [
    ("(also Dataset,", K), (" Distribution,", K), (" DataService)", K)])

# ---- generalisations (ODRL)
generalise("Offer", "Policy", 340)
generalise("Agreement", "Policy", 340)
generalise("Permission", "Rule", 340)
generalise("Prohibition", "Rule", 340)
generalise("Duty", "Rule", 270)
# DPROD subclasses of ODRL
generalise("DataOffer", "Offer", 640)
generalise("DataContract", "Agreement", 660)
generalise("DataProduct", "Asset", 660)

# ---- associations
# Policy -> Rule (permission/prohibition/obligation)
px, py = top("Policy"); rx, ry = top("Rule")
associate([(px, py), (px, 62), (rx, 62), (rx, ry)], "+permission / prohibition / obligation", (px+rx)/2, 72, anchor="middle")
# Rule -> Constraint
x1, y1 = right("Rule"); x2, y2 = left("Constraint")
associate([(x1, y1), (x2, y1)], "+constraint", (x1+x2)/2, y1-12, anchor="middle")
# Constraint -> LeftOperand
x1, y1 = bottom("Constraint"); x2, y2 = top("LeftOperand")
associate([(x1, y1), (x1, y2)], "+leftOperand", x1+8, (y1+y2)/2)
# LogicalConstraint -> Constraint
lx, ly = bottom("LogicalConstraint"); cx, cy = bottom("Constraint")
associate([(lx, ly), (lx, 235), (1150, 235), (1150, cy)], "+and / or / not", (lx+1150)/2, 250, anchor="middle")
# Policy/Rule -> Asset (target): route from Rule top-right across
x1, y1 = right("Rule"); ax, ay = top("Asset")
associate([(x1, y1+40), (ax+40, y1+40), (ax+40, ay)], "+target", ax+48, 262, anchor="start")
# Policy -> Party (assigner/assignee): route below
x1, y1 = bottom("Policy"); px, py = left("Party")
associate([(x1-60, y1), (x1-60, 555), (985, 555), (985, py), (px, py)],
          "+assigner / assignee", 560, 543, anchor="middle")
# DataContract -> DataOffer (acceptsOffer)
x1, y1 = left("DataContract"); x2, y2 = right("DataOffer")
associate([(x1, y1), (x2, y1)], "+acceptsOffer", (x1+x2)/2, y1-12, anchor="middle")
# EvaluationContext -> Party (agent)
ex, ey = top("EvaluationContext"); px, py = bottom("Party")
associate([(ex, ey), (ex, py)], "+agent", ex+8, 620)
# Duty -> Party (subjectOfDuty / objectOfDuty)
x1, y1 = right("Duty"); 
ptx, pty = top("Party")
associate([(x1, y1+30), (ptx, y1+30), (ptx, pty)], "+subjectOfDuty / objectOfDuty", (x1+ptx)/2, y1+44, anchor="middle")

svg = [f'<svg version="1.1" xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
       '<defs><marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto-start-reverse">'
       f'<path d="M 0 0 L 10 5 L 0 10" fill="none" stroke="{LINK}" stroke-width="1.5"/></marker></defs>',
       f'<rect x="0" y="0" width="{W}" height="{H}" fill="#ffffff"/>'] + out + ['</svg>']
open('assets/dprod-contracts-model.svg', 'w').write("\n".join(svg) + "\n")
print("svg written")
