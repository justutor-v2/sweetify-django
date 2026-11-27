import json

from django.template import engines
from django.test import RequestFactory, SimpleTestCase
from django.utils.translation import gettext_lazy

import sweetify


class SweetifyTests(SimpleTestCase):
    def setUp(self):
        self.request = RequestFactory().get("/")
        self.request.session = {}

    def render_alert(self, **context):
        template = engines["django"].from_string("{% load sweetify %}{% sweetify nonce=nonce %}")
        return template.render(context, self.request)

    def test_default_options(self):
        sweetify.sweetalert(self.request, "Welcome")
        self.assertEqual(
            json.loads(self.request.session["sweetify"]), sweetify.DEFAULT_OPTS | {"title": "Welcome"}
        )

    def test_stored_queue_is_rendered_once_in_order(self):
        self.request.session["sweetify"] = ['{"title":"First"}', '{"title":"Second"}']
        output = self.render_alert()
        self.assertIn(
            '<script type="application/json">[{"title": "First"}, {"title": "Second"}]</script>', output
        )
        self.assertEqual(self.render_alert(), "")

    def test_alert_data_and_nonce_are_escaped(self):
        sweetify.success(self.request, "Math <3 & more")
        output = self.render_alert(nonce='A"B')
        self.assertIn(r"Math \u003C3 \u0026 more", output)
        self.assertIn('nonce="A&quot;B"', output)

    def test_multiple_preserves_caller_options_and_normalizes_buttons(self):
        first = {"title": "First", "button": "Next"}
        sweetify.multiple(self.request, first, {"title": "Second", "persistent": "Done"})
        options = [json.loads(message) for message in self.request.session["sweetify"]]
        self.assertEqual(first, {"title": "First", "button": "Next"})
        self.assertEqual(options[0]["confirmButtonText"], "Next")
        self.assertEqual(options[1]["confirmButtonText"], "Done")
        self.assertIsNone(options[1]["timer"])
        self.assertFalse(options[1]["allowOutsideClick"])

    def test_toast_respects_overrides_and_lazy_titles(self):
        sweetify.toast(self.request, gettext_lazy("Saved"), icon="info", position="center")
        options = json.loads(self.request.session["sweetify"])
        self.assertEqual(options["title"], "Saved")
        self.assertEqual(options["position"], "center")
        self.assertEqual(options["icon"], "info")
        self.assertTrue(options["toast"])

    def test_legacy_alert_uses_legacy_client_and_options(self):
        with self.settings(SWEETIFY_SWEETALERT_LIBRARY="sweetalert"):
            sweetify.warning(self.request, "Review", button="OK")
            options = json.loads(self.request.session["sweetify"])
            self.assertEqual(options["button"], "OK")
            self.assertTrue(options["closeOnClickOutside"])
            self.assertIn("swal(alerts[0])", self.render_alert())
            with self.assertRaises(RuntimeError):
                sweetify.toast(self.request, "Saved")
            sweetify.multiple(self.request, {"title": "First"})
            with self.assertRaises(RuntimeError):
                self.render_alert()
