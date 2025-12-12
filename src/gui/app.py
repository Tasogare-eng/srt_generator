"""メインアプリケーションウィンドウ"""

import os
import threading
from tkinter import filedialog, messagebox

import customtkinter as ctk

from src.transcriber import Transcriber
from src.srt_generator import save_srt
from src.gui.file_selector import FileSelector
from src.gui.progress_view import ProgressView
from src.gui.editor import SubtitleEditor


class App(ctk.CTk):
    """メインアプリケーション"""

    def __init__(self):
        super().__init__()

        self.title("MP4 → SRT 字幕生成ツール")
        self.geometry("800x700")

        # 外観設定
        ctk.set_appearance_mode("system")
        ctk.set_default_color_theme("blue")

        self.transcriber = Transcriber()
        self.is_processing = False

        self._setup_ui()

    def _setup_ui(self):
        """UIを構築"""
        # メインコンテナ
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # ファイル選択セクション
        self.file_selector = FileSelector(
            main_frame,
            on_file_selected=self._on_file_selected
        )
        self.file_selector.pack(fill="x", pady=(0, 15))

        # モデル選択
        model_frame = ctk.CTkFrame(main_frame)
        model_frame.pack(fill="x", pady=(0, 15))

        ctk.CTkLabel(model_frame, text="モデル:").pack(side="left", padx=(0, 10))
        self.model_var = ctk.StringVar(value="small")
        self.model_menu = ctk.CTkOptionMenu(
            model_frame,
            values=["tiny", "base", "small", "medium", "large"],
            variable=self.model_var
        )
        self.model_menu.pack(side="left")

        # 生成ボタン
        self.generate_button = ctk.CTkButton(
            main_frame,
            text="字幕を生成",
            command=self._start_transcription,
            height=40
        )
        self.generate_button.pack(fill="x", pady=(0, 15))

        # 進捗表示
        self.progress_view = ProgressView(main_frame)
        self.progress_view.pack(fill="x", pady=(0, 15))

        # 字幕編集
        editor_label = ctk.CTkLabel(main_frame, text="字幕編集", font=("", 14, "bold"))
        editor_label.pack(anchor="w", pady=(0, 5))

        self.editor = SubtitleEditor(main_frame)
        self.editor.pack(fill="both", expand=True, pady=(0, 15))

        # 保存ボタン
        self.save_button = ctk.CTkButton(
            main_frame,
            text="SRTを保存",
            command=self._save_srt,
            height=40,
            state="disabled"
        )
        self.save_button.pack(fill="x")

    def _on_file_selected(self, file_path: str):
        """ファイル選択時の処理"""
        self.progress_view.reset()
        self.editor.set_segments([])
        self.save_button.configure(state="disabled")

    def _start_transcription(self):
        """文字起こしを開始"""
        file_path = self.file_selector.get_file_path()

        if not file_path:
            messagebox.showwarning("警告", "MP4ファイルを選択してください")
            return

        if not os.path.exists(file_path):
            messagebox.showerror("エラー", "ファイルが見つかりません")
            return

        if self.is_processing:
            return

        self.is_processing = True
        self.generate_button.configure(state="disabled")
        self.save_button.configure(state="disabled")

        # モデル名を更新
        self.transcriber.model_name = self.model_var.get()
        self.transcriber.model = None  # モデルを再読み込み

        # 別スレッドで処理
        thread = threading.Thread(
            target=self._transcribe_thread,
            args=(file_path,)
        )
        thread.start()

    def _transcribe_thread(self, file_path: str):
        """文字起こし処理（別スレッド）"""
        try:
            self.progress_view.set_indeterminate(True)

            def progress_callback(message: str):
                self.after(0, lambda: self.progress_view.set_status(message))

            segments = self.transcriber.transcribe(file_path, progress_callback)

            self.after(0, lambda: self._on_transcription_complete(segments))

        except Exception as e:
            self.after(0, lambda: self._on_transcription_error(str(e)))

    def _on_transcription_complete(self, segments):
        """文字起こし完了時の処理"""
        self.progress_view.set_indeterminate(False)
        self.progress_view.set_status(f"完了: {len(segments)}個のセグメント")
        self.progress_view.set_progress(1.0)

        self.editor.set_segments(segments)
        self.save_button.configure(state="normal")
        self.generate_button.configure(state="normal")
        self.is_processing = False

    def _on_transcription_error(self, error_message: str):
        """文字起こしエラー時の処理"""
        self.progress_view.set_indeterminate(False)
        self.progress_view.set_status("エラーが発生しました")

        messagebox.showerror("エラー", f"文字起こしに失敗しました:\n{error_message}")

        self.generate_button.configure(state="normal")
        self.is_processing = False

    def _save_srt(self):
        """SRTファイルを保存"""
        segments = self.editor.get_segments()

        if not segments:
            messagebox.showwarning("警告", "保存する字幕がありません")
            return

        # デフォルトのファイル名を生成
        input_path = self.file_selector.get_file_path()
        default_name = os.path.splitext(os.path.basename(input_path))[0] + ".srt"

        file_path = filedialog.asksaveasfilename(
            title="SRTファイルを保存",
            defaultextension=".srt",
            initialfile=default_name,
            filetypes=[("SRTファイル", "*.srt")]
        )

        if file_path:
            try:
                save_srt(segments, file_path)
                messagebox.showinfo("完了", f"SRTファイルを保存しました:\n{file_path}")
            except Exception as e:
                messagebox.showerror("エラー", f"保存に失敗しました:\n{e}")
