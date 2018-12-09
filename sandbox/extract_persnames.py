import csv
import os.path as osp
import re
import sys

from lxml import etree

IR_DIRECTORY = '/home/adim/var/projects/siaf/FRAN/'
BASE_IR_URL = 'https://www.siv.archives-nationales.culture.gouv.fr/siv/IR/'
NS = 'http://www.openarchives.org/OAI/2.0/'

persname_rgx = re.compile(r'(?P<lastname>.*?),\s*(?P<firstname>.*?)(\((?P<birthyear>\d{4})\s*-\s*(?P<deathyear>\d{4})\))?$')
codes = {
    'peintre': 'd699msit6xq-1e7tbhtd3o7v6',
    'artiste': 'd699msjzppc-y5cl997d1hxn',
    'chanteur': 'd699msk0pcw-gpdixmoh1g05',
    'danseur': 'd699msjdps0--1hzktwbvq279p',
    'dessinateur': 'd699msjehib--9u7knr7v4uyn',
    'compositeur': 'd699msjks42-vqaztu16yf9j',
}


def ir_list(filename):
    with open(filename) as listf:
        for line in listf:
            line = line.strip()
            if line:
                yield line


def extract_persname_infos(persname):
    match = persname_rgx.match(persname)
    if match is None:
        return {'fullname': persname, 'lastname': '', 'firstname': '', 'birthyear': '', 'deathyear': ''}
    else:
        infos = match.groupdict()
        return {
            'fullname': persname,
            'lastname': infos['lastname'] or '',
            'firstname': infos['firstname'] or '',
            'birthyear': int(infos['birthyear']) if infos['birthyear'] else '',
            'deathyear': int(infos['deathyear']) if infos['deathyear'] else '',
        }

def persnames(tree, code):
    persnames = []
    for controlaccess in tree.findall(f'//{{{NS}}}controlaccess'):
        # XXX check for authfilenumber to see if persname already exists in the
        # AN's referential
        persnames = [p.text for p in controlaccess.findall(f'{{{NS}}}persname')]
        for occupation in controlaccess.findall(f'{{{NS}}}occupation'):
            if occupation.get('authfilenumber') == code and occupation.get('source') == 'FRAN_RI_010':
                yield from persnames

def ir_read(filepath, code):
    tree = etree.parse(filepath)
    eadid = tree.find(f'//{{{NS}}}eadid').text
    if not eadid:
        eadid = osp.splitext(osp.basename(filepath))[0]
    for persname in persnames(tree, code):
        yield (eadid, '', *extract_persname_infos(persname).values())


def generate_csv(ir_list_fname, codename):
    code = codes[codename]
    rows = [
        ['eadid', 'cid', 'fullname', 'lastname', 'firstname', 'birthyear', 'deathyear', 'codename', 'code'],
    ]
    uniques = [rows[0]]
    persnames = set()
    for ir_filename in ir_list(ir_list_fname):
        filepath = osp.join(IR_DIRECTORY, ir_filename)
        assert osp.isfile(filepath)
        print('filepath', filepath)
        occurrences = ir_read(filepath, code)
        for eadid, cid, fullname, lastname, firstname, birthyear, deathyear in occurrences:
            row = [eadid, cid, fullname, lastname, firstname, birthyear, deathyear, codename, code]
            if fullname not in persnames:
                uniques.append(row)
                persnames.add(fullname)
            rows.append(row)
        rows.extend([[*row, codename, code] for row in occurrences])
    with open(f'{codename}_output.csv', 'w') as outf:
        writer = csv.writer(outf)
        writer.writerows(rows)
    with open(f'{codename}_output_uniques.csv', 'w') as outf:
        writer = csv.writer(outf)
        writer.writerows(uniques)


if __name__ == '__main__':
    ir_list_fname = sys.argv[1]
    codename = sys.argv[2]
    generate_csv(ir_list_fname, codename)
