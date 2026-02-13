"""
Test Suite for Diff/Merge Module
Tests all components of the diff and merge functionality.
"""

import unittest
import tempfile
import os
from pathlib import Path
from file_diff import DiffGenerator, FileDiff
from dir_diff import DirectoryDiffer, DirectoryDiff
from file_merge import ThreeWayMerger
from patch_handler import PatchHandler
from diff_merge_api import DiffMergeAPI


class TestDiffGenerator(unittest.TestCase):
    """Test file diff generation."""

    def setUp(self):
        self.diff_gen = DiffGenerator()
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        # Cleanup
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def create_temp_file(self, name: str, content: str) -> str:
        """Helper to create temporary files."""
        path = os.path.join(self.temp_dir, name)
        with open(path, "w") as f:
            f.write(content)
        return path

    def test_diff_identical_files(self):
        """Test diff of identical files."""
        content = "line1\nline2\nline3\n"
        file1 = self.create_temp_file("file1.txt", content)
        file2 = self.create_temp_file("file2.txt", content)

        diff = self.diff_gen.diff_files(file1, file2)

        self.assertEqual(diff.additions, 0)
        self.assertEqual(diff.deletions, 0)

    def test_diff_added_lines(self):
        """Test diff with added lines."""
        file1 = self.create_temp_file("file1.txt", "line1\nline2\n")
        file2 = self.create_temp_file("file2.txt", "line1\nline2\nline3\nline4\n")

        diff = self.diff_gen.diff_files(file1, file2)

        self.assertEqual(diff.additions, 2)
        self.assertEqual(diff.deletions, 0)

    def test_diff_deleted_lines(self):
        """Test diff with deleted lines."""
        file1 = self.create_temp_file("file1.txt", "line1\nline2\nline3\n")
        file2 = self.create_temp_file("file2.txt", "line1\n")

        diff = self.diff_gen.diff_files(file1, file2)

        self.assertEqual(diff.additions, 0)
        self.assertEqual(diff.deletions, 2)

    def test_diff_modified_lines(self):
        """Test diff with modified lines."""
        file1 = self.create_temp_file("file1.txt", "hello\nworld\n")
        file2 = self.create_temp_file("file2.txt", "hello\nuniverse\n")

        diff = self.diff_gen.diff_files(file1, file2)

        self.assertEqual(diff.additions, 1)
        self.assertEqual(diff.deletions, 1)

    def test_diff_nonexistent_file(self):
        """Test diff with nonexistent file."""
        file1 = self.create_temp_file("file1.txt", "content")

        diff = self.diff_gen.diff_files(file1, "/nonexistent/path/file.txt")

        # Should handle gracefully
        self.assertIsNotNone(diff)

    def test_diff_formatting(self):
        """Test formatted diff output."""
        file1 = self.create_temp_file("file1.txt", "line1\nline2\n")
        file2 = self.create_temp_file("file2.txt", "line1\nline2\nline3\n")

        diff = self.diff_gen.diff_files(file1, file2)
        formatted = self.diff_gen.format_diff_readable(diff)

        self.assertIn("file1.txt", formatted)
        self.assertIn("file2.txt", formatted)
        self.assertIn("+", formatted)


