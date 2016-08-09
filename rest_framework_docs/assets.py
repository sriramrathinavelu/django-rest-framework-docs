from django_assets import Bundle, register
js = Bundle(
    "third_party/rest_framework_docs/js/dist.min.js",
    output="packed/drf.js",
)
register('drf_js', js)

css = Bundle(
    "third_party/rest_framework_docs/css/style.css",
    output="packed/drf.css",
)
register('drf_css', css)
