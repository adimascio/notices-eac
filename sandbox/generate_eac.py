import csv
import sys

from unidecode import unidecode
# from slugify import slugify


BASE_INFOS = {
    'artistLabel': '',
    'nom_artiste': '',
    'prenom_artiste': '',
    'annee_naissance': '',
    'date_naissance': '',
    'date_mort': '',
    'annee_mort': '',
    'annee_commande': '',
    'lieu_naissance': '',
    'lieu_naissanceLabel': '',
    'lieu_mort': '',
    'genreLabel': '',
    'nationalite': '',
    'metier': '',
    'q': '',
    'bnf': '',
    'viaf': '',
    'isni': '',
    'rkd': '',
    'ulan': '',
    'snac': '',
    'URL_VIAF': '',
    'ark_bnf': '',
}


def slugify(s):
    return unidecode(s.lower()).replace(' ', '-').replace("'", '')


def iter_values(values_filename):
    with open(values_filename) as f:
        reader = csv.reader(f)
        headers = next(reader)
        for item_values in reader:
            infos = dict(zip(headers, item_values))
            if infos['date_mortLabel']:
                infos['annee_mort'] = infos['date_mortLabel'][:4]
            if infos['date_naissanceLabel']:
                infos['annee_naissance'] = infos['date_naissanceLabel'][:4]
            if infos['date_mortLabel']:
                infos['date_mortLabel'] = infos['date_mortLabel'][:10]
            if infos['date_naissanceLabel']:
                infos['date_naissanceLabel'] = infos['date_naissanceLabel'][:10]
            if not infos['nomLabel'] and infos['personneLabel']:
                infos['prenomLabel'] = ''
                infos['nomLabel'] = infos['personneLabel']
            yield {**BASE_INFOS, **infos}


def generate_eac(xmltemplate_filename, values_filename):
    with open(xmltemplate_filename) as f:
        xmltemplate = f.read()
    for item_values in iter_values(values_filename):
        data = xmltemplate % item_values
        slug = slugify(item_values['nomLabel'])
        with open(f'{slug}-eac.xml', 'w') as outf:
            outf.write(data)


if __name__ == '__main__':
    xmltemplate_filename, values_filename = sys.argv[1:]
    generate_eac(xmltemplate_filename, values_filename)