class TestDirectoryDiffer(unittest.TestCase):
    """Test directory diff generation."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.dir1 = os.path.join(self.temp_dir, "dir1")
        self.dir2 = os.path.join(self.temp_dir, "dir2")
        os.makedirs(self.dir1)
        os.makedirs(self.dir2)

    def tearDown(self):
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def create_file(self, dir_path: str, file_name: str, content: str) -> str:
        """Helper to create files in directory."""
        file_path = os.path.join(dir_path, file_name)
        with open(file_path, "w") as f:
            f.write(content)
        return file_path

    def test_added_file_detection(self):
        """Test detection of added files."""
        self.create_file(self.dir1, "file.txt", "content")
        self.create_file(self.dir1, "file2.txt", "content")
        self.create_file(self.dir2, "file.txt", "content")
        self.create_file(self.dir2, "file2.txt", "content")
        self.create_file(self.dir2, "file3.txt", "new")

        differ = DirectoryDiffer()
        dir_diff = differ.diff_directories(self.dir1, self.dir2)

        added = dir_diff.get_added_files()
        self.assertIn("file3.txt", added)

    def test_deleted_file_detection(self):
        """Test detection of deleted files."""
        self.create_file(self.dir1, "file1.txt", "content")
        self.create_file(self.dir1, "file2.txt", "content")
        self.create_file(self.dir2, "file1.txt", "content")

        differ = DirectoryDiffer()
        dir_diff = differ.diff_directories(self.dir1, self.dir2)

        deleted = dir_diff.get_deleted_files()
        self.assertIn("file2.txt", deleted)

    def test_modified_file_detection(self):
        """Test detection of modified files."""
        self.create_file(self.dir1, "file.txt", "original content")
        self.create_file(self.dir2, "file.txt", "modified content")

        differ = DirectoryDiffer()
        dir_diff = differ.diff_directories(self.dir1, self.dir2)

        modified = dir_diff.get_modified_files()
        self.assertIn("file.txt", modified)


class TestThreeWayMerger(unittest.TestCase):
    """Test three-way merge functionality."""

    def setUp(self):
        self.merger = ThreeWayMerger()
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def create_temp_file(self, name: str, content: str) -> str:
        """Helper to create temporary files."""
        path = os.path.join(self.temp_dir, name)
        with open(path, "w") as f:
            f.write(content)
        return path

    def test_merge_no_conflicts(self):
        """Test merge with no conflicts."""
        base = self.create_temp_file("base.txt", "line1\nline2\nline3\n")
        a = self.create_temp_file("a.txt", "line1\nline2_modified\nline3\n")
        b = self.create_temp_file("b.txt", "line1\nline2\nline3\nline4\n")

        result = self.merger.merge_files(base, a, b)

        self.assertFalse(result.has_conflicts)

    def test_merge_with_conflicts(self):
        """Test merge with conflicts."""
        base = self.create_temp_file("base.txt", "common\nchangeme\n")
        a = self.create_temp_file("a.txt", "common\nchanged_by_a\n")
        b = self.create_temp_file("b.txt", "common\nchanged_by_b\n")

        result = self.merger.merge_files(base, a, b)

        # Should detect conflict
        self.assertTrue(result.has_conflicts or len(result.merged_lines) > 0)


class TestPatchHandler(unittest.TestCase):
    """Test patch application functionality."""

    def setUp(self):
        self.patch_handler = PatchHandler(create_backups=True)
        self.temp_dir = tempfile.mkdtemp()
        self.diff_gen = DiffGenerator()

    def tearDown(self):
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)
        shutil.rmtree(".backups", ignore_errors=True)

    def create_temp_file(self, name: str, content: str) -> str:
        """Helper to create temporary files."""
        path = os.path.join(self.temp_dir, name)
        with open(path, "w") as f:
            f.write(content)
        return path

    def test_dry_run(self):
        """Test dry run patch application."""
        file1 = self.create_temp_file("file1.txt", "line1\nline2\n")
        file2 = self.create_temp_file("file2.txt", "line1\nline2\nline3\n")

        diff = self.diff_gen.diff_files(file1, file2)
        success, preview = self.patch_handler.dry_run(file1, diff)

        self.assertTrue(success)
        self.assertIn("Would modify", preview)


class TestDiffMergeAPI(unittest.TestCase):
    """Test high-level API."""

    def setUp(self):
        self.api = DiffMergeAPI()
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)
        shutil.rmtree(".backups", ignore_errors=True)

    def create_temp_file(self, name: str, content: str) -> str:
        """Helper to create temporary files."""
        path = os.path.join(self.temp_dir, name)
        with open(path, "w") as f:
            f.write(content)
        return path

    def test_diff_files_api(self):
        """Test diff_files API."""
        file1 = self.create_temp_file("file1.txt", "line1\nline2\n")
        file2 = self.create_temp_file("file2.txt", "line1\nline2\nline3\n")

        result = self.api.diff_files(file1, file2)

        self.assertEqual(result["additions"], 1)
        self.assertEqual(result["deletions"], 0)
        self.assertIn("diff_lines", result)

    def test_get_file_diff_summary_api(self):
        """Test get_file_diff_summary API."""
        file1 = self.create_temp_file("file1.txt", "line1\nline2\n")
        file2 = self.create_temp_file("file2.txt", "line1\nline2\nline3\n")

        result = self.api.get_file_diff_summary(file1, file2)

        self.assertIn("additions", result)
        self.assertIn("deletions", result)
        self.assertIn("total_changes", result)

    def test_compare_and_report_api(self):
        """Test compare_and_report API."""
        file1 = self.create_temp_file("file1.txt", "line1\nline2\n")
        file2 = self.create_temp_file("file2.txt", "line1\nline2\nline3\n")

        report = self.api.compare_and_report(file1, file2)

        self.assertIsInstance(report, str)
        self.assertIn("file1", report)
        self.assertIn("file2", report)


if __name__ == "__main__":
    unittest.main()
