#!/usr/bin/env python3
"""Regenerate the keyword data from the nextnano++ documentation.

The docs are built with Sphinx, whose searchindex.js carries both the page tree
(docnames such as user_guide/keywords/quantum/region/output_states) and every
section title verbatim ("gaussian_spectrum{ energy }", "direction_x"). That is
the whole keyword hierarchy in one fetch. A second pass over the keyword pages
picks up names that are documented in tables rather than headings, which is how
database{ } spells out most of its material parameters.

A name counts as a group (takes a brace) only if the docs write it as "name{ }"
or give it a sub-page; everything else is an attribute. Guessing from "has
children" would promote attributes such as carrier_statistics -- whose page
lists its allowed values -- into groups, and every real use would then be
flagged as unknown.

Writes syntax/nextnano_keywords.vim and lua/nextnano/keywords.lua.
"""

import json
import re
import sys
import urllib.request
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

BASE = "https://www.nextnano.com/docu/nextnanoplus/latest/"
KEYWORD_PREFIX = "user_guide/keywords/"
ROOT = "<root>"

FUNCTIONS = """
sqrt cbrt exp log ln log2 log10 sin cos tan asin acos atan sinh cosh tanh
asinh acosh atanh erf erfc gamma fdm3half fdmhalf fdzero fdphalf fdp3half
abs floor ceil round sign heaviside ispositive isnegative iszero
isnotpositive isnotnegative isnotzero string dim
""".split()

BOOLEANS = ["yes", "no"]

IDENT = re.compile(r"^[A-Za-z_]\w*$")
# Prose headings that live on keyword pages alongside the real keyword sections.
HEADING = {
    "Example", "Examples", "Keywords", "Maintained Keywords", "General", "Note",
    "Notes", "Syntax", "Attributes", "attributes", "Functionality", "Description",
    "Output", "Remark", "Remarks", "Introduction", "Usage", "Units", "Default",
}
# The docs abbreviate sibling keywords in a single heading or page name.
SHORTHAND = {
    "array_x_y_z": ["array_x", "array_y", "array_z"],
    "array2_x_y_z": ["array2_x", "array2_y", "array2_z"],
    "Gamma_L_X_Delta_HH_LH_SO": ["Gamma", "L", "X", "Delta", "HH", "LH", "SO"],
    "Gamma_HH_LH_SO": ["Gamma", "HH", "LH", "SO"],
    "quantize_x_y_z": ["quantize_x", "quantize_y", "quantize_z"],
    "classical_boundary_x": ["classical_boundary_x", "classical_boundary_y",
                             "classical_boundary_z"],
    "num_classical_x": ["num_classical_x", "num_classical_y", "num_classical_z"],
    "x_y_z": ["x", "y", "z"],
    "xgrid_ygrid_zgrid": ["xgrid", "ygrid", "zgrid"],
}

CODE_LITERAL = re.compile(r'<code[^>]*class="[^"]*docutils[^"]*"[^>]*>(.*?)</code>', re.S)
EXAMPLE = re.compile(r"<pre>(.*?)</pre>", re.S)
# An identifier in group or attribute position, or a closing brace.
EXAMPLE_TOKEN = re.compile(r"(?<![\w$])([A-Za-z_]\w*)\s*([{=])|(\})")
TAG = re.compile(r"<[^>]+>")


def fetch(url):
    with urllib.request.urlopen(url, timeout=60) as r:
        return r.read().decode("utf-8", "replace")


def load_index():
    raw = fetch(BASE + "searchindex.js")
    return json.loads(raw[raw.index("(") + 1:raw.rindex(")")])


def expand(name):
    """One documentation name -> the real keyword name(s) it stands for."""
    name = name.strip()
    if name in SHORTHAND:
        return SHORTHAND[name]
    if name in HEADING or not IDENT.match(name):
        return []
    return [name]


