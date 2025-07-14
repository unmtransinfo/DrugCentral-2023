import functools
import random

from django.db import models
from django.contrib.postgres.search import SearchQuery, SearchRank, SearchVectorField

def memoize(f):
    @functools.wraps(f)
    def g(self, *args):
        cache = getattr(self, '_memoize_cache', None)
        if cache is None:
            cache = {}
            self._memoize_cache = cache
        key = f, args
        cached = cache.get(key)
        if cached is None:
            cached = f(self, *args)
            cache[key] = cached
        return cached
    return g

class ActTableFull(models.Model):
    act_id = models.IntegerField(primary_key=True)
    struct = models.ForeignKey('Structures', models.DO_NOTHING, to_field='id')
    target = models.ForeignKey('TargetDictionary', models.DO_NOTHING)
    target_name = models.CharField(max_length=200, blank=True, null=True)
    target_class = models.ForeignKey('TargetClass', models.DO_NOTHING, db_column='target_class', blank=True, null=True, to_field='l1')
    accession = models.CharField(max_length=1000, blank=True, null=True)
    gene = models.CharField(max_length=1000, blank=True, null=True)
    swissprot = models.CharField(max_length=1000, blank=True, null=True)
    act_value = models.FloatField(blank=True, null=True)
    act_unit = models.CharField(max_length=100, blank=True, null=True)
    act_type = models.CharField(max_length=100, blank=True, null=True)
    act_comment = models.CharField(max_length=1000, blank=True, null=True)
    act_source = models.CharField(max_length=100, blank=True, null=True)
    relation = models.CharField(max_length=5, blank=True, null=True)
    moa = models.SmallIntegerField(blank=True, null=True)
    moa_source = models.CharField(max_length=100, blank=True, null=True)
    act_source_url = models.CharField(max_length=500, blank=True, null=True)
    moa_source_url = models.CharField(max_length=500, blank=True, null=True)
    action_type = models.ForeignKey('ActionType', models.DO_NOTHING, db_column='action_type', blank=True, null=True, to_field='action_type')
    first_in_class = models.SmallIntegerField(blank=True, null=True)
    tdl = models.CharField(max_length=500, blank=True, null=True)
    act_ref = models.ForeignKey('Reference', models.DO_NOTHING, blank=True, null=True, related_name='+')
    moa_ref = models.ForeignKey('Reference', models.DO_NOTHING, blank=True, null=True, related_name='+')
    organism = models.CharField(max_length=150, blank=True, null=True)

    def swissprot_short(self):
        swissprots = self.swissprots()
        if swissprots:
            return swissprots[0]
        return None

    @memoize
    def swissprots(self):
        swissprots = [] if self.swissprot is None else self.swissprot.split('|')
        accessions = [] if self.accession is None else self.accession.split('|')
        assert len(swissprots) == len(accessions)
        return list(zip(swissprots, accessions))

    def swissprots_human(self):
        return [(swissprot, _) for swissprot, _ in self.swissprots()
                if swissprot.lower().endswith('_human')]

    def swissprots_nonhuman(self):
        return [(swissprot, _) for swissprot, _ in self.swissprots()
                if not swissprot.lower().endswith('_human')]

    class Meta:
        managed = False
        db_table = 'act_table_full'


class ActionType(models.Model):
    action_type = models.CharField(unique=True, max_length=50)
    description = models.CharField(max_length=200)
    parent_type = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'action_type'


class ActiveIngredient(models.Model):
    active_moiety_unii = models.CharField(max_length=20, blank=True, null=True)
    active_moiety_name = models.CharField(max_length=4000, blank=True, null=True)
    unit = models.CharField(max_length=20, blank=True, null=True)
    quantity = models.FloatField(blank=True, null=True)
    substance_unii = models.CharField(max_length=20, blank=True, null=True)
    substance_name = models.CharField(max_length=4000, blank=True, null=True)
    ndc_product_code = models.ForeignKey('Product', models.DO_NOTHING, db_column='ndc_product_code', blank=True, null=True, to_field='ndc_product_code')
    struct = models.ForeignKey('Structures', models.DO_NOTHING, blank=True, null=True, to_field='id')
    quantity_denom_unit = models.CharField(max_length=20, blank=True, null=True)
    quantity_denom_value = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'active_ingredient'


class Approval(models.Model):
    struct = models.ForeignKey('Structures', models.DO_NOTHING, to_field='id')
    approval = models.DateField(blank=True, null=True)
    type = models.ForeignKey('ApprovalType', models.DO_NOTHING, db_column='type', to_field='descr')
    applicant = models.CharField(max_length=100, blank=True, null=True)
    orphan = models.BooleanField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'approval'
        unique_together = (('struct', 'type'),)


