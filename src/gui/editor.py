"""タイムスタンプ編集UIコンポーネント"""

import customtkinter as ctk
from tkinter import ttk
from typing import Callable

from src.transcriber import Segment


class SubtitleEditor(ctk.CTkFrame):
    """字幕編集コンポーネント"""

    def __init__(
        self,
        master,
        on_segments_changed: Callable[[], None] | None = None,
        **kwargs
    ):
        super().__init__(master, **kwargs)

        self.segments: list[Segment] = []
        self.on_segments_changed = on_segments_changed
        self.selected_index: int | None = None

        self._setup_ui()

    def _setup_ui(self):
        """UIを構築"""
        # 字幕リスト（上部）
        list_frame = ctk.CTkFrame(self)
        list_frame.pack(fill="both", expand=True, pady=(0, 10))

        # Treeview（リスト表示）
        columns = ("index", "start", "end", "text")
        self.tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=10)

        self.tree.heading("index", text="#")
        self.tree.heading("start", text="開始")
        self.tree.heading("end", text="終了")
        self.tree.heading("text", text="テキスト")

        self.tree.column("index", width=40, anchor="center")
        self.tree.column("start", width=100, anchor="center")
        self.tree.column("end", width=100, anchor="center")
        self.tree.column("text", width=400)

        # スクロールバー
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.tree.bind("<<TreeviewSelect>>", self._on_select)

        # 編集パネル（下部）
        edit_frame = ctk.CTkFrame(self)
        edit_frame.pack(fill="x", pady=(0, 10))

        # 開始時間
        ctk.CTkLabel(edit_frame, text="開始:").grid(row=0, column=0, padx=5, pady=5)
        self.start_entry = ctk.CTkEntry(edit_frame, width=120)
        self.start_entry.grid(row=0, column=1, padx=5, pady=5)

        # 終了時間
        ctk.CTkLabel(edit_frame, text="終了:").grid(row=0, column=2, padx=5, pady=5)
        self.end_entry = ctk.CTkEntry(edit_frame, width=120)
        self.end_entry.grid(row=0, column=3, padx=5, pady=5)

        # テキスト
        ctk.CTkLabel(edit_frame, text="テキスト:").grid(row=1, column=0, padx=5, pady=5)
        self.text_entry = ctk.CTkEntry(edit_frame, width=400)
        self.text_entry.grid(row=1, column=1, columnspan=3, padx=5, pady=5, sticky="ew")

        # 更新ボタン
        self.update_button = ctk.CTkButton(
            edit_frame,
            text="更新",
            width=80,
            command=self._update_segment
        )
        self.update_button.grid(row=0, column=4, rowspan=2, padx=10, pady=5)

        edit_frame.columnconfigure(3, weight=1)

    def set_segments(self, segments: list[Segment]):
        """セグメントをセット"""
        self.segments = segments
        self._refresh_list()

    def get_segments(self) -> list[Segment]:
        """現在のセグメントを取得"""
        return self.segments

    def _refresh_list(self):
        """リストを更新"""
        # 既存の項目をクリア
        for item in self.tree.get_children():
            self.tree.delete(item)

        # セグメントを追加
        for seg in self.segments:
            self.tree.insert("", "end", values=(
                seg.index,
                self._format_time(seg.start),
                self._format_time(seg.end),
                seg.text
            ))

    def _format_time(self, seconds: float) -> str:
        """秒数を時:分:秒.ミリ秒形式に変換"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = seconds % 60
        return f"{hours:02d}:{minutes:02d}:{secs:06.3f}"

    def _parse_time(self, time_str: str) -> float:
        """時:分:秒.ミリ秒形式を秒数に変換"""
        parts = time_str.split(":")
        if len(parts) != 3:
            raise ValueError(f"Invalid time format: {time_str}")
        hours = int(parts[0])
        minutes = int(parts[1])
        seconds = float(parts[2])
        return hours * 3600 + minutes * 60 + seconds

    def _on_select(self, event):
        """リスト選択時の処理"""
        selection = self.tree.selection()
        if not selection:
            return

        # 選択されたアイテムのインデックスを取得
        item = selection[0]
        values = self.tree.item(item, "values")
        self.selected_index = int(values[0]) - 1  # 0-indexed

        if 0 <= self.selected_index < len(self.segments):
            seg = self.segments[self.selected_index]
            self._set_edit_fields(seg)

    def _set_edit_fields(self, segment: Segment):
        """編集フィールドにセグメント情報をセット"""
        self.start_entry.delete(0, "end")
        self.start_entry.insert(0, self._format_time(segment.start))

        self.end_entry.delete(0, "end")
        self.end_entry.insert(0, self._format_time(segment.end))

        self.text_entry.delete(0, "end")
        self.text_entry.insert(0, segment.text)

    def _update_segment(self):
        """選択中のセグメントを更新"""
        if self.selected_index is None:
            return

        try:
            start = self._parse_time(self.start_entry.get())
            end = self._parse_time(self.end_entry.get())
            text = self.text_entry.get()

            self.segments[self.selected_index] = Segment(
                index=self.selected_index + 1,
                start=start,
                end=end,
                text=text
            )

            self._refresh_list()

            if self.on_segments_changed:
                self.on_segments_changed()

        except ValueError as e:
            # エラーハンドリング（時間フォーマットが不正な場合）
            print(f"Error updating segment: {e}")
