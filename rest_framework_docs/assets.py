from django_assets import Bundle, register
js = Bundle(
    "rest_framework_docs/js/dist.min.js",
    output="packed/dist.min.js",
)
register('drf_js', js)

css = Bundle(
    "rest_framework_docs/css/style.css",
    output="packed/style.css",
)
register('drf_css', css)
