"""進捗表示UIコンポーネント"""

import customtkinter as ctk


class ProgressView(ctk.CTkFrame):
    """処理進捗を表示するコンポーネント"""

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self._setup_ui()

    def _setup_ui(self):
        """UIを構築"""
        # 進捗メッセージ
        self.status_label = ctk.CTkLabel(self, text="待機中")
        self.status_label.pack(pady=(0, 5))

        # プログレスバー
        self.progress_bar = ctk.CTkProgressBar(self, width=400)
        self.progress_bar.pack(pady=(0, 5))
        self.progress_bar.set(0)

    def set_status(self, message: str):
        """ステータスメッセージを更新"""
        self.status_label.configure(text=message)
        self.update_idletasks()

    def set_progress(self, value: float):
        """プログレスバーを更新 (0.0 ~ 1.0)"""
        self.progress_bar.set(value)
        self.update_idletasks()

    def set_indeterminate(self, enabled: bool):
        """不確定モード（処理時間不明時）"""
        if enabled:
            self.progress_bar.configure(mode="indeterminate")
            self.progress_bar.start()
        else:
            self.progress_bar.stop()
            self.progress_bar.configure(mode="determinate")
            self.progress_bar.set(0)

    def reset(self):
        """初期状態にリセット"""
        self.set_status("待機中")
        self.set_progress(0)
