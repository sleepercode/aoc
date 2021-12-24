#!/usr/bin/env python3

import re
from collections import defaultdict

def get_desc():
    return 24, 'Day 24: Arithmetic Logic Unit'

def other_compile(describe, values):
    if describe:
        return "Compile the input to a python function"
    compile_internal(values, True, print)

def other_compile_raw(describe, values):
    if describe:
        return "Compile the input to a python function, skip all shortcuts"
    compile_internal(values, False, print)

def compile_internal(values, collapse, log):
    pos = [0]
    ret = []
    var = [""]
    def handle_inp(g):
        ret.append(None)
        ret.append([f"{g[0]}", f"val[{pos[0]}]"])
        pos[0] += 1
        var[0] = g[0]
    def handle_add(g):
        if var[0] == g[0] and collapse:
            if ret[-1][1] == "":
                ret[-1][1] = g[1]
            else:
                ret[-1][1] = f"({ret[-1][1]} + {g[1]})"
        else:
            ret.append([f"{g[0]}", f"({g[0]} + {g[1]})"])
            var[0] = g[0]
    def handle_mul(g):
        if g[1] == "0" and collapse:
            ret.append([g[0], ""])
            var[0] = g[0]
        else:
            if var[0] == g[0] and collapse:
                ret[-1][1] = f"({ret[-1][1]} * {g[1]})"
            else:
                ret.append([f"{g[0]}", f"({g[0]} * {g[1]})"])
                var[0] = g[0]
    def handle_div(g):
        if (g[1] != "1" and collapse) or not collapse:
            if var[0] == g[0] and collapse:
                ret[-1][1] = f"({ret[-1][1]} // {g[1]})"
            else:
                ret.append([f"{g[0]}", f"({g[0]} // {g[1]})"])
                var[0] = g[0]
    def handle_mod(g):
            if var[0] == g[0] and collapse:
                ret[-1][1] = f"({ret[-1][1]} % {g[1]})"
            else:
                ret.append([f"{g[0]}", f"({g[0]} % {g[1]})"])
                var[0] = g[0]
    def handle_eql(g):
        if g[1] == "0" and g[0] == ret[-1][0] and "==" in ret[-1][1] and collapse:
            ret[-1][1] = ret[-1][1][-1] + ret[-1][1][1:-1] + ret[-1][1][0]
            pass
        else:
            ret.append([f"{g[0]}", f"1 if {g[0]} == {g[1]} else 0"])

    log("def compiled(val, var_output=None):")
    log("    x = 0")
    log("    w = 0")
    log("    y = 0")
    log("    z = 0")

    for cur in values:
        m = re.search("^([a-z]+) ([a-z]+)$", cur)
        if m is not None:
            handle_inp(m.groups()[1:])
        else:
            m = re.search("^([a-z]+) ([a-z]+) ([a-z0-9-]+)$", cur)
            x, g = m.group(1), m.groups()[1:]
            if x == "add": handle_add(g)
            elif x == "div": handle_div(g)
            elif x == "mul": handle_mul(g)
            elif x == "mod": handle_mod(g)
            elif x == "eql": handle_eql(g)
            else:
                raise Exception()

    use = 0
    line = 0
    for cur in ret:
        if cur is None:
            use += 1
            log("")
            log(f"    if val[{use-1}] is not None:")
        else:
            x, y = cur
            if collapse:
                if y.startswith("("):
                    y = y[1:-1]
                y = y.replace("+ -", "- ")
            log("        " + x + " = " + y)
            if not collapse:
                log(f"        if var_output is not None: var_output({line}, {use-1}, '{values[line] if line < len(values) else '--'}', x, y, w, z)")
            line += 1

    log("")
    log("    return z")

    return 0

"""
This next function is a placeholder to make autocomplete happy.  It's really compilied 
at runtime using the helper above to something like this:

def compiled(val, var_output=None):
    x = 0
    w = 0
    y = 0
    z = 0

    if val[0] is not None:
        w = val[0]
        x = (z % 26) + 10
        x = 0 if x == w else 1
        y = (25 * x) + 1
        z = z * y
        y = (w + 12) * x
        z = z + y

    # ... removed most digits ...

    if val[13] is not None:
        w = val[13]
        x = z % 26
        z = z // 26
        x = x - 14
        x = 0 if x == w else 1
        y = (25 * x) + 1
        z = z * y
        y = (w + 13) * x
        z = z + y

    return z
"""
def compiled(val, var_output=None):
    print("Place holder function, replaced at runtime")
    return True

