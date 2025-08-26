#!/usr/bin/env python3
"""
Voice Playground - Compare TTS voices with sample text

Test and compare different voices using your own text samples.
Perfect for fine-tuning voice selection before processing full books.
"""

import typer
from pathlib import Path
from typing import List, Optional
from rich.console import Console
from rich.table import Table
from rich.progress import track
import time

from tts_utils import TTSManager

console = Console()
app = typer.Typer(help="🎭 Voice Playground - Test and compare TTS voices")

# Available voices in Kokoro
AVAILABLE_VOICES = ["af_heart", "af_sarah", "af_bella"]


@app.command()
def compare(
    text_file: str = typer.Argument(..., help="Path to text file to convert"),
    voices: Optional[List[str]] = typer.Option(
        None, "--voice", "-v", help="Specific voices to test (repeat for multiple)"
    ),
    output_dir: str = typer.Option("voice_comparisons", help="Output directory name"),
    all_voices: bool = typer.Option(False, "--all", help="Test all available voices"),
):
    """🎭 Compare different voices with your sample text"""

    text_path = Path(text_file)
    if not text_path.exists():
        console.print(f"❌ Text file not found: {text_file}", style="bold red")
        raise typer.Exit(1)

    # Read the text
    try:
        with open(text_path, "r", encoding="utf-8") as f:
            text_content = f.read().strip()
    except Exception as e:
        console.print(f"❌ Error reading file: {e}", style="bold red")
        raise typer.Exit(1)

    if not text_content:
        console.print("❌ Text file is empty", style="bold red")
        raise typer.Exit(1)

    # Determine which voices to test
    if all_voices:
        voices_to_test = AVAILABLE_VOICES.copy()
    elif voices:
        voices_to_test = voices
        # Validate voices
        invalid_voices = [v for v in voices_to_test if v not in AVAILABLE_VOICES]
        if invalid_voices:
            console.print(f"❌ Invalid voices: {invalid_voices}", style="bold red")
            console.print(f"Available voices: {AVAILABLE_VOICES}")
            raise typer.Exit(1)
    else:
        voices_to_test = AVAILABLE_VOICES.copy()  # Default to all

    console.print(f"📝 [bold blue]Voice Playground[/bold blue]")
    console.print(f"📄 Text file: [cyan]{text_file}[/cyan]")
    console.print(f"📊 Text length: [green]{len(text_content)} characters[/green]")
    console.print(f"🎭 Testing voices: [yellow]{', '.join(voices_to_test)}[/yellow]")
    console.print()

    # Show text preview
    preview_text = (
        text_content[:200] + "..." if len(text_content) > 200 else text_content
    )
    console.print("📖 [bold]Text Preview:[/bold]")
    console.print(f"[dim]{preview_text}[/dim]")
    console.print()

    # Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)

    # Create subdirectory based on text filename
    text_slug = text_path.stem.replace(" ", "-").lower()
    session_dir = output_path / text_slug
    session_dir.mkdir(exist_ok=True)

    console.print(f"📁 Output directory: [cyan]{session_dir}[/cyan]")
    console.print()

    # Initialize TTS Manager
    tts_manager = TTSManager(output_dir=str(session_dir))

    # Results tracking
    results = []

    # Generate audio for each voice
    for voice in track(voices_to_test, description="🎙️ Generating voices..."):
        console.print(f"🎵 Processing with voice: [magenta]{voice}[/magenta]")

        start_time = time.time()

        try:
            audio_files = tts_manager.generate_speech(
                text=text_content,
                voice=voice,
                filename_prefix=f"{text_slug}_{voice}",
                combine_segments=True,
            )

            generation_time = time.time() - start_time

            if audio_files:
                audio_file = Path(audio_files[0])
                file_size_mb = audio_file.stat().st_size / (1024 * 1024)

                # Calculate duration (rough estimate: 24000 Hz sample rate)
                import soundfile as sf

                try:
                    data, samplerate = sf.read(audio_file)
                    duration_seconds = len(data) / samplerate
                    duration_minutes = duration_seconds / 60
                except:
                    duration_minutes = 0

                results.append(
                    {
                        "voice": voice,
                        "file": audio_file.name,
                        "size_mb": file_size_mb,
                        "duration_min": duration_minutes,
                        "generation_time": generation_time,
                        "success": True,
                    }
                )

                console.print(
                    f"   ✅ Generated: [green]{audio_file.name}[/green] ({file_size_mb:.1f}MB, {duration_minutes:.1f}min)"
                )
            else:
                results.append(
                    {
                        "voice": voice,
                        "file": "Failed",
                        "size_mb": 0,
                        "duration_min": 0,
                        "generation_time": generation_time,
                        "success": False,
                    }
                )
                console.print(f"   ❌ Failed to generate audio")

        except Exception as e:
            console.print(f"   ❌ Error: {e}")
            results.append(
                {
                    "voice": voice,
                    "file": "Error",
                    "size_mb": 0,
                    "duration_min": 0,
                    "generation_time": 0,
                    "success": False,
                }
            )

    console.print()

    # Show results table
    table = Table(title="🎭 Voice Comparison Results")
    table.add_column("Voice", style="magenta", no_wrap=True)
    table.add_column("Audio File", style="cyan")
    table.add_column("Size", justify="right", style="green")
    table.add_column("Duration", justify="right", style="blue")
    table.add_column("Gen Time", justify="right", style="yellow")
    table.add_column("Status", justify="center")

    for result in results:
        status = "✅" if result["success"] else "❌"
        size_str = f"{result['size_mb']:.1f}MB" if result["success"] else "-"
        duration_str = f"{result['duration_min']:.1f}min" if result["success"] else "-"
        gen_time_str = (
            f"{result['generation_time']:.1f}s"
            if result["generation_time"] > 0
            else "-"
        )

        table.add_row(
            result["voice"],
            result["file"],
            size_str,
            duration_str,
            gen_time_str,
            status,
        )

    console.print(table)
    console.print()

    # Show file listing
    successful_files = [r for r in results if r["success"]]
    if successful_files:
        console.print("📁 [bold green]Generated Files:[/bold green]")
        for result in successful_files:
            file_path = session_dir / result["file"]
            console.print(f"   🎵 [cyan]{file_path}[/cyan]")

        console.print()
        console.print("💡 [bold blue]Next Steps:[/bold blue]")
        console.print(
            f"   1. Listen to the generated files in: [cyan]{session_dir}[/cyan]"
        )
        console.print("   2. Compare voice quality, tone, and clarity")
        console.print("   3. Choose your favorite voice for book processing")
        console.print(
            "   4. Use: [green]python book_processor.py generate-audio books/book-name chapters --voice YOUR_CHOICE[/green]"
        )


