#!/bin/bash

# Cleanup script for unused Python files
# Created to remove deprecated/unused files from the project

echo "🗑️  Cleaning up unused files..."
echo ""

# List of files to delete
files_to_delete=(
    "main.py"
    "ui.py"
    "main_v1.py"
    "filehandler.py"
    "file_editing.py"
    "file_editing2.py"
    "file_editor.py"
    "file_editor_tools.py"
    "test.py"
    "test2.py"
)

# Confirm before deleting
echo "The following files will be deleted:"
for file in "${files_to_delete[@]}"; do
    if [ -f "$file" ]; then
        size=$(ls -lh "$file" | awk '{print $5}')
        echo "  ❌ $file ($size)"
    fi
done

echo ""
read -p "Are you sure you want to delete these files? (y/N): " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    echo "Deleting files..."
    
    deleted_count=0
    for file in "${files_to_delete[@]}"; do
        if [ -f "$file" ]; then
            rm "$file"
            echo "  ✓ Deleted: $file"
            ((deleted_count++))
        else
            echo "  ⚠️  Not found: $file"
        fi
    done
    
    echo ""
    echo "✅ Cleanup complete! Deleted $deleted_count files."
else
    echo ""
    echo "❌ Cleanup cancelled."
fi
