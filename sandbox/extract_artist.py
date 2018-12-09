import csv
from datetime import datetime
from pprint import pprint as pp
import re

from lxml import etree

rgx = re.compile(r"([A-Z' -]+)\s+([\w'-]+)")
location_rgx = re.compile(r'(.+?)\s+\((.+?)\)')


def parse_date(date):
    try:
        return datetime.strptime(date, '%d/%m/%Y').strftime('%d/%m/%Y')
    except ValueError:
        try:
            dateobj =  datetime.strptime(date, '%d/%m/%y')
            if dateobj.year > 2000:
                dateobj = datetime(dateobj.year - 100, dateobj.month, dateobj.day)
            return dateobj.strftime('%d/%m/%Y')
        except ValueError:
            try:
                return datetime.strptime(date, '%m/%Y').strftime('%d/%m/%Y')
            except ValueError:
                return date
    return date


def extract_location(location):
    match = location_rgx.match(location)
    if match is None:
        return location, None
    return match.group(1), match.group(2)


def extract_lastname(fullname):
    match = rgx.match(fullname)
    if match is None:
        return None, None
    else:
        return match.group(1), match.group(2)


def parse_unittitle(elt):
    text = elt.text.replace(' ', ' ').replace('´', "'").strip()
    lowered = text.lower()
    prefixes = [
        ('nom de la commune : ', 'commune', False),
        ("nom de l'établissement : ", 'commanditaire', False),
        ('date de la commission : ', 'date', False),
        ("date de l'arrêté : ", 'arrete', False),
        ('nom des artistes : ', 'artiste', True),
        ("nom de l'artiste : ", 'artiste', False),
    ]
    for prefix, propname, multiple in prefixes:
        if lowered.startswith(prefix):
            value = text[len(prefix):].strip()
            if propname == 'artiste':
                lastname, firstname = extract_lastname(value)
                if lastname is None:
                    value = {'fullname': value, 'firstname': None, 'lastname': None}
                else:
                    value = {'fullname': value, 'firstname': firstname, 'lastname': lastname}
            elif propname in ('date', 'arrete'):
                value = parse_date(value)
            elif propname == 'commune':
                commune, dept = extract_location(value)
                value = {'commune': commune, 'dept': dept}
            return propname, value, multiple


def iter_application_elements(tree):
    for did in tree.findall('//did'):
        unitid = did.find('unitid').text
        props = {'unitid': unitid}
        for unittitle in did.findall('unittitle'):
            if unittitle.text == '***':
                yield props
                props = {'unitid': unitid}
            else:
                propinfos = parse_unittitle(unittitle)
                if propinfos is not None:
                    propname, value, multiple = propinfos
                    props[propname] = value
                    if propname == 'artiste':
                        if 'refusé' in value['fullname']:
                            props['statut'] = 'refusé'
                        else:
                            props['statut'] = 'accepté'
    if len(props) > 1:
        yield props



def parse_applications(tree):
    for props in iter_application_elements(tree):
        pp(props)

"""
{'artiste': {'firstname': 'Frédéric',
             'fullname': 'ZELLER Frédéric',
             'lastname': 'ZELLER'},
 'commanditaire': 'Groupes scolaires Paul Bert et Condorcet',
 'commune': 'VILLENEUVE-SAINT-GEORGES',
 'date': {'date': datetime.datetime(1963, 7, 23, 0, 0),
          'datestr': '23/07/1963'},
 'unitid': '19880466/139'}
"""


def dump_csv(tree):
    with open('candidatures.csv', 'w') as outf:
        writer = csv.writer(outf)
        writer.writerow(['eadid', 'unitid', 'date', 'arrete', 'artiste', 'nom', 'prenom', 'commune', 'departement', 'commanditaire', 'statut'])
        for props in iter_application_elements(tree):
            artist = props.get('artiste', {})
            location = props.get('commune', {})
            row = [
                'FRAN_IR_015069',
                props['unitid'],
                props.get('date', ''),
                props.get('arrete', ''),
                artist.get('fullname', ''),
                artist.get('lastname', ''),
                artist.get('firstname', ''),
                location.get('commune', ''),
                location.get('dept', ''),
                props.get('commanditaire'),
                props.get('statut')]
            writer.writerow(row)

if __name__ == '__main__':
    tree = etree.parse('FRAN_IR_015069.xml')
    parse_applications(tree)
    # dump_csv(tree)


# def extract_names()
# tree = etree.parse('FRAN_IR_015069.xml')

# artists = set()

# for elt in tree.findall('//unittitle'):
#     text = elt.text.replace(' ', ' ').strip()
#     if "Nom de l'artiste :" in text:
#         artist_name = text.split("Nom de l'artiste :")[-1].strip(' :,.')
#     else:
#         continue
#     artist_name = artist_name.split('(')[0].strip(' .,')
#     if 'WETZS' in artist_name:
#         print(artist_name)

#     artists.add(artist_name)

# print('\n'.join(sorted(artists)))
