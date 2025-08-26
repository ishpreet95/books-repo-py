# 📚 Books TTS Repository (Python/Local Models)

A Python-based book repository manager that converts EPUBs to structured Markdown and generates high-quality TTS audio using **local AI models** like Kokoro, Coqui, and others.

## 🎯 Focus: Local AI TTS Models Only

This repository specializes in **offline/local TTS models** available as Python packages. For API-based providers (Google, OpenAI, ElevenLabs), use the separate TypeScript repository.

## ✨ Key Features

- **📖 EPUB to Markdown**: Convert EPUBs to clean, structured Markdown
- **🎵 Per-Chapter Audio**: Generate TTS audio for individual chapters on-demand
- **🤖 Local AI Models**: Kokoro, Coqui TTS, and other Python-based models
- **📁 Organized Structure**: Clean, hierarchical organization with metadata
- **⚡ Efficient Processing**: Generate audio only for chapters you need
- **🔒 Privacy**: All processing happens locally, no API calls
- **💰 Cost-Free**: No usage fees or rate limits

## 🏗️ Book Structure

Each processed book follows this organized structure:

```
books/[book-slug]/
├── metadata.yml              # Book metadata (title, author, etc.)
├── toc.yml                  # Table of contents
├── source/                  # Original files
│   └── book.epub           # Original EPUB
├── content/                 # Processed content
│   ├── chapters/           # Individual chapter markdown files
│   │   ├── 01-chapter-title.md
│   │   └── ...
│   ├── text/               # Plain text versions
│   └── full-text.md        # Complete book in single file
├── audio/                   # Generated audio files (model-specific)
│   ├── kokoro/             # Kokoro TTS audio
│   │   └── chapters/       # Individual chapter audio
│   │       ├── 01-chapter-title.wav
│   │       └── ...
│   └── coqui/              # Coqui TTS audio
│       └── chapters/       # Individual chapter audio
│           ├── 01-chapter-title.wav
│           └── ...
└── processing/             # Processing logs and temp files
    ├── logs/
    └── temp/
```

## 🚀 Quick Start

### 1. Installation

```bash
# Install pipenv if you don't have it
pip install pipenv

# Install dependencies
pipenv install
pipenv install --dev

# Activate virtual environment
pipenv shell
```

### 2. Convert a Book

```bash
# Convert EPUB to structured Markdown
python book_processor.py convert path/to/book.epub "Book Title"

# Example
python book_processor.py convert ./source/mythos.epub "Mythos"
```

### 2. Generate Audio Per Chapter

```bash
# List all chapters
python book_processor.py list-chapters books/mythos

# Generate audio for specific chapters
python book_processor.py generate-audio books/mythos 10

# Generate for multiple chapters with specific voice
python book_processor.py generate-audio books/mythos 1 5 10 --voice af_sarah

# Try different Kokoro voices
python book_processor.py generate-audio books/mythos 1 --voice af_bella
```

### 3. Voice Testing & Comparison

```bash
# Create sample text files for voice testing
python voice_playground.py create-sample

# Test all voices with your text file
python voice_playground.py compare your_text.txt --all

# Test specific voices only
python voice_playground.py compare your_text.txt -v af_bella -v af_sarah

# List available voices and descriptions
python voice_playground.py list-voices

# Use the provided samples
python voice_playground.py compare voice_samples/medium_sample.txt --all

# Test extreme challenges
python voice_playground.py compare voice_samples/long_sample.txt -v af_bella
```

### 🧠 Advanced Testing Challenges

Our voice samples are designed to push TTS systems to their limits:

**🔥 Short Sample**: Rapid-fire phonetic challenges
- Homographs: `lead/lead`, `bass/bass`, `tear/tear`
- Foreign names: `Wojciech Szczęsny`, `Reykjavik`
- Medical terminology: `pneumonoultramicroscopicsilicovolcanoconiosis`
- Math symbols, currencies, time formats

**⚔️ Medium Sample**: "The Detective's Dilemma"  
- Garden path sentences (syntactically confusing)
- Chemical formulas: `C₆H₁₂O₆ + 6O₂ → 6CO₂ + 6H₂O`
- Multiple character voices with different emotions
- Complex punctuation and nested quotations

**🚀 Long Sample**: "The Quantum Heist" 
- Quantum physics equations: `iℏ ∂ψ/∂t = Ĥψ`
- Multiple languages (Russian, Shakespeare)
- Character differentiation (scientist, agent, hacker, janitor)
- Technical jargon mixed with emotional narrative

## 📋 Available Commands

