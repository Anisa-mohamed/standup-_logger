"""
Secure file upload utilities.

Security measures applied:
- Allowlist of safe extensions (no .exe, .php, .sh, etc.)
- Werkzeug's secure_filename strips path traversal attempts
- UUID-based filenames prevent enumeration and collisions
- File size enforced at the Flask config level (MAX_CONTENT_LENGTH)
"""
import os
import uuid
from werkzeug.utils import secure_filename
from flask import current_app


ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf'}


def allowed_file(filename: str) -> bool:
    """Return True only if the file has a permitted extension."""
    return (
        '.' in filename
        and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
    )


def save_upload(file_storage) -> str | None:
    """
    Persist an uploaded FileStorage object to disk.

    Returns:
        Relative filename (e.g. 'abc123.jpg') on success, None if no valid file.

    Raises:
        ValueError: If the file type is not permitted.
    """
    if not file_storage or file_storage.filename == '':
        return None

    original_name = secure_filename(file_storage.filename)

    if not allowed_file(original_name):
        raise ValueError(
            f'File type not allowed. Permitted types: {", ".join(sorted(ALLOWED_EXTENSIONS))}'
        )

    ext = original_name.rsplit('.', 1)[1].lower()
    unique_filename = f'{uuid.uuid4().hex}.{ext}'

    upload_dir = current_app.config['UPLOAD_FOLDER']
    os.makedirs(upload_dir, exist_ok=True)

    dest_path = os.path.join(upload_dir, unique_filename)
    file_storage.save(dest_path)

    return unique_filename


def delete_upload(filename: str) -> bool:
    """Remove a previously saved upload. Returns True if deleted."""
    if not filename:
        return False
    path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
    if os.path.exists(path):
        os.remove(path)
        return True
    return False
