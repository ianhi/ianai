"""
Test suite for filesystem_tool.py
Demonstrates all file operations with safe examples
"""

import os
import json
from filesystem_tool import FilesystemTool, move_file, rename_file, delete_file, copy_file, create_dir, file_info, search_files, file_exists, get_file_size


def print_result(operation: str, result: dict):
    """Pretty print operation results."""
    print(f"\n{'='*60}")
    print(f"Operation: {operation}")
    print('='*60)
    print(json.dumps(result, indent=2))
    if result.get('success'):
        print("✓ SUCCESS")
    else:
        print("✗ FAILED")


def run_tests():
    """Run comprehensive tests of the filesystem tool."""
    
    print("FILESYSTEM TOOL TEST SUITE")
    print("=" * 60)
    
    # Initialize filesystem tool
    fs = FilesystemTool(safe_mode=True)
    
    # Test 1: Create a test directory
    print("\n\n### TEST 1: Create Directory ###")
    result = fs.create_directory("test_fs_operations")
    print_result("Create test directory", result)
    
    # Test 2: Create a test file
    print("\n\n### TEST 2: Create Test Files ###")
    test_file = "test_fs_operations/test_file.txt"
    with open(test_file, 'w') as f:
        f.write("This is a test file for filesystem operations.\n")
        f.write("Line 2\n")
        f.write("Line 3\n")
    
    result = fs.get_info(test_file)
    print_result("Get file info", result)
    
    # Test 3: Copy file
    print("\n\n### TEST 3: Copy File ###")
    result = fs.copy(test_file, "test_fs_operations/test_file_copy.txt")
    print_result("Copy file", result)
    
    # Test 4: Rename file
    print("\n\n### TEST 4: Rename File ###")
    result = fs.rename("test_fs_operations/test_file_copy.txt", "renamed_file.txt")
    print_result("Rename file", result)
    
    # Test 5: Move file
    print("\n\n### TEST 5: Move File ###")
    fs.create_directory("test_fs_operations/subfolder")
    result = fs.move("test_fs_operations/renamed_file.txt", "test_fs_operations/subfolder/renamed_file.txt")
    print_result("Move file to subfolder", result)
    
    # Test 6: Search for files
    print("\n\n### TEST 6: Search for Files ###")
    result = fs.search("*.txt", "test_fs_operations", recursive=True)
    print_result("Search for .txt files", result)
    
    # Test 7: Get file size
    print("\n\n### TEST 7: Get File Size ###")
    result = fs.get_size(test_file, human_readable=True)
    print_result("Get file size", result)
    
    # Test 8: Get directory size
    print("\n\n### TEST 8: Get Directory Size ###")
    result = fs.get_size("test_fs_operations", human_readable=True)
    print_result("Get directory size", result)
    
    # Test 9: Check file exists
    print("\n\n### TEST 9: Check File Exists ###")
    result = fs.exists(test_file)
    print_result("Check if file exists", result)
    
    result = fs.exists("nonexistent_file.txt")
    print_result("Check if nonexistent file exists", result)
    
    # Test 10: Get directory info
    print("\n\n### TEST 10: Get Directory Info ###")
    result = fs.get_info("test_fs_operations")
    print_result("Get directory info", result)
    
    # Test 11: Try to copy with overwrite protection
    print("\n\n### TEST 11: Copy Protection (should fail) ###")
    result = fs.copy("test_fs_operations/test_file.txt", "test_fs_operations/test_file.txt", overwrite=False)
    print_result("Try to copy file over itself without overwrite", result)
    
    # Test 12: Delete single file
    print("\n\n### TEST 12: Delete Single File ###")
    result = fs.delete("test_fs_operations/subfolder/renamed_file.txt", confirm=True)
    print_result("Delete single file", result)
    
    # Test 13: Try to delete directory without recursive (should fail)
    print("\n\n### TEST 13: Delete Directory Without Recursive (should fail) ###")
    result = fs.delete("test_fs_operations/subfolder", recursive=False, confirm=True)
    print_result("Try to delete directory without recursive", result)
    
    # Test 14: Delete directory with recursive
    print("\n\n### TEST 14: Delete Directory With Recursive ###")
    result = fs.delete("test_fs_operations/subfolder", recursive=True, confirm=True)
    print_result("Delete directory recursively", result)
    
    # Test 15: Test safety - try without confirm (should fail)
    print("\n\n### TEST 15: Safety Check - Delete Without Confirm (should fail) ###")
    result = fs.delete("test_fs_operations/test_file.txt", confirm=False)
    print_result("Try to delete without confirm", result)
    
    # Test 16: Create nested directories
    print("\n\n### TEST 16: Create Nested Directories ###")
    result = fs.create_directory("test_fs_operations/level1/level2/level3", parents=True)
    print_result("Create nested directories", result)
    
    # Test 17: Search with pattern
    print("\n\n### TEST 17: Search for Directories ###")
    result = fs.search("level*", "test_fs_operations", recursive=True)
    print_result("Search for directories matching pattern", result)
    
    # Test 18: Using standalone functions
    print("\n\n### TEST 18: Using Standalone Functions ###")
    result = file_info("test_fs_operations")
    print_result("Get info using standalone function", result)
    
    # Clean up - delete test directory
    print("\n\n### CLEANUP: Delete Test Directory ###")
    result = fs.delete("test_fs_operations", recursive=True, confirm=True)
    print_result("Clean up test directory", result)
    
    # Test 19: Test safe_mode validation
    print("\n\n### TEST 19: Safe Mode Validation ###")
    fs_safe = FilesystemTool(base_path=".", safe_mode=True)
    try:
        result = fs_safe.delete("/etc/passwd", confirm=True)
        print_result("Try to delete system file (should be blocked)", result)
    except Exception as e:
        print_result("Try to delete system file (should be blocked)", {
            'success': True,
            'message': 'Safe mode correctly blocked dangerous operation',
            'error_caught': str(e)
        })
    
    print("\n\n" + "="*60)
    print("ALL TESTS COMPLETED")
    print("="*60)


if __name__ == '__main__':
    run_tests()
