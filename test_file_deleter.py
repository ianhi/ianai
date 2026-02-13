"""Test the FileDeleter class"""
from file_deleter import FileDeleter
import os


def test_delete_file():
    """Test deleting a single file"""
    deleter = FileDeleter()
    
    # Create a test file
    test_file = "test_delete_me.txt"
    with open(test_file, "w") as f:
        f.write("This file should be deleted")
    
    # Verify it exists
    assert os.path.exists(test_file), "Test file was not created"
    
    # Delete it
    result = deleter.delete_file(test_file)
    print(f"Delete result: {result}")
    
    # Verify it's gone
    assert not os.path.exists(test_file), "File was not deleted"
    assert "Successfully deleted" in result, "Success message not returned"
    print("✓ Test passed: Single file deletion works")


def test_delete_multiple_files():
    """Test deleting multiple files"""
    deleter = FileDeleter()
    
    # Create test files
    test_files = ["test_delete_1.txt", "test_delete_2.txt", "test_delete_3.txt"]
    for file in test_files:
        with open(file, "w") as f:
            f.write(f"Test file: {file}")
    
    # Verify they exist
    for file in test_files:
        assert os.path.exists(file), f"Test file {file} was not created"
    
    # Delete them
    result = deleter.delete_files(test_files)
    print(f"Delete multiple result:\n{result}")
    
    # Verify they're gone
    for file in test_files:
        assert not os.path.exists(file), f"File {file} was not deleted"
    
    assert "3 deleted, 0 failed" in result, "Summary incorrect"
    print("✓ Test passed: Multiple file deletion works")


def test_delete_nonexistent_file():
    """Test deleting a file that doesn't exist"""
    deleter = FileDeleter()
    
    result = deleter.delete_file("this_file_does_not_exist.txt")
    print(f"Delete nonexistent result: {result}")
    
    assert "Error" in result, "Should return error for nonexistent file"
    assert "not found" in result, "Should mention file not found"
    print("✓ Test passed: Error handling for nonexistent file works")


if __name__ == "__main__":
    print("Testing FileDeleter class...\n")
    test_delete_file()
    print()
    test_delete_multiple_files()
    print()
    test_delete_nonexistent_file()
    print("\n✓ All tests passed!")
