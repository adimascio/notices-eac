# NOTE: run in python2

from flask import Flask, Response
from SPARQLWrapper import SPARQLWrapper, JSON


def query_wikidata(qid):

    sparql = SPARQLWrapper("https://query.wikidata.org/sparql")
    sparql.setQuery("""

select distinct ?personneLabel ?personneDescription ?nomLabel ?prenomLabel ?date_naissanceLabel ?date_mortLabel ?lieu_naissanceLabel ?lieu_mortLabel ?genreLabel ?nationaliteLabel ?metierLabel ?artist ?bnf ?viaf ?isni ?rkd ?ulan ?snac
where {

BIND (wd:%s as ?personne) . 

  OPTIONAL  {?personne wdt:P734 ?nom.}
  ?personne wdt:P735 ?prenom.

  OPTIONAL {?personne wdt:P569 ?date_naissance.}
  OPTIONAL {?personne wdt:P570 ?date_mort.}
  OPTIONAL {?personne wdt:P19 ?lieu_naissance.}
  OPTIONAL {?personne wdt:P20 ?lieu_deces.}
  OPTIONAL {?personne wdt:P21 ?genre.}
  OPTIONAL {?personne wdt:P27 ?nationalite.}
  OPTIONAL {?personne wdt:P106 ?metier.}

  OPTIONAL {?personne wdtn:P268 ?bnf.}
  OPTIONAL {?personne wdtn:P214 ?viaf.}
  OPTIONAL {?personne wdtn:P213 ?isni.}
  OPTIONAL {?personne wdtn:P650 ?rkd.}
  OPTIONAL {?personne wdtn:P245 ?ulan.}
  OPTIONAL {?personne wdtn:P3430 ?snac.}


  service wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en,nl". }
}

        """ % qid)

    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    processed = {}

    for var in results["head"]["vars"]:
        try:
            processed[var] = results["results"]["bindings"][0][var]["value"]
        except (IndexError, KeyError) as err:
            processed[var] = ""
    return processed


app = Flask(__name__)
template = open('template_eac.xml').read().decode('utf-8')



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


@app.route('/eac/<qid>')
def generate_eac(qid):
    infos = BASE_INFOS.copy()
    infos['q'] = 'http://www.wikidata.org/entity/%s' % qid 
    infos.update(query_wikidata(qid))  
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
    data = template % infos
    return Response(data, mimetype='text/xml')
   

@app.route('/')
def home():
    return 'hello'


