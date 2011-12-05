from django.db import models
from django import forms
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.core.exceptions import ObjectDoesNotExist

from metrics.models import *

class BaseOrderedList(models.Model):
    name = models.CharField(blank=True, max_length=255)
    slug = models.SlugField(unique=True)
    default = models.BooleanField(default=False)
    _ordered_items = None
    
    class Meta:
        abstract = True
        ordering = ('-default', 'name')
    
    def __unicode__(self):
        return "List: {name}".format(name=self.name)
    
    def save(self):
        if self.default:
            try:
                obj = self.__class__.objects.get(default=True)
                if self != obj:
                    obj.default = False
                    obj.save()
            except ObjectDoesNotExist:
                pass
        super(BaseOrderedList, self).save()
        
    def ordered(self):
        """returns a list of units ordered by their membership order value"""
        if not self._ordered_items:
            if self.items:
                ordered_items = self.items.through.objects.order_by('order')
                self._ordered_items = [i.unit for i in ordered_items]
            else:
                self._ordered_items =  []
        return self._ordered_items
        
class OrderedListItem(models.Model):
    order = models.SmallIntegerField(blank=False)
    class Meta:
        abstract = True
    
    def __unicode__(self):
        return u"OrderedListItem"

# Unit List and Membership
class UnitList(BaseOrderedList):
    items = models.ManyToManyField(Unit, through='UnitListMembership')

class UnitListMembership(OrderedListItem):
    orderedlist = models.ForeignKey(UnitList)
    unit = models.ForeignKey(Unit)
    
    class Meta:
        ordering = ['order',]

# Project list and Membership
class ProjectList(BaseOrderedList):
    items = models.ManyToManyField(Project, through='ProjectListMembership')
        
class ProjectListMembership(OrderedListItem):
    orderedlist = models.ForeignKey(ProjectList)
    project = models.ForeignKey(Project)

    class Meta:
        ordering = ['order',]

# Metric list and Membership
class MetricList(BaseOrderedList):
    items = models.ManyToManyField(Metric, through='MetricListMembership')

class MetricListMembership(OrderedListItem):
    orderedlist = models.ForeignKey(MetricList)
    project = models.ForeignKey(Metric)

    class Meta:
        ordering = ['order',]



class DateRangeForm(forms.Form):
    """Form for date-range searches"""
    from_datetime = forms.DateField(widget=forms.DateInput(attrs={'class':'datefield'}))
    to_datetime = forms.DateField(widget=forms.DateInput(attrs={'class':'datefield'}), required=False)
        