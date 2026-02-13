"""Test that file_lister properly respects .gitignore"""

from file_lister import FileLister


def test_gitignore_respected():
    """Test that gitignored files are not shown"""
    lister = FileLister()
    
    # List current directory
    result = lister.list_files(directory=".", recursive=False)
    print("Non-recursive listing:")
    print(result)
    print("\n" + "="*80 + "\n")
    
    # List recursively
    result_recursive = lister.list_files(directory=".", recursive=True)
    print("Recursive listing:")
    print(result_recursive)
    print("\n" + "="*80 + "\n")
    
    # Verify .venv is not in results
    assert ".venv" not in result, ".venv should be gitignored"
    assert ".venv" not in result_recursive, ".venv should be gitignored in recursive"
    
    # Verify __pycache__ is not in results
    assert "__pycache__" not in result, "__pycache__ should be gitignored"
    assert "__pycache__" not in result_recursive, "__pycache__ should be gitignored in recursive"
    
    # Verify .git is not in results
    assert ".git" not in result, ".git should be gitignored"
    assert ".git" not in result_recursive, ".git should be gitignored in recursive"
    
    # Verify .env is not in results (it's in our .gitignore)
    assert ".env" not in result, ".env should be gitignored"
    assert ".env" not in result_recursive, ".env should be gitignored in recursive"
    
    # Verify uv.lock is not in results (it's in our .gitignore)
    assert "uv.lock" not in result, "uv.lock should be gitignored"
    assert "uv.lock" not in result_recursive, "uv.lock should be gitignored in recursive"
    
    print("✓ All gitignore tests passed!")


if __name__ == "__main__":
    test_gitignore_respected()
