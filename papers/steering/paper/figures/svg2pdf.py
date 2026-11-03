#!/usr/bin/env python3
"""svg2pdf.py -- minimal SVG->PDF for the estate's hand-rolled figure SVGs.

Supports the exact subset the generators emit: svg/rect/line/text with
absolute coords, #rrggbb colors, stroke-dasharray, fill-opacity, and
text-anchor. Output is vector PDF (base-14 Helvetica, AFM widths).
"""
import sys, re
import xml.etree.ElementTree as ET

HELV = {32:278,33:278,34:355,35:556,36:556,37:889,38:667,39:191,40:333,41:333,
42:389,43:584,44:278,45:333,46:278,47:278,48:556,49:556,50:556,51:556,52:556,
53:556,54:556,55:556,56:556,57:556,58:278,59:278,60:584,61:584,62:584,63:556,
64:1015,65:667,66:667,67:722,68:722,69:667,70:611,71:778,72:722,73:278,74:500,
75:667,76:556,77:833,78:722,79:778,80:667,81:778,82:722,83:667,84:611,85:722,
86:667,87:944,88:667,89:667,90:611,91:278,92:278,93:278,94:469,95:556,96:333,
97:556,98:556,99:500,100:556,101:556,102:278,103:556,104:556,105:222,106:222,
107:500,108:222,109:833,110:556,111:556,112:556,113:556,114:333,115:500,116:278,
117:556,118:500,119:722,120:500,121:500,122:500,123:334,124:260,125:334,126:584}
# Latin-1 extras we can emit verbatim; everything else gets an ASCII fallback
ASCII_FALLBACK = {0x2192:"->",0x2033:'"',0x2013:"-",0x2014:"--",0x2019:"'",
0x2018:"'",0x201C:'"',0x201D:'"',0x2248:"~",0x00b7:chr(0xB7),0x2260:"!="}

def sw(s):
    total = 0
    for ch in s:
        o = ord(ch)
        if o < 128: total += HELV.get(o, 556)
        elif o in ASCII_FALLBACK: total += sw(ASCII_FALLBACK[o])
        else: total += 556
    return total / 1000.0

def latin(s):
    out = []
    for ch in s:
        o = ord(ch)
        if o < 256: out.append(ch)
        elif o in ASCII_FALLBACK: out.append(ASCII_FALLBACK[o])
        else: out.append("?")
    return "".join(out)

def esc(s): return s.replace("\\", r"\\").replace("(", r"\(").replace(")", r"\)")

def color(attr, default=(0,0,0)):
    if not attr: return default
    a = attr.strip()
    names = {"white":(1,1,1),"black":(0,0,0),"red":(1,0,0),"green":(0,.5,0),"blue":(0,0,1)}
    if a in names: return names[a]
    m = re.fullmatch(r"#([0-9a-fA-F]{3})", a)
    if m: return tuple(int(c*2,16)/255 for c in m.group(1))
    m = re.fullmatch(r"#([0-9a-fA-F]{6})", a)
    if m: return tuple(int(m.group(1)[i:i+2],16)/255 for i in (0,2,4))
    return default

def blend(c, op):  # over white
    return tuple(v*op + (1-op) for v in c)

def num(v, d=0.0):
    try: return float(re.sub(r"[^0-9.\-]", "", v))
    except Exception: return d

def parse_path(d):
    """Return list of (x,y) absolute points + closed flag for M/L/m/l/Z paths."""
    toks = re.findall(r"([MLmlZz])|(-?\d+\.?\d*)", d)
    pts, cur, start, closed = [], (0.0, 0.0), None, False
    i, cmd = 0, None
    vals = []
    for c, v in toks:
        if c: cmd = c; continue
        vals.append(v)
        if cmd in "MmLl" and len(vals) == 2:
            dx, dy = float(vals[0]), float(vals[1])
            if cmd in "ml": x, y = cur[0]+dx, cur[1]+dy
            else: x, y = dx, dy
            if cmd in "Mm" and start is None: start = (x, y)
            pts.append((x, y)); cur = (x, y); vals = []
        elif cmd in "Zz" and vals: vals = []
    if start is not None and pts and pts[-1] != start: closed = True; pts.append(start)
    return pts, closed

