"""
Shared configuration used by every feature module.
Keeping this in one place means every folder points to the
same uploads directory instead of duplicating the path.
"""
import os

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
