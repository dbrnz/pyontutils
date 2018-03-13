from pyontutils.core import qname, simpleOnt, displayGraph, oc, oop, olit, oec, olist, flattenTriples, OntTerm
from pyontutils.core import restrictions, annotation
from pyontutils.core import NIFTTL, NIFRID, ilxtr
from pyontutils.core import definition, realizes, hasParticipant, hasPart, hasInput, hasOutput, TEMP
from pyontutils.core import owl, rdf, rdfs
from methods_core import methods_core, asp, tech

filename = 'methods'
prefixes = ('ilxtr', 'NIFRID', 'definition', 'realizes', 'hasParticipant', 'hasPart', 'hasInput', 'hasOutput')
imports = methods_core.iri, NIFTTL['bridge/chebi-bridge.ttl'], NIFTTL['bridge/tax-bridge.ttl']
comment = 'The ontology of techniques and methods.'
_repo = True
debug = False

def t(subject, label, def_, *synonyms):
    yield from oc(subject, ilxtr.technique)
    yield from olit(subject, rdfs.label, label)
    if def_:
        yield from olit(subject, definition, def_)

    if synonyms:
        yield from olit(subject, NIFRID.synonyms, *synonyms)


def _t(subject, label, *rests, def_=None, synonyms=tuple()):
    members = tuple()
    _rests = tuple()
    for rest in rests:
        if isinstance(rest, tuple):
            _rests += rest,
        else:
            members += rest,

    rests = _rests
    if not members:
        members = ilxtr.technique,


    yield from oc(subject)
    yield from oec(subject, *members, *restrictions(*rests))
    yield from olit(subject, rdfs.label, label)
    if def_:
        yield from olit(subject, definition, def_)

    if synonyms:
        if not isinstance(synonyms, tuple):
            # this is why python sucks and racket is awesome if this was racket
            # the error would show up on the line where the problem was :/
            raise TypeError(f'Type of {synonyms!r} should not be {type(synonyms)}!')
        yield from olit(subject, NIFRID.synonyms, *synonyms)


class I:
    counter = iter(range(999999))
    @property
    def d(self): return TEMP[str(next(self.counter))]
i = I()

