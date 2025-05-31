import argparse
import subprocess
import unittest

ARGS = argparse.Namespace(findup = '../src/python3/findup.py')


class TestVersionArgument(unittest.TestCase):
    def test_version_argument(self):
        """Test that the program correctly returns its version when --version is passed."""
        result = subprocess.run(["python3", ARGS.findup, "-V"], capture_output=True, text=True)

        self.assertEqual(result.returncode, 0, "Program did not exit successfully")
        self.assertRegex(result.stdout.strip(), "findup\\s+[.\\d]+\\s+Copyright.*Kirill Shirokov.*",
            "Version output does not match expected value")

    def test_simple_dups(self):
        """Test that the program correctly returns its version when --version is passed."""
        result = subprocess.run(["python3", ARGS.findup,
             "data/dups"],
            capture_output=True, text=True)

        self.assertEqual(result.returncode, 0, "Program did not exit successfully")
        self.assertRegex(result.stdout.strip(), "Duplicates \\(wasted [\\d.]+ MB\\):\\s+"
            "data/dups/dir1/dup11.txt\\s+"
            "data/dups/dir1/dup12.txt\\s+"
            "data/dups/dir2/dup21.txt\\s+"
            "Total wasted disk space in 2 files: [\\d.]+ MB\\s*",
            "Duplicate output does not match expected value")

    def test_no_summary(self):
        """Test that the program correctly returns its version when --version is passed."""
        result = subprocess.run(["python3", ARGS.findup,
             "-S",
             "data/dups"],
            capture_output=True, text=True)

        self.assertEqual(result.returncode, 0, "Program did not exit successfully")
        self.assertRegex(result.stdout.strip(), "Duplicates \\(wasted [\\d.]+ MB\\):\\s+"
            "data/dups/dir1/dup11.txt\\s+"
            "data/dups/dir1/dup12.txt\\s+"
            "data/dups/dir2/dup21.txt\\s*",
            "Duplicate output does not match expected value")

    def test_prefix_size(self):
        """Test that the program correctly returns its version when --version is passed."""
        result = subprocess.run(["python3", ARGS.findup,
             "--mock-full-hash", "0", "--prefix-size", "10",
             "data/dups"],
            capture_output=True, text=True)

        self.assertEqual(result.returncode, 0, "Program did not exit successfully")
        self.assertRegex(result.stdout.strip(), "Duplicates \\(wasted [\\d.]+ MB\\):\\s+"
            "data/dups/dir1/dup11.txt\\s+"
            "data/dups/dir1/dup12.txt\\s+"
            "data/dups/dir1/notdup13-sameSize-differentLastChar.txt\\s+"
            "data/dups/dir2/dup21.txt\\s+"
            "Total wasted disk space in 3 files: [\\d.]+ MB\\s*",
            "Duplicate output does not match expected value")

    def test_min_file_size(self):
        """Test that the program correctly returns its version when --version is passed."""
        result = subprocess.run(["python3", ARGS.findup,
             "--min-file-size", "100",
             "data/dups", "data/largeDups"],
            capture_output=True, text=True)

        self.assertEqual(result.returncode, 0, "Program did not exit successfully")
        self.assertRegex(result.stdout.strip(), "Duplicates \\(wasted [\\d.]+ MB\\):\\s+"
            "data/largeDups/largeDir1/largeDup11.txt\\s+"
            "data/largeDups/largeDir2/largeDup21.txt\\s+"
            "Total wasted disk space in 1 files: [\\d.]+ MB\\s*",
            "Duplicate output does not match expected value")

    def test_exec(self):
        """Test that the program correctly returns its version when --version is passed."""
        result = subprocess.run(["python3", ARGS.findup,
             "-q", "-e", "echo TESTING TESTING",
             "data/dups", "data/largeDups"],
            capture_output=True, text=True)

        self.assertEqual(result.returncode, 0, "Program did not exit successfully")
        self.assertRegex(result.stdout.strip(),
            "TESTING TESTING data/dups/dir1/dup11.txt data/dups/dir1/dup12.txt data/dups/dir2/dup21.txt\\s+"
            "TESTING TESTING data/largeDups/largeDir1/largeDup11.txt data/largeDups/largeDir2/largeDup21.txt\\s*",
            "Duplicate output does not match expected value")

    def test_exec_with_hash(self):
        """Test that the program correctly returns its version when --version is passed."""
        result = subprocess.run(["python3", ARGS.findup,
             "-q", "-a", "-e", "echo TESTING TESTING",
             "data/dups", "data/largeDups"],
            capture_output=True, text=True)

        self.assertEqual(result.returncode, 0, "Program did not exit successfully")
        self.assertRegex(result.stdout.strip(),
            "TESTING TESTING 2554083253_-1451544911 data/dups/dir1/dup11.txt data/dups/dir1/dup12.txt data/dups/dir2/dup21.txt\\s+"
            "TESTING TESTING 1150183819_-460366701 data/largeDups/largeDir1/largeDup11.txt data/largeDups/largeDir2/largeDup21.txt\\s*",
            "Duplicate output does not match expected value")

    def test_paranoid(self):
        """Test that the program correctly returns its version when --version is passed."""
        result = subprocess.run(["python3", ARGS.findup,
             "--mock-prefix-hash", "0", "--mock-full-hash", "1",
             "data/dups"],
            capture_output=True, text=True)

        self.assertEqual(result.returncode, 0, "Program did not exit successfully")
        self.assertRegex(result.stdout.strip(), "Duplicates \\(wasted [\\d.]+ MB\\):\\s+"
            "data/dups/dir1/dup11.txt\\s+"
            "data/dups/dir1/dup12.txt\\s+"
            "data/dups/dir1/notdup13-sameSize-differentLastChar.txt\\s+"
            "data/dups/dir2/dup21.txt\\s+"
            "Duplicates \\(wasted [\\d.]+ MB\\):\\s+"
            "data/dups/dir1/notdup11.txt\\s+"
            "data/dups/dir1/notdup12-additionalLFs.txt\\s+"
            "Total wasted disk space in 4 files: [\\d.]+ MB\\s*",
            "Duplicate output does not match expected value")

        result = subprocess.run(["python3", ARGS.findup,
             "--mock-prefix-hash", "0", "--mock-full-hash", "1", "-d",
             "data/dups"],
            capture_output=True, text=True)

        self.assertEqual(result.returncode, 0, "Program did not exit successfully")
        self.assertRegex(result.stdout.strip(), "Duplicates \\(wasted [\\d.]+ MB\\):\\s+"
            "data/dups/dir1/dup11.txt\\s+"
            "data/dups/dir1/dup12.txt\\s+"
            "data/dups/dir2/dup21.txt\\s+"
            "Total wasted disk space in 2 files: [\\d.]+ MB\\s*",
            "Duplicate output does not match expected value")

def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("-e", "--findup", help="Path to findup executable", required=True)

    global ARGS
    ARGS = p.parse_args()


if __name__ == "__main__":
    parse_args()
    unittest.main()
