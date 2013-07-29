from uuid import uuid4

from pyramid.testing import DummyRequest
from pyramid.testing import setUp
from pyramid.testing import tearDown
from unittest2 import TestCase
from webtest import TestApp

from ichnaea import main


def _make_app():
    wsgiapp = main({}, database='sqlite://')
    return TestApp(wsgiapp)


class TestContentViews(TestCase):

    def setUp(self):
        request = DummyRequest()
        self.config = setUp(request=request)

    def tearDown(self):
        tearDown()

    def _make_view(self, request):
        from ichnaea.content.views import ContentViews
        return ContentViews(request)

    def test_homepage(self):
        request = DummyRequest()
        inst = self._make_view(request)
        result = inst.homepage_view()
        self.assertEqual(result['page_title'], 'Overview')

    def test_map(self):
        request = DummyRequest()
        inst = self._make_view(request)
        result = inst.map_view()
        self.assertEqual(result['page_title'], 'Coverage Map')

    def test_stats_empty(self):
        app = _make_app()
        request = DummyRequest()
        request.database = app.app.registry.database
        inst = self._make_view(request)
        result = inst.stats_view()
        self.assertEqual(result['page_title'], 'Statistics')
        self.assertEqual(result['total_measures'], 0)
        self.assertEqual(result['leaders'], [])

    def test_stats(self):
        app = _make_app()
        uid = uuid4().hex
        nickname = 'World Tr\xc3\xa4veler'
        app.post_json(
            '/v1/submit', {"items": [
                {"lat": 1.0, "lon": 2.0, "wifi": [{"key": "a"}]},
                {"lat": 2.0, "lon": 3.0, "wifi": [{"key": "b"}]},
            ]},
            headers={'X-Token': uid, 'X-Nickname': nickname},
            status=204)
        request = DummyRequest()
        request.database = app.app.registry.database
        inst = self._make_view(request)
        result = inst.stats_view()
        self.assertEqual(result['page_title'], 'Statistics')
        self.assertEqual(result['total_measures'], 2)
        self.assertEqual(result['leaders'],
                         [{'nickname': nickname.decode('utf-8'),
                           'num': 2, 'token': uid[:8]}])


class TestFunctionalContent(TestCase):

    def test_favicon(self):
        app = _make_app()
        app.get('/favicon.ico', status=200)

    def test_homepage(self):
        app = _make_app()
        app.get('/', status=200)

    def test_map(self):
        app = _make_app()
        app.get('/map', status=200)

    def test_robots_txt(self):
        app = _make_app()
        app.get('/robots.txt', status=200)

    def test_stats(self):
        app = _make_app()
        app.get('/stats', status=200)


class TestLayout(TestCase):

    def setUp(self):
        request = DummyRequest()
        self.config = setUp(request=request)

    def tearDown(self):
        tearDown()

    def _make_layout(self):
        from ichnaea.content.views import Layout
        return Layout()

    def test_base_template(self):
        from chameleon.zpt.template import Macro
        layout = self._make_layout()
        self.assertEqual(layout.base_template.__class__, Macro)

    def test_base_macros(self):
        from chameleon.zpt.template import Macros
        layout = self._make_layout()
        self.assertEqual(layout.base_macros.__class__, Macros)
