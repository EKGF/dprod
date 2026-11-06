"""Publication maintenance must retain the historical normative source bytes."""
import hashlib
import json
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]

class MainPublicationTests(unittest.TestCase):
    def test_normative_source_hashes_are_unchanged(self):
        manifest = json.loads((ROOT / 'publication/source-provenance.json').read_text())
        self.assertEqual(manifest['label'], 'DPROD 1.0 beta')
        for path, digest in manifest['source_sha256'].items():
            self.assertEqual(hashlib.sha256((ROOT / path).read_bytes()).hexdigest(), digest, path)

    def test_publication_definitions_do_not_import_develop_contracts(self):
        definitions = (ROOT / 'publication/standards.ttl').read_text()
        self.assertIn('ga:releaseVersion "1.0 beta"', definitions)
        self.assertNotIn('/spec/develop/', definitions)
        self.assertNotIn('dprod-contracts/', definitions)
        self.assertIn('ga:publicationDate "2024-08-31"', definitions)

    def test_extracted_sections_are_accounted_for(self):
        manifest = json.loads((ROOT / 'publication/source-provenance.json').read_text())
        for path, digest in manifest['publication_sha256'].items():
            self.assertEqual(hashlib.sha256((ROOT / path).read_bytes()).hexdigest(), digest, path)

if __name__ == '__main__':
    unittest.main()
