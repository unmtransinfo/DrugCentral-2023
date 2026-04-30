import datetime
import hashlib
import json
import re

from django.conf.urls import url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.http import HttpResponse, Http404
from django.shortcuts import get_object_or_404
from django.views import View
from django.views.decorators.cache import cache_control
from django.views.decorators.http import condition
from django.views.generic.base import TemplateView
from django.views.generic.detail import DetailView

from drugcen import models, settings

DRUG_COUNT = '{:,}'.format(models.Structures.objects.count())
PHARMACEUTICAL_COUNT = '{:,}'.format(models.Product.objects.count())

def stats(request):
    return {
        'DRUG_COUNT': DRUG_COUNT,
        'PHARMACEUTICAL_COUNT': PHARMACEUTICAL_COUNT,
    }

def q(request):
    context = {}
    q = request.GET.get('q')
    if q is not None:
        context['q'] = q
        approval = request.GET.get('approval')
        if approval is not None:
            approval = approval.strip().lower()
            if approval in ('fda', 'ema', 'pmda'):
                context['approval'] = approval
    m = request.GET.get('m')
    if m is not None:
        context['m'] = m
    s = request.GET.get('s')
    if s is not None:
        context['s'] = s
    return context

def named_digits(name):
    return r'(?P<%s>\d+)' % name

def named_slug(name):
    return r'(?P<%s>[-A-Za-z0-9]+)' % name

def named_upper_word(name):
    return r'(?P<%s>[A-Z0-9_]+)' % name

DIGITS = named_digits('slug')
SLUG = named_slug('slug')
UPPER_WORD = named_upper_word('slug')

TARGETS = {key: target.accession for target in models.TargetComponent.objects.all() for key in (target.accession.lower(), target.name.lower(), target.swissprot.lower().replace('_', ''))}

class RootView(TemplateView):
    template_name = 'root.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        q = self.request.GET.get('q')
        if q is not None:
            approval = self.request.GET.get('approval')
            if approval is not None:
                approval = approval.strip().lower()
            results = list(models.Structures.search(q, approval=approval))
            context['results'] = results
            context['result_count'] = len(results)
            accession = TARGETS.get(''.join(q.lower().split()).replace('_', ''))
            if accession is not None:
                context['target_result'] = models.TargetComponent.objects.get(accession=accession)
        else:
            context['image'] = models.Structures.random_with_image()
        return context

class SubstructureView(TemplateView):
    template_name = 'substructure.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        m = self.request.GET.get('m')
        if m is not None:
            try:
                results = list(models.Structures.substructure_search(m))
            except Exception:
                context['error'] = 'Queries must be in the Simplified Molecular Input Line Entry System (SMILES) format.'
            else:
                context['results'] = results
                context['result_count'] = len(results)
        else:
            context['image'] = models.Structures.random_with_image()
        return context

class SimilarityView(TemplateView):
    template_name = 'similarity.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        s = self.request.GET.get('s')
        if s is not None:
            context['s'] = s
            try:
                results = list(models.Structures.similarity_search(s))
            except Exception:
                context['error'] = 'Queries must be in the Simplified Molecular Input Line Entry System (SMILES) format.'
            else:
                context['results'] = results
                context['result_count'] = len(results)
        else:
            context['image'] = models.Structures.random_with_image()
        return context

class DrugCardView(DetailView):
    model = models.Structures
    template_name = 'drugcard_view.html'
    context_object_name = 'drug'
    slug_field = 'id'

class TargetView(DetailView):
    model = models.TargetComponent
    template_name = 'target_view.html'
    context_object_name = 'target'
    slug_field = 'swissprot'
    def get_object(self, queryset=None):
        if queryset is None:
            queryset = self.get_queryset()
        try:
            return super().get_object(queryset)
        except Http404:
            return get_object_or_404(queryset, accession=self.kwargs.get(self.slug_url_kwarg))

def sanitize(name, prog=re.compile('[-() ,:_+\\.]+')):
    return prog.sub('', name).lower()

def get_names():
    drugs = [drug.name for drug in models.Structures.objects.all()]
    synonyms = [synonym.name for synonym in models.Synonyms.objects.all()]
    return sorted(set(drugs + synonyms), key=sanitize)

