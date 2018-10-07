#!/usr/bin/env python3
import inspect
from pathlib import Path
from git.repo import Repo
from rdflib import Graph, URIRef
from pyontutils.neurons import *
from pyontutils.core import OntId
from pyontutils.utils import subclasses
from pyontutils.config import devconfig, checkout_ok as ont_checkout_ok
from pyontutils.neurons.core import NeuronBase  # FIXME temporary until we can rework the config

__all__ = [
    'AND',
    'OR',
    'graphBase',
    'Config',
    'config',
    'pred',
    'setLocalContext',
    'getLocalContext',
    'setLocalNames',
    'getLocalNames',
    'Phenotype',
    'NegPhenotype',
    'LogicalPhenotype',
    'Neuron',
    'NeuronCUT',
    'NeuronEBM',
    'ilxtr',  # FIXME
]


class Config:
    _subclasses = set()
    def __init__(self,
                 name =                 'test-neurons',
                 prefixes =             tuple(),  # dict or list
                 imports =              tuple(),  # iterable
                 import_as_local =      False,  # also load from local?
                 load_from_local =      True,
                 branch =               devconfig.neurons_branch,
                 sources =              tuple(),
                 source_file =          None,
                 ignore_existing =      False):
        import os  # FIXME probably should move some of this to neurons.py?

        python_subclasses = list(subclasses(NeuronEBM)) + [Neuron, NeuronCUT]
        graphBase.knownClasses = [OntId(c.owlClass).u
                                    for c in python_subclasses]

        imports = list(imports)
        remote = OntId('NIFTTL:') if branch == 'master' else OntId(f'NIFRAW:{branch}/ttl/')
        imports += [remote.iri + 'phenotype-core.ttl', remote.iri + 'phenotypes.ttl']
        local = Path(devconfig.ontology_local_repo, 'ttl')
        out_local_base = Path(devconfig.ontology_local_repo, 'ttl/generated/neurons')
        out_remote_base = os.path.join(remote.iri, 'generated/neurons')
        out_base = out_local_base if False else out_remote_base  # TODO switch or drop local?
        imports = [OntId(i) for i in imports]

        remote_base = remote.iri.rsplit('/', 2)[0]
        local_base = local.parent

        if import_as_local:
            # NOTE: we currently do the translation more ... inelegantly inside of config so we
            # have to keep the translation layer out here (sigh)
            core_graph_paths = [Path(local, i.iri.replace(remote.iri, '')).relative_to(local_base).as_posix()
                                if remote.iri in i.iri else
                                i for i in imports]
        else:
            core_graph_paths = imports

        out_graph_path = (out_local_base / f'{name}.ttl')

        class lConfig(self.__class__):
            iri = os.path.join(out_remote_base, f'{name}.ttl')

        self.__class__._subclasses.add(lConfig)

        self.pred = config(remote_base = remote_base,  # leave it as raw for now?
                           local_base = local_base.as_posix(),
                           core_graph_paths = core_graph_paths,
                           out_graph_path = out_graph_path.as_posix(),
                           out_imports = imports, #[i.iri for i in imports],
                           prefixes = prefixes,
                           force_remote = not load_from_local,
                           branch = branch,
                           iri = lConfig.iri,
                           sources = sources,
                           source_file = source_file,
                           # FIXME conflation of import from local and render with local
                           use_local_import_paths = import_as_local,
                           ignore_existing = ignore_existing)

        # temporary fix to persist graphs and neurons with a config
        # until I have time to rewrite Config so that multiple configs
        # can co-exist but only one config at a time can be operated on
        # when creating new neurons (since only CUTs can be modified)
        # the 'proper' way to move neurons from one config to another
        # is not to switch everything behind the scenes, which is very confusin
        # but simply to take neurons that are statically tied to another config
        # and add them to another config, or just recreate them under the current
        # config, this means that we will do away with the in graph and out graph
        # every config will only have one graph and it will be in or out not both
        # note that different configs can read and write to the same file
        # NOTE that we will need to modify how the superclass is handled as well
        # because at the moment the code assumes that the superclass is invariant
        # this is not the case, and we need equality with and without the superclass
        # we are currently missing equality with the superclass
        # we can probably us a conjuctive graph to 
        self.out_graph = graphBase.out_graph
        self.existing_pes = NeuronBase.existing_pes

    @property
    def neurons(self):
        yield from self.existing_pes

    def activate(self):
        """ set this config as the active config """
        raise NotImplemented

    def load_existing(self):
        """ advanced usage allows loading multiple sets of neurons and using a config
            object to keep track of the different graphs """
        # bag existing

        if not graphBase.ignore_existing:
            ogp = Path(graphBase.ng.filename)  # FIXME ng.filename <-> out_graph_path property ...
            if ogp.exists():
                from itertools import chain
                from rdflib import Graph  # FIXME
                graphBase.load_graph = Graph().parse(graphBase.ng.filename, format='turtle')
                # FIXME memory inefficiency here ...
                _ = [graphBase.in_graph.add(t) for t in graphBase.load_graph]  # FIXME use conjuctive ...
                for sc in python_subclasses:
                    if sc._ocTrip in graphBase.load_graph or sc == Neuron:
                        sc._load_existing()


