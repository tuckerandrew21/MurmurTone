"""
Usage statistics tracking for MurmurTone.
Tracks transcriptions, characters, and estimated time saved.
"""
import json
import os
from datetime import datetime, date


# Time saving calculations
# Average typing speed: 40 WPM (200 chars/min)
# Average speech speed: 150 WPM (750 chars/min)
TYPING_CHARS_PER_MIN = 200
SPEECH_CHARS_PER_MIN = 750


def get_stats_path():
    """Get path to stats.json in user's AppData directory."""
    app_data = os.environ.get("APPDATA", os.path.expanduser("~"))
    config_dir = os.path.join(app_data, "MurmurTone")
    os.makedirs(config_dir, exist_ok=True)
    return os.path.join(config_dir, "stats.json")


def load_stats():
    """Load statistics from disk."""
    stats_path = get_stats_path()
    default_stats = {
        "total_transcriptions": 0,
        "total_characters": 0,
        "total_words": 0,
        "first_use_date": None,
        "daily_stats": {},  # {"2024-01-15": {"transcriptions": 5, "characters": 500}}
    }

    if os.path.exists(stats_path):
        try:
            with open(stats_path, "r") as f:
                saved = json.load(f)
                # Merge with defaults for any missing keys
                for key in default_stats:
                    if key not in saved:
                        saved[key] = default_stats[key]
                return saved
        except (json.JSONDecodeError, IOError):
            pass

    return default_stats


def save_stats(stats):
    """Save statistics to disk."""
    stats_path = get_stats_path()
    with open(stats_path, "w") as f:
        json.dump(stats, f, indent=2)


def record_transcription(text):
    """
    Record a transcription in statistics.

    Args:
        text: The transcribed text
    """
    if not text:
        return

    stats = load_stats()

    # Update totals
    char_count = len(text)
    word_count = len(text.split())

    stats["total_transcriptions"] += 1
    stats["total_characters"] += char_count
    stats["total_words"] += word_count

    # Set first use date if not set
    if not stats["first_use_date"]:
        stats["first_use_date"] = date.today().isoformat()

    # Update daily stats
    today = date.today().isoformat()
    if today not in stats["daily_stats"]:
        stats["daily_stats"][today] = {"transcriptions": 0, "characters": 0, "words": 0}

    stats["daily_stats"][today]["transcriptions"] += 1
    stats["daily_stats"][today]["characters"] += char_count
    stats["daily_stats"][today]["words"] += word_count

    save_stats(stats)


def calculate_time_saved(total_characters):
    """
    Calculate estimated time saved by using voice vs typing.

    Returns:
        Tuple of (minutes_saved, hours_saved)
    """
    if total_characters == 0:
        return 0, 0

    # Time it would take to type
    typing_minutes = total_characters / TYPING_CHARS_PER_MIN

    # Time it took to speak
    speaking_minutes = total_characters / SPEECH_CHARS_PER_MIN

    # Net time saved
    minutes_saved = typing_minutes - speaking_minutes
    hours_saved = minutes_saved / 60

    return minutes_saved, hours_saved


def get_stats_summary():
    """
    Get a formatted summary of usage statistics.

    Returns:
        Dict with formatted statistics
    """
    stats = load_stats()

    total_chars = stats["total_characters"]
    minutes_saved, hours_saved = calculate_time_saved(total_chars)

    # Calculate streak and usage patterns
    today = date.today().isoformat()
    today_stats = stats["daily_stats"].get(today, {"transcriptions": 0, "characters": 0})

    # Calculate days active
    days_active = len(stats["daily_stats"])

    # Calculate average per day
    avg_transcriptions = stats["total_transcriptions"] / max(days_active, 1)
    avg_characters = total_chars / max(days_active, 1)

    return {
        "total_transcriptions": stats["total_transcriptions"],
        "total_characters": total_chars,
        "total_words": stats["total_words"],
        "minutes_saved": round(minutes_saved, 1),
        "hours_saved": round(hours_saved, 2),
        "days_active": days_active,
        "first_use_date": stats["first_use_date"],
        "today_transcriptions": today_stats["transcriptions"],
        "today_characters": today_stats.get("characters", 0),
        "avg_transcriptions_per_day": round(avg_transcriptions, 1),
        "avg_characters_per_day": round(avg_characters, 0),
    }


def format_time_saved(minutes):
    """Format minutes saved as a human-readable string."""
    if minutes < 1:
        return "< 1 minute"
    elif minutes < 60:
        return f"{int(minutes)} minute{'s' if minutes != 1 else ''}"
    else:
        hours = minutes / 60
        if hours < 24:
            return f"{hours:.1f} hour{'s' if hours != 1 else ''}"
        else:
            days = hours / 24
            return f"{days:.1f} day{'s' if days != 1 else ''}"


def reset_stats():
    """Reset all statistics to zero."""
    stats = {
        "total_transcriptions": 0,
        "total_characters": 0,
        "total_words": 0,
        "first_use_date": None,
        "daily_stats": {},
    }
    save_stats(stats)