class AutocompleteView(View):
    data = ('var autocompleteNames = ' + json.dumps(get_names()) + ';').encode('utf-8')
    last_modified = datetime.datetime.now()
    etag = hashlib.sha256(data).hexdigest()
    def get(self, request, *args, **kwargs):
        return HttpResponse(self.data, content_type='text/javascript; charset=\'utf-8\'')

def structure_image(request, slug):
    structure = get_object_or_404(models.Structures.objects.filter(id=slug, molimg__isnull=False).exclude(molimg=b''))
    img = structure.molimg
    response = HttpResponse(img)
    response['Content-Disposition'] = 'inline; filename=%s.png' % slug
    response['Content-Type'] = 'image/png'
    return response

def structure_molfile(request, slug):
    structure = get_object_or_404(models.Structures.objects.filter(id=slug, molfile__isnull=False).exclude(molfile=''))
    molfile = structure.molfile
    response = HttpResponse(molfile)
    response['Content-Disposition'] = 'inline; filename=molfile-%s.txt' % slug
    response['Content-Type'] = 'text/plain'
    return response

def structure_inchi(request, slug):
    structure = get_object_or_404(models.Structures.objects.filter(id=slug, inchi__isnull=False).exclude(inchi=''))
    inchi = structure.inchi
    response = HttpResponse(inchi)
    response['Content-Disposition'] = 'inline; filename=inchi-%s.txt' % slug
    response['Content-Type'] = 'text/plain'
    return response

def structure_smiles(request, slug):
    structure = get_object_or_404(models.Structures.objects.filter(id=slug, smiles__isnull=False).exclude(smiles=''))
    smiles = structure.smiles
    response = HttpResponse(smiles)
    response['Content-Disposition'] = 'inline; filename=smiles-%s.txt' % slug
    response['Content-Type'] = 'text/plain'
    return response

urlpatterns = [
    url(r'^$', RootView.as_view(), name='root-view'),
    url(r'^substructure$', SubstructureView.as_view(), name='substructure-view'),
    url(r'^similarity$', SimilarityView.as_view(), name='similarity-view'),
    url(r'^drugcard/' + DIGITS + r'(?:/(?:view)?)?$', DetailView.as_view(
        model=models.Structures,
        template_name='drugcard_view.html',
        context_object_name='drug',
        slug_field='id',
    ), name='drugcard-view'),
    url(r'^drug/' + DIGITS + r'/image$', structure_image, name='drug-image'),
    url(r'^drug/' + DIGITS + r'/molfile$', structure_molfile, name='drug-molfile'),
    url(r'^drug/' + DIGITS + r'/inchi$', structure_inchi, name='drug-inchi'),
    url(r'^drug/' + DIGITS + r'/smiles$', structure_smiles, name='drug-smiles'),
    url(r'^target/' + UPPER_WORD + r'(?:/(?:view))?$', TargetView.as_view(), name='target-view'),
    url(r'^label/' + SLUG + r'/view$', DetailView.as_view(
        model=models.Label,
        template_name='label_view.html',
        context_object_name='label',
        slug_field='id',

    ), name='label-view'),
    url(r'^autocomplete.js$', cache_control(must_revalidate=True, max_age=0)(condition(
        last_modified_func=lambda request: AutocompleteView.last_modified,
        etag_func=lambda request: AutocompleteView.etag,
    )(AutocompleteView.as_view())), name='autocomplete'),
    url(r'^download', TemplateView.as_view(
        template_name='download.html',
    ), name='download'),
    url(r'^ActiveDownload', TemplateView.as_view(
        template_name='ActiveDownload.html',
    ), name='ActiveDownload'),
    url(r'^help', TemplateView.as_view(
        template_name='help.html',
    ), name='help'),
    url(r'^about', TemplateView.as_view(
        template_name='about.html',
    ), name='about'),
    url(r'^privacy', TemplateView.as_view(
        template_name='privacy.html',
    ), name='privacy'),
    url(r'^direct', TemplateView.as_view(
        template_name='direct.html',
    ), name='direct'),
    url(r'^LINCS', TemplateView.as_view(
        template_name='LINCSsimilarity.html',
    ), name='LINCS'),
    url(r'^Redial', TemplateView.as_view(
        template_name='Redial.html',
    ), name='Redial'),
    url(r'^TestRedial2020', TemplateView.as_view(
        template_name='TestRedial2020.html',
    ), name='TestRedial2020'),
]
if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns()
