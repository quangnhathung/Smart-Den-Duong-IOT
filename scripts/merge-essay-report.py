#!/usr/bin/env python3
"""Inherit source cover/style package; replace only report body and new media relationships."""
import argparse
import copy
import hashlib
import json
import posixpath
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
from lxml import etree as E

parser = argparse.ArgumentParser()
parser.add_argument('source', type=Path)
parser.add_argument('body', type=Path)
parser.add_argument('output', type=Path)
args = parser.parse_args()
assert not args.output.exists(), 'Refusing to overwrite'
W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
R = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'
REL = 'http://schemas.openxmlformats.org/package/2006/relationships'
NS = {'w': W, 'r': R}
sha = lambda b: hashlib.sha256(b).hexdigest()
with ZipFile(args.source) as z:
    original = {n: z.read(n) for n in z.namelist() if not n.endswith('/')}
with ZipFile(args.body) as z:
    body_parts = {n: z.read(n) for n in z.namelist() if not n.endswith('/')}
parts = dict(original)
tree = E.fromstring(original['word/document.xml'])
body = tree.find(f'{{{W}}}body')
cover_end = [i for i, child in enumerate(body) if child.find('w:pPr/w:sectPr', NS) is not None]
assert cover_end == [11], cover_end
cover = [copy.deepcopy(x) for x in list(body)[:12]]
section = copy.deepcopy(body[-1])
assert section.tag == f'{{{W}}}sectPr'
fresh = E.fromstring(body_parts['word/document.xml']).find(f'{{{W}}}body')
nodes = [copy.deepcopy(n) for n in fresh if n.tag != f'{{{W}}}sectPr']
rels = E.fromstring(original['word/_rels/document.xml.rels'])
new_rels = E.fromstring(body_parts['word/_rels/document.xml.rels'])
mapping = {}
for relationship in new_rels:
    kind = relationship.get('Type').rsplit('/', 1)[-1]
    if kind not in ('image', 'hyperlink'):
        continue
    rid = f'rIdEssay{len(mapping) + 1}'
    assert not any(r.get('Id') == rid for r in rels)
    cloned = copy.deepcopy(relationship)
    mapping[relationship.get('Id')] = rid
    cloned.set('Id', rid)
    if kind == 'image':
        target = relationship.get('Target')
        source_part = posixpath.normpath(posixpath.join('word', target))
        new_name = f'word/media/essay-{len(mapping):02}{Path(target).suffix}'
        assert new_name not in parts
        parts[new_name] = body_parts[source_part]
        cloned.set('Target', new_name.removeprefix('word/'))
    rels.append(cloned)
for node in nodes:
    for element in node.iter():
        for name, value in list(element.attrib.items()):
            if name.startswith(f'{{{R}}}'):
                assert value in mapping, (name, value)
                element.set(name, mapping[value])
        # Drawing IDs must be unique across retained cover and new body.
        if element.tag in ('{http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing}docPr',
                           '{http://schemas.openxmlformats.org/drawingml/2006/picture}cNvPr'):
            element.set('id', str(1000 + int(element.get('id', '0'))))
for child in list(body):
    body.remove(child)
body.extend(cover + nodes + [section])
parts['word/document.xml'] = E.tostring(tree, xml_declaration=True, encoding='UTF-8', standalone=True)
parts['word/_rels/document.xml.rels'] = E.tostring(rels, xml_declaration=True, encoding='UTF-8', standalone=True)
content_types = E.fromstring(parts['[Content_Types].xml'])
assert any(x.get('Extension') == 'png' for x in content_types)
assert all(E.tostring(a, method='c14n') == E.tostring(b, method='c14n') for a, b in zip(cover, list(body)[:12]))
assert E.tostring(section, method='c14n') == E.tostring(body[-1], method='c14n')
headings = [''.join(p.itertext()) for p in body.findall('w:p', NS)
            if p.find('w:pPr/w:pStyle[@w:val="Heading1"]', NS) is not None]
chapters = [t for t in headings if t.startswith('CHƯƠNG ')]
assert len(chapters) == 4, chapters
retained_parts = [n for n in original if n not in ('word/document.xml', 'word/_rels/document.xml.rels')]
assert all(parts[n] == original[n] for n in retained_parts)
args.output.parent.mkdir(parents=True, exist_ok=True)
with args.output.open('xb') as f:
    with ZipFile(f, 'w', ZIP_DEFLATED) as z:
        for name, data in parts.items():
            z.writestr(name, data)
proof = dict(source=str(args.source.resolve()), source_sha256=sha(args.source.read_bytes()), output=str(args.output.resolve()),
             output_sha256=sha(args.output.read_bytes()), cover_nodes_preserved=12, retained_parts=retained_parts,
             all_retained_parts_byte_identical=True, section_properties_preserved=True, chapters=chapters,
             new_media=len(mapping), package_files=len(parts))
args.output.with_suffix('.inheritance.json').write_text(json.dumps(proof, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({k: proof[k] for k in ('output', 'cover_nodes_preserved', 'new_media', 'chapters')}, ensure_ascii=False))
