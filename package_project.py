import os
import zipfile
from pathlib import Path


def package_project():
    project_dir = Path(__file__).resolve().parent
    archive_name = project_dir / "UnrealScrap_Migration_Package.zip"

    print(f"Starting packaging process for: {project_dir}")
    print(f"Target archive: {archive_name}")

    # Files/folders to explicitly exclude
    exclude_folders = {"__pycache__", ".git", ".venv", ".idea", ".vscode"}
    exclude_files = {"UnrealScrap_Migration_Package.zip", "package_project.py"}

    count = 0
    with zipfile.ZipFile(archive_name, "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(project_dir):
            # Exclude folders in-place to prevent os.walk from entering them
            dirs[:] = [d for d in dirs if d not in exclude_folders]

            for file in files:
                if file in exclude_files:
                    continue

                file_path = Path(root) / file
                # Get path relative to project root
                relative_path = file_path.relative_to(project_dir)

                zipf.write(file_path, relative_path)
                count += 1

    archive_size_mb = archive_name.stat().st_size / (1024 * 1024)
    print(f"\nSuccessfully created package: {archive_name.name}")
    print(f"Total files archived: {count}")
    print(f"Archive file size: {archive_size_mb:.2f} MB")


if __name__ == "__main__":
    package_project()
