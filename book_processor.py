#!/usr/bin/env python3
"""
Book Processor for Local AI TTS Models
Convert EPUBs to structured Markdown and generate TTS audio using local models
"""

import os
import re
import yaml
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup
import typer
from rich.console import Console
from rich.progress import track, Progress
from rich.table import Table
from rich.panel import Panel

from tts_utils import TTSManager

console = Console()
app = typer.Typer(help="📚 Process books with local AI TTS models")


class BookProcessor:
    """Processes EPUBs into structured format for TTS generation"""

    def __init__(self, base_path: Path = Path("books")):
        self.base_path = base_path
        self.base_path.mkdir(exist_ok=True)

    def create_book_structure(self, book_slug: str) -> Dict[str, Path]:
        """Create organized book directory structure"""
        book_dir = self.base_path / book_slug

        structure = {
            "root": book_dir,
            "source": book_dir / "source",
            "content": book_dir / "content",
            "chapters": book_dir / "content" / "chapters",
            "text": book_dir / "content" / "text",
            "audio": book_dir / "audio",
            "kokoro": book_dir / "audio" / "kokoro" / "chapters",
            "processing": book_dir / "processing",
            "logs": book_dir / "processing" / "logs",
            "temp": book_dir / "processing" / "temp",
        }

        # Create all directories
        for path in structure.values():
            path.mkdir(parents=True, exist_ok=True)

        return structure

    def extract_epub_content(self, epub_path: Path) -> Tuple[Dict, List[Dict]]:
        """Extract metadata and chapters from EPUB"""
        book = epub.read_epub(str(epub_path))

        # Extract metadata
        metadata = {
            "title": (
                book.get_metadata("DC", "title")[0][0]
                if book.get_metadata("DC", "title")
                else "Unknown"
            ),
            "author": (
                book.get_metadata("DC", "creator")[0][0]
                if book.get_metadata("DC", "creator")
                else "Unknown"
            ),
            "language": (
                book.get_metadata("DC", "language")[0][0]
                if book.get_metadata("DC", "language")
                else "en"
            ),
            "publisher": (
                book.get_metadata("DC", "publisher")[0][0]
                if book.get_metadata("DC", "publisher")
                else "Unknown"
            ),
            "description": (
                book.get_metadata("DC", "description")[0][0]
                if book.get_metadata("DC", "description")
                else ""
            ),
        }

        # Extract chapters
        chapters = []
        chapter_num = 1

        for item in book.get_items():
            if item.get_type() == ebooklib.ITEM_DOCUMENT:
                soup = BeautifulSoup(item.get_content(), "html.parser")

                # Extract text content
                text = soup.get_text()
                if not text.strip():
                    continue

                # Try to get chapter title
                title_elem = soup.find(["h1", "h2", "h3", "title"])
                title = (
                    title_elem.get_text().strip()
                    if title_elem
                    else f"Chapter {chapter_num}"
                )

                # Clean and format title for filename
                clean_title = re.sub(r"[^\w\s-]", "", title)
                clean_title = re.sub(r"[-\s]+", "-", clean_title)
                filename = f"{chapter_num:02d}-{clean_title.lower()}"

                chapters.append(
                    {
                        "number": chapter_num,
                        "title": title,
                        "filename": filename,
                        "content": self._clean_text(text),
                        "word_count": len(text.split()),
                    }
                )

                chapter_num += 1

        return metadata, chapters

    def _clean_text(self, text: str) -> str:
        """Clean and normalize text for TTS"""
        # Remove excessive whitespace
        text = re.sub(r"\s+", " ", text)
        # Remove page numbers and headers/footers patterns
        text = re.sub(r"\n\s*\d+\s*\n", "\n", text)
        # Clean up paragraph breaks
        text = re.sub(r"\n\s*\n", "\n\n", text)
        return text.strip()

    def save_metadata(self, book_dir: Path, metadata: Dict, chapters: List[Dict]):
        """Save book metadata and table of contents"""
        # Save metadata.yml
        metadata_path = book_dir / "metadata.yml"
        with open(metadata_path, "w") as f:
            yaml.dump(metadata, f, default_flow_style=False)

        # Save toc.yml (table of contents)
        toc = {
            "chapters": [
                {
                    "number": ch["number"],
                    "title": ch["title"],
                    "filename": ch["filename"],
                    "word_count": ch["word_count"],
                }
                for ch in chapters
            ]
        }

        toc_path = book_dir / "toc.yml"
        with open(toc_path, "w") as f:
            yaml.dump(toc, f, default_flow_style=False)

    def save_chapters(self, chapters_dir: Path, chapters: List[Dict]):
        """Save individual chapter markdown files"""
        for chapter in chapters:
            chapter_path = chapters_dir / f"{chapter['filename']}.md"
            with open(chapter_path, "w", encoding="utf-8") as f:
                f.write(f"# {chapter['title']}\n\n")
                f.write(chapter["content"])


