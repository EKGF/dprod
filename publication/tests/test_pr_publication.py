"""Publication maintenance must retain the historical normative source bytes."""
import hashlib
import json
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]

class BranchPublicationTests(unittest.TestCase):
    def test_normative_source_hashes_are_unchanged(self):
        manifest = json.loads((ROOT / 'publication/source-provenance.json').read_text())
        self.assertEqual(manifest['label'], 'DPROD PR 234 Schedule model')
        for path, digest in manifest['source_sha256'].items():
            self.assertEqual(hashlib.sha256((ROOT / path).read_bytes()).hexdigest(), digest, path)

    def test_publication_definitions_do_not_import_develop_contracts(self):
        definitions = (ROOT / 'publication/standards.ttl').read_text()
        self.assertIn('ga:releaseVersion "PR 234 Schedule model"', definitions)
        self.assertNotIn('/spec/develop/', definitions)
        self.assertNotIn('ga:source \"dprod-contracts/docs/', definitions)
        self.assertIn('dprod-contracts/dprod-contracts.ttl', definitions)
        self.assertIn('ga:publicationDate "2026-08-04"', definitions)

    def test_extracted_sections_are_accounted_for(self):
        manifest = json.loads((ROOT / 'publication/source-provenance.json').read_text())
        for path, digest in manifest['publication_sha256'].items():
            self.assertEqual(hashlib.sha256((ROOT / path).read_bytes()).hexdigest(), digest, path)

if __name__ == '__main__':
    unittest.main()
