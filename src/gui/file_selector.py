"""ファイル選択UIコンポーネント"""

import customtkinter as ctk
from tkinter import filedialog
from typing import Callable


class FileSelector(ctk.CTkFrame):
    """MP4ファイル選択コンポーネント"""

    def __init__(
        self,
        master,
        on_file_selected: Callable[[str], None] | None = None,
        **kwargs
    ):
        super().__init__(master, **kwargs)

        self.on_file_selected = on_file_selected
        self.file_path = ""

        self._setup_ui()

    def _setup_ui(self):
        """UIを構築"""
        # ラベル
        self.label = ctk.CTkLabel(self, text="MP4ファイル:")
        self.label.pack(side="left", padx=(0, 10))

        # ファイルパス表示
        self.path_entry = ctk.CTkEntry(self, width=400, state="readonly")
        self.path_entry.pack(side="left", padx=(0, 10), fill="x", expand=True)

        # ファイル選択ボタン
        self.browse_button = ctk.CTkButton(
            self,
            text="参照",
            width=80,
            command=self._browse_file
        )
        self.browse_button.pack(side="right")

    def _browse_file(self):
        """ファイル選択ダイアログを開く"""
        file_path = filedialog.askopenfilename(
            title="MP4ファイルを選択",
            filetypes=[
                ("MP4ファイル", "*.mp4"),
                ("すべてのファイル", "*.*")
            ]
        )

        if file_path:
            self.file_path = file_path
            self.path_entry.configure(state="normal")
            self.path_entry.delete(0, "end")
            self.path_entry.insert(0, file_path)
            self.path_entry.configure(state="readonly")

            if self.on_file_selected:
                self.on_file_selected(file_path)

    def get_file_path(self) -> str:
        """選択されたファイルパスを取得"""
        return self.file_path