triples = (
    oc(ilxtr.analysisRole,
       OntTerm('BFO:0000023', label='role')
    ),

    _t(i.d, 'randomization technique',  # FIXME this is not defined correctly
       (ilxtr.hasPrimaryAspect, asp.informationEntropy),
       (ilxtr.hasPrimaryAspect_dAdT, ilxtr.positive),
    ),

    _t(i.d, 'chemical technique',  # FIXME but not molecular? or are molecular subset?
       (hasParticipant,
        OntTerm('CHEBI:24431', label='chemical entity')
       ),),

    _t(i.d, 'molecular technique',  # FIXME help I have no idea how to model this same with chemical technique
       (hasParticipant,
        OntTerm('CHEBI:25367', label='molecule')
       ),),

    _t(i.d, 'cellular technique',
       (hasParticipant,
        OntTerm('SAO:1813327414', label='Cell')
       ),),

    _t(i.d, 'cell type induction technique',
       (hasParticipant, ilxtr.inducationFactor),
    ),

    _t(i.d, 'cloning technique',
       (hasParticipant,
        OntTerm('CHEBI:16991', label='deoxyribonucleic acid')
        # FIXME other options are OntTerm('SAO:454034570') or OntTerm('SO:0000352')
        ),
    ),
    _t(i.d, 'microarray technique',
       (hasInput,
        # OntTerm(search='microarray', limit=20, prefix='NIFSTD')  # nice trick
        OntTerm('BIRNLEX:11031', label='Microarray platform')
        ),
    ),

    _t(tech.sequencing, 'sequencing technique',
       # hasParticipant molecule or chemical?
       (hasParticipant, ilxtr.thingWithSequence),  # peptide nucleotie sacharide
        ),

    _t(tech._naSeq, 'nucleic acid sequencing technique',
       (ilxtr.hasPrimaryParticipant,
        # hasParticipant molecule or chemical?
        #OntTerm(term='nucleic acid')
         OntTerm('CHEBI:33696', label='nucleic acid')
        ),
       (ilxtr.hasPrimaryAspect,
        #OntTerm(term='sequence')
        OntTerm('SO:0000001', label='sequence')  # label='region'
       ),
        ),

    _t(i.d, 'deep sequencing technique',
       tech._naSeq,
       synonyms=('deep sequencing',)
    ),

    _t(i.d, 'sanger sequencing technique',
       tech._naSeq,
       synonyms=('sanger sequencing',)
    ),

    _t(i.d, 'shotgun sequencing technique',
       tech._naSeq,
       synonyms=('shotgun sequencing',)
    ),

    _t(i.d, 'single cell sequencing technique',
       tech.sequencing,
       # FIXME vs pp -> *NA from a single cell
       (hasParticipant, OntTerm('SAO:1813327414', label='Cell')),
       # (ilxtr.hasPrimaryParticipantCardinality, 1)  # FIXME need this...
       synonyms=('single cell sequencing',)
    ),

    _t(i.d, 'single nucleus sequencing technique',
       tech.sequencing,
       (hasParticipant, OntTerm('GO:0005634', label='nucleus')),
       # (ilxtr.hasPrimaryParticipantCardinality, 1)  # FIXME need this...
       synonyms=('single nucleus sequencing',)
    ),

    # sequencing TODO

    _t(i.d, 'RNAseq',
       (ilxtr.hasPrimaryParticipant, OntTerm('CHEBI:33697', label='RNA')),
       synonyms=('RNA-seq',)),

    _t(i.d, 'mRNA-seq',
       (ilxtr.hasPrimaryParticipant,
        #OntTerm(term='mRNA')
        ilxtr.mRNA
        # FIXME wow... needed a rerun on this fellow OntTerm('SAO:116515730', label='MRNA', synonyms=[])
       ),
    ),

    _t(i.d, 'snRNAseq',
       (ilxtr.hasPrimaryParticipant, OntTerm('CHEBI:33697', label='RNA')),
       (hasParticipant, OntTerm('GO:0005634', label='nucleus')),
       synonyms=('snRNA-Seq',
                 'single nucleus RNAseq',)),

    _t(i.d, 'scRNAseq',
       (ilxtr.hasPrimaryParticipant, OntTerm('CHEBI:33697', label='RNA')),
       (hasParticipant, OntTerm('SAO:1813327414', label='Cell')),
       synonyms=('scRNA-Seq',
                 'single cell RNAseq',)),
        # 'deep-dive scRNA-Seq'  # deep-dive vs wide-shallow I think is what this is


    _t(i.d, 'Patch-seq',
       (ilxtr.hasPrimaryParticipant, OntTerm('CHEBI:33697', label='RNA')),
       (hasParticipant, ilxtr.microPipette),  # FIXME TODO
       synonyms=('Patch-Seq',
                 'patch seq',)),

    _t(i.d, 'mC-seq',
       (ilxtr.hasSomething, i.d),
       def_='non CG methylation',
    ),

    _t(i.d, 'snmC-seq',
       (hasParticipant, OntTerm('GO:0005634', label='nucleus')),
    ),

    _t(tech.ATACseq, 'ATAC-seq',
       (ilxtr.hasSomething, i.d),
    ),

    _t(i.d, 'snATAC-seq',
       tech.ATACseq,  # FIXME primary participant...
       (hasParticipant, OntTerm('GO:0005634', label='nucleus')),
       synonyms=('single-nucleus ATAC-seq',
                 'single nucleus ATAC-seq',)),

    _t(i.d, 'scATAC-seq',
       tech.ATACseq,  # FIXME
       (hasParticipant, OntTerm('SAO:1813327414', label='Cell')),
       def_='enriched for open chromatin',
       synonyms=('single-cell ATAC-seq',
                 'single cell ATAC-seq',)),

    _t(i.d, 'Bulk-ATAC-seq',
       tech.ATACseq,  # FIXME
       (ilxtr.hasSomething, i.d),
    ),

    #'scranseq'  # IS THIS FOR REAL!?
    #'ssranseq'  # oh boy, this is just me being bad at spelling scrnaseq?

    _t(i.d, 'Drop-seq',
       (ilxtr.hasSomething, i.d),
       synonyms=('DroNc-seq',)),

    _t(i.d, '10x Genomics',
       (ilxtr.hasSomething, i.d),
       def_='commercialized drop seq',
       synonyms=('10x',)),

    _t(i.d, 'MAP seq',
       (ilxtr.hasSomething, i.d),
    ),

    _t(i.d, 'Smart-seq',
       (ilxtr.hasSomething, i.d),
       synonyms=('Smart-seq2',
                 'SMART-seq',
                 'SMART-seq v4',)),

    # 'deep smart seq',



    _t(i.d, ' technique',
       (ilxtr.hasSomething, i.d),
    ),

    _t(i.d, ' technique',
       (ilxtr.hasSomething, i.d),
    ),

    _t(i.d, ' technique',
       (ilxtr.hasSomething, i.d),
    ),

    _t(tech.ISH, 'in situ hybridization technique',
       (ilxtr.hasSomething, i.d),
       synonyms=('in situ hybridization', 'ISH'),
    ),

    _t(tech.FISH, 'fluorescence in situ hybridization technique',
       (ilxtr.hasSomething, i.d),
       synonyms=('fluorescence in situ hybridization', 'FISH'),
    ),

    _t(tech.smFISH, 'single-molecule fluorescence in situ hybridization technique',
       (ilxtr.hasSomething, i.d),
       synonyms=('single-molecule fluorescence in situ hybridization',
                 'single molecule fluorescence in situ hybridization',
                 'single-molecule FISH',
                 'single molecule FISH',
                 'smFISH'),
    ),

    _t(tech.MERFISH, 'multiplexed error-robust fluorescence in situ hybridization technique',
       (ilxtr.hasSomething, i.d),
       synonyms=('multiplexed error-robust fluorescence in situ hybridization',
                 'multiplexed error robust fluorescence in situ hybridization',
                 'multiplexed error-robust FISH',
                 'multiplexed error robust FISH',
                 'MERFISH'),
    ),

    _t(tech.ISH, 'in situ hybridization technique',
       (ilxtr.hasSomething, i.d),
       synonyms=('in situ hybridization', 'ISH'),
    ),

    _t(i.d, 'genetic technique',
       (hasParticipant,
        OntTerm('SO:0000704', label='gene')  # prefer SO for this case
        #OntTerm(term='gene', prefix='obo')  # representing a gene
        ),
       # FIXME OR has participant some nucleic acid...
    ),

    _t(i.d, 'amplification technique',
       (ilxtr.hasPrimaryAspect, asp['count']),
       (ilxtr.hasPrimaryAspect_dAdT, ilxtr.increase),
       def_='increase number',
    ),

    _t(i.d, 'enrichment technique',
       (ilxtr.hasSomething, i.d),
       def_='increase proporation',
    ),

    _t(i.d, 'expression manipulation technique',
       (ilxtr.hasSomething, i.d)),
    _t(i.d, 'conditional expression manipulation technique',
       (ilxtr.hasSomething, i.d)),

    _t(i.d, 'knock in technique',
       (ilxtr.hasSomething, i.d)),

    _t(i.d, 'knock down technique',
       (ilxtr.hasSomething, i.d),
       synonyms=('underexpression technique',),
    ),

    _t(i.d, 'knock out technique',
       (ilxtr.hasSomething, i.d)),

    _t(i.d, 'mutagenesis technique',
       (ilxtr.hasSomething, i.d)),

    _t(i.d, 'overexpression technique',
       (ilxtr.hasSomething, i.d)),

    _t(i.d, 'delivery technique',
       (ilxtr.hasSomething, i.d),
       def_='A technique for moving something from point a to point b.',),

    _t(i.d, 'physical delivery technique',
       (ilxtr.hasSomething, i.d)),
    _t(i.d, 'diffusion based delivery technique',
       (ilxtr.hasSomething, i.d)),
    _t(i.d, 'bath application technique',
       (ilxtr.hasSomething, i.d)),
    _t(i.d, 'topical application technique',
       (ilxtr.hasSomething, i.d)),

    _t(i.d, 'mechanical delivery technique',
       (ilxtr.hasSomething, i.d)),
    _t(i.d, 'rocket delivery technique',
       (ilxtr.hasSomething, i.d)),
    _t(i.d, 'injection technique',
       (ilxtr.hasSomething, i.d)),
    _t(i.d, 'ballistic technique',
       (ilxtr.hasSomething, i.d)),
    _t(i.d, 'pressure technique',
       (ilxtr.hasSomething, i.d)),

    _t(i.d, 'electrical delivery technique',
       (ilxtr.hasSomething, i.d)),
    _t(i.d, 'electroporation technique',
       (ilxtr.hasSomething, i.d)),
    _t(i.d, 'in utero electroporation technique',
       (ilxtr.hasSomething, i.d)),
    _t(i.d, 'single cell electroporation technique',
       (ilxtr.hasSomething, i.d)),
    _t(i.d, 'chemical delivery technique',
       (ilxtr.hasSomething, i.d)),

    _t(i.d, 'DNA delivery technique',
       (ilxtr.hasSomething, i.d)),
    _t(i.d, 'transfection technique',
       (ilxtr.hasSomething, i.d)),
    _t(i.d, 'delivery exploiting some pre-existing mechanism technique',
       (ilxtr.hasSomething, i.d)),
    _t(i.d, 'DNA delivery via primary genetic code technique',
       (ilxtr.hasSomething, i.d)),
    _t(i.d, 'DNA delivery via germ line technique',
       (ilxtr.hasSomething, i.d)),
    _t(i.d, 'DNA delivery via plasmid technique',
       (ilxtr.hasSomething, i.d)),
    _t(i.d, 'DNA delivery via viral particle technique',
       (ilxtr.hasSomething, i.d)),

    _t(i.d, 'tracing technique',
       (ilxtr.hasSomething, i.d)),
    _t(i.d, 'anterograde tracing technique',
       (ilxtr.hasSomething, i.d)),
    _t(i.d, 'retrograde tracing technique',
       (ilxtr.hasSomething, i.d)),
    _t(i.d, 'diffusion tracing technique',
       (ilxtr.hasSomething, i.d)),
    _t(i.d, 'transsynaptic tracing technique',
       (ilxtr.hasSomething, i.d)),

    _t(i.d, 'statistical technique',
       (ilxtr.hasSomething, i.d)),
    _t(i.d, 'computational technique',
       (ilxtr.hasSomething, i.d)),
    _t(i.d, 'simulation technique',
       (ilxtr.hasSomething, i.d)),

    _t(i.d, 'storage technique',
       (ilxtr.hasSomething, i.d)),

    _t(i.d, 'preservation technique',
       (ilxtr.hasSomething, i.d)),

    _t(i.d, 'tissue preservation technique',
       (ilxtr.hasSomething, i.d)),

    _t(i.d, 'colocalization technique',
       (ilxtr.hasSomething, i.d)),
    _t(i.d, 'image reconstruction technique',
       (ilxtr.hasSomething, i.d)),

    _t(i.d, 'tomographic technique',
       (ilxtr.hasSomething, i.d),
       (ilxtr.isConstrainedBy, ilxtr.radonTransform),
       synonyms=('tomography',)),
    _t(i.d, 'positron emission tomography',
       (ilxtr.hasSomething, i.d),
       synonyms=('PET', 'PET scan')),

    _t(i.d, 'stereology technique',
       (ilxtr.hasSomething, i.d),
       synonyms=('stereology',)),
    _t(i.d, 'design based stereology technique',
       (ilxtr.hasSomething, i.d),
       synonyms=('design based stereology',)),

    _t(i.d, 'spike sorting technique',
       (ilxtr.hasSomething, i.d),
       synonyms=('spike sorting',)),

    _t(i.d, 'detection technique',
       (ilxtr.hasSomething, i.d)),
    _t(i.d, 'identification technique',
       (ilxtr.hasSomething, i.d)),
    _t(i.d, 'characterization technique',
       (ilxtr.hasSomething, i.d)),
    _t(i.d, 'classification technique',
       (ilxtr.hasSomething, i.d)),
    _t(i.d, 'curation technique',
       (ilxtr.hasSomething, i.d)),

    _t(i.d, 'angiographic technique',
       (ilxtr.hasSomething, i.d),
       synonyms=('angiography',)),

    _t(i.d, 'ex vivo technique',
       (hasParticipant, ilxtr.somethingThatUsedToBeAlive),
       synonyms=('ex vivo',),),
    _t(i.d, 'in situ technique',  # TODO FIXME
       # detecting something in the location that it was originally in
       # not in the dissociated remains thereof...
       (ilxtr.hasSomething, i.d),
       synonyms=('in situ',),),
    _t(i.d, 'in vivo technique',
       (hasParticipant, ilxtr.somethingThatIsAlive),
       synonyms=('in vivo',),),
    _t(i.d, 'in utero technique',
       (hasParticipant, ilxtr.somethingThatIsAliveAndIsInAUterus),
       synonyms=('in vitro',),),
    _t(i.d, 'in vitro technique',
       (hasParticipant, ilxtr.somethingThatIsAliveAndIsInAGlassContainer),
       synonyms=('in vitro',),),

    _t(i.d, 'high throughput technique',
       (ilxtr.hasSomething, i.d),
       synonyms=('high throughput',),),

    _t(i.d, 'fourier analysis technique',
       (realizes, ilxtr.analysisRole),  # FIXME needs to be subClassOf role...
       (ilxtr.isConstrainedBy, ilxtr.fourierTransform),
       synonyms=('fourier analysis',),),

    _t(i.d, 'preparation technique',
       (ilxtr.hasSomething, i.d),
       synonyms=('sample preparation technique',
                 'specimine preparation technique',
                 'sample preparation',
                 'specimine preparation',),),

    _t(i.d, 'dissection technique',
       (ilxtr.hasOutput, ilxtr.partOfSomePrimaryInput),  #FIXME
       synonyms=('dissection',),),

    _t(i.d, 'atlas guided microdissection technique',
       (ilxtr.hasOutput, ilxtr.partOfSomePrimaryInput),  #FIXME
       synonyms=('atlas guided microdissection',),),

    _t(i.d, 'crystallization technique',
       (ilxtr.hasSomething, i.d),
       synonyms=('crystallization',)),

    _t(tech.fixation, 'fixation technique',
       # prevent decay, decomposition
       # modify the mechanical properties to prevent disintegration
       # usually crosslinks proteins?
       (ilxtr.hasSomething, i.d),
       synonyms=('fixation',)),

    _t(i.d, 'tissue fixation technique',
       tech.fixation,
       (ilxtr.hasPrimaryParticipant, ilxtr.tissue),
       synonyms=('tissue fixation',)),

    _t(i.d, 'sensitization technique',
       (ilxtr.hasSomething, i.d),
    ),
    _t(i.d, 'permeabalization technique',
       (ilxtr.hasSomething, i.d),
    ),

    _t(i.d, 'chemical synthesis technique',
       # involves some chemical reaction ...
       # is ioniziation a chemical reaction? e.g. NaCl -> Na+ Cl-??
       (ilxtr.hasOutput,  OntTerm('CHEBI:24431', label='chemical entity')),
       tech.creating,),
    _t(i.d, 'physical synthesis technique',
       tech.creating,),
    _t(i.d, 'mixing technique',
       #tech.creating,  # not entirely clear that this is the case...
       #ilxtr.mixedness is circular
       (ilxtr.hasSomething, i.d),
       synonyms=('mixing',),),
    _t(i.d, 'agitating technique',
       #tech.mixing,
       (ilxtr.hasSomething, i.d),
       synonyms=('agitating',),),
    _t(i.d, 'stirring technique',
       #tech.mixing,  # not clear, the intended outcome may be that the thing is 'mixed'...
       (ilxtr.hasSomething, i.d),
       synonyms=('stirring',),),
    _t(i.d, 'dissolving technique',
       (ilxtr.hasSomething, i.d),
       synonyms=('dissolve',),),


    _t(i.d, 'husbandry technique',
       # FIXME maintenance vs growth
       # also how about associated techniques?? like feeding
       # include in the oec or 'part of some husbandry technique'??
       # alternately we can change it to hasParticipant ilxtr.livingOrganism
       # to allow them to include techniques where locally the
       # primary participant is something like food, instead of the organism HRM
       tech.maintaining,
       (hasParticipant,  # vs primary participant
        OntTerm('NCBITaxon:1', label='ncbitaxon')
       ),
       synonyms=('culture technique', 'husbandry', 'culture'),),

    _t(i.d, 'bacterial culture technique',
       tech.maintaining,
       (hasParticipant, OntTerm('NCBITaxon:2', label='Bacteria <prokaryote>')),
       synonyms=('bacterial culture',),),

    _t(i.d, 'cell culture technique',
       tech.maintaining,
       (hasParticipant, OntTerm('SAO:1813327414', label='Cell')),
       synonyms=('cell culture',),),

    _t(i.d, 'yeast culture technique',
       tech.maintaining,
       (hasParticipant, OntTerm('NCBITaxon:4932', label='Saccharomyces cerevisiae')),
       synonyms=('yeast culture',),),

    _t(i.d, 'tissue culture technique',
       tech.maintaining,
       (hasParticipant, ilxtr.tissue),
       synonyms=('tissue culture',),),

    _t(i.d, 'slice culture technique',
       tech.maintaining,
       (hasParticipant, ilxtr.brainSlice),  # FIXME
       synonyms=('slice culture',),),

    _t(i.d, 'open book preparation technique',
       (ilxtr.hasInput,
        OntTerm('UBERON:0001049', label='neural tube')
        #OntTerm(term='neural tube', prefix='UBERON')  # FIXME dissected out neural tube...
       ),
       synonyms=('open book culture', 'open book preparation'),),

    _t(i.d, 'fly culture technique',
       tech.maintaining,
       (hasParticipant,
        OntTerm('NCBITaxon:7215', label='Drosophila <fruit fly, genus>')
        #OntTerm(term='drosophila')
       ),
       synonyms=('fly culture',),),

    _t(i.d, 'rodent husbandry technique',
       (ilxtr.hasPrimaryParticipant,
        OntTerm('NCBITaxon:9989', label='Rodentia')  # FIXME population vs individual?
       ),
       synonyms=('rodent husbandry', 'rodent culture technique'),),


    _t(i.d, 'enclosure design technique',  # FIXME design technique? produces some information artifact?
       (ilxtr.hasSomething, i.d)),

    _t(i.d, 'feeding technique',
       (ilxtr.hasSomething, i.d),
       synonyms=('feeding',),
    ),
    _t(i.d, 'housing technique',
       (ilxtr.hasSomething, i.d),
       synonyms=('housing',),
    ),
    _t(i.d, 'mating technique',
       (ilxtr.hasSomething, i.d),
       synonyms=('mating',),
    ),
    _t(i.d, 'watering technique',
       (ilxtr.hasSomething, i.d),
       synonyms=('watering',),
    ),

    _t(tech.contrastEnhancement, 'contrast enhancement technique',
       (ilxtr.hasPrimaryAspect, ilxtr.contrast),  # some contrast
       (ilxtr.hasPrimaryAspect_dAdT, ilxtr.positive),
       synonyms=('contrast enhancement',),),
    _t(i.d, 'taggin technique',
       (ilxtr.hasSomething, i.d)),
    _t(i.d, 'staining technique',
       (ilxtr.hasSomething, i.d)),

    _t(i.d, 'immunochemical technique',
       (ilxtr.hasSomething, i.d)),
    _t(i.d,'immunocytochemical technique',
       (ilxtr.hasSomething, i.d),
       synonyms=('immunocytochemistry technique',
                 'immunocytochemistry')),
    _t(i.d,'immunohistochemical technique',
       (ilxtr.hasSomething, i.d),
       synonyms=('immunohistochemistry technique',
                 'immunohistochemistry')),

    _t(i.d, 'direct immunohistochemical technique',
       (ilxtr.hasSomething, i.d),
       synonyms=('direct immunohistochemistry technique',
                 'direct immunohistochemistry')),
    _t(i.d, 'indirect immunohistochemical technique',
       (ilxtr.hasSomething, i.d),
       synonyms=('indirect immunohistochemistry technique',
                 'indirect immunohistochemistry')),

    _t(tech.stateBasedContrastEnhancement, 'state based contrast enhancement technique',
       tech.contrastEnhancement,  # FIXME compare this to how we modelled fMRI below? is BOLD and _enhancement_?
    ),

    _t(i.d, 'separation technique',
       (ilxtr.hasSomething, i.d),
    ),
    _t(i.d, 'sorting technique',
       (ilxtr.hasSomething, i.d),),
    _t(i.d, 'sampling technique',
       (ilxtr.hasSomething, i.d),),
    _t(i.d, 'extraction technique',
       (ilxtr.hasSomething, i.d),),
    _t(i.d, 'pull-down technique',
       (ilxtr.hasSomething, i.d),),
    _t(i.d, 'isolation technique',
       (ilxtr.hasSomething, i.d),),
    _t(i.d, 'purification technique',
       (ilxtr.hasSomething, i.d),),

    _t(i.d, 'selection technique',
       (ilxtr.hasSomething, i.d),),
    _t(i.d, 'blind selection technique',
       (ilxtr.hasSomething, i.d),),
    _t(i.d, 'random selection technique',
       (ilxtr.hasSomething, i.d),),
    _t(i.d, 'targeted selection technique',
       (ilxtr.hasSomething, i.d),),

    _t(i.d, 'fractionation technique',
       (ilxtr.hasSomething, i.d),),
    _t(i.d, 'chromatography technique',
       (ilxtr.hasSomething, i.d),
       synonyms=('chromatography',),),
    _t(i.d, 'distillation technique',
       (ilxtr.hasSomething, i.d),
       synonyms=('distillation',),),
    _t(i.d, 'electrophoresis technique',
       (ilxtr.hasSomething, i.d),
       synonyms=('electrophoresis',),),
    _t(i.d, 'centrefugation technique',
       (ilxtr.hasSomething, i.d),
       synonyms=('centrefugation',),),
    _t(i.d, 'ultracentrefugation technique',
       (ilxtr.hasSomething, i.d),
       synonyms=('ultracentrefugation',),),

    _t(tech.measure, 'measurement technique',
       (hasParticipant,
        # FIXME vs material entity (alignment to what I mean by 'being')
        OntTerm('BFO:0000001', label='entity')
       ),
       (ilxtr.hasInformationOutput, ilxtr.informationEntity),
       synonyms=('measure',),
    ),

    _t(i.d, 'observational technique',
       tech.measure,
       (ilxtr.hasSomething, i.d),
       synonyms=('observation', 'observation technique'),),

    _t(i.d, 'procurement technique',
       (ilxtr.hasPrimaryParticipant,
        OntTerm('BFO:0000040', label='material entity')
        #OntTerm(term='material entity', prefix='BFO')
       ),
       (ilxtr.hasOutput,
        OntTerm('BFO:0000040', label='material entity')
        #OntTerm(term='material entity', prefix='BFO')
       ),
       def_='A technique for getting or retrieving something.',
       synonyms=('acquisition technique', 'procurement', 'acquistion', 'get')
    ),

    _t(tech.ising, 'ising technique',
       (ilxtr.hasPrimaryAspect, ilxtr['is']),),

    _t(tech.creating, 'creating technique',   # FIXME mightent we want to subclass off of these directly?
       tech.ising,
       (ilxtr.hasPrimaryAspect_dAdT, ilxtr.positive),
       synonyms=('synthesis technique',),
    ),

    _t(tech.destroying, 'destroying technique',
       tech.ising,
       (ilxtr.hasPrimaryAspect_dAdT, ilxtr.negative),),

    _t(tech.maintaining, 'maintaining technique',
       tech.ising,
       (ilxtr.hasPrimaryAspect_dAdT, ilxtr.zero),
       synonyms=('maintenance technique',),
    ),

    _t(i.d, 'analysis technique',
       (realizes, ilxtr.analysisRole),
       synonyms=('analysis',),),

    _t(i.d, 'data processing technique',
       (ilxtr.hasInformationInput, ilxtr.informationArtifact),
       (ilxtr.hasInformationOutput, ilxtr.informationArtifact),
       synonyms=('data processing',),),

    _t(i.d, 'image processing technique',
       (ilxtr.hasInformationInput, ilxtr.image),
       (ilxtr.hasInformationOutput, ilxtr.image),
       synonyms=('image processing',),),

    _t(tech.sigproc, 'signal processing technique',
       (ilxtr.hasInformationInput, ilxtr.timeSeries),  # FIXME are information inputs the priamry participant?
       (ilxtr.hasInformationOutput, ilxtr.timeSeries),
       synonyms=('signal processing',),),

    _t(i.d, 'signal filtering technique',
       # FIXME aspects of information entities...
       # lots of stuff going on here...
       tech.sigproc,
       (ilxtr.hasInformationPrimaryAspect, ilxtr.spectru),
       (ilxtr.hasInformationPrimaryAspect_dAdT, ilxtr.negative),
       (ilxtr.hasInformationPrimaryParticipant, ilxtr.timeSeries),  # FIXME
       synonyms=('signal filtering',),
    ),

    _t(i.d, 'electrophysiology technique',
       (ilxtr.hasPrimaryAspect, asp.electrical),  # FIXME...
       (ilxtr.hasPrimaryParticipant, ilxtr.physiologicalSystem),
       synonyms=('electrophysiology', 'electrophysiological technique'),
    ),

    _t(tech.contrastDetection, 'contrast detection technique',
       # a subclass could be differential contrast to electron scattering or something...
       #(ilxtr.hasPrimaryAspect_dAdPartOfPrimaryParticipant, ilxtr.nonZero),  # TODO FIXME this is MUCH better
       (ilxtr.hasPrimaryAspect, ilxtr.contrast),  # contrast to something? FIXME this seems a bit off...
       (ilxtr.hasPrimaryAspect_dAdS, ilxtr.nonZero),
       synonyms=('contrast detection',),
    ),

    _t(i.d, 'microscopy technique',
       (hasParticipant, ilxtr.microscope),  # electrophysiology microscopy techinque?
       synonyms=('microscopy',),
    ),

    _t(tech.imaging, 'imaging technique',
       (ilxtr.hasInformationOutput, ilxtr.image),
       synonyms=('imaging',),
    ),

    _t(i.d, 'photographic technique',
       (ilxtr.hasInformationOutput, ilxtr.photograph),
       synonyms=('photography',),
    ),

    _t(i.d, 'positron emission imaging',
       tech.imaging,
       (ilxtr.detects, ilxtr.positron)),

    _t(tech.opticalImaging, 'optical imaging',
       tech.imaging,
       (ilxtr.detects, ilxtr.visibleLight),  # owl:Class photon and hasWavelenght range ...
       synonyms=('light imaging', 'visible light imaging'),
    ),

    _t(i.d, 'intrinsic optical imaging',
       tech.opticalImaging,
       tech.contrastDetection,
       # this is a good counter example to x-ray imaging concernts
       # because it shows clearly how
       # "the reflectance to infared light by the brain"
       # that is not a thing that is a derived thing I think...
       # it is an aspect of the black box, it is not a _part_ of the back box
       (ilxtr.hasPrimaryAspect, ilxtr.intrinsicSignal),
       synonyms=('intrinsic signal optical imaging',),
    ),

    _t(i.d, 'x-ray imaging',
       tech.imaging,
       # VS contrast in the primary aspect being the signal created by the xrays...
       # can probably expand detects in cases where there are non-aspects...
       # still not entirely sure these shouldn't all be aspects too...
       (ilxtr.detects, ilxtr.xrays),
    ),  # owl:Class photon and hasWavelenght range ...

    _t(tech.MRI, 'magnetic resonance imaging',
       tech.imaging,
       tech.contrastDetection,
       # NRM is an aspect not one of the mediators
       (ilxtr.hasPrimaryAspect, ilxtr.nuclearMagneticResonance),
       # as long as the primaryAspect is subClassOf ilxtr.nuclearMagneticResonance then we are ok
       # and we won't get duplication of primary aspects
       synonyms=('MRI', 'nuclear magnetic resonance imaging'),
    ),

    _t(tech.fMRI, 'functional magnetic resonance imaging',
       # AAAAAAA how to deal with
       # "change in nuclear magnetic resonance of iron molecules as a function of time and their bound oxygen"
       # "BOLD" blood oxygenation level dependent contrast is something different...
       #ilxtr.NMR_of_iron_in_the_blood  # ICK
       #(hasPrimaryParticipant, ilxtr.???)
       #(hasPart, tech.MRI),  # FIXME how to deal with this...
       #(hasPart, tech.bloodOxygenLevel),
       #(ilxtr.hasPrimaryAspect, ilxtr.nuclearMagneticResonance),
       tech.MRI,  # FIXME vs respeccing everything?
       (ilxtr.hasPrimaryParticipant, ilxtr.haemoglobin),
       (ilxtr.hasPrimaryParticipantSubsetRule, ilxtr.hasBoundOxygen),  # FIXME not quite right still?
       synonyms=('fMRI', 'functional nuclear magnetic resonance imaging'),),
    olit(tech.fMRI, rdfs.comment,
         ('Note that this deals explicitly only with the image acquistion portion of fMRI. '
          'Other parts of the full process and techniques in an fMRI study should be modelled separately. '
          'They can be tied to fMRI using hasPart: or hasPriorTechnique something similar.')),  # TODO

    _t(tech.dwMRI, 'diffusion weighted magnetic resonance imaging',
       tech.MRI,
       (ilxtr.hasPrimaryParticipant, OntTerm('CHEBI:15377', label='water')),
       synonyms=('dwMRI', 'diffusion weighted nuclear magnetic resonance imaging'),),

    _t(tech.DTI, 'diffusion tensor imaging',
       tech.dwMRI,
       synonyms=('DTI',),),

    # modification techniques
    _t(i.d, 'modification technique',
       (ilxtr.hasPrimaryAspect, asp['']),
    ),

    _t(i.d, 'activation technique',
       (ilxtr.hasSomething, i.d),
    ),

    _t(i.d, 'deactivation technique',
       (ilxtr.hasSomething, i.d),
    ),

    _t(i.d, 'euthanasia technique',
       tech.destroying,  # FIXME this is not quite right
       (ilxtr.hasSomething, i.d),
    ),

    _t(i.d, 'pharmacological technique',
       (ilxtr.hasSomething, i.d),
       synonyms=('pharmacology',)
    ),

    _t(i.d, 'photoactivation technique',
       (ilxtr.hasSomething, i.d),
    ),

    _t(i.d, 'photoinactivation technique',
       (ilxtr.hasSomething, i.d),
    ),

    _t(i.d, 'photobleaching technique',
       (ilxtr.hasSomething, i.d),
    ),

    _t(i.d, 'photoconversion technique',
       (ilxtr.hasSomething, i.d),
    ),

    _t(i.d, 'molecular uncaging technique',
       (ilxtr.hasSomething, i.d),
       synonyms=('uncaging', 'uncaging technique')
    ),

    _t(i.d, 'physical modification technique',
       # FIXME for all physical things is it that the aspect is physical?
       # or that there is actually a physical change induced?
       (ilxtr.hasSomething, i.d),
    ),

    _t(i.d, 'ablation technique',
       (ilxtr.hasSomething, i.d),
    ),

    _t(i.d, 'blinding technique',
       (ilxtr.hasPrimaryAspect, asp.vision),
       (ilxtr.hasPrimaryAspect_dAdT, ilxtr.negative),
    ),

    _t(i.d, 'crushing technique',
       (ilxtr.hasSomething, i.d),
    ),

    _t(i.d, 'deafferenting technique',
       (ilxtr.hasSomething, i.d),
    ),

    _t(i.d, 'depolarization technique',
       (ilxtr.hasPrimaryAspect, asp.voltage),
       (ilxtr.hasPrimaryAspect_dAdT, ilxtr.positive),
       # yes this is confusing, but cells have negative membrane potentials
    ),

    _t(i.d, 'hyperpolarization technique',
       (ilxtr.hasPrimaryAspect, asp.voltage),
       (ilxtr.hasPrimaryAspect_dAdT, ilxtr.negative),
    ),

    _t(i.d, 'illumination technique',
       (ilxtr.hasSomething, i.d),
    ),

    _t(i.d, 'lesioning technique',
       (ilxtr.hasSomething, i.d),
    ),

    _t(i.d, 'sensory deprivation technique',
       (ilxtr.hasSomething, i.d),
    ),

    _t(i.d, 'transection technique',
       (ilxtr.hasSomething, i.d),
    ),

    _t(i.d, 'stimulation technique',
       (ilxtr.hasPrimaryAspect, ilxtr.physiologicalActivity),  # TODO
    ),

    _t(i.d, 'physical stimulation technique',  # FIXME another use of physical
       (ilxtr.hasSomething, i.d),
    ),

    _t(i.d, 'electrical stimulation technique',
       (ilxtr.hasProbe, asp.electrical),
       (ilxtr.hasSomething, i.d),
    ),

    _t(tech.stim_Magnetic, 'magnetic stimulation technique',
       (ilxtr.hasProbe, asp.magnetic),  # FIXME this doesn't seem right...
       (ilxtr.hasSomething, i.d),
    ),

    _t(i.d, 'transcranial magnetic stimulation technique',
       tech.stim_Magnetic,
       (ilxtr.hasSomething, i.d),
    ),

    _t(i.d, 'cortico-cortical evoked potential technique',
       (ilxtr.hasSomething, i.d),
    ),

    _t(i.d, 'microstimulation technique',
       (ilxtr.hasSomething, i.d),
    ),

    _t(tech.surgery, 'surgical technique',
       (ilxtr.hasSomething, i.d),
       synonyms=('surgery',),),

    _t(i.d, 'biopsy technique',
       tech.surgery,  # FIXME
       tech.maintaining,  # things that have output tissue that don't unis something
       (ilxtr.hasOutput, ilxtr.tissue),  # TODO
    ),

    _t(i.d, 'craniotomy technique',
       tech.surgery,  # FIXME
       (ilxtr.hasSomething, i.d),
       def_='Makes a hold in the cranium (head).',
    ),

    _t(i.d, 'durotomy technique',
       tech.surgery,  # FIXME
       (ilxtr.hasSomething, i.d),
       def_='Makes a hold in the dura.',
    ),

    _t(i.d, 'transplantation technique',
       tech.surgery,  # FIXME
       (ilxtr.hasSomething, i.d),
       synonyms=('transplant',)
    ),

    _t(i.d, 'implantation technique',
       tech.surgery,  # FIXME
       (ilxtr.hasSomething, i.d),
    ),

    _t(i.d, 'stereotaxic technique',
       tech.surgery,  # FIXME
       (hasParticipant, ilxtr.stereotax),
    ),

    _t(i.d, 'behavioral technique',  # FIXME this is almost always actually some environmental manipulation
       # asp.behavioral -> 'Something measurable aspect of an organisms behavior. i.e. the things that it does.'
       (ilxtr.hasPrimaryAspect, asp.behavioral),
    ),

    _t(i.d, 'behavioral conditioning technique',
       (ilxtr.hasSomething, i.d),
       def_='A technique for producing a specific behavioral response to a set of stimuli.',  # FIXME
       synonyms=('behavioral conditioning', 'conditioning', 'conditioning technique')
    ),

    _t(i.d, 'environmental manipulation technique',
       # FIXME extremely broad, includes basically everything we do in science that is not
       # done directly to the primary subject
       (ilxtr.hasPrimarySubject, ilxtr.notTheSubject),
    ),

    _t(i.d, 'environmental enrichment technique',
       (ilxtr.hasSomething, i.d),
       synonyms=('behavioral enrichment technique',)
       # and here we see the duality between environment and behavior
    ),

    _t(i.d, 'dietary technique',
       (ilxtr.hasSomething, i.d),
    ),

    _t(i.d, 'dietary restriction technique',
       (ilxtr.hasSomething, i.d),
    ),

    _t(i.d, 'food deprivation technique',
       (ilxtr.hasPrimaryParticipant, ilxtr.food),
       (ilxtr.hasPrimaryAspect, asp.amount),
       (ilxtr.hasPrimaryAspect_dAdT, ilxtr.negative),
       synonyms=('starvation technique',
                 'food restriction technique',
       )
    ),

    _t(i.d, 'water deprivation technique',
       (ilxtr.hasPrimaryParticipant,
        OntTerm('CHEBI:15377', label='water')
       ),
       (ilxtr.hasPrimaryAspect, asp.amount),
       (ilxtr.hasPrimaryAspect_dAdT, ilxtr.negative),
       synonyms=('water restriction technique',
                 'water restriction',
       )
    ),

    _t(tech.sectioning, 'sectioning technique',
       (ilxtr.hasOutput, ilxtr.sectionsOfPrimaryInput),  # FIXME circular
       synonyms=('sectioning',),),  # FIXME

    _t(i.d, 'block face sectioning technique',
       tech.sectioning,
       (ilxtr.hasSomething, i.d),
    ),

    _t(i.d, 'microtomy technique',
       (ilxtr.hasParticipant, ilxtr.microtome),
       synonyms=('microtomy',)
    ),

    _t(i.d, 'ultramicrotomy technique',
       (ilxtr.hasParticipant, ilxtr.ultramicrotome),
       synonyms=('ultramicrotomy',)
    ),

    _t(i.d, 'array tomographic technique',
       (hasParticipant, ilxtr.microscope),  # FIXME more precisely?
       (ilxtr.isConstrainedBy, ilxtr.radonTransform),
       synonyms=('array tomography', 'array tomography technique')
    ),

    _t(i.d, 'correlative light-electron microscopy technique',
       (hasParticipant, ilxtr.electronMicroscope),
       (hasParticipant, ilxtr.lightMicroscope),
       synonyms=('correlative light-electron microscopy',)
    ),

    _t(i.d, 'serial blockface electron microscopy technique',
       (hasParticipant, ilxtr.electronMicroscope),
       (hasParticipant, ilxtr.ultramicrotome),
       synonyms=('serial blockface electron microscopy',)
    ),

    _t(i.d, 'super resolution microscopy technique',
       (hasParticipant, ilxtr.microscope),  # FIXME more
       (ilxtr.isConstrainedBy, ilxtr.superResolutionAlgorithem),
       synonyms=('super resolution microscopy',)
    ),

    _t(i.d, 'northern blotting technique',
       (ilxtr.hasSomething, i.d),
       synonyms=('northern blot',)
    ),
    _t(i.d, 'southern blotting technique',
       (ilxtr.hasSomething, i.d),
       synonyms=('southern blot',)
    ),
    _t(i.d, 'western blotting technique',
       (ilxtr.hasSomething, i.d),
       synonyms=('wester blot',)
    ),

    _t(i.d, 'patch clamp technique',
       (ilxtr.hasSomething, i.d),
    ),

    _t(i.d, 'cell attached patch technique',
       (ilxtr.hasSomething, i.d),
    ),

    _t(i.d, 'inside out patch technique',
       (ilxtr.hasSomething, i.d),
    ),

    _t(i.d, 'loose patch technique',
       (ilxtr.hasSomething, i.d),
    ),

    _t(i.d, 'outside out patch technique',
       (ilxtr.hasSomething, i.d),
    ),

    _t(i.d, 'perforated patch technique',
       (ilxtr.hasSomething, i.d),
    ),

    _t(i.d, 'whole cell patch clamp technique',
       (ilxtr.hasSomething, i.d),
    ),

    _t(i.d, 'current clamp technique',
       (ilxtr.hasSomething, i.d),
    ),

    _t(i.d, 'voltage clamp technique',
       (ilxtr.hasSomething, i.d),
    ),

    _t(i.d, ' technique',
       (ilxtr.hasSomething, i.d),
    ),

    _t(i.d, ' technique',
       (ilxtr.hasSomething, i.d),
    ),

) + (  # aspects
    oc(asp.amount, ilxtr.aspect),
    oc(asp['count'], ilxtr.amount),

    oc(asp.behavioral, ilxtr.aspect),

    oc(asp.physiological, ilxtr.aspect),  # FIXME vs ilxtr.physiologicalSystem?

    oc(asp.sensory, ilxtr.aspect),
    oc(asp.vision, asp.sensory),

    oc(asp.electromagnetic, ilxtr.aspect),
    oc(asp.electrical, asp.electromagnetic),
    oc(asp.voltage, asp.electrical),
    oc(asp.current, asp.electrical),
    oc(asp.charge, asp.electrical),
    oc(asp.magnetic, asp.electromagnetic),

) + (  # other
    oc(ilxtr.thingWithSequence),
    oc(OntTerm('CHEBI:33696', label='nucleic acid'), ilxtr.thingWithSequence),  # FIXME should not have to put oc here, but byto[ito] becomes unhappy
)