class ApprovalType(models.Model):
    descr = models.CharField(unique=True, max_length=200, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'approval_type'


class Atc(models.Model):
    code = models.CharField(unique=True, max_length=7)
    chemical_substance = models.CharField(max_length=250)
    l1_code = models.CharField(max_length=1)
    l1_name = models.CharField(max_length=200)
    l2_code = models.CharField(max_length=3)
    l2_name = models.CharField(max_length=200)
    l3_code = models.CharField(max_length=4)
    l3_name = models.CharField(max_length=200)
    l4_code = models.CharField(max_length=5)
    l4_name = models.CharField(max_length=200)
    chemical_substance_count = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'atc'


class AtcDdd(models.Model):
    atc_code = models.CharField(max_length=7, blank=True, null=True)
    ddd = models.FloatField()
    unit_type = models.CharField(max_length=10, blank=True, null=True)
    route = models.CharField(max_length=20, blank=True, null=True)
    comment = models.CharField(max_length=100, blank=True, null=True)
    struct = models.ForeignKey('Structures', models.DO_NOTHING, to_field='id')

    class Meta:
        managed = False
        db_table = 'atc_ddd'


class AttrType(models.Model):
    name = models.CharField(unique=True, max_length=100)
    type = models.CharField(max_length=20)

    class Meta:
        managed = False
        db_table = 'attr_type'


class DataSource(models.Model):
    src_id = models.SmallIntegerField(primary_key=True)
    source_name = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'data_source'


class Dbversion(models.Model):
    version = models.BigIntegerField(primary_key=True)
    dtime = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'dbversion'


class Ddi(models.Model):
    drug_class1 = models.ForeignKey('DrugClass', models.DO_NOTHING, db_column='drug_class1', related_name='+')
    drug_class2 = models.ForeignKey('DrugClass', models.DO_NOTHING, db_column='drug_class2', related_name='+')
    ddi_ref_id = models.IntegerField()
    ddi_risk = models.ForeignKey('DdiRisk', models.DO_NOTHING, db_column='ddi_risk')
    description = models.CharField(max_length=4000, blank=True, null=True)
    source_id = models.CharField(max_length=200, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'ddi'
        unique_together = (('drug_class1', 'drug_class2', 'ddi_ref_id'),)


class DdiRisk(models.Model):
    risk = models.CharField(max_length=200)
    ddi_ref_id = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'ddi_risk'
        unique_together = (('risk', 'ddi_ref_id'),)


class Doid(models.Model):
    id = models.IntegerField(primary_key=True)
    label = models.CharField(max_length=1000, blank=True, null=True)
    doid = models.CharField(unique=True, max_length=50, blank=True, null=True)
    url = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'doid'


class DoidXref(models.Model):
    doid = models.ForeignKey(Doid, models.DO_NOTHING, db_column='doid', blank=True, null=True, to_field='doid')
    source = models.CharField(max_length=50, blank=True, null=True)
    xref = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'doid_xref'
        unique_together = (('doid', 'source', 'xref'),)


class DrugClass(models.Model):
    name = models.CharField(unique=True, max_length=500)
    is_group = models.SmallIntegerField()
    source = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'drug_class'


class Faers(models.Model):
    struct = models.ForeignKey('Structures', models.DO_NOTHING, blank=True, null=True, to_field='id')
    meddra_name = models.CharField(max_length=200)
    meddra_code = models.BigIntegerField()
    level = models.CharField(max_length=5, blank=True, null=True)
    llr = models.FloatField(blank=True, null=True)
    llr_threshold = models.FloatField(blank=True, null=True)
    drug_ae = models.IntegerField(blank=True, null=True)
    drug_no_ae = models.IntegerField(blank=True, null=True)
    no_drug_ae = models.IntegerField(blank=True, null=True)
    no_drug_no_ae = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'faers'


class FaersFemale(models.Model):
    struct = models.ForeignKey('Structures', models.DO_NOTHING, blank=True, null=True, to_field='id')
    meddra_name = models.CharField(max_length=200)
    meddra_code = models.BigIntegerField()
    level = models.CharField(max_length=5, blank=True, null=True)
    llr = models.FloatField(blank=True, null=True)
    llr_threshold = models.FloatField(blank=True, null=True)
    drug_ae = models.IntegerField(blank=True, null=True)
    drug_no_ae = models.IntegerField(blank=True, null=True)
    no_drug_ae = models.IntegerField(blank=True, null=True)
    no_drug_no_ae = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'faers_female'


class FaersGer(models.Model):
    struct = models.ForeignKey('Structures', models.DO_NOTHING, blank=True, null=True, to_field='id')
    meddra_name = models.CharField(max_length=200)
    meddra_code = models.BigIntegerField()
    level = models.CharField(max_length=5, blank=True, null=True)
    llr = models.FloatField(blank=True, null=True)
    llr_threshold = models.FloatField(blank=True, null=True)
    drug_ae = models.IntegerField(blank=True, null=True)
    drug_no_ae = models.IntegerField(blank=True, null=True)
    no_drug_ae = models.IntegerField(blank=True, null=True)
    no_drug_no_ae = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'faers_ger'


class FaersMale(models.Model):
    struct = models.ForeignKey('Structures', models.DO_NOTHING, blank=True, null=True, to_field='id')
    meddra_name = models.CharField(max_length=200)
    meddra_code = models.BigIntegerField()
    level = models.CharField(max_length=5, blank=True, null=True)
    llr = models.FloatField(blank=True, null=True)
    llr_threshold = models.FloatField(blank=True, null=True)
    drug_ae = models.IntegerField(blank=True, null=True)
    drug_no_ae = models.IntegerField(blank=True, null=True)
    no_drug_ae = models.IntegerField(blank=True, null=True)
    no_drug_no_ae = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'faers_male'


class FaersPed(models.Model):
    struct = models.ForeignKey('Structures', models.DO_NOTHING, blank=True, null=True, to_field='id')
    meddra_name = models.CharField(max_length=200)
    meddra_code = models.BigIntegerField()
    level = models.CharField(max_length=5, blank=True, null=True)
    llr = models.FloatField(blank=True, null=True)
    llr_threshold = models.FloatField(blank=True, null=True)
    drug_ae = models.IntegerField(blank=True, null=True)
    drug_no_ae = models.IntegerField(blank=True, null=True)
    no_drug_ae = models.IntegerField(blank=True, null=True)
    no_drug_no_ae = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'faers_ped'


class Humanim(models.Model):
    struct = models.ForeignKey('Structures', models.DO_NOTHING, blank=True, null=True, to_field='id')
    human = models.BooleanField(blank=True, null=True)
    animal = models.BooleanField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'humanim'


class IdType(models.Model):
    type = models.CharField(unique=True, max_length=50)
    description = models.CharField(max_length=500, blank=True, null=True)
    url = models.CharField(max_length=500, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'id_type'


class Identifier(models.Model):
    identifier = models.CharField(max_length=50)
    id_type = models.ForeignKey(IdType, models.DO_NOTHING, db_column='id_type', to_field='type')
    struct = models.ForeignKey('Structures', models.DO_NOTHING, to_field='id')
    parent_match = models.BooleanField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'identifier'
        unique_together = (('identifier', 'id_type', 'struct'),)


class IjcConnectItems(models.Model):
    id = models.CharField(primary_key=True, max_length=32)
    username = models.CharField(max_length=128, blank=True, null=True)
    type = models.CharField(max_length=200)
    data = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'ijc_connect_items'
        unique_together = (('type', 'username'),)


class IjcConnectStructures(models.Model):
    id = models.CharField(primary_key=True, max_length=32)
    structure_hash = models.CharField(max_length=64)
    structure = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'ijc_connect_structures'
        unique_together = (('id', 'structure_hash'),)


class InnStem(models.Model):
    stem = models.CharField(unique=True, max_length=50, blank=True, null=True)
    definition = models.CharField(max_length=1000)
    national_name = models.CharField(max_length=20, blank=True, null=True)
    length = models.SmallIntegerField(blank=True, null=True)
    discontinued = models.BooleanField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'inn_stem'


class Label(models.Model):
    id = models.CharField(primary_key=True, max_length=50)
    category = models.CharField(max_length=100, blank=True, null=True)
    title = models.CharField(max_length=1000, blank=True, null=True)
    effective_date = models.DateField(blank=True, null=True)
    assigned_entity = models.CharField(max_length=500, blank=True, null=True)
    pdf_url = models.CharField(max_length=500, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'label'


class LincsSignature(models.Model):
    struct_id1 = models.IntegerField(blank=True, null=True)
    struct_id2 = models.IntegerField(blank=True, null=True)
    is_parent1 = models.BooleanField(blank=True, null=True)
    is_parent2 = models.BooleanField(blank=True, null=True)
    cell_id = models.CharField(max_length=10, blank=True, null=True)
    rmsd = models.FloatField(blank=True, null=True)
    rmsd_norm = models.FloatField(blank=True, null=True)
    pearson = models.FloatField(blank=True, null=True)
    euclid = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'lincs_signature'
        unique_together = (('struct_id1', 'struct_id2', 'is_parent1', 'is_parent2', 'cell_id'),)


class ObExclusivity(models.Model):
    appl_type = models.CharField(max_length=1, blank=True, null=True)
    appl_no = models.CharField(max_length=6, blank=True, null=True)
    product_no = models.CharField(max_length=3, blank=True, null=True)
    exclusivity_code = models.ForeignKey('ObExclusivityCode', models.DO_NOTHING, db_column='exclusivity_code', blank=True, null=True)
    exclusivity_date = models.DateField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'ob_exclusivity'


class ObExclusivityCode(models.Model):
    code = models.CharField(primary_key=True, max_length=10)
    description = models.CharField(max_length=500, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'ob_exclusivity_code'


class ObPatent(models.Model):
    appl_type = models.CharField(max_length=1, blank=True, null=True)
    appl_no = models.CharField(max_length=6, blank=True, null=True)
    product_no = models.CharField(max_length=3, blank=True, null=True)
    patent_no = models.CharField(max_length=200, blank=True, null=True)
    patent_expire_date = models.DateField(blank=True, null=True)
    drug_substance_flag = models.CharField(max_length=1, blank=True, null=True)
    drug_product_flag = models.CharField(max_length=1, blank=True, null=True)
    patent_use_code = models.ForeignKey('ObPatentUseCode', models.DO_NOTHING, db_column='patent_use_code', blank=True, null=True)
    delist_flag = models.CharField(max_length=1, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'ob_patent'


class ObPatentUseCode(models.Model):
    code = models.CharField(primary_key=True, max_length=10)
    description = models.CharField(max_length=500, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'ob_patent_use_code'


class ObProduct(models.Model):
    ingredient = models.CharField(max_length=500, blank=True, null=True)
    trade_name = models.CharField(max_length=200, blank=True, null=True)
    applicant = models.CharField(max_length=50, blank=True, null=True)
    strength = models.CharField(max_length=500, blank=True, null=True)
    appl_type = models.CharField(max_length=1, blank=True, null=True)
    appl_no = models.CharField(max_length=6, blank=True, null=True)
    te_code = models.CharField(max_length=20, blank=True, null=True)
    approval_date = models.DateField(blank=True, null=True)
    rld = models.SmallIntegerField(blank=True, null=True)
    type = models.CharField(max_length=5, blank=True, null=True)
    applicant_full_name = models.CharField(max_length=200, blank=True, null=True)
    dose_form = models.CharField(max_length=50, blank=True, null=True)
    route = models.CharField(max_length=100, blank=True, null=True)
    product_no = models.CharField(max_length=3, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'ob_product'


class OmopRelationship(models.Model):
    struct = models.ForeignKey('Structures', models.DO_NOTHING, to_field='id')
    concept_id = models.IntegerField()
    relationship_name = models.CharField(max_length=256)
    concept_name = models.CharField(max_length=256)
    umls_cui = models.CharField(max_length=8, blank=True, null=True)
    snomed_full_name = models.CharField(max_length=500, blank=True, null=True)
    cui_semantic_type = models.CharField(max_length=4, blank=True, null=True)
    snomed_conceptid = models.BigIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'omop_relationship'
        unique_together = (('struct', 'concept_id'),)


class Parentmol(models.Model):
    cd_id = models.AutoField(primary_key=True)
    name = models.CharField(unique=True, max_length=250, blank=True, null=True)
    cas_reg_no = models.CharField(unique=True, max_length=50, blank=True, null=True)
    inchi = models.CharField(max_length=32672, blank=True, null=True)
    nostereo_inchi = models.CharField(max_length=32672, blank=True, null=True)
    molfile = models.TextField(blank=True, null=True)
    molimg = models.BinaryField(blank=True, null=True)
    smiles = models.CharField(max_length=32672, blank=True, null=True)
    inchikey = models.CharField(max_length=27, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'parentmol'


class Pdb(models.Model):
    struct = models.ForeignKey('Structures', models.DO_NOTHING, to_field='id')
    pdb = models.CharField(max_length=4)
    chain_id = models.CharField(max_length=3, blank=True, null=True)
    accession = models.CharField(max_length=20, blank=True, null=True)
    title = models.CharField(max_length=1000, blank=True, null=True)
    pubmed_id = models.IntegerField(blank=True, null=True)
    exp_method = models.CharField(max_length=50, blank=True, null=True)
    deposition_date = models.DateField(blank=True, null=True)
    ligand_id = models.CharField(max_length=20, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'pdb'
        unique_together = (('struct', 'pdb'),)


class PharmaClass(models.Model):
    struct = models.ForeignKey('Structures', models.DO_NOTHING, blank=True, null=True, to_field='id')
    type = models.CharField(max_length=20)
    name = models.CharField(max_length=1000)
    class_code = models.CharField(max_length=20, blank=True, null=True)
    source = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'pharma_class'
        unique_together = (('struct', 'type', 'name'),)


class Pka(models.Model):
    struct = models.ForeignKey('Structures', models.DO_NOTHING, to_field='id')
    pka_level = models.CharField(max_length=5, blank=True, null=True)
    value = models.FloatField(blank=True, null=True)
    pka_type = models.CharField(max_length=1)

    class Meta:
        managed = False
        db_table = 'pka'


class Prd2Label(models.Model):
    ndc_product_code = models.OneToOneField('Product', models.DO_NOTHING, db_column='ndc_product_code', to_field='ndc_product_code')
    label = models.ForeignKey(Label, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'prd2label'
        unique_together = (('ndc_product_code', 'label'),)


class Product(models.Model):
    ndc_product_code = models.CharField(unique=True, max_length=20)
    form = models.CharField(max_length=250, blank=True, null=True)
    generic_name = models.CharField(max_length=4000, blank=True, null=True)
    product_name = models.CharField(max_length=1000, blank=True, null=True)
    route = models.CharField(max_length=50, blank=True, null=True)
    marketing_status = models.CharField(max_length=500, blank=True, null=True)
    active_ingredient_count = models.IntegerField(blank=True, null=True)
    labels_set = models.ManyToManyField(Label, through='Prd2Label')

    class Meta:
        managed = False
        db_table = 'product'


class Property(models.Model):
    property_type = models.ForeignKey('PropertyType', models.DO_NOTHING, blank=True, null=True, to_field='id')
    property_type_symbol = models.CharField(max_length=10, blank=True, null=True)
    struct = models.ForeignKey('Structures', models.DO_NOTHING, blank=True, null=True, to_field='id')
    value = models.FloatField(blank=True, null=True)
    reference = models.ForeignKey('Reference', models.DO_NOTHING, blank=True, null=True, to_field='id')
    reference_type = models.CharField(max_length=50, blank=True, null=True)
    source = models.CharField(max_length=80, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'property'


class PropertyType(models.Model):
    category = models.CharField(max_length=20, blank=True, null=True)
    name = models.CharField(max_length=80, blank=True, null=True)
    symbol = models.CharField(max_length=10, blank=True, null=True)
    units = models.CharField(max_length=10, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'property_type'


class ProteinType(models.Model):
    type = models.CharField(unique=True, max_length=50)

    class Meta:
        managed = False
        db_table = 'protein_type'


class RefType(models.Model):
    type = models.CharField(unique=True, max_length=50)

    class Meta:
        managed = False
        db_table = 'ref_type'


class Reference(models.Model):
    pmid = models.IntegerField(unique=True, blank=True, null=True)
    doi = models.CharField(unique=True, max_length=50, blank=True, null=True)
    document_id = models.CharField(unique=True, max_length=200, blank=True, null=True)
    type = models.ForeignKey(RefType, models.DO_NOTHING, db_column='type', blank=True, null=True)
    authors = models.CharField(max_length=4000, blank=True, null=True)
    title = models.CharField(max_length=500, blank=True, null=True)
    isbn10 = models.CharField(unique=True, max_length=10, blank=True, null=True)
    url = models.CharField(max_length=1000, blank=True, null=True)
    journal = models.CharField(max_length=100, blank=True, null=True)
    volume = models.CharField(max_length=20, blank=True, null=True)
    issue = models.CharField(max_length=20, blank=True, null=True)
    dp_year = models.IntegerField(blank=True, null=True)
    pages = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'reference'


class Section(models.Model):
    text = models.TextField(blank=True, null=True)
    label = models.ForeignKey(Label, models.DO_NOTHING, blank=True, null=True)
    code = models.CharField(max_length=20, blank=True, null=True)
    title = models.CharField(max_length=4000, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'section'


class Struct2Atc(models.Model):
    struct = models.OneToOneField('Structures', models.DO_NOTHING, to_field='id')
    atc_code = models.ForeignKey(Atc, models.DO_NOTHING, db_column='atc_code', to_field='code')

    class Meta:
        managed = False
        db_table = 'struct2atc'
        unique_together = (('struct', 'atc_code'),)


class Struct2Drgclass(models.Model):
    struct = models.ForeignKey('Structures', models.DO_NOTHING, to_field='id')
    drug_class = models.ForeignKey(DrugClass, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'struct2drgclass'
        unique_together = (('struct', 'drug_class'),)


class Struct2Obprod(models.Model):
    struct = models.OneToOneField('Structures', models.DO_NOTHING, primary_key=True, to_field='id')
    prod = models.ForeignKey(ObProduct, models.DO_NOTHING)
    strength = models.CharField(max_length=4000, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'struct2obprod'
        unique_together = (('struct', 'prod'),)


class Struct2Parent(models.Model):
    struct = models.OneToOneField('Structures', models.DO_NOTHING, primary_key=True, to_field='id')
    parent = models.ForeignKey(Parentmol, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'struct2parent'
        unique_together = (('struct', 'parent'),)


class StructTypeDef(models.Model):
    type = models.CharField(unique=True, max_length=50, blank=True, null=True)
    description = models.CharField(max_length=200, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'struct_type_def'


class StructureType(models.Model):
    struct = models.ForeignKey('Structures', models.DO_NOTHING, blank=True, null=True, to_field='id')
    type = models.ForeignKey(StructTypeDef, models.DO_NOTHING, db_column='type')

    class Meta:
        managed = False
        db_table = 'structure_type'
        unique_together = (('struct', 'type'),)


class Structures(models.Model):
    cd_id = models.AutoField(primary_key=True)
    cd_formula = models.CharField(max_length=100, blank=True, null=True)
    cd_molweight = models.FloatField(blank=True, null=True)
    id = models.IntegerField(unique=True)
    clogp = models.FloatField(blank=True, null=True)
    alogs = models.FloatField(blank=True, null=True)
    cas_reg_no = models.CharField(unique=True, max_length=50, blank=True, null=True)
    tpsa = models.FloatField(blank=True, null=True)
    lipinski = models.IntegerField(blank=True, null=True)
    name = models.CharField(max_length=250, blank=True, null=True)
    no_formulations = models.IntegerField(blank=True, null=True)
    stem = models.ForeignKey(InnStem, models.DO_NOTHING, db_column='stem', blank=True, null=True, to_field='stem')
    molfile = models.TextField(blank=True, null=True)
    mrdef = models.CharField(max_length=32672, blank=True, null=True)
    enhanced_stereo = models.BooleanField()
    arom_c = models.IntegerField(blank=True, null=True)
    sp3_c = models.IntegerField(blank=True, null=True)
    sp2_c = models.IntegerField(blank=True, null=True)
    sp_c = models.IntegerField(blank=True, null=True)
    halogen = models.IntegerField(blank=True, null=True)
    hetero_sp2_c = models.IntegerField(blank=True, null=True)
    rotb = models.IntegerField(blank=True, null=True)
    molimg = models.BinaryField(blank=True, null=True)
    o_n = models.IntegerField(blank=True, null=True)
    oh_nh = models.IntegerField(blank=True, null=True)
    inchi = models.CharField(max_length=32672, blank=True, null=True)
    smiles = models.CharField(max_length=32672, blank=True, null=True)
    rgb = models.IntegerField(blank=True, null=True)
    fda_labels = models.IntegerField(blank=True, null=True)
    inchikey = models.CharField(max_length=27, blank=True, null=True)
    status = models.CharField(max_length=10, blank=True, null=True)
    tsv = SearchVectorField()
    tsv_fda = SearchVectorField()
    tsv_ema = SearchVectorField()
    tsv_pmda = SearchVectorField()
    atcs_set = models.ManyToManyField(Atc, through=Struct2Atc)
    drug_classes_set = models.ManyToManyField(DrugClass, through=Struct2Drgclass)
    prods_set = models.ManyToManyField(ObProduct, through=Struct2Obprod)
    vetprods_set = models.ManyToManyField('Vetprod', through='Vetprod2Struct')
    parents_set = models.ManyToManyField(Parentmol, through=Struct2Parent)
    @classmethod
    def random_with_image(cls):
        try:
            latest = cls.objects.filter(molimg__isnull=False).exclude(molimg=b'').latest('pk').pk
        except cls.DoesNotExist:
            return None
        else:
            while True:
                rand_pk = random.randint(0, latest)
                rand = cls.objects.filter(pk=rand_pk, molimg__isnull=False).exclude(molimg=b'').first()
                if rand is not None:
                    return rand
    @classmethod
    def search(cls, value, limit=100, approval=None):
        value = value.lower().replace('-', '').replace('_', '').replace('covid19', 'coronavirus').replace('vicodin', 'hydrocodone').replace('muscarinic m1', 'chrm1').replace('p11229', 'chrm1').replace('prilosec', 'omeprazole').replace('acm1_human', 'chrm1').replace('veklury', 'remdesivir')
        if approval == 'fda':
            vector = models.F('tsv_fda')
        elif approval == 'ema':
            vector = models.F('tsv_ema')
        elif approval == 'pmda':
            vector = models.F('tsv_pmda')
        else:
            vector = models.F('tsv')
        query = SearchQuery(value)
        rank = SearchRank(vector, query, weights=[0.000001, 0.0001, 0.01, 1.0])
        return cls.objects.annotate(rank=rank).filter(rank__gt=0.0000005).order_by('-rank')[:limit]
    @classmethod
    def substructure_search(cls, value, limit=100):
        return cls.objects.raw('SELECT * FROM structures WHERE m@>%s LIMIT %s;', [value, int(limit)])
    @classmethod
    def similarity_search(cls, value, limit=100):
        return cls.objects.raw('SELECT * FROM structures WHERE mfp2%%morganbv_fp(%s) LIMIT %s;', [value, int(limit)])
    @memoize
    def synonyms(self):
        return self.synonyms_set.all()
    @memoize
    def approvals(self):
        return self.approval_set.all()
    @memoize
    def atcs(self):
        return self.atcs_set.all()
    @memoize
    def pharma_classes(self):
        return self.pharmaclass_set.all()
    @memoize
    def omops(self):
        return list(OmopRelationship.objects.raw('''
SELECT omop_relationship.*, first_doid_xref.doid AS doid_xref_doid,
CASE LOWER(omop_relationship.relationship_name)
    WHEN 'indication' THEN 1
    WHEN 'off-label use' THEN 2
    WHEN 'contraindication' THEN 3
    ELSE 4
END AS relationship_type
FROM omop_relationship
LEFT JOIN (
    SELECT DISTINCT ON (doid_xref.xref) *
    FROM doid_xref
    WHERE doid_xref.source LIKE 'SNOMED%%'
) AS first_doid_xref
ON omop_relationship.snomed_conceptid=CAST(first_doid_xref.xref AS BIGINT)
WHERE omop_relationship.struct_id = %s
ORDER BY relationship_type, omop_relationship.snomed_conceptid
''', [self.id]))
    @memoize
    def vetomops(self):
        return list(self.vetomop_set.order_by('relationship_type'))
    @memoize
    def activities(self):
        activities = sorted(
            self.acttablefull_set.order_by('moa'), # python sort is stable
            key=lambda a: bool(a.swissprots()) + bool(a.swissprots_human()) - bool(a.swissprots_nonhuman()),
            reverse=True,
        )
        return activities
    @memoize
    def identifiers(self):
        return self.identifier_set.select_related('id_type')
    @memoize
    def active_ingredients(self, limit=None):
        query = '''
SELECT active_ingredient.*,
product.product_name AS product_product_name,
label.category AS label_category,
product.active_ingredient_count AS product_active_ingredient_count,
product.ndc_product_code AS product_ndc_product_code,
product.form AS product_form,
product.route AS product_route,
product.marketing_status AS product_marketing_status,
label.id AS label_id,
COUNT(section.id) AS section_count
FROM active_ingredient
JOIN product ON active_ingredient.ndc_product_code = product.ndc_product_code
JOIN prd2label ON product.ndc_product_code = prd2label.ndc_product_code
JOIN label ON prd2label.label_id = label.id
LEFT JOIN section ON section.label_id = label.id
WHERE active_ingredient.struct_id = %s
GROUP BY active_ingredient.id, product.id, label.id
ORDER BY active_ingredient.ndc_product_code
'''
        args = [self.id]
        if limit is not None:
            query += 'LIMIT %s'
            args.append(limit)
        return list(ActiveIngredient.objects.raw(query, args))
    def active_ingredients_limit_30(self):
        return self.active_ingredients(30)
    @memoize
    def dosages(self):
        return self.atcddd_set.all()
    @memoize
    def pkas(self):
        return self.pka_set.all()
    @memoize
    def faers(self, limit=None):
        qs = self.faers_set.filter(llr__gt=models.F('llr_threshold')).order_by('-llr')
        if limit is not None:
            qs = qs[:limit]
        return qs
    @memoize
    def faers_male(self, limit=None):
        qs = self.faersmale_set.filter(llr__gt=models.F('llr_threshold')).order_by('-llr')
        if limit is not None:
            qs = qs[:limit]
        return qs
    @memoize
    def faers_female(self, limit=None):
        qs = self.faersfemale_set.filter(llr__gt=models.F('llr_threshold')).order_by('-llr')
        if limit is not None:
            qs = qs[:limit]
        return qs
    @memoize
    def faers_ger(self, limit=None):
        qs = self.faersger_set.filter(llr__gt=models.F('llr_threshold')).order_by('-llr')
        if limit is not None:
            qs = qs[:limit]
        return qs
    @memoize
    def faers_ped(self, limit=None):
        qs = self.faersped_set.filter(llr__gt=models.F('llr_threshold')).order_by('-llr')
        if limit is not None:
            qs = qs[:limit]
        return qs
    @memoize
    def properties(self):
        qs = self.property_set.select_related('property_type', 'reference')
        return qs
    @memoize
    def ob_patents(self):
        return sorted(ObPatent.objects.raw('''
SELECT DISTINCT ON (struct2obprod.struct_id, struct2obprod.strength, ob_patent.patent_no, ob_patent_use_code.description, ob_product.trade_name, ob_product.applicant, ob_product.appl_type, ob_product.appl_no, ob_product.type, ob_product.dose_form, ob_product.route)
struct2obprod.strength AS strength,
ob_patent_use_code.description AS description,
ob_product.trade_name AS trade_name,
ob_product.applicant AS applicant,
ob_product.appl_type AS appl_type,
ob_product.appl_no AS appl_no,
ob_product.type AS type,
ob_product.dose_form AS dose_form,
ob_product.route AS route,
ob_product.approval_date AS approval_date,
ob_patent.*
FROM ob_product, ob_patent, ob_patent_use_code, struct2obprod
WHERE ob_product.appl_no = ob_patent.appl_no AND ob_product.product_no = ob_patent.product_no AND ob_patent.patent_use_code = ob_patent_use_code.code AND ob_product.id = struct2obprod.prod_id AND struct2obprod.struct_id = %s
''', [self.id]),
            key=lambda p: (p.patent_expire_date, p.appl_type, p.appl_no, p.strength),
        )
    @memoize
    def ob_exclusivities(self):
        return sorted(ObExclusivity.objects.raw('''
SELECT DISTINCT ON (struct2obprod.struct_id, struct2obprod.strength, ob_product.trade_name, ob_product.applicant, ob_product.appl_type, ob_product.appl_no, ob_product.type, ob_product.dose_form, ob_product.route, ob_exclusivity.exclusivity_date, ob_exclusivity_code.description)
struct2obprod.strength AS strength,
ob_product.trade_name AS trade_name,
ob_product.applicant AS applicant,
ob_product.appl_type AS appl_type,
ob_product.appl_no AS appl_no,
ob_product.approval_date AS approval_date,
ob_product.type AS type,
ob_product.dose_form AS dose_form,
ob_product.route AS route,
ob_exclusivity.*,
ob_exclusivity_code.description AS description
FROM ob_product, ob_exclusivity, ob_exclusivity_code, struct2obprod
WHERE ob_product.appl_no = ob_exclusivity.appl_no AND ob_product.product_no = ob_exclusivity.product_no AND ob_exclusivity.exclusivity_code = ob_exclusivity_code.code AND ob_product.id = struct2obprod.prod_id AND struct2obprod.struct_id = %s
''', [self.id]),
            key=lambda e: (e.exclusivity_date, e.appl_type, e.appl_no, e.strength),
        )
    @memoize
    def vetprods(self):
        return self.vetprods_set.all()

    class Meta:
        managed = False
        db_table = 'structures'


class Synonyms(models.Model):
    syn_id = models.AutoField(primary_key=True)
    id = models.ForeignKey(Structures, models.DO_NOTHING, db_column='id', blank=True, null=True, to_field='id')
    name = models.CharField(unique=True, max_length=250)
    preferred_name = models.SmallIntegerField(blank=True, null=True)
    parent = models.ForeignKey(Parentmol, models.DO_NOTHING, blank=True, null=True)
    lname = models.CharField(unique=True, max_length=250, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'synonyms'
        unique_together = (('id', 'preferred_name'), ('parent', 'preferred_name'),)


class TargetClass(models.Model):
    l1 = models.CharField(primary_key=True, max_length=50)

    class Meta:
        managed = False
        db_table = 'target_class'


class TargetComponent(models.Model):
    accession = models.CharField(unique=True, max_length=20, blank=True, null=True)
    swissprot = models.CharField(unique=True, max_length=20, blank=True, null=True)
    organism = models.CharField(max_length=150, blank=True, null=True)
    name = models.CharField(max_length=200, blank=True, null=True)
    gene = models.CharField(max_length=25, blank=True, null=True)
    geneid = models.BigIntegerField(blank=True, null=True)
    tdl = models.CharField(max_length=5, blank=True, null=True)
    dictionaries_set = models.ManyToManyField('TargetDictionary', through='Td2Tc')
    gos_set = models.ManyToManyField('TargetGo', through='Tdgo2Tc')
    keywords_set = models.ManyToManyField('TargetKeyword', through='Tdkey2Tc')

    @memoize
    def target_classes(self):
        tds = self.dictionaries_set.order_by('target_class').distinct('target_class')
        return [td.target_class for td in tds if td.target_class]
    @memoize
    def drugs(self):
        query = self.dictionaries_set.prefetch_related(models.Prefetch('acttablefull_set', queryset=ActTableFull.objects.select_related('struct')))
        struct_is_not_mao = {}
        structs = set()
        for td in query:
            for acttablefull in td.acttablefull_set.all():
                struct = acttablefull.struct
                struct_is_not_mao[struct] = struct_is_not_mao.get(struct, True) and not acttablefull.moa
                structs.add(struct)
        for struct in structs:
            struct.is_mao = not struct_is_not_mao[struct]
        return sorted(structs, key=lambda struct:(not struct.is_mao, struct.name, struct))

    class Meta:
        managed = False
        db_table = 'target_component'


class TargetDictionary(models.Model):
    name = models.CharField(max_length=200)
    target_class = models.CharField(max_length=50)
    protein_components = models.SmallIntegerField()
    protein_type = models.CharField(max_length=50, blank=True, null=True)
    tdl = models.CharField(max_length=500, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'target_dictionary'


class TargetGo(models.Model):
    id = models.CharField(primary_key=True, max_length=10)
    term = models.CharField(max_length=200, blank=True, null=True)
    type = models.CharField(max_length=1, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'target_go'


class TargetKeyword(models.Model):
    id = models.CharField(primary_key=True, max_length=7)
    descr = models.CharField(max_length=4000, blank=True, null=True)
    category = models.CharField(max_length=50, blank=True, null=True)
    keyword = models.CharField(max_length=200, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'target_keyword'


class Td2Tc(models.Model):
    target = models.OneToOneField(TargetDictionary, models.DO_NOTHING, primary_key=True)
    component = models.ForeignKey(TargetComponent, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'td2tc'
        unique_together = (('target', 'component'),)


class Tdgo2Tc(models.Model):
    go = models.ForeignKey(TargetGo, models.DO_NOTHING)
    component = models.ForeignKey(TargetComponent, models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tdgo2tc'


class Tdkey2Tc(models.Model):
    tdkey = models.ForeignKey(TargetKeyword, models.DO_NOTHING)
    component = models.ForeignKey(TargetComponent, models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tdkey2tc'


class Vetomop(models.Model):
    omopid = models.AutoField(primary_key=True)
    struct = models.ForeignKey('Structures', models.DO_NOTHING, blank=True, null=True, to_field='id')
    species = models.CharField(max_length=100, blank=True, null=True)
    relationship_type = models.CharField(max_length=50, blank=True, null=True)
    concept_name = models.CharField(max_length=500, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'vetomop'


class Vetprod(models.Model):
    prodid = models.AutoField(primary_key=True)
    appl_type = models.ForeignKey('VetprodType', models.DO_NOTHING, db_column='appl_type', to_field='appl_type')
    appl_no = models.CharField(unique=True, max_length=7)
    trade_name = models.CharField(max_length=200, blank=True, null=True)
    applicant = models.CharField(max_length=100, blank=True, null=True)
    active_ingredients_count = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'vetprod'


class Vetprod2Struct(models.Model):
    prodid = models.ForeignKey('Vetprod', models.DO_NOTHING, db_column='prodid', blank=True, null=True, to_field='prodid')
    struct = models.ForeignKey('Structures', models.DO_NOTHING, blank=True, null=True, to_field='id')

    class Meta:
        managed = False
        db_table = 'vetprod2struct'


class VetprodType(models.Model):
    id = models.IntegerField(unique=True)
    appl_type = models.CharField(primary_key=True, max_length=1)
    description = models.CharField(max_length=11, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'vetprod_type'


class Vettype(models.Model):
    prodid = models.ForeignKey('Vetprod', models.DO_NOTHING, db_column='prodid', blank=True, null=True, to_field='prodid')
    type = models.CharField(max_length=3, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'vettype'