| Command            | Description                    | Example                                                       |
| ------------------ | ------------------------------ | ------------------------------------------------------------- |
| `convert`          | Convert EPUB to Markdown       | `python book_processor.py convert book.epub "Title"`          |
| `list-chapters`    | List all chapters in a book    | `python book_processor.py list-chapters books/mythos`         |
| `generate-audio`   | Generate audio for chapters    | `python book_processor.py generate-audio books/mythos 1 5 10` |
| `compare` (voices) | Test and compare voice quality | `python voice_playground.py compare text.txt --all`           |
| `create-sample`    | Create voice test samples      | `python voice_playground.py create-sample`                    |
| `list-voices`      | List available voices          | `python voice_playground.py list-voices`                      |

## 🎵 Local TTS Models

### 🥇 Kokoro TTS (Default)

**Why Kokoro?**

- 🎯 **High Quality**: 82M parameter model with natural voices
- ⚡ **Fast**: Optimized for CPU and GPU
- 🔒 **Private**: Completely offline
- 💰 **Free**: No usage costs
- 🎭 **Multiple Voices**: Different character voices available

**Available Voices:**

- **af_heart** - Natural, clear narrator voice (default)
- **af_sarah** - Expressive female voice
- **af_bella** - Warm storytelling voice

### 🎤 Future Models

Ready to add support for:

- **Coqui TTS** - Multi-speaker, multi-language
- **Bark** - Realistic speech with emotions
- **Tortoise TTS** - Ultra-realistic but slower
- **XTTS** - Voice cloning capabilities

## 📖 Usage Examples

### Basic Workflow

```bash
# 1. Convert book
python book_processor.py convert ./source/mythos.epub "Mythos"

# 2. List chapters
python book_processor.py list-chapters books/mythos

# 3. Generate audio for interesting chapters
python book_processor.py generate-audio books/mythos 10    # "Out of Chaos"
python book_processor.py generate-audio books/mythos 17    # "Prometheus"
python book_processor.py generate-audio books/mythos 29    # "Sisyphus"

# 4. Listen to generated audio files
# Files saved as: books/mythos/audio/kokoro/chapters/XX-chapter-name.wav
```

### Multiple Chapters & Voices

```bash
# Generate multiple chapters at once
python book_processor.py generate-audio books/mythos 1 10 20 30

# Try different voices
python book_processor.py generate-audio books/mythos 5 --voice af_sarah
python book_processor.py generate-audio books/mythos 10 --voice af_bella
```

### Interactive Development

```bash
# Use TTS utilities directly
python -c "
from tts_utils import TTSManager
tts = TTSManager()
tts.generate_speech('Hello world!', voice='af_heart')
"
```

## 🔧 Advanced Features

### Custom Voices per Character

Future feature: Configure different voices for different characters in dialogue.

### Batch Processing

Process multiple books:

```bash
# Process all EPUBs in a directory
for epub in ./source-books/*.epub; do
  python book_processor.py convert "$epub" "$(basename "$epub" .epub)"
done
```

## 🆚 Compared to API-Based Solutions

| Feature     | This Repo (Local Models) | API-Based (TS Repo)    |
| ----------- | ------------------------ | ---------------------- |
| **Cost**    | ✅ Free                  | ❌ Pay per use         |
| **Privacy** | ✅ Fully offline         | ❌ Data sent to APIs   |
| **Speed**   | ⚡ No network delay      | 🐌 Network dependent   |
| **Limits**  | ✅ None                  | ❌ Rate limits         |
| **Quality** | 🎯 Very good             | 🎯 Excellent           |
| **Voices**  | 🎭 Growing selection     | 🎭 Extensive selection |

## 🐛 Troubleshooting

### Common Issues

**"Module not found" errors**

- Make sure you're in the virtual environment: `pipenv shell`
- Install dependencies: `pipenv install`

**EPUB conversion fails**

- Check the EPUB file is valid
- Try with a different EPUB file first

**Audio generation slow**

- Kokoro downloads models on first use (~300MB)
- GPU acceleration available if PyTorch detects CUDA

## 🎯 Why Local Models?

This repository is optimized for:

- **🔒 Privacy**: Your books never leave your machine
- **💰 Cost**: No API fees or usage limits
- **⚡ Speed**: No network latency
- **🤖 AI Development**: Perfect for training data generation
- **📚 Large Collections**: Process hundreds of books without cost
- **🎨 Experimentation**: Try different models and voices freely

## 🚀 Next Steps

1. **Convert your first book**: `python book_processor.py convert book.epub "Title"`
2. **Explore chapters**: `python book_processor.py list-chapters books/book-slug`
3. **Generate sample audio**: `python book_processor.py generate-audio books/book-slug 1`
4. **Try different voices**: Experiment with `af_heart`, `af_sarah`, `af_bella`
5. **Scale up**: Process entire books or collections

---

**Perfect for creating audiobooks with complete privacy and zero ongoing costs! 📚🎵**

_Local AI models + structured book processing = unlimited audiobook generation_