@app.command()
def create_sample():
    """📝 Create sample text files for voice testing"""

    samples_dir = Path("voice_samples")
    samples_dir.mkdir(exist_ok=True)

    # Short sample
    short_sample = """Hello, this is a short voice test. I'm testing different AI voices to see which one sounds the most natural and pleasant for audiobook narration."""

    # Medium sample with variety
    medium_sample = """
# Voice Test Sample

This is a medium-length text sample for voice comparison testing. It includes various sentence structures and punctuation to help evaluate voice quality.

Here are some different types of content:

**Narrative Text**: The golden sunlight filtered through the ancient oak trees, casting dancing shadows across the forest floor. A gentle breeze rustled the leaves, creating a symphony of natural sounds.

**Dialogue**: "Hello there!" she called out cheerfully. "How are you doing today?"

"I'm doing well, thank you," he replied with a warm smile. "What brings you to this part of the forest?"

**Technical Content**: The process involves three key steps: initialization, data processing, and output generation. Each step requires careful attention to detail and proper error handling.

**Numbers and Lists**: The recipe calls for 2 cups of flour, 1.5 cups of sugar, and 3 large eggs. Bake at 350 degrees Fahrenheit for approximately 25-30 minutes.

This sample should give you a good sense of how each voice handles different types of content, punctuation, and emotional tone.
""".strip()

    # Long sample for extensive testing
    long_sample = """
# Extended Voice Comparison Sample

## Introduction

This extended sample is designed to thoroughly test AI voice capabilities across various content types, sentence lengths, and emotional tones. Use this when you want to really understand how a voice performs over longer passages.

## Storytelling Test

Once upon a time, in a kingdom far beyond the misty mountains and rolling green hills, there lived a young inventor named Elena. She spent her days in a cluttered workshop filled with gears, springs, and curious contraptions that whirred and clicked with mysterious purpose.

Elena had always been fascinated by the possibility of flight. While other children played with dolls or wooden swords, she built model airplanes from scraps of wood and fabric. Her dream was to create a flying machine that could carry a person high above the clouds, where the world would look like a patchwork quilt spread across the earth.

## Technical Explanation

The principles of aerodynamics involve four fundamental forces: lift, weight, thrust, and drag. Lift is generated by the difference in air pressure above and below an aircraft's wings. Weight, of course, is the gravitational force pulling the aircraft toward the earth. Thrust propels the aircraft forward, typically provided by propellers or jet engines. Drag is the resistance that opposes the aircraft's motion through the air.

Understanding these forces is crucial for anyone designing aircraft, from simple paper airplanes to complex commercial jets. The interplay between these forces determines whether an aircraft can achieve sustained flight.

## Emotional Range Test

The news hit Elena like a thunderbolt. Her mentor, Professor Aldrich, had passed away suddenly in his sleep. For a moment, she couldn't breathe. The workshop seemed to spin around her as grief washed over her in waves.

But then she remembered his words: "Elena, my dear, invention is not just about creating new things. It's about solving problems and making the world a better place. Promise me you'll never stop dreaming, never stop building."

With tears streaming down her face, she smiled. She would honor his memory by finishing their greatest project together: the first human-carrying flying machine.

## Dialogue and Character Voices

"Are you absolutely certain this contraption will fly?" asked her assistant, Marcus, eyeing the peculiar aircraft with obvious skepticism.

Elena laughed, a sound filled with nervous excitement. "Certain? Marcus, nothing in invention is certain! But I believe in our calculations, and more importantly, I believe in the dream."

"The dream is all well and good," Marcus replied dryly, "but I'd prefer not to become a pancake in the town square."

"Then perhaps," Elena suggested with a mischievous grin, "I should be the one to take the maiden flight."

## Conclusion

This sample provides a comprehensive test of voice capabilities, including narrative description, technical content, emotional passages, and character dialogue. Use it to evaluate which voice best suits your specific needs for audiobook narration or other voice applications.

Remember: the best voice is the one that keeps listeners engaged and makes the content come alive.
""".strip()

    # Write sample files
    samples = [
        ("short_sample.txt", short_sample),
        ("medium_sample.txt", medium_sample),
        ("long_sample.txt", long_sample),
    ]

    console.print("📝 [bold blue]Creating Sample Text Files[/bold blue]")
    console.print()

    for filename, content in samples:
        file_path = samples_dir / filename
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

        console.print(f"✅ Created: [cyan]{file_path}[/cyan] ({len(content)} chars)")

    console.print()
    console.print("🎯 [bold green]Sample files created![/bold green]")
    console.print(f"📁 Location: [cyan]{samples_dir}[/cyan]")
    console.print()
    console.print("💡 [bold blue]Usage Examples:[/bold blue]")
    console.print("   # Test all voices with short sample")
    console.print(
        f"   python voice_playground.py compare {samples_dir}/short_sample.txt --all"
    )
    console.print()
    console.print("   # Test specific voices with medium sample")
    console.print(
        f"   python voice_playground.py compare {samples_dir}/medium_sample.txt -v af_bella -v af_sarah"
    )
    console.print()
    console.print("   # Test single voice with long sample")
    console.print(
        f"   python voice_playground.py compare {samples_dir}/long_sample.txt -v af_heart"
    )


@app.command()
def list_voices():
    """🎭 List all available voices"""
    console.print("🎭 [bold blue]Available Voices in Kokoro TTS[/bold blue]")
    console.print()

    voice_descriptions = {
        "af_heart": "Natural, clear narrator voice (default) - Great for general content",
        "af_sarah": "Expressive female voice - Good for dialogue and emotional content",
        "af_bella": "Warm storytelling voice - Perfect for narratives and fiction",
    }

    table = Table()
    table.add_column("Voice Name", style="magenta", no_wrap=True)
    table.add_column("Description", style="cyan")

    for voice in AVAILABLE_VOICES:
        description = voice_descriptions.get(voice, "High-quality voice")
        table.add_row(voice, description)

    console.print(table)
    console.print()
    console.print("💡 [bold blue]Usage:[/bold blue]")
    console.print("   python voice_playground.py compare your_text.txt -v af_bella")
    console.print("   python voice_playground.py compare your_text.txt --all")


if __name__ == "__main__":
    app()
