import argparse
import json
import re
import sys
from pathlib import Path

from pypdf import PdfReader, PdfWriter

try:
    import pypdfium2 as pdfium
except ModuleNotFoundError as exc:  # pragma: no cover - exercised in CLI usage
    raise SystemExit(
        "pypdfium2 is required for cover extraction. Install it with "
        "`pip install pypdfium2` or add it from the project requirements."
    ) from exc


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from musicae_content.book_chapter_upload_data import (  # noqa: E402
    AUTHOR_NAMES_BG,
    BOOK_CHAPTERS,
    BOOK_TITLE_BG,
    FILE_PREFIX,
    LANGUAGE,
    PUBLISHED_PLACE,
    PUBLISHED_YEAR,
    PUBLISHER,
    build_bib_info,
)


def _safe_filename_part(value):
    cleaned = re.sub(r'[<>:"/\\\\|?*]+', " ", value).strip()
    return re.sub(r"\s+", " ", cleaned)


def _combined_filename(title_bg):
    return f"{FILE_PREFIX}_{_safe_filename_part(title_bg)}.pdf"


def _load_text(path):
    reader = PdfReader(str(path))
    parts = []
    for page in reader.pages:
        parts.append((page.extract_text() or "").strip())
    return "\n\n".join(part for part in parts if part).strip()


def _merge_pdfs(output_path, *pdf_paths):
    writer = PdfWriter()
    for pdf_path in pdf_paths:
        reader = PdfReader(str(pdf_path))
        for page in reader.pages:
            writer.add_page(page)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("wb") as handle:
        writer.write(handle)


def _render_cover(cover_pdf, output_path):
    output_path.parent.mkdir(parents=True, exist_ok=True)
    document = pdfium.PdfDocument(str(cover_pdf))
    page = document[0]
    bitmap = page.render(scale=2.5)
    image = bitmap.to_pil()
    image.save(output_path)
    page.close()
    document.close()


def _validate_abstracts(chapter):
    prefixes = {
        "abstract_bg": "Тази глава",
        "abstract_en": "This chapter",
        "abstract_de": "Dieses Kapitel",
    }
    for field_name, prefix in prefixes.items():
        value = chapter[field_name]
        if not value.startswith(prefix):
            raise ValueError(f"{field_name} for {chapter['title_bg']} must start with '{prefix}'.")


def build_manifest(source_root, header_pdf, disclaimer_pdf, cover_pdf, output_dir):
    output_dir.mkdir(parents=True, exist_ok=True)
    processed_dir = output_dir / "processed_pdfs"
    extracted_dir = output_dir / "extracted_text"
    shared_dir = output_dir / "shared_assets"
    banner_path = shared_dir / "devedzhiev_vasilev_muzikalno_razvitie_cover_front.png"

    _render_cover(cover_pdf, banner_path)

    entries = []
    for chapter in BOOK_CHAPTERS:
        _validate_abstracts(chapter)

        source_path = source_root / chapter["source_relpath"]
        if not source_path.exists():
            raise FileNotFoundError(f"Source PDF not found: {source_path}")

        extracted_text = _load_text(source_path)
        if not extracted_text:
            raise ValueError(f"No extractable text found in {source_path}")

        text_output_path = extracted_dir / f"{_safe_filename_part(chapter['title_bg'])}.txt"
        text_output_path.parent.mkdir(parents=True, exist_ok=True)
        text_output_path.write_text(extracted_text, encoding="utf-8")

        combined_pdf_path = processed_dir / _combined_filename(chapter["title_bg"])
        _merge_pdfs(combined_pdf_path, header_pdf, source_path, disclaimer_pdf)

        entry = {
            "ptype": "chapter",
            "title_bg": chapter["title_bg"],
            "title_en": chapter["title_en"],
            "title_de": chapter["title_de"],
            "abstract_bg": chapter["abstract_bg"],
            "abstract_en": chapter["abstract_en"],
            "abstract_de": chapter["abstract_de"],
            "page_range": chapter["page_range"],
            "published_year": PUBLISHED_YEAR,
            "published_place": PUBLISHED_PLACE,
            "publisher_txt": PUBLISHER,
            "container_title": BOOK_TITLE_BG,
            "language": LANGUAGE,
            "internal": False,
            "authors_bg": AUTHOR_NAMES_BG,
            "bib_info": build_bib_info(chapter["title_bg"], chapter["page_range"]),
            "file_path": str(combined_pdf_path),
            "banner_path": str(banner_path),
            "source_pdf": str(source_path),
            "extracted_text_path": str(text_output_path),
        }
        entries.append(entry)

    manifest = {
        "book_title_bg": BOOK_TITLE_BG,
        "publisher_txt": PUBLISHER,
        "published_place": PUBLISHED_PLACE,
        "published_year": PUBLISHED_YEAR,
        "author_names_bg": AUTHOR_NAMES_BG,
        "banner_path": str(banner_path),
        "entries": entries,
    }

    manifest_path = output_dir / "book_chapters_manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    return manifest_path


def main():
    parser = argparse.ArgumentParser(description="Prepare merged PDFs and a manifest for book chapter upload.")
    parser.add_argument("--source-root", required=True, help="Root folder containing the source chapter PDFs.")
    parser.add_argument("--header-pdf", required=True, help="Header PDF to prepend to each chapter.")
    parser.add_argument("--disclaimer-pdf", required=True, help="Disclaimer PDF to append to each chapter.")
    parser.add_argument("--cover-pdf", required=True, help="Cover PDF whose first page will be used as the banner.")
    parser.add_argument("--output-dir", required=True, help="Directory for generated PDFs, text extracts, and manifest.")
    args = parser.parse_args()

    source_root = Path(args.source_root)
    header_pdf = Path(args.header_pdf)
    disclaimer_pdf = Path(args.disclaimer_pdf)
    cover_pdf = Path(args.cover_pdf)
    output_dir = Path(args.output_dir)

    manifest_path = build_manifest(source_root, header_pdf, disclaimer_pdf, cover_pdf, output_dir)
    print(f"Prepared {len(BOOK_CHAPTERS)} entries.")
    print(f"Manifest: {manifest_path}")


if __name__ == "__main__":
    main()
