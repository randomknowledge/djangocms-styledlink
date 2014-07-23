# coding: utf-8
import warnings
from django.db import models
from django.conf import settings
from importlib import import_module


evaluated_models = []


def evaluate_models(force=False):
    global evaluated_models

    if not force and len(evaluated_models) > 0:
        return evaluated_models

    evaluated_models = []
    if hasattr(settings, 'DJANGOCMS_STYLEDLINK_MODELS'):
        model_descriptions = settings.DJANGOCMS_STYLEDLINK_MODELS
    else:
        model_descriptions = [{
            'type': 'CMS Pages',
            'class_path': 'cms.models.Page',
            'manager_method': 'public',
            'filter': {'publisher_is_draft': False},
        }]

    #
    # Let's make sure that we can load the given configuration...
    #
    for model in model_descriptions:
        parts = model['class_path'].rsplit('.', 1)

        try:
            # Ensure we can resolve this class
            cls = getattr(import_module(parts[0]), parts[1])
        except:
            warnings.warn('djangocms_styledlink: Unable to resolve model: %s. Skipping...' % model['class_path'], SyntaxWarning)
            continue

        # Check that the class defines a get_absolute_url() method on its objects.
        if 'get_absolute_url' not in cls.__dict__:
            warnings.warn('djangocms_styledlink: Model %s does not appear to define get_absolute_url() for its object. Skipping...' % model['class_path'], SyntaxWarning)
            continue

        # Check that any manager method defined is legit
        if 'manager_method' in model and not getattr(cls.objects, model['manager_method']):
            warnings.warn('djangocms_styledlink: Specified manager_method %s for model %s does not appear to exist. Skipping...' %(model['manager_method'], model['class_path'], ), SyntaxWarning)
            continue

        ok = True
        if 'filter' in model:
            for field in model['filter'].iterkeys():
                try:
                    cls._meta.get_field_by_name(field.split('__')[0])
                except models.FieldDoesNotExist:
                    warnings.warn('StyledLink: Defined filter expression refers to a field (%s) in model %s that do not appear to exist. Skipping...' % (field, model['class_path'], ), SyntaxWarning)
                    ok = False
                    break
        if not ok:
            continue

        if 'order_by' in model:
            fields = model['order_by'].split(',')
            # Strip any leading -/+ chars
            fields = [ f.translate(None, '-+') for f in fields ]
            for field in fields:
                try:
                    cls._meta.get_field_by_name(field)
                except models.FieldDoesNotExist:
                    warnings.warn('StyledLink: Defined order_by expression refers to a field (%s) in model %s that do not appear to exist. Skipping...' % (field, model['class_path'], ), SyntaxWarning)
                    ok = False
                    break
        if not ok:
            continue

        #
        # Still here? Awesome...
        # Store the class name for our use.
        #
        model.update({
            '_cls_name': parts[1]
        })

        # Add this configuration
        evaluated_models.append(model)
    return evaluated_models
