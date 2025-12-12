"""Whisperを使用した音声認識モジュール"""

import os
import tempfile
from dataclasses import dataclass
from typing import Callable

import whisper
import ffmpeg


@dataclass
class Segment:
    """字幕セグメント"""
    index: int
    start: float
    end: float
    text: str


class Transcriber:
    """MP4ファイルから音声を認識してセグメントを生成"""

    def __init__(self, model_name: str = "small"):
        """
        Args:
            model_name: Whisperモデル名 (tiny, base, small, medium, large)
        """
        self.model_name = model_name
        self.model = None

    def load_model(self, progress_callback: Callable[[str], None] | None = None):
        """モデルを読み込む"""
        if progress_callback:
            progress_callback(f"モデル '{self.model_name}' を読み込み中...")
        self.model = whisper.load_model(self.model_name)
        if progress_callback:
            progress_callback("モデルの読み込み完了")

    def extract_audio(self, video_path: str, progress_callback: Callable[[str], None] | None = None) -> str:
        """MP4から音声を抽出してWAVファイルとして保存"""
        if progress_callback:
            progress_callback("音声を抽出中...")

        # 一時ファイルを作成
        temp_audio = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
        temp_audio_path = temp_audio.name
        temp_audio.close()

        try:
            # ffmpegで音声抽出
            (
                ffmpeg
                .input(video_path)
                .output(temp_audio_path, acodec="pcm_s16le", ar="16000", ac=1)
                .overwrite_output()
                .run(quiet=True)
            )
        except ffmpeg.Error as e:
            raise RuntimeError(f"音声抽出に失敗しました: {e}")

        if progress_callback:
            progress_callback("音声抽出完了")

        return temp_audio_path

    def transcribe(
        self,
        video_path: str,
        progress_callback: Callable[[str], None] | None = None
    ) -> list[Segment]:
        """動画ファイルを文字起こし"""
        if self.model is None:
            self.load_model(progress_callback)

        # 音声抽出
        audio_path = self.extract_audio(video_path, progress_callback)

        try:
            if progress_callback:
                progress_callback("文字起こし中...")

            # Whisperで文字起こし
            result = self.model.transcribe(
                audio_path,
                language="ja",
                verbose=False
            )

            if progress_callback:
                progress_callback("文字起こし完了")

            # セグメントを生成
            segments = []
            for i, seg in enumerate(result["segments"], start=1):
                segments.append(Segment(
                    index=i,
                    start=seg["start"],
                    end=seg["end"],
                    text=seg["text"].strip()
                ))

            return segments

        finally:
            # 一時ファイルを削除
            if os.path.exists(audio_path):
                os.unlink(audio_path)