def halp():
    import rdflib
    from IPython import embed
    trips = sorted(flattenTriples(triples))
    graph = rdflib.Graph()
    *(graph.add(t) for t in trips),
    *(print(tuple(qname(e) if not isinstance(e, rdflib.BNode) else e[:5] for e in t)) for t in trips),
    embed()
    return trips
#trips = halp()

methods = simpleOnt(filename=filename,
                    prefixes=prefixes,
                    imports=imports,
                    triples=triples,
                    comment=comment,
                    _repo=_repo)

def expand(_makeGraph, *graphs, debug=False):
    import rdflib
    import RDFClosure as rdfc
    graph = rdflib.Graph()
    for graph_ in graphs:
        [graph.bind(k, v) for k, v in graph_.namespaces()]
        [graph.add(t) for t in graph_]
    g = _makeGraph.__class__('', graph=graph)
    g.filename = _makeGraph.filename
    # other options are
    # OWLRL_Semantis RDFS_OWLRL_Semantics but both cuase trouble
    # all of these are SUPER slow to run on cpython, very much suggest pypy3
    #rdfc.DeductiveClosure(rdfc.OWLRL_Extension_Trimming).expand(graph)  # monumentally slow even on pypy3
    #rdfc.DeductiveClosure(rdfc.OWLRL_Extension).expand(graph)
    eg = rdflib.Graph()
    [eg.add(t) for t in graph_]
    closure = rdfc.OWLRL_Semantics
    rdfc.DeductiveClosure(closure).expand(eg)
    [not graph.add((s, rdfs.subClassOf, o))
     and [graph.add(t) for t in annotation(ilxtr.isDefinedBy, closure.__name__,
                                           s, rdfs.subClassOf, o)]
     for s, o in eg.subject_objects(rdfs.subClassOf)
     if s != o and  # prevent cluttering the graph
     #o not in [to for o_ in eg.objects(s, rdfs.subClassOf)  # not working correctly
               #for to in eg.objects(o_) if o_ != o] and
     not isinstance(s, rdflib.BNode) and
     not isinstance(o, rdflib.BNode) and
     'interlex' in s and 'interlex' in o]
    g.write()
    displayGraph(graph, debug=debug)

#displayGraph(methods.graph, debug)
methods._graph.add_namespace('asp', str(asp))
methods._graph.add_namespace('ilxtr', str(ilxtr))  # FIXME why is this now showing up...
methods._graph.add_namespace('tech', str(tech))
#mc = methods.graph.__class__()
#mc.add(t) for t in methods_core.graph if t[0] not in
expand(methods._graph, methods_core.graph)#, methods_core.graph)  # FIXME including core breaks everying?
expand(methods._graph, methods.graph)#, methods_core.graph)  # FIXME including core breaks everying?

