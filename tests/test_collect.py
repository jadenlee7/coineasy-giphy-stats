import importlib.util
import unittest
from pathlib import Path

spec = importlib.util.spec_from_file_location("collect", Path(__file__).resolve().parents[1] / "scripts/collect.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class ParserTests(unittest.TestCase):
    def test_rendered_count_and_hidden_script(self):
        html = '<h1>CoinEasy</h1><script>999M GIF Views</script><b>7.4M</b><span>GIF Views</span>'
        self.assertEqual(module.parse_display(html), "7.4M")

    def test_spaces_entities_and_commas(self):
        self.assertEqual(module.parse_display('CoinEasy <b>7.4 M</b>&nbsp; GIF Views'), "7.4M")
        self.assertEqual(module.approximate_views("1,234"), 1234)
        self.assertEqual(module.approximate_views("7.4M"), 7400000)
        self.assertEqual(module.approximate_views("1.2B"), 1200000000)

    def test_reject_missing_wrong_identity_or_conflicting_counts(self):
        for html in ['CoinEasy 181 Uploads', 'Other 7.4M GIF Views', 'CoinEasy 7.4M GIF Views 8M GIF Views']:
            with self.subTest(html=html), self.assertRaises(ValueError):
                module.parse_display(html)

    def test_reject_invalid_numbers(self):
        for value in ['0', 'NaN', '-1', '7.4M trailing', '1e9']:
            with self.subTest(value=value), self.assertRaises(ValueError):
                module.approximate_views(value)


if __name__ == '__main__':
    unittest.main()