def build_tree(index):
    """-> children {path: {name}}, is_group {name}, pages {url: [path]}."""
    children = defaultdict(set)
    is_group = set()
    pages = {}  # url -> list of node paths the page documents

    docs = {}  # docname index -> list of node paths
    introduced = {}  # docname index -> group nodes the page's titles create
    leaves = {}  # docname index -> (parent path, leaf name)
    for i, docname in enumerate(index["docnames"]):
        if not docname.startswith(KEYWORD_PREFIX):
            continue
        parts = docname[len(KEYWORD_PREFIX):].split("/")
        if parts[-1] == "index":
            parts = parts[:-1]

        parent = (ROOT,)
        for part in parts[:-1]:
            names = expand(part)
            if not names:
                break
            is_group.update(names)  # owning a sub-page means it takes a brace
            children[parent].add(names[0])
            parent = parent + (names[0],)
        else:
            leaves[i] = (parent, parts[-1] if parts else None)
            pages[BASE + docname + ".html"] = []

    documented = set()
    for title, refs in index["alltitles"].items():
        if any(ref[0] in leaves for ref in refs):
            documented.update(re.findall(r"[A-Za-z_]\w*", title))

    for i, (parent, leaf) in leaves.items():
        # Some keywords get extra pages named after a sibling plus a topic,
        # "structure/region_shapes" documenting more of structure{ region{} }.
        # Their titles belong to the sibling, not to a keyword of their own.
        owner = None
        if leaf and "_" in leaf and leaf not in documented:
            bits = leaf.split("_")
            for cut in range(len(bits) - 1, 0, -1):
                candidate = "_".join(bits[:cut])
                if candidate in children.get(parent, ()):
                    owner = parent + (candidate,)
                    break
        if owner:
            nodes = [owner]
        else:
            # A page named for prose rather than a keyword ("region/attributes")
            # documents its parent, so hang its titles on the parent node.
            nodes = [parent + (n,) for n in expand(leaf)] if leaf else []
            nodes = nodes or [parent]
            for node in nodes:
                if len(node) > 1:
                    children[parent].add(node[-1])
        docs[i] = nodes

    titles = defaultdict(list)
    for title, refs in index["alltitles"].items():
        for ref in refs:
            if ref[0] in docs:
                titles[ref[0]].append(title)

    for i, nodes in docs.items():
        for title in titles.get(i, ()):
            if "{" in title:
                is_group.update(re.findall(r"([A-Za-z_]\w*)\s*\{", title))
                # "xgrid{ line{ pos } }" nests left to right, so the plain
                # identifier order is the path; the braces only say which of
                # them are groups.
                chain = re.findall(r"[A-Za-z_]\w*", title)
                for node in nodes:
                    # A title may repeat the page's own ancestry, "optics{ x{ } }".
                    rest = list(chain)
                    while rest and rest[0] in node:
                        rest.pop(0)
                    base = node
                    for name in rest:
                        names = expand(name)
                        for real in names:
                            children[base].add(real)
                        if not names:
                            break
                        base = base + (names[0],)
                        introduced.setdefault(i, set()).add(base)
            else:
                for part in re.split(r",\s*", title):
                    for real in expand(part):
                        for node in nodes:
                            children[node].add(real)

    # A page also documents the groups its own titles introduce, so the recall
    # pass can hand table-documented attributes to them and not just to the
    # page's node ("region_shapes" documents rectangle{ }, circle{ }, ...).
    for url in list(pages):
        i = index["docnames"].index(url[len(BASE):-len(".html")])
        pages[url] = docs[i] + sorted(introduced.get(i, ()))

    return children, is_group, pages


def parse_example(text, base, children, is_group, top_level, strict=False):
    """Read a documentation example the way the syntax file reads a file:
    "name{" opens a group, "name =" is an attribute of the group in scope.
    Most shape and material keywords are documented only this way."""
    text = re.sub(r"#[^\n]*", "", text)
    stack = [base]
    started = not strict
    for name, sym, close in EXAMPLE_TOKEN.findall(text):
        if close:
            if len(stack) > 1:
                stack.pop()
        elif sym == "{":
            if len(stack) == 1 and name in top_level:
                stack = [(ROOT,)]  # the example starts from the file scope
                started = True
            elif not started:
                continue
            children[stack[-1]].add(name)
            is_group.add(name)
            stack.append(stack[-1] + (name,))
        elif started:
            children[stack[-1]].add(name)


def recall_pass(children, is_group, pages):
    """Add names the docs only spell out inside tables (database{ } mostly)."""
    top_level = set(children[(ROOT,)])

    def grab(url):
        try:
            return url, fetch(url)
        except Exception as exc:  # one missing page must not sink the run
            print(f"  skip {url}: {exc}", file=sys.stderr)
            return url, ""

    with ThreadPoolExecutor(max_workers=8) as pool:
        for url, html in pool.map(grab, list(pages)):
            tokens = set()
            for literal in CODE_LITERAL.findall(html):
                token = TAG.sub("", literal).strip()
                if IDENT.match(token) and token not in FUNCTIONS and token not in BOOLEANS:
                    tokens.add(token)
            for node in pages[url]:
                # An attribute page lists its allowed values, not its children:
                # those names belong to the enclosing group.
                target = node if node[-1] in is_group else node[:-1]
                if len(target) > 1 or node[-1] in is_group:
                    children[target] |= tokens
                for example in EXAMPLE.findall(html):
                    text = TAG.sub("", example).replace("&quot;", '"')
                    text = text.replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")
                    parse_example(text, target, children, is_group, top_level)


def mirror_axes(children):
    """ygrid{ } and zgrid{ } are documented as "same as xgrid{ }"."""

    def copy_subtree(src, dst):
        for kid in children.get(src, ()):
            children[dst].add(kid)
            copy_subtree(src + (kid,), dst + (kid,))

    for node in sorted(children, key=len):
        for kid in sorted(children[node]):
            if children.get(node + (kid,)):
                continue
            for twin in (re.sub(r"^[yz]", "x", kid), re.sub(r"_[yz]$", "_x", kid)):
                if twin != kid and children.get(node + (twin,)):
                    copy_subtree(node + (twin,), node + (kid,))
                    break


