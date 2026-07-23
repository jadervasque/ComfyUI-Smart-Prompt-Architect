"""Bootstrap contract tests for the importable core package."""

import unittest

import prompt_architect


class PackageContractTests(unittest.TestCase):
    """Verify public bootstrap package metadata."""

    def test_package_exposes_pep440_development_version(self) -> None:
        """The package should expose the same canonical version as project metadata."""
        self.assertEqual(prompt_architect.__version__, "0.2.0.dev0")


if __name__ == "__main__":
    unittest.main()
