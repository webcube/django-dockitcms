from dockitcms.widgetblock.models import BaseTemplateWidget, Widget, ReusableWidget

from dockit import schema

#from dockitcms.viewpoints.common import IndexMixin

from django.utils.translation import ugettext_lazy as _
from django.utils.safestring import mark_safe
from django.template import Context
from django.template.loader import get_template

class TextWidget(Widget):
    text = schema.TextField()
    
    class Meta:
        typed_key = 'widgetblock.textwidget'
    
    def render(self, context):
        return self.text

class ImageWidget(Widget):
    image = schema.FileField()
    alt = schema.CharField(blank=True)
    link = schema.CharField(blank=True)
    
    class Meta:
        typed_key = 'widgetblock.imagewidget'
    
    def get_template(self):
        return get_template('widgetblock/image_widget.html')
    
    def get_context(self, context):
        return Context({'widget': self})
    
    def render(self, context):
        template = self.get_template()
        context = self.get_context(context)
        return mark_safe(template.render(context))

class CTAImage(schema.Schema):
    image = schema.FileField(upload_to='ctas')
    url = schema.CharField(blank=True)
    
    def __unicode__(self):
        if self.image:
            return unicode(self.image)
        return repr(self)

class CTAWidget(BaseTemplateWidget):
    default_url = schema.CharField()
    width = schema.CharField()
    height = schema.CharField()
    delay = schema.DecimalField(help_text=_("Display interval of each item"), max_digits=5, decimal_places=2, default=5)
    
    images = schema.ListField(schema.SchemaField(CTAImage)) #TODO the following will be an inline when supported
    
    class Meta:
        typed_key = 'widgetblock.ctawidget'
    
    @classmethod
    def get_admin_form_class(cls):
        from dockitcms.widgetblock.forms import CTAWidgetForm
        return CTAWidgetForm
"""
class IndexWidget(BaseTemplateWidget, IndexMixin):
    '''
    A widget that is powered by an index
    '''
    
    class Meta:
        typed_key = 'widgetblock.indexwidget'
    
    def get_context(self, context):
        context = BaseTemplateWidget.get_context(self, context)
        index = self.get_index()
        context['object_list'] = index
        return context
"""
class FlatMenuEntry(schema.Schema):
    title = schema.CharField()
    url = schema.CharField()

class FlatMenuWidget(BaseTemplateWidget):
    entries = schema.ListField(schema.SchemaField(FlatMenuEntry))
    
    class Meta:
        typed_key = 'widgetblock.flatmenuwidget'
    
    def get_context(self, context):
        context = BaseTemplateWidget.get_context(self, context)
        #TODO find the active menu entry
        return context

class PredefinedWidget(Widget):
    widget = schema.ReferenceField(ReusableWidget)
    
    def render(self, context):
        return self.widget.render(context)
    
    def __unicode__(self):
        if self.widget:
            return unicode(self.widget)
        return repr(self)
    
    class Meta:
        typed_key = 'widgetblock.predefinedwidget'