def example_pass(children, is_group, top_level, urls):
    """The tutorials embed complete input files; they are the only place some
    keywords are ever shown."""

    def grab(url):
        try:
            return fetch(url)
        except Exception:
            return ""

    with ThreadPoolExecutor(max_workers=8) as pool:
        for html in pool.map(grab, urls):
            for example in EXAMPLE.findall(html):
                text = TAG.sub("", example).replace("&quot;", '"')
                text = text.replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")
                parse_example(text, (ROOT,), children, is_group, top_level, strict=True)


def prune(children):
    """Drop self-references and anything that named an ancestor."""
    for node in list(children):
        children[node] -= set(node)
        if not children[node]:
            del children[node]


def vim_group(path):
    return "nnG_" + "_".join(path[1:])


def wrap(prefix, words, width=96):
    lines, cur = [], prefix
    for word in words:
        if len(cur) + len(word) + 1 > width and cur != prefix:
            lines.append(cur)
            cur = prefix
        cur += " " + word
    if cur != prefix:
        lines.append(cur)
    return lines


def emit_vim(children, is_group, out):
    lines = [
        '" Generated by tools/gen_keywords.py -- do not edit.',
        '" Source: ' + BASE + KEYWORD_PREFIX,
        "",
    ]
    # Every group is a region, even one with nothing documented inside it:
    # a group spelled as a bare keyword would leave its braces to the enclosing
    # region, and "global{ simulate3D{} ... }" would end at the inner brace.
    nodes = set(children)
    for node, kids in children.items():
        nodes |= {node + (k,) for k in kids if k in is_group}
    nodes.discard((ROOT,))

    # Deepest node first: Vim gives priority to the item defined last, so a
    # parent region must be defined after the children it contains.
    for node in sorted(nodes, key=lambda p: (-len(p), p)):
        kids = sorted(children.get(node, ()))
        groups = [k for k in kids if k in is_group]
        attrs = [k for k in kids if k not in is_group]

        grp = vim_group(node)
        contains = [vim_group(node + (k,)) for k in groups]
        if attrs:
            contains.append(grp + "_attr")
        if groups:
            contains.append(grp + "_gattr")
        contains += ["@nextnanoCommon", "nextnanoUnknown", "nextnanoUnknownGroup"]

        lines.append(
            'syn region {} matchgroup=nextnanoGroupName start="\\<{}\\>\\_s*{{" '
            'matchgroup=nextnanoDelim end="}}" fold{}'.format(
                grp, node[-1], "" if len(node) == 2 else " contained"))
        lines.append("      \\ contains=" + ",".join(contains))
        if attrs:
            lines += wrap("syn keyword {}_attr contained".format(grp), attrs)
            lines.append("hi def link {}_attr nextnanoAttribute".format(grp))
        if groups:
            # Some keywords are written both as "SRH{ }" and as "SRH = yes".
            # A keyword list would take priority over the group's own region and
            # stop it opening, so accept the second form as a match instead.
            lines.append('syn match {}_gattr "\\<\\%({}\\)\\>\\ze\\s*=" contained'.format(
                grp, "\\|".join(groups)))
            lines.append("hi def link {}_gattr nextnanoAttribute".format(grp))
        lines.append("")

    out.write_text("\n".join(lines) + "\n")


def emit_lua(children, is_group, out):
    """tree: path -> children; groups: syntax group name -> path (the syntax
    group name alone is ambiguous, keyword names contain underscores too)."""
    body = ["-- Generated by tools/gen_keywords.py -- do not edit.", "return {", "  tree = {"]
    for node in sorted(children):
        entries = ", ".join(
            '{{"{}","{}"}}'.format(k, "g" if k in is_group else "a")
            for k in sorted(children[node]))
        body.append('    ["{}"] = {{{}}},'.format(".".join(node[1:]), entries))
    body += ["  },", "  groups = {"]
    for node in sorted(children):
        if len(node) > 1:
            body.append('    {} = "{}",'.format(vim_group(node), ".".join(node[1:])))
    body += ["  },", "}"]
    out.write_text("\n".join(body) + "\n")


def main():
    repo = Path(__file__).resolve().parent.parent
    print("fetching searchindex.js ...")
    index = load_index()
    children, is_group, pages = build_tree(index)
    print(f"  {len(children)} nodes, {sum(len(v) for v in children.values())} edges")
    print(f"fetching {len(pages)} keyword pages ...")
    mirror_axes(children)  # before the recall pass, which would fill the
    recall_pass(children, is_group, pages)  # y/z twins with noise and hide it
    rest = [BASE + n + ".html" for n in index["docnames"]
            if not n.startswith(KEYWORD_PREFIX)]
    print(f"reading examples from {len(rest)} further pages ...")
    example_pass(children, is_group, set(children[(ROOT,)]), rest)
    prune(children)
    print(f"  {len(children)} nodes, {sum(len(v) for v in children.values())} edges,"
          f" {len(is_group)} group names")

    emit_vim(children, is_group, repo / "syntax" / "nextnano_keywords.vim")
    (repo / "lua" / "nextnano").mkdir(parents=True, exist_ok=True)
    emit_lua(children, is_group, repo / "lua" / "nextnano" / "keywords.lua")
    print("wrote syntax/nextnano_keywords.vim and lua/nextnano/keywords.lua")


if __name__ == "__main__":
    main()
