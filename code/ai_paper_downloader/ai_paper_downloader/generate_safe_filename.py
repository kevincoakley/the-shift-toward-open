import hashlib
import re

MAX_FILENAME_LENGTH = 255
EXTENSION = ".pdf"
HASH_LENGTH = 8
SEPARATOR = "__"


def slugify_title(title):
    """
    Converts a paper title into a lowercase, underscore-separated slug.
    Removes special characters and collapses whitespace.
    """
    title = title.lower()
    title = re.sub(r"\s+", "_", title)  # Replace spaces with underscores
    title = re.sub(
        r"[^\w_]", "", title
    )  # Remove all non-alphanumeric and non-underscore
    return title


def generate_deterministic_hash(conference, year, title, hash_len=HASH_LENGTH):
    """
    Generates a deterministic short hash from conference, year, and title.
    """
    key = f"{conference.lower()}_{year}_{title.strip().lower()}"
    return hashlib.sha256(key.encode("utf-8")).hexdigest()[:hash_len]


def generate_safe_filename(conference, year, title, extension=EXTENSION):
    """
    Generates a safe, unique, and human-readable filename within 255 characters.
    Format: truncated_slug__hash.pdf
    """
    safe_hash = generate_deterministic_hash(conference, year, title)
    base_slug = slugify_title(title)

    # Calculate the max length for the slug to stay within filename limit
    reserved = len(SEPARATOR) + len(safe_hash) + len(extension)
    max_slug_len = MAX_FILENAME_LENGTH - reserved
    truncated_slug = base_slug[:max_slug_len]

    return f"{truncated_slug}{SEPARATOR}{safe_hash}{extension}"
