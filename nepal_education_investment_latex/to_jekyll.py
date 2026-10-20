#!/usr/bin/env python3
"""Convert main.tex (+ tab_*.tex, refs.bib) into a Jekyll post for the website.

Handles only the LaTeX this paper uses. Re-run after editing the paper:
    python3 nepal_education_investment_latex/to_jekyll.py
Figures must be rendered to PNG in the post assets dir first:
    pdftoppm -png -r 200 -singlefile fig_X.pdf <assets>/fig_X
"""
import html
import pathlib
import re

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent
OUT = ROOT / "_posts/2026-10-20-Public-Investment-in-School-Education-Nepal.html"
PDF = "Public_Investment_in_School_Education_Nepal.pdf"

MONTHS = dict(jan="January", feb="February", mar="March", apr="April", may="May", jun="June",
              jul="July", aug="August", sep="September", oct="October", nov="November", dec="December")


# ---------------------------------------------------------------- helpers

def braced(s, i):
    """s[i] == '{'; return (content, index after closing brace)."""
    assert s[i] == "{", s[i:i + 30]
    depth = 0
    for j in range(i, len(s)):
        if s[j] == "{" and (j == 0 or s[j - 1] != "\\"):
            depth += 1
        elif s[j] == "}" and s[j - 1] != "\\":
            depth -= 1
            if depth == 0:
                return s[i + 1:j], j + 1
    raise ValueError("unbalanced braces: " + s[i:i + 60])


def replace_cmd(s, name, fn):
    """Replace \\name{arg} (brace-matched) with fn(arg)."""
    pat = re.compile(r"\\" + name + r"\s*(?=\{)")
    while True:
        m = pat.search(s)
        if not m:
            return s
        arg, end = braced(s, m.end())
        s = s[:m.start()] + fn(arg) + s[end:]


def slug(label):
    return re.sub(r"[^a-z0-9]+", "-", label.lower()).strip("-")


# ---------------------------------------------------------------- bibliography

def parse_bib(text):
    entries = {}
    for m in re.finditer(r"@(\w+)\{([^,]+),", text):
        kind, key, i = m.group(1), m.group(2).strip(), m.end()
        fields = {}
        while True:
            while i < len(text) and text[i] in " \n\t,":
                i += 1
            if text[i] == "}":
                break
            eq = text.index("=", i)
            name = text[i:eq].strip().lower()
            i = eq + 1
            if text[i] == "{":
                val, i = braced(text, i)
            else:
                j = i
                while text[j] not in ",}":
                    j += 1
                val, i = text[i:j].strip(), j
            fields[name] = val
        entries[key] = (kind, fields)
    return entries


def format_ref(kind, f):
    parts = [f.get("author", ""), f.get("title", "")]
    month = f.get("month", "")
    month = MONTHS.get(month.lower(), month)
    date = " ".join(x for x in (month, f.get("year", "")) if x)
    if kind == "techreport":
        parts.append(", ".join(x for x in ("Technical report", f.get("institution"), date) if x))
    elif kind == "incollection":
        parts.append("In <em>" + f.get("booktitle", "") + "</em>")
        parts.append(", ".join(x for x in (f.get("publisher"), f.get("address"), date) if x))
    else:
        parts.append(", ".join(x for x in (f.get("howpublished"), date) if x))
    if f.get("note"):
        parts.append(f["note"])
    return " ".join(p if p[-1] in ".!?" else p + "." for p in (p.strip() for p in parts) if p)


# ---------------------------------------------------------------- main conversion

