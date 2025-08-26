"""
TTS Utilities for Kokoro and other models
"""

import os
import sys
from pathlib import Path
from typing import Generator, Tuple, List
import soundfile as sf

try:
    from kokoro import KPipeline
    from rich.console import Console
    from rich.progress import track
except ImportError as e:
    print(f"Missing dependency: {e}")
    print("Install with: pipenv install")


def create_audio_directory(name: str = "audio_output") -> Path:
    """Create and return path to audio output directory"""
    audio_dir = Path(name)
    audio_dir.mkdir(exist_ok=True)
    return audio_dir


class TTSManager:
    """Manages TTS model operations with better organization"""

    def __init__(self, lang_code: str = "a", output_dir: str = "audio_output"):
        self.lang_code = lang_code
        self.output_dir = create_audio_directory(output_dir)
        self.console = Console()

        self.console.print(f"[blue]Initializing Kokoro TTS (lang: {lang_code})[/blue]")
        try:
            self.pipeline = KPipeline(lang_code=lang_code)
            self.console.print("[green]✅ TTS initialized successfully[/green]")
        except Exception as e:
            self.console.print(f"[red]❌ TTS initialization failed: {e}[/red]")
            raise

    def generate_speech(
        self,
        text: str,
        voice: str = "af_heart",
        filename_prefix: str = "output",
        save_files: bool = True,
        combine_segments: bool = True,
    ) -> List[str]:
        """
        Generate speech from text

        Args:
            text: Text to convert
            voice: Voice model to use
            filename_prefix: Prefix for output files
            save_files: Whether to save audio files
            combine_segments: Whether to combine all segments into one file

        Returns:
            List of generated audio file paths
        """
        self.console.print(f"[green]🎙️ Generating speech with voice: {voice}[/green]")

        generator = self.pipeline(text, voice=voice)
        audio_files = []
        all_audio_segments = []

        segments = list(generator)  # Convert to list to get length

        for i, (gs, ps, audio) in enumerate(
            track(segments, description="Generating...")
        ):
            self.console.print(f"Segment {i+1}/{len(segments)}: gs={gs}, ps={ps}")
            all_audio_segments.append(audio)

            if save_files and not combine_segments:
                filename = self.output_dir / f"{filename_prefix}_{i:03d}.wav"
                sf.write(str(filename), audio, 24000)
                audio_files.append(str(filename))
                self.console.print(f"[yellow]💾 Saved segment: {filename}[/yellow]")

        # Combine all segments into one file if requested
        if save_files and combine_segments and all_audio_segments:
            import numpy as np

            # Concatenate all audio segments
            combined_audio = np.concatenate(all_audio_segments)
            combined_filename = self.output_dir / f"{filename_prefix}.wav"

            sf.write(str(combined_filename), combined_audio, 24000)
            audio_files.append(str(combined_filename))

            duration_mins = len(combined_audio) / 24000 / 60
            self.console.print(
                f"[bold green]🎵 Combined audio saved: {combined_filename}[/bold green]"
            )
            self.console.print(
                f"[cyan]📊 Duration: {duration_mins:.1f} minutes, {len(segments)} segments combined[/cyan]"
            )
        elif save_files and not combine_segments:
            # Individual files were already saved above
            pass

        return audio_files

    def available_voices(self) -> List[str]:
        """Return list of available voices (if accessible from model)"""
        # This would need to be implemented based on Kokoro's API
        # For now, return common ones
        return ["af_heart", "af_sarah", "af_bella"]

    def convert_file(
        self, filepath: str, voice: str = "af_heart", max_chars: int = None
    ) -> List[str]:
        """Convert a text file to speech"""
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                text = f.read()

            if max_chars and len(text) > max_chars:
                text = text[:max_chars]
                self.console.print(
                    f"[yellow]⚠️ Text truncated to {max_chars} characters[/yellow]"
                )

            filename_prefix = Path(filepath).stem
            return self.generate_speech(text, voice, filename_prefix)

        except FileNotFoundError:
            self.console.print(f"[red]❌ File not found: {filepath}[/red]")
            return []
        except Exception as e:
            self.console.print(f"[red]❌ Error converting file: {e}[/red]")
            return []


def quick_tts(text: str, voice: str = "af_heart", play: bool = False) -> str:
    """Quick TTS function for simple use cases"""
    tts = TTSManager()
    files = tts.generate_speech(text, voice, "quick")

    if play and files:
        # Could add audio playback here
        print(f"Generated: {files[0]}")

    return files[0] if files else None


if __name__ == "__main__":
    # CLI usage example
    import argparse

    parser = argparse.ArgumentParser(description="TTS Utilities")
    parser.add_argument("text", help="Text to convert")
    parser.add_argument("--voice", default="af_heart", help="Voice to use")
    parser.add_argument("--output", default="cli_output", help="Output directory")

    args = parser.parse_args()

    tts = TTSManager(output_dir=args.output)
    files = tts.generate_speech(args.text, args.voice)
    print(f"Generated {len(files)} audio files")