def config(remote_base=       'https://raw.githubusercontent.com/SciCrunch/NIF-Ontology/',
           local_base=        None,  # devconfig.ontology_local_repo by default
           branch=            devconfig.neurons_branch,
           core_graph_paths= ['ttl/phenotype-core.ttl',
                              'ttl/phenotypes.ttl'],
           core_graph=        None,
           in_graph_paths=    tuple(),
           out_graph_path=    '/tmp/_Neurons.ttl',
           out_imports=      ['ttl/phenotype-core.ttl'],
           out_graph=         None,
           prefixes=          tuple(),
           force_remote=      False,
           checkout_ok=       ont_checkout_ok,
           scigraph=          None,
           iri=               None,
           sources=           tuple(),
           source_file=       None,
           use_local_import_paths=True,
           ignore_existing=   True):  # defaults to devconfig.scigraph_api
    """ Wraps graphBase.configGraphIO to provide a set of sane defaults
        for input ontologies and output files. """
    graphBase.configGraphIO(remote_base=remote_base,
                            local_base=local_base,
                            branch=branch,
                            core_graph_paths=core_graph_paths,
                            core_graph=core_graph,
                            in_graph_paths=in_graph_paths,
                            out_graph_path=out_graph_path,
                            out_imports=out_imports,
                            out_graph=out_graph,
                            prefixes=prefixes,
                            force_remote=force_remote,
                            checkout_ok=checkout_ok,
                            scigraph=scigraph,
                            iri=iri,
                            sources=sources,
                            source_file=source_file,
                            use_local_import_paths=use_local_import_paths,
                            ignore_existing=ignore_existing)

    pred = graphBase._predicates
    return pred  # because the python module system is opinionated :/

try:
    pred = config()
except FileNotFoundError as e:
    pred = None
    from pyontutils.utils import TermColors as tc
    print(e)
    print(tc.red('WARNING:'),
          'config() failed to run at import (see the above error). Please',
          'call pred = config(*args, **kwargs) again in your local file with',
          'corrected arguments.')

# set the import to this file instead of neurons
graphBase.__import_name__ = __name__

# add a handy ipython line magic for scig to look up terms
try:
    ip = get_ipython()
    python_magic = ip.find_cell_magic('python')
    def scig_func(*vals):
        python_magic('-m pyontutils.scig ' + ' '.join(vals), '')
    ip.register_magic_function(scig_func, 'line', 'scig')
except NameError:
    pass  # not in an IPython environment so can't register magics


if __name__ == '__main__':
    main()