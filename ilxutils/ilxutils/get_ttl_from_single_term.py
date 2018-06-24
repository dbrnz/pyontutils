""" Uses term ID to contruct a personal turtle file of its data from interlex

Usage:  foo.py [-h | --help]
        foo.py [-v | --version]
        foo.py [-e ENGINE_KEY] [-o OUTPUT] [--id ID]

Options:
    -h, --help                  Display this help message
    -v, --version               Current version of file
    -e, --engine_key=<path>     Engine key path             [default: ../production_engine_scicrunch_key.txt]
    -o, --output=<path>         Output path                 [default: ../personal_turtle.ttl]
    --id                        Id of Term to have personal ttl
"""
from docopt import docopt
from sqlalchemy import create_engine, inspect, Table, Column
import pandas as pd
from pyontutils.utils import *
from pyontutils.core import *
import sys
import pathlib
VERSION = '0.2'



class Single_Term_Turtle_Generator():

    def __init__(self):
        self.args = self.read_doc(docopt(__doc__, version=VERSION))
        self.p = pathlib.PurePath(self.args.output)
        self.g = self.create_graph()
        self.pref_dict, self.ilx_to_pref, self.unpref_dict =  self.make_preferred_iris_dict()

    def myopen(self, path):
        with open(path, 'r') as infile:
            output = infile.read().strip()
            infile.close()
        return output

    def test(self, args):
        engine = create_engine(args.engine_key)
        data =  """
                SELECT *
                FROM terms as t
                WHERE t.id = %s
                """ % args.ID
        try:
            if pd.read_sql(data, args.engine_key).empty:
                sys.exit('Engine key provided does not work.')
        except:
            sys.exit('Must be connected to school Internet.')
        print('=== Engine Successful ===')

    def read_doc(self, doc):
        args = pd.Series({k.replace('--',''):v for k, v in doc.items()})
        args.engine_key = self.myopen(args.engine_key)
        self.test(args)
        return args

    def create_graph(self):
        g = createOntology(filename=self.p.stem,
                           name='Interlex Total',
                           prefixes={**{'Testernvs':'http://whatever.com/'},
                                        **makePrefixes('ILXREPLACE',
                                                 'ilx',
                                                 'NIFRID',
                                                 'NCBIGene',
                                                 'NCBITaxon',
                                                 'skos',
                                                 'owl',
                                                 'definition',
                                                 'ILX',
                                                 'ilxtr',
                                                 'oboInOwl'
                                                 )},
                           shortname=str(self.p.stem),
                           version='Generated by scripts/get_ttl_from_single_Term.py',
                           remote_base='http://uri.interlex.org/ontologies/',
                           path='',
                           local_base=str(self.p.parent))
        return g

    def helper_pref_filter(self, iri_list, pref_list, terms_ilx):
        #print(pref_list)
        if 1 in pref_list:
            pref_index = pref_list.index(1)
            if '/ilx' in iri_list[pref_index]:
                nonpref_iris = [iri for iri in iri_list if iri != iri_list[pref_index]]
                return iri_list[pref_index], nonpref_iris

        for i, iri in enumerate(iri_list):
            if 'ilx' in iri:
                index = i
        try:
            ilx_iri = iri_list[index] #ilx is auto preferred right here
        except:
            ilx_iri = 'http://uri.interlex.org/base/' + terms_ilx
            iri_list.append(ilx_iri)

        return ilx_iri, iri_list

    def get_pref_unpref_iris(self, seg_df, terms_ilx):
        iri_list = list(map(str, list(seg_df.iri)))
        pref_list = list(map(int, list(seg_df.preferred)))
        return self.helper_pref_filter(iri_list=iri_list, pref_list=pref_list, terms_ilx=terms_ilx)

    def make_preferred_iris_dict(self):
        data =  '''
            SELECT t.id, tei.tid, tei.iri, tei.preferred, t.ilx, t.type, t.label, t.definition
            FROM terms AS t
            JOIN term_existing_ids AS tei ON t.id=tei.tid
            WHERE t.id = %s
            ''' % str(self.args.ID)

        df = pd.read_sql(data, self.args.engine_key)

        pref_dict = {}
        ilx_to_pref = {}
        unpref_dict = {}
        for i, curr_id in enumerate(df.id):

            seg_df = df.loc[df.id == (curr_id)]
            pref_iri, unpref_iris = self.get_pref_unpref_iris(seg_df=seg_df, terms_ilx=list(seg_df.ilx)[0])
            pref_dict[curr_id] = pref_iri
            unpref_dict[curr_id] = unpref_iris
            ilx_to_pref[list(seg_df.ilx)[0]] = pref_iri

        return pref_dict, ilx_to_pref, unpref_dict

    def label_def_prefix(self):
        data = '''
               SELECT t.id, t.ilx, t.type, t.label, t.definition
               FROM terms AS t
               WHERE t.id = %s
               ''' % str(self.args.ID)
        df = pd.read_sql(data, self.args.engine_key)

        for i, curr_id in enumerate(df.id):

            seg_df = df.loc[df.id == (curr_id)]
            pref_iri = self.pref_dict[curr_id]
            unpref_iris = self.unpref_dict[curr_id]
            for row in seg_df.itertuples():

                if row.type == 'relationship':
                    self.g.add_op(self.g.qname(pref_iri), row.label)
                elif row.type == 'annotation':
                    self.g.add_ap(self.g.qname(pref_iri), row.label)
                else:
                    self.g.add_class(pref_iri, label=row.label)

                if row.definition:
                    self.g.add_trip(pref_iri, 'definition:', row.definition)

                #http://www.geneontology.org/formats/oboInOwl#DbXref
                for unpref_iri in unpref_iris:
                    if 'ilx' in unpref_iri.lower():
                        continue
                    if 'neurolex.' in unpref_iri:
                        self.g.add_trip(pref_iri, oboInOwl.DbXref, unpref_iri)
                    else:
                        self.g.add_trip(pref_iri, 'ilxtr:existingIds', unpref_iri)
                        #g.add_trip(pref_iri, oboInOwl.hasDbXref, unpref_iri)
                        #g.add_trip(pref_iri, owl.equivalentClass, unpref_iri)

        print('=== LABEL COMPLETE ===')
        print('=== DEFINITION COMPLETE ===')
        print('=== PREFIXES COMPLETE ===')

    def synonym(self):
        data =  '''
                SELECT t.id, t.ilx, t.label, t.definition, ts.type, ts.literal AS syn_abbrev
                FROM terms AS t
                INNER JOIN term_synonyms AS ts
                ON ts.tid = t.id
                WHERE t.id = %s
                ''' % str(self.args.ID)

        df = pd.read_sql(data, self.args.engine_key)

        for i, row in df.iterrows():

            seg_df = df.loc[df.id == (row.id)]
            pref_iri = self.pref_dict[row.id]

            for seg_row in seg_df.itertuples():
                if seg_row.type == 'abbrev':
                    self.g.add_trip(pref_iri, "NIFRID:abbrev", seg_row.syn_abbrev)
                else:
                    self.g.add_trip(pref_iri, "NIFRID:synonym", seg_row.syn_abbrev)

        print('=== SYNONYM COMPLETE ===')

    def superclasses(self):
        data =  '''
                SELECT ts.*, t1.id as curr_id, t2.id as superclass_id
                FROM term_superclasses as ts
                JOIN terms as t1 ON ts.tid = t1.id
                JOIN terms as t2 ON ts.superclass_tid = t2.id
                WHERE t1.id = %s
                ''' % str(self.args.ID)
        df = pd.read_sql(data, self.args.engine_key)

        for i, row in enumerate(df.itertuples()):
            g.add_trip(self.pref_dict[row.curr_id], 'rdfs:subClassOf', self.pref_dict[row.superclass_id])

        print('=== SUPERCLASSES COMPLETE ===')

    def annotation(self):
        data =  '''
                SELECT t1.id, t1.ilx, t2.ilx AS annotation_ilx, ta.value FROM term_annotations AS ta
                INNER JOIN terms AS t1 ON t1.id = ta.tid
                INNER JOIN terms AS t2 ON t2.id = ta.annotation_tid
                WHERE t1.id = %s
                ''' % str(self.args.ID)

        df = pd.read_sql(data, self.args.engine_key)

        for i, row in df.iterrows():

            seg_df = df.loc[df.id == (row.id)]
            pref_iri = self.pref_dict[row.id]

            for seg_row in seg_df.itertuples():
                self.g.add_trip(pref_iri, 'ilx:'+row.annotation_ilx, seg_row.value)

        print('=== ANNOTATION COMPLETE ===')

    def relationship(self):
        data =  '''
                SELECT
                    tr.term1_id,
                    t1.ilx AS term1_ilx,
                    tr.relationship_tid,
                    t2.ilx AS relationship_ilx,
                    tr.term2_id,
                    t3.ilx AS term2_ilx
                FROM term_relationships as tr
                JOIN terms as t1 ON t1.id = tr.term1_id
                JOIN terms as t2 ON t2.id = tr.relationship_tid
                JOIN terms as t3 ON t3.id = tr.term2_id
                WHERE tr.relationship_tid = %s;
                ''' % str(self.args.ID)
        df = pd.read_sql(data, self.args.engine_key)

        for i, row_rel in df.iterrows():
            subj, pred, obj = row_rel.term1_ilx, row_rel.relationship_ilx, row_rel.term2_ilx
            subj, pred, obj = self.ilx_to_pref[subj], self.ilx_to_pref[pred], self.ilx_to_pref[obj]
            self.g.add_trip(subj, pred, obj)

def main():
    sttg = Single_Term_Turtle_Generator()
    sttg.label_def_prefix()
    sttg.synonym()
    sttg.annotation()
    sttg.relationship()
    sttg.g.g.serialize(destination=sttg.args.output, format='turtle') #g.write() bugged
    print('=== COMPLETE ===')

if __name__ == '__main__':
    main()
