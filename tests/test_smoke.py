import os
import re
import subprocess
import sys
import unittest

SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class ScoutSmokeTests(unittest.TestCase):
    def test_skill_md_exists(self):
        self.assertTrue(os.path.isfile(os.path.join(SKILL_DIR, "SKILL.md")))

    def test_frontmatter_declares_config(self):
        text = open(os.path.join(SKILL_DIR, "SKILL.md")).read()
        try:
            import yaml
        except ImportError:
            self.skipTest("yaml module unavailable")
        parts = text.split("---")
        self.assertGreaterEqual(len(parts), 3, "missing frontmatter fences")
        fm = yaml.safe_load(parts[1])
        self.assertIsInstance(fm, dict)
        self.assertIn("metadata", fm)
        self.assertIn("hermes", fm["metadata"])
        self.assertIn("config", fm["metadata"]["hermes"])

    def test_all_py_scripts_help(self):
        sdir = os.path.join(SKILL_DIR, "scripts")
        scripts = sorted(f for f in os.listdir(sdir) if f.endswith(".py") and not f.startswith("_"))
        self.assertTrue(scripts, "no scripts found")
        for s in scripts:
            path = os.path.join(sdir, s)
            rc = subprocess.run(
                [sys.executable, path, "--help"],
                capture_output=True,
                text=True,
                timeout=10,
                cwd=SKILL_DIR,
            ).returncode
            self.assertEqual(rc, 0, "%s --help exited %d" % (s, rc))

    def test_cited_references_exist(self):
        text = open(os.path.join(SKILL_DIR, "SKILL.md")).read()
        refs = sorted(set(re.findall(r"`(references/[^`]+)`", text)))
        self.assertTrue(refs, "no references cited")
        for r in refs:
            self.assertTrue(os.path.exists(os.path.join(SKILL_DIR, r)), "dead ref: %s" % r)


if __name__ == "__main__":
    unittest.main()