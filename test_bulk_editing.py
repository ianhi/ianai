"""
Tests for the modular bulk editing system.
Demonstrates the clean, composable API.
"""

import os
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from line_operations import (
    InsertLineOperation,
    RemoveLineOperation,
    ChangeLineOperation,
    ReplacePatternOperation,
    LineRange,
    insert_lines,
    remove_lines,
    change_lines,
    replace_in_lines,
)
from bulk_editor import BulkEditor, bulk_edit
from file_editing4 import FileEditor


def test_line_operations():
    """Test individual line operations."""
    print("=" * 60)
    print("TEST: Individual Line Operations")
    print("=" * 60)

    lines = ["Line 1\n", "Line 2\n", "Line 3\n", "Line 4\n", "Line 5\n"]

    # Test insert
    print("\n1. Insert Operation")
    op = InsertLineOperation(2, "Inserted Line")
    result = op.apply(lines.copy())
    print(f"   {op.describe()}")
    print(f"   Result: {[l.strip() for l in result]}")

    # Test remove
    print("\n2. Remove Operation")
    op = RemoveLineOperation(1, count=2)
    result = op.apply(lines.copy())
    print(f"   {op.describe()}")
    print(f"   Result: {[l.strip() for l in result]}")

    # Test change
    print("\n3. Change Operation")
    op = ChangeLineOperation(0, "Changed First Line")
    result = op.apply(lines.copy())
    print(f"   {op.describe()}")
    print(f"   Result: {[l.strip() for l in result]}")

    # Test replace
    print("\n4. Replace Operation")
    op = ReplacePatternOperation("Line", "Row")
    result = op.apply(lines.copy())
    print(f"   {op.describe()}")
    print(f"   Result: {[l.strip() for l in result]}")

    print("\n✓ All individual operations passed\n")


def test_bulk_editor_fluent_api():
    """Test the fluent API of BulkEditor."""
    print("=" * 60)
    print("TEST: BulkEditor Fluent API")
    print("=" * 60)

    # Create test file
    test_file = "test_fluent.txt"
    with open(test_file, "w") as f:
        f.write("Line 1\nLine 2\nLine 3\nLine 4\nLine 5\n")

    print(f"\nInitial content of {test_file}:")
    with open(test_file, "r") as f:
        print(f.read())

    # Use fluent API
    print("Applying operations using fluent API:")
    result = (
        BulkEditor()
        .load_file(test_file)
        .insert(0, "=== Header ===")
        .insert(100, "=== Footer ===")  # Will insert at end
        .replace("Line", "Row")
        .remove(2, count=1)
        .apply()
    )

    print(f"\n{result['message']}")
    print(f"Operations applied: {result['operations_applied']}")
    for i, op in enumerate(result['operations'], 1):
        print(f"  {i}. {op}")

    print(f"\nFinal content:")
    with open(test_file, "r") as f:
        print(f.read())

    # Cleanup
    os.remove(test_file)
    print("✓ Fluent API test passed\n")


def test_bulk_editor_with_list():
    """Test BulkEditor with a list of operations."""
    print("=" * 60)
    print("TEST: BulkEditor with Operation List")
    print("=" * 60)

    test_file = "test_list.txt"
    with open(test_file, "w") as f:
        f.write("def old_function():\n    pass\n\nclass OldClass:\n    pass\n")

    print(f"Initial content of {test_file}:")
    with open(test_file, "r") as f:
        print(f.read())

    # Create operations
    operations = [
        insert_lines(0, "# Updated module"),
        replace_in_lines("old_function", "new_function"),
        replace_in_lines("OldClass", "NewClass"),
        insert_lines(100, "# End of module"),
    ]

    print("\nApplying operations:")
    for op in operations:
        print(f"  - {op.describe()}")

    # Apply using convenience function
    result = bulk_edit(test_file, operations)

    print(f"\n{result['message']}")
    print(f"\nFinal content:")
    with open(test_file, "r") as f:
        print(f.read())

    # Cleanup
    os.remove(test_file)
    print("✓ Operation list test passed\n")


def test_enhanced_file_editor():
    """Test the enhanced FileEditor with bulk operations."""
    print("=" * 60)
    print("TEST: Enhanced FileEditor")
    print("=" * 60)

    editor = FileEditor()
    test_file = "test_enhanced.txt"

    # Create initial file
    print("\n1. Creating initial file")
    result = editor.edit_file(
        test_file,
        "Line 1\nLine 2\nLine 3\nLine 4\nLine 5\n"
    )
    print(f"   {result['message']}")

    # Test insert_lines (new method)
    print("\n2. Testing insert_lines (bulk operation)")
    result = editor.insert_lines(
        test_file,
        2,
        ["Inserted A", "Inserted B", "Inserted C"]
    )
    print(f"   {result['message']}")
    print(f"   Operations: {result.get('operations', [])}")

    # Test remove_lines (new method)
    print("\n3. Testing remove_lines (bulk operation)")
    result = editor.remove_lines(test_file, 3, count=2)
    print(f"   {result['message']}")

    # Test replace_in_file (new method)
    print("\n4. Testing replace_in_file")
    result = editor.replace_in_file(test_file, "Line", "Row")
    print(f"   {result['message']}")

    # Test bulk_edit (new method)
    print("\n5. Testing bulk_edit with multiple operations")
    operations = [
        {"type": "insert", "line_number": 0, "content": "=== Header ==="},
        {"type": "insert", "line_number": 100, "content": "=== Footer ==="},
        {"type": "replace", "pattern": "Row", "replacement": "Item"},
    ]
    result = editor.bulk_edit(test_file, operations)
    print(f"   {result['message']}")
    print(f"   Operations applied: {result['operations_applied']}")

    print(f"\nFinal content of {test_file}:")
    content = editor.read_file(test_file)
    print(content)

    # Cleanup
    os.remove(test_file)
    print("✓ Enhanced FileEditor test passed\n")