def convert(src, dst):
    tree = ET.parse(src); root = tree.getroot()
    W = num(root.get("width", 800)); H = num(root.get("height", 400))
    ops = []
    stats = {"rect":0,"line":0,"text":0,"path":0,"circle":0}
    for el in root.iter():
        tag = el.tag.split("}")[-1]
        if tag == "path":
            pts, closed = parse_path(el.get("d",""))
            if len(pts) < 2: continue
            fill = el.get("fill"); stroke = el.get("stroke")
            fc = color(fill) if fill and fill != "none" else None
            sc = color(stroke) if stroke and stroke != "none" else None
            sw_ = num(el.get("stroke-width","1"), 1.0)
            p = f"{pts[0][0]:.2f} {H-pts[0][1]:.2f} m " + " ".join(f"{x:.2f} {H-y:.2f} l" for x,y in pts[1:]) + (" h" if closed and fc else "")
            if fc is not None:
                ops.append(f"{fc[0]:.3f} {fc[1]:.3f} {fc[2]:.3f} rg {p} f")
            if sc is not None:
                ops.append(f"{sc[0]:.3f} {sc[1]:.3f} {sc[2]:.3f} RG {sw_:.2f} w [] 0 d {p} S")
            stats["path"] += 1
        elif tag == "circle":
            cx, cy, r = num(el.get("cx")), num(el.get("cy")), num(el.get("r"))
            if r <= 0: continue
            fill = el.get("fill"); stroke = el.get("stroke")
            fc = color(fill) if fill and fill != "none" else None
            sc = color(stroke) if stroke and stroke != "none" else None
            k = 0.5523 * r
            seg = (f"{cx+r:.2f} {H-cy:.2f} m "
                   f"{cx+r:.2f} {H-cy+k:.2f} {cx+k:.2f} {H-cy+r:.2f} {cx:.2f} {H-cy+r:.2f} c "
                   f"{cx-k:.2f} {H-cy+r:.2f} {cx-r:.2f} {H-cy+k:.2f} {cx-r:.2f} {H-cy:.2f} c "
                   f"{cx-r:.2f} {H-cy-k:.2f} {cx-k:.2f} {H-cy-r:.2f} {cx:.2f} {H-cy-r:.2f} c "
                   f"{cx+k:.2f} {H-cy-r:.2f} {cx+r:.2f} {H-cy-k:.2f} {cx+r:.2f} {H-cy:.2f} c h")
            if fc is not None:
                ops.append(f"{fc[0]:.3f} {fc[1]:.3f} {fc[2]:.3f} rg {seg} f")
            if sc is not None:
                ops.append(f"{sc[0]:.3f} {sc[1]:.3f} {sc[2]:.3f} RG 1.00 w [] 0 d {seg} S")
            stats["circle"] += 1
        elif tag == "rect":
            x,y = num(el.get("x")), num(el.get("y"))
            w,h = num(el.get("width")), num(el.get("height"))
            if w <= 0 or h <= 0: continue
            fill = el.get("fill"); stroke = el.get("stroke")
            fop = num(el.get("fill-opacity", "1"), 1.0)
            fc = blend(color(fill, (1,1,1)), fop) if fill and fill != "none" else None
            sc = color(stroke) if stroke and stroke != "none" else None
            sw_ = num(el.get("stroke-width", "1"), 1.0)
            yy = H - y - h
            if fc is not None and sc is not None:
                ops.append(f"{fc[0]:.3f} {fc[1]:.3f} {fc[2]:.3f} rg {sc[0]:.3f} {sc[1]:.3f} {sc[2]:.3f} RG {sw_:.2f} w {x:.2f} {yy:.2f} {w:.2f} {h:.2f} re B")
            elif fc is not None:
                ops.append(f"{fc[0]:.3f} {fc[1]:.3f} {fc[2]:.3f} rg {x:.2f} {yy:.2f} {w:.2f} {h:.2f} re f")
            elif sc is not None:
                ops.append(f"{sc[0]:.3f} {sc[1]:.3f} {sc[2]:.3f} RG {sw_:.2f} w {x:.2f} {yy:.2f} {w:.2f} {h:.2f} re S")
            stats["rect"] += 1
        elif tag == "line":
            x1,y1,x2,y2 = (num(el.get(k)) for k in ("x1","y1","x2","y2"))
            sc = color(el.get("stroke")); sw_ = num(el.get("stroke-width","1"), 1.0)
            dash = el.get("stroke-dasharray")
            d = f"[{dash.replace(',', ' ')}] 0 d" if dash else "[] 0 d"
            ops.append(f"{sc[0]:.3f} {sc[1]:.3f} {sc[2]:.3f} RG {sw_:.2f} w {d} {x1:.2f} {H-y1:.2f} m {x2:.2f} {H-y2:.2f} l S")
            stats["line"] += 1
        elif tag == "text":
            txt = latin("".join(el.itertext()))
            if not txt.strip(): continue
            x,y = num(el.get("x")), num(el.get("y"))
            fs = num(el.get("font-size","12"), 12)
            fc = color(el.get("fill"))
            anchor = el.get("text-anchor","start")
            wpt = sw(txt) * fs
            if anchor == "middle": x -= wpt/2
            elif anchor == "end": x -= wpt
            tr = el.get("transform","")
            m = re.match(r"rotate\(\s*(-?[\d.]+)\s+(-?[\d.]+)\s+(-?[\d.]+)\s*\)", tr)
            if m:
                a, cx_, cy_ = float(m.group(1)), float(m.group(2)), float(m.group(3))
                import math as _m
                rad = _m.radians(a); co, si = _m.cos(rad), _m.sin(rad)
                e = cx_ - co*cx_ + si*cy_; f_ = cy_ - si*cx_ - co*cy_
                ops.append(f"BT /F1 {fs:.1f} Tf {fc[0]:.3f} {fc[1]:.3f} {fc[2]:.3f} rg {co:.4f} {si:.4f} {-si:.4f} {co:.4f} {e:.2f} {f_:.2f} Tm ({esc(txt)}) Tj ET")
            else:
                ops.append(f"BT /F1 {fs:.1f} Tf {fc[0]:.3f} {fc[1]:.3f} {fc[2]:.3f} rg {x:.2f} {H-y:.2f} Td ({esc(txt)}) Tj ET")
            stats["text"] += 1
    content = "\n".join(ops).encode("latin-1", "replace")
    objs = []
    objs.append(b"<< /Type /Catalog /Pages 2 0 R >>")
    objs.append(b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>")
    objs.append(f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 {W:.0f} {H:.0f}] /Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>".encode())
    objs.append(b"<< /Length " + str(len(content)).encode() + b" >>\nstream\n" + content + b"\nendstream")
    objs.append(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>")
    out = bytearray(b"%PDF-1.4\n")
    offsets = []
    for i, o in enumerate(objs, 1):
        offsets.append(len(out))
        out += f"{i} 0 obj\n".encode() + o + b"\nendobj\n"
    xref = len(out)
    out += f"xref\n0 {len(objs)+1}\n0000000000 65535 f \n".encode()
    for off in offsets: out += f"{off:010d} 00000 n \n".encode()
    out += f"trailer\n<< /Size {len(objs)+1} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF\n".encode()
    open(dst, "wb").write(out)
    print(f"{src} -> {dst}: {W:.0f}x{H:.0f}pt, {stats}")

if __name__ == "__main__":
    convert(sys.argv[1], sys.argv[2])
