# djangocms-styledlink

A universal, styled link plugin for django-cms.

The plugin can be used in any placeholder and is "text-enabled" for use in
text plugins such as djangocms-text-ckeditor.


## Operator Configuration

Operators can configure the link to go to:

1.   A hash (works by itself for linking to an anchor on the current page, or on an internal object page);
2.   An internal object (more below);
3.   An external URL;
4.   A file-download (coming soon).

In addition to being very flexible with the link destination, the operator can also affect:

1.   The linked text;
2.   The link’s title attribute for browser implemented tooltips;
3.   The target attribute to open the link in one of `same window` (default), `new window`, `parent window`, `top-most frame`;
4.   Whether search engines should follow this link when indexing via the rel="nofollow" attribute.
5.   Zero or more styles as defined by the developer (see below);


## Developer Configuration

### Available Internal Destination Choices

The developer can easily configure which internal objects may be link destinations as follows:

In the projects settings.py, define the setting `DJANGOCMS_STYLEDLINK_MODELS`.

By default, this is set to:

```` python
DJANGOCMS_STYLEDLINK_MODELS = [
    {
        'type': 'CMS Pages',
        'class_path': 'cms.models.Page',
        'manager_method': 'published',
        'filter': { 'publisher_is_draft': False },
    }
]
````

which will allow the user to select any published CMS Page as an internal
destination.

The developer may update this setting to include other models as well. Each
model is specified within its own dict.  The resulting drop-down list will
contain objects grouped by their `type`.  The order of the `type`s in the list
is defined by the order of their definition in this setting.

The only required attribute for each model is `class_path`, which must be the
full path to the model.

Additional attributes are:

* `type`: This is the name that will appear in the grouped dropdown menu. If
not specified, the name of the class will be used E.g., "Page".

* `filter`: You can specify additional filtering rules here. This must be
specified as a dict but is converted directly into kwargs internally, so,
`{'published': True}` becomes `filter(published=True)` for example.

* `order_by`: Specify the ordering of any found objects exactly as you would
in a queryset. If this is not provided, the objects will be ordered in the
natural order of your model, if any.


NOTE: Each of the defined models **must** define a get_absolute_url() method
on its objects or the configuration will be rejected.


#### An example of mutliple types.

```` python
DJANGOCMS_STYLEDLINK_MODELS = [
    {
        'type': 'Clients',
        'class_path': 'myapp.Client',
        'manager_method': 'published',
        'order_by': 'title'
    },
    {
        'type': 'Projects',
        'class_path': 'myapp.Project',
        'filter': { 'approved': True },
        'order_by': 'title',
    },
    {
        'type': 'Solutions',
        'class_path': 'myapp.Solution',
        'filter': { 'published': True },
        'order_by': 'name',
    }
]

````


### Link Styles

The developer can also define a number of link styles. These are "defined" by creating the appropriate CSS class and rules and adding this class to the StyledLinkStyle objects in the appropriate Administration panel.

The template for the resulting link is carefully crafted using only <span>'s so that the link will work as a inline element and, with appropriate styling, as an inline-block or even block-level element.

Note that the operator can choose multiple styles, so the CSS rules should allow for this.