@app.command()
def convert(
    epub_path: str = typer.Argument(..., help="Path to EPUB file"),
    book_title: str = typer.Argument(..., help="Book title for organization"),
    book_slug: Optional[str] = typer.Option(None, help="Custom book directory name"),
):
    """📖 Convert EPUB to structured Markdown"""

    epub_file = Path(epub_path)
    if not epub_file.exists():
        console.print(f"❌ EPUB file not found: {epub_path}", style="bold red")
        raise typer.Exit(1)

    # Generate book slug
    if not book_slug:
        book_slug = re.sub(r"[^\w\s-]", "", book_title.lower())
        book_slug = re.sub(r"[-\s]+", "-", book_slug)

    console.print(f"📚 Converting: [bold]{book_title}[/bold]")
    console.print(f"📁 Book slug: [cyan]{book_slug}[/cyan]")

    processor = BookProcessor()

    # Create book structure
    structure = processor.create_book_structure(book_slug)

    # Copy source EPUB (only if not already in target location)
    source_epub = structure["source"] / epub_file.name
    import shutil

    if epub_file.resolve() != source_epub.resolve():
        shutil.copy2(epub_file, source_epub)
        console.print(f"📄 Copied EPUB to: [cyan]{source_epub}[/cyan]")
    else:
        console.print(f"📄 EPUB already in place: [cyan]{source_epub}[/cyan]")

    # Extract content
    with console.status("Extracting EPUB content..."):
        metadata, chapters = processor.extract_epub_content(epub_file)
        metadata["slug"] = book_slug

    # Save processed content
    processor.save_metadata(structure["root"], metadata, chapters)
    processor.save_chapters(structure["chapters"], chapters)

    console.print(f"✅ Converted [bold green]{len(chapters)} chapters[/bold green]")
    console.print(f"📂 Book saved to: [cyan]{structure['root']}[/cyan]")

    # Show summary table
    table = Table(title=f"Book: {book_title}")
    table.add_column("Chapter", justify="right", style="cyan")
    table.add_column("Title", style="magenta")
    table.add_column("Words", justify="right", style="green")

    for ch in chapters[:10]:  # Show first 10 chapters
        table.add_row(str(ch["number"]), ch["title"][:50], str(ch["word_count"]))

    if len(chapters) > 10:
        table.add_row("...", f"... and {len(chapters) - 10} more chapters", "...")

    console.print(table)


@app.command()
def list_chapters(
    book_path: str = typer.Argument(..., help="Path to book directory"),
    show_audio: bool = typer.Option(True, help="Show audio status"),
):
    """📋 List all chapters in a book"""

    book_dir = Path(book_path)
    if not book_dir.exists():
        console.print(f"❌ Book directory not found: {book_path}", style="bold red")
        raise typer.Exit(1)

    # Load table of contents
    toc_path = book_dir / "toc.yml"
    if not toc_path.exists():
        console.print(
            f"❌ Table of contents not found. Run convert first.", style="bold red"
        )
        raise typer.Exit(1)

    with open(toc_path) as f:
        toc = yaml.safe_load(f)

    # Load metadata
    metadata_path = book_dir / "metadata.yml"
    with open(metadata_path) as f:
        metadata = yaml.safe_load(f)

    console.print(
        Panel(f"📚 {metadata['title']} by {metadata['author']}", style="bold blue")
    )

    # Create chapters table
    table = Table()
    table.add_column("#", justify="right", style="cyan")
    table.add_column("Title", style="magenta")
    table.add_column("Words", justify="right", style="green")

    if show_audio:
        table.add_column("Kokoro Audio", justify="center", style="yellow")

    audio_dir = book_dir / "audio" / "kokoro" / "chapters"

    for chapter in toc["chapters"]:
        # Check if audio exists
        audio_status = "⚪"
        if show_audio:
            audio_file = audio_dir / f"{chapter['filename']}.wav"
            if audio_file.exists():
                audio_status = "🎵"

        row = [
            str(chapter["number"]),
            chapter["title"][:60],
            str(chapter["word_count"]),
        ]

        if show_audio:
            row.append(audio_status)

        table.add_row(*row)

    console.print(table)
    console.print(f"\n🎵 = Audio available, ⚪ = No audio yet")


@app.command()
def generate_audio(
    book_path: str = typer.Argument(..., help="Path to book directory"),
    chapters: List[int] = typer.Argument(..., help="Chapter numbers to generate"),
    voice: str = typer.Option("af_heart", help="Voice to use"),
    model: str = typer.Option("kokoro", help="TTS model to use"),
    combine: bool = typer.Option(
        True, help="Combine segments into one file per chapter"
    ),
):
    """🎵 Generate TTS audio for specific chapters"""

    book_dir = Path(book_path)
    if not book_dir.exists():
        console.print(f"❌ Book directory not found: {book_path}", style="bold red")
        raise typer.Exit(1)

    # Load table of contents
    toc_path = book_dir / "toc.yml"
    with open(toc_path) as f:
        toc = yaml.safe_load(f)

    chapters_dict = {ch["number"]: ch for ch in toc["chapters"]}

    # Validate chapter numbers
    invalid_chapters = [ch for ch in chapters if ch not in chapters_dict]
    if invalid_chapters:
        console.print(f"❌ Invalid chapters: {invalid_chapters}", style="bold red")
        raise typer.Exit(1)

    # Initialize TTS
    tts_manager = TTSManager(output_dir=str(book_dir / "audio" / model / "chapters"))

    console.print(
        f"🎙️ Generating audio for {len(chapters)} chapters with voice: [bold cyan]{voice}[/bold cyan]"
    )

    # Process each chapter
    for chapter_num in track(chapters, description="Generating audio..."):
        chapter = chapters_dict[chapter_num]

        # Read chapter content
        chapter_file = book_dir / "content" / "chapters" / f"{chapter['filename']}.md"
        with open(chapter_file, "r", encoding="utf-8") as f:
            content = f.read()

        console.print(f"🎵 Processing Chapter {chapter_num}: {chapter['title']}")

        # Generate audio
        audio_files = tts_manager.generate_speech(
            text=content,
            voice=voice,
            filename_prefix=chapter["filename"],
            combine_segments=combine,
        )

        if audio_files:
            console.print(f"✅ Generated: [green]{audio_files[0]}[/green]")
        else:
            console.print(f"❌ Failed to generate audio for chapter {chapter_num}")


if __name__ == "__main__":
    app()
