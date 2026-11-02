"""The project-site pilot is authored content, not another web application."""
import pathlib
import re
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
CONTENT = ROOT / "publication" / "project-site"


class ProjectSiteTests(unittest.TestCase):
    def test_static_routes_are_source_owned_markdown(self):
        routes = {"index.md": "/", "why.md": "/why/", "concepts.md": "/concepts/", "adopt.md": "/adopt/", "roadmap.md": "/roadmap/"}
        self.assertEqual(set(path.name for path in CONTENT.iterdir()), set(routes))
        for name, route in routes.items():
            source = (CONTENT / name).read_text()
            self.assertIn(f"permalink: {route}\n", source)
            self.assertIn("  subject: urn:dprod:project-site:page:", source)
            self.assertRegex(source, r"(?m)^# .+")
            self.assertNotIn("<div", source)
            self.assertNotIn("className=", source)
            for target in re.findall(r"\]\(([^)]+)\)", source):
                if target.endswith(".md"):
                    self.assertTrue((CONTENT / target).is_file(), target)

    def test_current_specification_service_is_not_replaced_by_a_stale_snapshot(self):
        home = (CONTENT / "index.md").read_text()
        self.assertIn("https://ekgf.org/dprod/spec-versions/", home)
        self.assertFalse((CONTENT / "spec-versions.md").exists())
        configuration = (ROOT / "publication" / "project-site.ttl").read_text()
        self.assertIn('ga:style "ekgf-project"', configuration)
        self.assertIn('ga:url "https://ekgf.org/dprod/spec-versions/"', configuration)

    def test_ci_retains_a_static_project_preview(self):
        workflow = (ROOT / ".github" / "workflows" / "grapharch-pdfs.yml").read_text()
        self.assertIn("Generate the source-owned project website preview", workflow)
        self.assertIn("--source publication/project-site", workflow)
        self.assertIn("--definitions publication/project-site.ttl", workflow)
        self.assertIn("name: dprod-project-website-${{ github.sha }}", workflow)
        self.assertIn("path: output/grapharch-project-site/site/", workflow)

    def test_code_examples_have_explicit_language(self):
        source = (CONTENT / "adopt.md").read_text()
        self.assertIn("```json\n", source)
        self.assertIn("```text\nObject Management Group", source)


if __name__ == "__main__":
    unittest.main()
