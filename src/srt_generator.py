"""SRTファイル生成モジュール"""

from src.transcriber import Segment


def format_timestamp(seconds: float) -> str:
    """秒数をSRT形式のタイムスタンプに変換

    Args:
        seconds: 秒数

    Returns:
        "HH:MM:SS,mmm" 形式の文字列
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds % 1) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


def segments_to_srt(segments: list[Segment]) -> str:
    """セグメントリストをSRT形式の文字列に変換

    Args:
        segments: 字幕セグメントのリスト

    Returns:
        SRT形式の文字列
    """
    lines = []
    for seg in segments:
        lines.append(str(seg.index))
        lines.append(f"{format_timestamp(seg.start)} --> {format_timestamp(seg.end)}")
        lines.append(seg.text)
        lines.append("")  # 空行で区切る

    return "\n".join(lines)


def save_srt(segments: list[Segment], output_path: str) -> None:
    """セグメントをSRTファイルとして保存

    Args:
        segments: 字幕セグメントのリスト
        output_path: 出力ファイルパス
    """
    srt_content = segments_to_srt(segments)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(srt_content)
