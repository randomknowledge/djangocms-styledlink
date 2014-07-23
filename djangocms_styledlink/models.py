# -*- coding: utf-8 -*-
from django.db import models
from django.utils.encoding import force_unicode
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from cms.models import CMSPlugin
from djangocms_styledlink.helper import evaluate_models


class StyledLinkStyle(models.Model):

    label = models.CharField(_('label'),
        max_length=32,
        default='',
        help_text=_('The internal name of this link style.'),
    )

    link_class = models.CharField(
        _('link class'),
        max_length=32,
        default='',
        help_text=('The class to add to this link (do NOT preceed with a ".").'),
    )

    def __unicode__(self):
        return self.label


class StyledLink(CMSPlugin):

    """
    A link to an other page or to an external website
    """

    label = models.CharField(_('link text'),
        blank=True,
        default='',
        help_text=_("Required. The text that is linked."),
        max_length=255,
    )

    title = models.CharField(_('title'),
        blank=True,
        default='',
        help_text=_("Optional. If provided, will provide a tooltip for the link."),
        max_length=255,
    )

    int_destination_type = models.ForeignKey(ContentType,
        null=True,
        blank=True,
    )

    int_destination_id = models.PositiveIntegerField(
        blank=True,
        null=True,
    )

    int_destination = generic.GenericForeignKey(
        'int_destination_type',
        'int_destination_id',
    )

    #
    # Hash, for current page or internal page destination
    #
    page_destination = models.CharField(_('intra-page destination'),
        blank=True,
        help_text=_(u'Use this to specify an intra-page link. Can be used for the <em>current page</em> or with a specific internal destination. Do <strong>not</strong> include a leading “#”.'),
        max_length=64,
    )

    #
    # See note in save()
    #
    int_hash = models.BooleanField(default=False)

    #
    # External links
    #
    ext_destination = models.TextField(_('external destination'),
        blank=True,
        default='',
    )

    ext_follow = models.BooleanField(_('follow external link?'),
        default=True,
        help_text=_('Let search engines follow this hyperlink?'),
    )

    mailto = models.EmailField(
        _("email address"),
        blank=True,
        null=True,
        help_text=_("An email address. This will override an external url."),
    )

    target = models.CharField(_("target"),
        blank=True,
        choices=((
            ("", _("same window")),
            ("_blank", _("new window")),
            ("_parent", _("parent window")),
            ("_top", _("topmost frame")),
        )),
        default='',
        help_text=_('Optional. Specify if this link should open in a new tab or window.'),
        max_length=100,
    )

    styles = models.ManyToManyField(StyledLinkStyle,
        blank=True,
        default=None,
        null=True,
        help_text=_('Optional. Choose one or more styles for this link.'),
        related_name='styled_link_style',
        verbose_name=_("link style"),
    )

    def __init__(self, *args, **kwargs):
        super(StyledLink, self).__init__(*args, **kwargs)
        for f in self._meta.fields:
            if f.attname == "int_destination_type":
                f.limit_choices_to = {
                    "model__in": [model['_cls_name'] for model in evaluate_models()]
                }

    @property
    def link(self):
        """Returns the specified destination url"""

        if self.int_destination:
            # This is an intra-site link and the destination object is still
            # here, nice.
            url = self.int_destination.get_absolute_url()
            if self.page_destination:
                # Oooh, look, it also has a hash component
                return u'%s#%s' % (url, self.page_destination, )
            return url
        elif self.page_destination and not self.int_hash:
            # OK, this was just an intra-page hash
            return u'#%s' % (self.page_destination, )
        elif self.ext_destination:
            # External link
            return self.ext_destination
        elif self.mailto:
            # Mailto: link
            return u'mailto:%s' % (self.mailto, )
        else:
            return ''


    def save(self, **kwargs):
        #
        # We always need to remember if `page_destination` (hash) was set in
        # the context of `int_destination` (internal cms page/model view)
        # because if it was, and the `int_destination` object was subsequently
        # deleted, then the page_destination by itself would mistakenly be
        # applied to the *current* page.
        #
        self.int_hash = bool(self.int_destination and self.page_destination)

        #
        # As a convenience, if the operator omits the label, extract one from
        # the linked model object.
        #
        if not self.label and self.int_destination:
            self.label = force_unicode(self.int_destination)

        super(StyledLink, self).save(**kwargs)


    def copy_relations(self, oldinstance):
        self.styles = oldinstance.styles.all()


    def __unicode__(self):
        return self.label
