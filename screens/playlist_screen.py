"""
Playlist Screen
플레이리스트 목록 화면
"""

from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QListWidget,
    QLabel,
    QListWidgetItem,
    QFrame,
    QScrollArea,
    QSizePolicy,
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
import config
from ui_styles import BASE_STYLESHEET


class PlaylistLoadWorker(QThread):
    """플레이리스트 로딩 Worker Thread"""

    finished = pyqtSignal(list)

    def __init__(self, spotify_manager):
        super().__init__()
        self.spotify = spotify_manager

    def run(self):
        playlists = self.spotify.get_user_playlists()
        self.finished.emit(playlists)


class PlaylistScreen(QWidget):
    """플레이리스트 화면 클래스"""

    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.playlists = []
        self.worker = None
        self.buttons = []
        self.setup_ui()

    def setup_ui(self):
        """UI 구성"""
        self.setObjectName("playlistScreen")

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        container = QWidget()
        self.scroll_area.setWidget(container)

        self.content_layout = QVBoxLayout(container)
        self.content_layout.setSpacing(20)
        self.content_layout.setContentsMargins(0, 0, 0, 0)

        header = QHBoxLayout()
        header.setSpacing(14)

        back_btn = QPushButton("← Back")
        back_btn.setProperty("variant", "ghost")
        back_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        back_btn.clicked.connect(self.parent.go_back)
        header.addWidget(back_btn)
        self.buttons.append(back_btn)
        self.back_btn = back_btn

        title = QLabel("My Playlists")
        title.setObjectName("playlistTitle")
        title.setProperty("role", "title")
        header.addWidget(title)

        header.addStretch()

        refresh_btn = QPushButton("Refresh")
        refresh_btn.setProperty("variant", "surface")
        refresh_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        refresh_btn.clicked.connect(self.load_playlists)
        header.addWidget(refresh_btn)
        self.buttons.append(refresh_btn)
        self.refresh_btn = refresh_btn

        self.content_layout.addLayout(header)

        self.card = QFrame()
        self.card.setObjectName("card")
        self.card.setFrameShape(QFrame.Shape.NoFrame)

        self.card_layout = QVBoxLayout(self.card)
        self.card_layout.setContentsMargins(24, 24, 24, 24)
        self.card_layout.setSpacing(16)

        self.info_label = QLabel("Loading playlists…")
        self.info_label.setObjectName("infoLabel")
        self.info_label.setProperty("role", "caption")
        self.card_layout.addWidget(self.info_label)

        self.playlists_list = QListWidget()
        self.playlists_list.setObjectName("playlistsList")
        self.playlists_list.setMinimumHeight(220)
        self.playlists_list.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.playlists_list.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.playlists_list.itemClicked.connect(self.open_playlist)
        self.card_layout.addWidget(self.playlists_list)

        self.content_layout.addWidget(self.card, alignment=Qt.AlignmentFlag.AlignHCenter)
        self.content_layout.addStretch(1)

        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.addWidget(self.scroll_area)

        self.apply_styles()
        self.adjust_layout()

    def load_playlists(self):
        """플레이리스트 로드"""
        self.info_label.setText("Loading playlists…")
        self.info_label.setStyleSheet(f"color: {config.COLOR_PRIMARY};")
        self.playlists_list.clear()

        self.worker = PlaylistLoadWorker(self.parent.spotify)
        self.worker.finished.connect(self.display_playlists)
        self.worker.start()

    def display_playlists(self, playlists):
        """플레이리스트 표시"""
        self.playlists = playlists or []
        self.playlists_list.clear()

        if not self.playlists:
            self.info_label.setText("No playlists found")
            self.info_label.setStyleSheet(f"color: {config.COLOR_TEXT_SECONDARY};")
            self.playlists_list.addItem("You don't have any playlists yet.")
            return

        self.info_label.setText(f"Found {len(self.playlists)} playlists")
        self.info_label.setStyleSheet(f"color: {config.COLOR_TEXT_SECONDARY};")

        current_user = None
        try:
            current_user = self.parent.spotify.sp.current_user()
        except Exception:
            pass

        current_user_id = current_user.get("id") if current_user else None

        for playlist in self.playlists:
            if not playlist:
                continue

            name = playlist.get("name", "Unknown Playlist")
            owner = playlist.get("owner", {}).get("display_name", "Unknown")
            track_count = playlist.get("tracks", {}).get("total", 0)

            owner_id = playlist.get("owner", {}).get("id")
            owner_text = "You" if current_user_id and owner_id == current_user_id else owner

            item_text = f"📝 {name}\n   👤 {owner_text}  ·  🎵 {track_count} tracks"

            item = QListWidgetItem(item_text)
            item.setData(Qt.ItemDataRole.UserRole, playlist)
            self.playlists_list.addItem(item)

    def open_playlist(self, item):
        """플레이리스트 열기"""
        playlist = item.data(Qt.ItemDataRole.UserRole)

        if playlist:
            self.parent.detail_screen.load_playlist(playlist)
            self.parent.navigate_to(7)

    def apply_styles(self):
        """스타일 시트 적용"""
        self.setStyleSheet(
            BASE_STYLESHEET
            + f"""
            QWidget#playlistScreen {{
                background: {config.GRADIENT_NIGHTFALL};
            }}

            QWidget#playlistScreen QLabel#playlistTitle {{
                font-size: 210%;
                font-weight: 800;
                color: {config.COLOR_TEXT};
            }}

            QWidget#playlistScreen QListWidget#playlistsList {{
                font-size: 105%;
                line-height: 1.5em;
            }}

            QWidget#playlistScreen QListWidget#playlistsList::item {{
                padding: 14px 12px;
                border-radius: 12px;
                margin: 2px 0;
                border: 1px solid transparent;
            }}

            QWidget#playlistScreen QListWidget#playlistsList::item:selected {{
                border-color: rgba(102, 255, 224, 0.35);
                background-color: rgba(102, 255, 224, 0.18);
            }}

            QWidget#playlistScreen QListWidget#playlistsList::item:hover {{
                background-color: rgba(255, 255, 255, 0.08);
            }}
            """
        )

    def adjust_layout(self):
        """화면 크기에 따라 여백/카드 폭 조정"""
        width = max(320, self.width())
        margin_side = max(10, int(width * 0.045))
        margin_top = max(6, int(width * 0.015))
        margin_bottom = max(10, int(width * 0.04))
        self.content_layout.setContentsMargins(margin_side, margin_top, margin_side, margin_bottom)

        if self.card:
            max_width = int(width * 0.94)
            self.card.setMaximumWidth(max_width)
            self.card.setMinimumWidth(min(max_width, width - (margin_side * 2)))

        button_height = max(40, int(width * 0.085))
        for btn in self.buttons:
            btn.setMinimumHeight(button_height)

        if hasattr(self, "back_btn"):
            self.back_btn.setMinimumWidth(max(90, int(width * 0.22)))
        if hasattr(self, "refresh_btn"):
            self.refresh_btn.setMinimumWidth(max(90, int(width * 0.22)))

    def resizeEvent(self, event):
        """창 크기 변경 대응"""
        super().resizeEvent(event)
        self.adjust_layout()

    def showEvent(self, event):
        """화면 표시시 자동 로드"""
        super().showEvent(event)
        if not self.playlists:
            self.load_playlists()