class Converter:
    def __init__(self):
        tex = (HERE / "main.tex").read_text()
        tex = re.sub(r"\\csname @@input\\endcsname\s+(\S+)",
                     lambda m: (HERE / m.group(1)).read_text(), tex)
        tex = re.sub(r"(?<!\\)%.*", "", tex)  # comments
        self.title_raw = re.search(r"\\title\{\\textbf\{(.*?)\}\\\\\[4pt\]\\large (.*?)\}\n", tex)
        self.body = tex[tex.index("\\maketitle") + len("\\maketitle"):tex.index("\\bibliographystyle")]
        self.bib = parse_bib((HERE / "refs.bib").read_text())
        self.labels = {}
        self.cite_order = []
        self.toc = []
        self.number_things()

    def number_things(self):
        sec = sub = fig = tab = 0
        current, in_float = None, None
        pat = re.compile(r"\\(section|subsection)\{|\\begin\{(figure|table)\}|\\end\{(figure|table)\}"
                         r"|\\label\{([^}]*)\}|\\cite\{([^}]*)\}")
        for m in pat.finditer(self.body):
            if m.group(1) == "section":
                sec, sub = sec + 1, 0
                current = str(sec)
            elif m.group(1) == "subsection":
                sub += 1
                current = f"{sec}.{sub}"
            elif m.group(2) == "figure":
                fig += 1
                in_float = str(fig)
            elif m.group(2) == "table":
                tab += 1
                in_float = str(tab)
            elif m.group(3):
                in_float = None
            elif m.group(4):
                self.labels[m.group(4)] = in_float or current
            else:
                for k in m.group(5).split(","):
                    if k.strip() not in self.cite_order:
                        self.cite_order.append(k.strip())

    # ---- inline text
    def cite(self, keys):
        nums = sorted(self.cite_order.index(k.strip()) + 1 for k in keys.split(","))
        link = lambda n: f'<a href="#ref-{slug(self.cite_order[n - 1])}">{n}</a>'
        out, i = [], 0
        while i < len(nums):
            j = i
            while j + 1 < len(nums) and nums[j + 1] == nums[j] + 1:
                j += 1
            if j - i >= 2:
                out.append(link(nums[i]) + "–" + link(nums[j]))
            else:
                out.extend(link(n) for n in nums[i:j + 1])
            i = j + 1
        return '<span class="cite">[' + ", ".join(out) + "]</span>"

    def inline(self, s):
        keep = []

        def hold(x):
            keep.append(x)
            return f"\x00{len(keep) - 1}\x00"

        s = s.replace("\\$", hold("$")).replace("\\&", hold("&amp;"))
        s = replace_cmd(s, "url", lambda u: hold(
            '<a href="{0}">{0}</a>'.format(html.escape(u.replace("\\%", "%").replace("\\_", "_")))))
        s = re.sub(r"\\cite\{([^}]*)\}", lambda m: hold(self.cite(m.group(1))), s)
        s = re.sub(r"\\ref\{([^}]*)\}",
                   lambda m: hold(f'<a href="#{slug(m.group(1))}">{self.labels[m.group(1)]}</a>'), s)
        s = re.sub(r"\\label\{[^}]*\}", "", s)
        s = html.escape(s, quote=False)
        s = re.sub(r"\$([^$]*)\$", lambda m: hold(self.math(m.group(1))), s)
        s = replace_cmd(s, "textbf", lambda a: "<strong>" + a + "</strong>")
        s = replace_cmd(s, "emph", lambda a: "<em>" + a + "</em>")
        s = replace_cmd(s, "text", lambda a: a)
        for a, b in [("``", "“"), ("''", "”"), ("`", "‘"), ("---", "—"), ("--", "–"),
                     ("~", "&nbsp;"), ("\\%", "%"), ("\\ ", " "), ("\\quad", "&emsp;"),
                     ("\\noindent", ""), ("\\ldots", "…")]:
            s = s.replace(a, b)
        s = s.replace("{", "").replace("}", "")
        s = re.sub(r"\s+", " ", s).strip()
        while "\x00" in s:
            s = re.sub(r"\x00(\d+)\x00", lambda m: keep[int(m.group(1))], s)
        return s

    @staticmethod
    def math(m):
        for a, b in [("^\\ast", "<sup>*</sup>"), ("^\\dagger", "<sup>†</sup>"), ("\\div", "÷"),
                     ("\\times", "×"), ("-", "−"), ("\\ldots", "…")]:
            m = m.replace(a, b)
        return m.strip()

    # ---- blocks
    def paragraphs(self, text):
        out = []
        for para in re.split(r"\n\s*\n", text):
            if para.strip():
                out.append("<p>" + self.inline(para) + "</p>")
        return out

    def items(self, text, tag):
        text = re.sub(r"^\[[^\]]*\]", "", text.strip())
        items = [self.inline(x) for x in re.split(r"\\item\b", text) if x.strip()]
        return [f"<{tag}>" + "".join("<li>" + i + "</li>" for i in items) + f"</{tag}>"]

    def figure(self, text):
        src = re.search(r"\\includegraphics(?:\[[^\]]*\])?\{([^}]*)\}", text).group(1)
        src = src.replace(".pdf", ".png")
        label = re.search(r"\\label\{([^}]*)\}", text).group(1)
        cap = self.caption(text)
        return [f'<figure id="{slug(label)}">'
                f'<a href="{{{{ page.post_assets | relative_url }}}}/{src}">'
                f'<img src="{{{{ page.post_assets | relative_url }}}}/{src}" alt="Figure {self.labels[label]}"></a>'
                f"<figcaption><strong>Figure {self.labels[label]}.</strong> {self.inline(cap)}</figcaption></figure>"]

    def caption(self, text):
        i = text.index("\\caption")
        return braced(text, text.index("{", i))[0]

    def table(self, text):
        label = re.search(r"\\label\{([^}]*)\}", text).group(1)
        cap = self.caption(text)
        m = re.search(r"\\begin\{(tabularx?)\}", text)
        env = m.group(1)
        i = m.end()
        if env == "tabularx":
            _, i = braced(text, i)
        spec, i = braced(text, i)
        end = text.index("\\end{" + env + "}")
        rows_src = text[i:end]
        notes = text[end + len("\\end{" + env + "}"):]
        notes = re.sub(r"\\(par|smallskip|raggedright|footnotesize|small)\b", "", notes).strip()

        spec = re.sub(r">\{[^{}]*(\{[^}]*\})?[^{}]*\}", "", spec)
        spec = re.sub(r"p\{[^}]*\}", "l", spec)
        aligns = ["right" if c in "rR" else "center" if c == "c" else "left" for c in spec if c in "lrcLRX"]

        head_src, _, body_src = rows_src.partition("\\midrule")
        head_src = head_src.replace("\\toprule", "")
        body_src = body_src.replace("\\bottomrule", "")

        def rows(src, cell_tag):
            out = []
            src = re.sub(r"\\cmidrule(\([^)]*\))?\{[^}]*\}", "", src)
            src = src.replace("\\&", "\x01")
            for row in re.split(r"\\\\", src):
                if not row.strip():
                    continue
                cells, col = [], 0
                for cell in row.split("&"):
                    cell = cell.replace("\x01", "\\&").strip()
                    mc = re.match(r"\\multicolumn\{(\d+)\}\{\w\}\{(.*)\}$", cell)
                    span = int(mc.group(1)) if mc else 1
                    content = mc.group(2) if mc else cell
                    align = "center" if mc else aligns[min(col, len(aligns) - 1)]
                    attrs = f' colspan="{span}"' if span > 1 else ""
                    cells.append(f'<{cell_tag}{attrs} class="{align}">{self.inline(content)}</{cell_tag}>')
                    col += span
                out.append("<tr>" + "".join(cells) + "</tr>")
            return "".join(out)

        html_ = (f'<div class="paper-table" id="{slug(label)}">'
                 f'<p class="table-caption"><strong>Table {self.labels[label]}.</strong> {self.inline(cap)}</p>'
                 f'<div class="table-wrap"><table><thead>{rows(head_src, "th")}</thead>'
                 f"<tbody>{rows(body_src, 'td')}</tbody></table></div>")
        if notes:
            html_ += f'<p class="table-note">{self.inline(notes)}</p>'
        return [html_ + "</div>"]

    def align(self, text):
        out = []
        for line in re.split(r"\\\\", text):
            if not line.strip():
                continue
            lhs, rhs = line.split("&=")
            num, den = re.match(r"\s*\\frac\{\\text\{(.*?)\}\}\{\\text\{(.*?)\}\}", rhs).groups()
            out.append(f'<div class="eq-row"><span>{self.inline(lhs)}</span><span>=</span>'
                       f'<span class="frac"><span>{self.inline(num)}</span><span>{self.inline(den)}</span></span></div>')
        return ['<div class="equation">' + "".join(out) + "</div>"]

    def convert(self):
        out = []
        body = self.body
        pat = re.compile(r"\\begin\{(abstract|itemize|enumerate|figure|table|align\*)\}(\[[^\]]*\])?"
                         r"|\\(section|subsection)\{")
        pos = 0
        while True:
            m = pat.search(body, pos)
            out += self.paragraphs(body[pos:m.start()] if m else body[pos:])
            if not m:
                break
            if m.group(3):
                title, end = braced(body, m.end() - 1)
                lm = re.match(r"\s*\\label\{([^}]*)\}", body[end:])
                level = 2 if m.group(3) == "section" else 3
                if lm:
                    anchor, number = slug(lm.group(1)), self.labels[lm.group(1)]
                    end += lm.end()
                else:
                    number = self.next_number(level)
                    anchor = "s-" + number.replace(".", "-")
                self.last_number = number
                t = self.inline(title)
                self.toc.append((level, anchor, number, t))
                out.append(f'<h{level} id="{anchor}">{number}&ensp;{t}</h{level}>')
                pos = end
                continue
            env = m.group(1)
            close = "\\end{" + env + "}"
            end = body.index(close, m.end())
            inner = body[m.end():end]
            pos = end + len(close)
            if env == "abstract":
                self.abstract = self.inline(inner)
            elif env in ("itemize", "enumerate"):
                out += self.items(inner, "ul" if env == "itemize" else "ol")
            elif env == "figure":
                out += self.figure(inner)
            elif env == "table":
                out += self.table(inner)
            else:
                out += self.align(inner)
        return out

    last_number = "0"

    def next_number(self, level):
        parts = self.last_number.split(".")
        if level == 2:
            return str(int(parts[0]) + 1)
        if len(parts) == 1:
            return parts[0] + ".1"
        return f"{parts[0]}.{int(parts[1]) + 1}"

    def render(self):
        body = self.convert()
        subtitle = self.inline(self.title_raw.group(2))
        pdf = "{{ page.post_assets | relative_url }}/" + PDF

        toc, open_sub = ["<ol>"], False
        for level, anchor, number, title in self.toc:
            if level == 3 and not open_sub:
                toc[-1] = toc[-1].removesuffix("</li>")
                toc.append("<ol>")
                open_sub = True
            elif level == 2 and open_sub:
                toc.append("</ol></li>")
                open_sub = False
            toc.append(f'<li><a href="#{anchor}">{number}&ensp;{title}</a></li>')
        toc.append("</ol></li>" if open_sub else "")
        toc.append(f'<li><a href="#references">References</a></li></ol>')

        refs = []
        for n, key in enumerate(self.cite_order, 1):
            kind, fields = self.bib[key]
            refs.append(f'<li id="ref-{slug(key)}">{self.inline(format_ref(kind, fields))}</li>')

        return "\n".join([
            "---",
            "layout: post",
            'title: "Public Investment in School Education in Nepal"',
            "co_written_with_ai: true",
            "post_assets: /assets/posts/2026-10-20-nepal-education",
            "# Generated by nepal_education_investment_latex/to_jekyll.py from main.tex -- edit the LaTeX, not this file.",
            "---",
            '<div class="paper">',
            f'<p class="paper-subtitle">{subtitle}</p>',
            f'<p class="paper-actions"><a class="paper-button" href="{pdf}" download>Download PDF</a>'
            f'<a class="paper-button secondary" href="{pdf}">Open PDF in browser</a></p>',
            f'<section class="paper-abstract"><h2>Abstract</h2><p>{self.abstract}</p></section>',
            '<nav class="paper-toc"><details open><summary>Contents</summary>' + "".join(toc) + "</details></nav>",
            *body,
            '<h2 id="references">References</h2>',
            '<ol class="paper-references">', *refs, "</ol>",
            "</div>",
            "",
        ])


if __name__ == "__main__":
    OUT.write_text(Converter().render())
    print("wrote", OUT.relative_to(ROOT))
