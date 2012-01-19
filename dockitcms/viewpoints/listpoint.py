from dockitcms.common import register_view_point_class
from dockitcms.utils import ConfigurableTemplateResponseMixin, generate_object_detail_scaffold, generate_object_list_scaffold

from common import BaseViewPointClass, BaseViewPointForm

from dockit.views import ListView, DetailView

from django.conf.urls.defaults import patterns, url
from django import forms
from django.template import Template, TemplateSyntaxError
from django.utils.translation import ugettext_lazy as _


TEMPLATE_SOURCE_CHOICES = [
    ('name', _('By Template Name')),
    ('html', _('By Template HTML')),
]


class ListViewPointForm(BaseViewPointForm):
    list_template_source = forms.ChoiceField(choices=TEMPLATE_SOURCE_CHOICES)
    list_template_name = forms.CharField(initial='dockitcms/list.html', required=False)
    list_template_html = forms.CharField(widget=forms.Textarea, required=False)
    detail_template_source = forms.ChoiceField(choices=TEMPLATE_SOURCE_CHOICES)
    detail_template_name = forms.CharField(initial='dockitcms/detail.html', required=False)
    detail_template_html = forms.CharField(widget=forms.Textarea, required=False)
    paginate_by = forms.IntegerField(required=False)
    
    def __init__(self, **kwargs):
        super(ListViewPointForm, self).__init__(**kwargs)
        document = self.collection.get_document()
        self.initial['list_template_html'] = generate_object_list_scaffold(document)
        self.initial['detail_template_html'] = generate_object_detail_scaffold(document)
    
    def _clean_template_html(self, content):
        if not content:
            return content
        try:
            Template(content)
        except TemplateSyntaxError, e:
            raise forms.ValidationError(unicode(e))
        return content
    
    def clean_list_template_html(self):
        return self._clean_template_html(self.cleaned_data.get('list_template_html'))
    
    def clean_detail_template_html(self):
        return self._clean_template_html(self.cleaned_data.get('detail_template_html'))
    
    def clean(self):
        #TODO pump the error to their perspective field
        if self.cleaned_data.get('list_template_source') == 'name':
            if not self.cleaned_data.get('list_template_name'):
                raise forms.ValidationError(_('Please specify a list template name'))
        if self.cleaned_data.get('list_template_source') == 'html':
            if not self.cleaned_data.get('list_template_html'):
                raise forms.ValidationError(_('Please specify the list template html'))
        
        if self.cleaned_data.get('detail_template_source') == 'name':
            if not self.cleaned_data.get('detail_template_name'):
                raise forms.ValidationError(_('Please specify a detail template name'))
        if self.cleaned_data.get('detail_template_source') == 'html':
            if not self.cleaned_data.get('detail_template_html'):
                raise forms.ValidationError(_('Please specify the detail template html'))
        return self.cleaned_data

class PointListView(ConfigurableTemplateResponseMixin, ListView):
    pass

class PointDetailView(ConfigurableTemplateResponseMixin, DetailView):
    pass

class ListViewPointClass(BaseViewPointClass):
    form_class = ListViewPointForm
    list_view_class = PointListView
    detail_view_class = PointDetailView
    label = _('List View')
    
    def get_document(self, collection, view_point_doc):
        doc_cls = collection.get_document()
        view_point = self
        class WrappedDoc(doc_cls):
            def get_absolute_url(self):
                return view_point.reverse(collection, view_point_doc, 'detail', self.pk)
            
            class Meta:
                proxy = True
        
        return WrappedDoc
    
    def _configuration_from_prefix(self, params, prefix):
        config = dict()
        for key in ('template_source', 'template_name', 'template_html'):
            config[key] = params.get('%s_%s' % (prefix, key), None)
        return config
    
    def get_urls(self, collection, view_point_doc):
        document = self.get_document(collection, view_point_doc)
        params = view_point_doc.view_config
        return patterns('',
            url(r'^$', 
                self.list_view_class.as_view(document=document,
                                      configuration=self._configuration_from_prefix(params, 'list'),
                                      paginate_by=params.get('paginate_by', None)),
                name='index',
            ),
            url(r'^(?P<pk>.+)/$', 
                self.detail_view_class.as_view(document=document,
                                        configuration=self._configuration_from_prefix(params, 'detail'),),
                name='detail',
            ),
        )

register_view_point_class('list', ListViewPointClass)

