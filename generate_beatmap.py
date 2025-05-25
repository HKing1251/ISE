import librosa
import json

def extract_beats(mp3_path, output_json):
    y, sr = librosa.load(mp3_path)
    tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr)
    beat_times = librosa.frames_to_time(beat_frames, sr=sr)

    with open(output_json, 'w') as f:
        json.dump(beat_times.tolist(), f)

    print(f"Saved {len(beat_times)} beats to {output_json}")

extract_beats("music/Tetris.mp3", "beatmap.json")
extract_beats("music/eighties.mp3", "beatmap1.json")
extract_beats("music/8-bit-music.mp3", "beatmap2.json")
extract_beats("music/Checker.mp3", "beatmap3.json")
extract_beats("music/Heartache.mp3", "beatmap4.json")