def other_animate(describe, values):
    if describe:
        return "Animate this"

    from PIL import ImageDraw, ImageFont, Image
    from dummylog import DummyLog
    from grid import Grid
    import animate
    animate.prep()
    grid = Grid()

    attempts = calc(DummyLog(), values, 2, True)

    data = []
    def helper_log(x):
        data.append(x)
    compile_internal(values, False, log=helper_log)
    # print(data)
    exec("\n".join(data), globals())

    digits = [[] for _ in range(14)]
    line_to_digit = {}
    to_line_no = {}
    total_lines = [0]
    skip = [-1]
    skip_amt = [10]

    def grab_desc(line_no, group_no, line, x, y, w, z):
        to_line_no[(group_no, len(digits[group_no]))] = line_no
        digits[group_no].append(line)
        total_lines[0] = max(total_lines[0], len(digits[group_no]))
    compiled([1] * 14, var_output=grab_desc)

    font = grid.get_font(10)
    font_w, font_h = grid.get_font_size(10)

    frame_no = [0]
    val = [None] * 14
    to_show = set()
    locked = set()
    testing = set()

    def draw_step(line_no, group_no, line, x, y, w, z):
        if group_no not in to_show:
            return
        skip[0] += 1
        if skip[0] % skip_amt[0] != 0:
            return

        im = Image.new('RGB', (1270, 409), (0, 0, 0))
        dr = ImageDraw.Draw(im)
        xy = [5, 5]

        for off in testing | locked:
            dr.rectangle((
                5 + font_w * (off * 10), 
                5 + font_h * 1,
                5 + font_w * ((off + 1) * 10),
                5 + font_h * (3 + 18),
            ), (0, 0, 100) if off in testing else (90, 60, 0))

        def add_line(msg, bright=None):
            if bright is None:
                dr.text(xy, msg, (255, 255, 255), font)
            else:
                dr.text(xy, msg, (128, 128, 128), font)
                dr.text(xy, bright, (255, 255, 255), font)
            xy[1] += font_h

        add_line(f"x, y, z, w = {x}, {y}, {z}, {w}")
        line = ""
        for digit in range(14):
            line += f" Digit {digit:2d} "
        add_line(line)
        # print("width", len(line) * font_w)

        line = ""
        for digit in range(14):
            if val[digit] is None:
                line += "  (none)  "
            else:
                line += f"     {val[digit]}    "
        add_line(line)

        for row in range(total_lines[0]):
            line = ""
            line_bright = ""
            for digit in range(14):
                part = f"{digits[digit][row]:<10}"
                line += part
                if to_line_no[(digit, row)] == line_no:
                    line_bright += part
                else:
                    line_bright += " " * len(part)
            add_line(line, line_bright)

        # print("height", xy[1] + 5)

        im.save(f"frame_{frame_no[0]:05d}.png")
        frame_no[0] += 1

    skip_amt[0] = 4
    for a, b, use1, use2 in attempts:
        if (use1 not in testing) or (use2 not in testing):
            for x in [x for x in testing]:
                testing.remove(x)
                locked.add(x)
            testing.add(use1)
            testing.add(use2)
        val[use1] = a
        val[use2] = b
        print(" ".join("-" if x is None else str(x) for x in val))
        to_show.add(use1)
        to_show.add(use2)
        compiled(val, var_output=draw_step)
        to_show.remove(use1)
        to_show.remove(use2)

    for x in [x for x in testing]:
        testing.remove(x)
        locked.add(x)
    skip[0] = -1
    skip_amt[0] = 1
    [locked.add(x) for x in range(14)]
    [testing.remove(x) for x in range(14) if x in testing]
    [to_show.add(x) for x in range(14)]
    compiled(val, var_output=draw_step)

    animate.create_mp4(get_desc(), rate=30)
        

def calc(log, values, mode, ret_attempts=False):
    data = []
    def helper_log(x):
        data.append(x)
    compile_internal(values, True, log=helper_log)
    exec("\n".join(data), globals())

    def tryout(use1, use2, val, possible):
        for a in range(1, 10):
            for b in range(1, 10):
                val[use1] = a
                val[use2] = b
                if compiled(val) == 0:
                    possible.append((a, b, use1, use2, True))
                else:
                    possible.append((a, b, use1, use2, False))
        val[use1] = None
        val[use2] = None

    def level(depth, apply, val, attempts):
        if apply is not None:
            a, b, use1, use2, valid = apply
            attempts.append((a, b, use1, use2))
            if valid:
                val[use1] = a
                val[use2] = b
                if sum(1 for x in val if x is None) == 0:
                    return val, attempts
            else:
                return None
        attempts = attempts[:]
        use1 = val.index(None)
        use2 = 13 - val[::-1].index(None)
        possible = []
        tryout(use1, use2, val, possible)
        if sum(x[4] for x in possible) == 0:
            use1 = val.index(None)
            use2 = val[use1+1:].index(None) + use1 + 1
            tryout(use1, use2, val, possible)
        possible.sort(reverse=mode==1)
        for x in possible:
            ret = level(depth + 1, x, val[:], attempts)
            if ret is not None:
                return ret
        return None
    
    val, attempts = level(0, None, [None for _ in range(14)], [])
    if ret_attempts:
        return attempts
    return "".join(str(x) for x in val)

def test(log):
    log("No test")

def run(log, values):
    log(calc(log, values, 1))
    log(calc(log, values, 2))