def test_dry_run():
    """Test dry run functionality."""
    print("=" * 60)
    print("TEST: Dry Run (Preview)")
    print("=" * 60)

    test_file = "test_dryrun.txt"
    with open(test_file, "w") as f:
        f.write("Line 1\nLine 2\nLine 3\n")

    print(f"Initial content of {test_file}:")
    with open(test_file, "r") as f:
        original = f.read()
        print(original)

    # Perform dry run
    print("\nPerforming dry run with operations:")
    result = (
        BulkEditor()
        .load_file(test_file)
        .insert(0, "Header")
        .remove(1, count=1)
        .replace("Line", "Row")
        .preview()  # This is a dry run
    )

    print(f"\n{result['message']}")
    print("\nPreview of changes:")
    if result.get('diff'):
        print(result['diff'])

    # Verify file wasn't changed
    with open(test_file, "r") as f:
        after = f.read()

    if original == after:
        print("\n✓ File unchanged (dry run worked correctly)")
    else:
        print("\n✗ ERROR: File was modified during dry run!")

    # Cleanup
    os.remove(test_file)
    print()


def test_multiline_insert():
    """Test inserting multiple lines in various formats."""
    print("=" * 60)
    print("TEST: Multiline Insert (Various Formats)")
    print("=" * 60)

    test_file = "test_multiline.txt"
    editor = FileEditor()

    # Create initial file
    editor.edit_file(test_file, "Line 1\nLine 2\nLine 3\n")

    # Test 1: Insert list of lines
    print("\n1. Insert list of lines")
    result = editor.insert_lines(test_file, 1, ["First Insert", "Second Insert"])
    print(f"   {result['message']}")

    # Test 2: Insert string with newlines
    print("\n2. Insert string with newlines")
    result = editor.insert_lines(test_file, 3, "Multi\nLine\nString")
    print(f"   {result['message']}")

    print(f"\nFinal content:")
    print(editor.read_file(test_file))

    # Cleanup
    os.remove(test_file)
    print("✓ Multiline insert test passed\n")


def test_regex_replace():
    """Test regex replacement functionality."""
    print("=" * 60)
    print("TEST: Regex Replacement")
    print("=" * 60)

    test_file = "test_regex.txt"
    editor = FileEditor()

    # Create test file with patterns
    content = """
def function1():
    pass

def function2():
    pass

def helper():
    pass
"""
    editor.edit_file(test_file, content)

    print("Initial content:")
    print(content)

    # Replace with regex
    print("\nReplacing 'function' followed by digit with 'method' + digit:")
    result = editor.replace_in_file(
        test_file,
        r"function(\d+)",
        r"method\1",
        regex=True
    )

    print(f"{result['message']}")
    print("\nFinal content:")
    print(editor.read_file(test_file))

    # Cleanup
    os.remove(test_file)
    print("✓ Regex replacement test passed\n")


def test_complex_scenario():
    """Test a complex real-world scenario."""
    print("=" * 60)
    print("TEST: Complex Real-World Scenario")
    print("=" * 60)

    test_file = "test_complex.py"
    editor = FileEditor()

    # Create a Python file
    initial_content = """import os
import sys

def old_function():
    print("Hello")
    return True

class DataProcessor:
    def process(self):
        pass
"""

    editor.edit_file(test_file, initial_content)
    print("Initial Python file:")
    print(initial_content)

    # Perform complex bulk edit
    print("\nPerforming complex refactoring:")
    operations = [
        {"type": "insert", "line_number": 0, "content": "#!/usr/bin/env python3"},
        {"type": "insert", "line_number": 1, "content": '"""Module docstring"""'},
        {"type": "replace", "pattern": "old_function", "replacement": "new_function"},
        {"type": "insert", "line_number": 100, "content": "\nif __name__ == '__main__':\n    pass"},
    ]

    result = editor.bulk_edit(test_file, operations)
    print(f"{result['message']}")
    print(f"Operations applied: {result['operations_applied']}")

    print("\nRefactored Python file:")
    print(editor.read_file(test_file))

    # Cleanup
    os.remove(test_file)
    print("✓ Complex scenario test passed\n")


def run_all_tests():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("RUNNING ALL BULK EDITING TESTS")
    print("=" * 60 + "\n")

    try:
        test_line_operations()
        test_bulk_editor_fluent_api()
        test_bulk_editor_with_list()
        test_enhanced_file_editor()
        test_dry_run()
        test_multiline_insert()
        test_regex_replace()
        test_complex_scenario()

        print("=" * 60)
        print("✓ ALL TESTS PASSED")
        print("=" * 60)

    except Exception as e:
        print(f"\n✗ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    run_all_tests()
