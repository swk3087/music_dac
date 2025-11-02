"""
Album Screen
앨범 목록 화면
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
from ui_styles import (
    BASE_STYLESHEET,
    apply_font_scaling,
    compute_responsive_scale,
    scale_padding,
)


class AlbumLoadWorker(QThread):
    """앨범 로딩 Worker Thread"""

    finished = pyqtSignal(list)

    def __init__(self, spotify_manager):
        super().__init__()
        self.spotify = spotify_manager

    def run(self):
        albums = self.spotify.get_saved_albums()
        self.finished.emit(albums)


class AlbumScreen(QWidget):
    """앨범 화면 클래스"""

    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.albums = []
        self.worker = None
        self.buttons = []
        self.setup_ui()

    def setup_ui(self):
        """UI 구성"""
        self.setObjectName("albumScreen")

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

        title = QLabel("Saved Albums")
        title.setObjectName("albumTitle")
        title.setProperty("role", "title")
        header.addWidget(title)
        self.title_label = title

        header.addStretch()

        refresh_btn = QPushButton("Refresh")
        refresh_btn.setProperty("variant", "surface")
        refresh_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        refresh_btn.clicked.connect(self.load_albums)
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

        self.info_label = QLabel("Loading albums…")
        self.info_label.setObjectName("infoLabel")
        self.info_label.setProperty("role", "caption")
        self.card_layout.addWidget(self.info_label)

        self.albums_list = QListWidget()
        self.albums_list.setObjectName("albumsList")
        self.albums_list.setMinimumHeight(220)
        self.albums_list.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.albums_list.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.albums_list.itemClicked.connect(self.open_album)
        self.card_layout.addWidget(self.albums_list)

        self.content_layout.addWidget(self.card, alignment=Qt.AlignmentFlag.AlignHCenter)
        self.content_layout.addStretch(1)

        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.addWidget(self.scroll_area)

        self.setup_styles()
        self.adjust_layout()

    def load_albums(self):
        """앨범 로드"""
        self.info_label.setText("Loading albums…")
        self.info_label.setStyleSheet(f"color: {config.COLOR_PRIMARY};")
        self.albums_list.clear()

        self.worker = AlbumLoadWorker(self.parent.spotify)
        self.worker.finished.connect(self.display_albums)
        self.worker.start()

    def display_albums(self, albums):
        """앨범 표시"""
        self.albums = albums or []
        self.albums_list.clear()

        if not self.albums:
            self.info_label.setText("No saved albums found")
            self.info_label.setStyleSheet(f"color: {config.COLOR_TEXT_SECONDARY};")
            self.albums_list.addItem("You haven't saved any albums yet.")
            return

        self.info_label.setText(f"Found {len(self.albums)} saved albums")
        self.info_label.setStyleSheet(f"color: {config.COLOR_TEXT_SECONDARY};")

        for item in self.albums:
            if not item:
                continue

            album = item.get("album", {})
            name = album.get("name", "Unknown Album")
            artists = album.get("artists", [])
            artist_names = ", ".join([a.get("name", "Unknown") for a in artists]) if artists else "Unknown"
            track_count = album.get("total_tracks", 0)
            release_date = album.get("release_date", "Unknown")[:4]

            item_text = (
                f"💿 {name}\n   👤 {artist_names}  ·  🎵 {track_count} tracks  ·  📅 {release_date}"
            )

            list_item = QListWidgetItem(item_text)
            list_item.setData(Qt.ItemDataRole.UserRole, album)
            self.albums_list.addItem(list_item)

    def open_album(self, item):
        """앨범 열기"""
        album = item.data(Qt.ItemDataRole.UserRole)

        if album:
            self.parent.detail_screen.load_album(album)
            self.parent.navigate_to(7)

    def setup_styles(self):
        """기본 스타일 템플릿 저장"""
        self._base_style = (
            BASE_STYLESHEET
            + f"""
            QWidget#albumScreen {{
                background: {config.GRADIENT_NIGHTFALL};
            }}

            QWidget#albumScreen QLabel#albumTitle {{
                font-weight: 800;
                color: {config.COLOR_TEXT};
            }}

            QWidget#albumScreen QListWidget#albumsList {{
                line-height: 1.5em;
            }}

            QWidget#albumScreen QListWidget#albumsList::item {{
                padding: 14px 12px;
                border-radius: 12px;
                margin: 2px 0;
                border: 1px solid transparent;
            }}

            QWidget#albumScreen QListWidget#albumsList::item:selected {{
                border-color: rgba(102, 255, 224, 0.35);
                background-color: rgba(102, 255, 224, 0.18);
            }}

            QWidget#albumScreen QListWidget#albumsList::item:hover {{
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

        current_height = self.height()
        height = current_height if current_height > 0 else config.SCREEN_HEIGHT
        self.update_dynamic_style(width, height)

    def update_dynamic_style(self, width, height):
        """화면 크기에 맞춰 글꼴 및 패딩 조정"""
        scale = compute_responsive_scale(width, height)

        scaling_config = []
        if hasattr(self, "title_label"):
            scaling_config.append(("title", self.title_label, 20, 12))
        if hasattr(self, "info_label"):
            scaling_config.append(("caption", self.info_label, 11, 9))
        if hasattr(self, "albums_list"):
            scaling_config.append(("list", self.albums_list, 11, 9))

        scaling_config.extend(("button", btn, 12, 9) for btn in self.buttons)

        applied_sizes = apply_font_scaling(
            [(item[1], item[2], item[3]) for item in scaling_config],
            scale,
        )

        applied_map = {}
        for config_item, size in zip(scaling_config, applied_sizes):
            role = config_item[0]
            if size is None:
                continue
            applied_map.setdefault(role, []).append(size)

        title_pt = applied_map.get("title", [16])[0]
        caption_pt = applied_map.get("caption", [10])[0]
        list_pt = applied_map.get("list", [11])[0]
        button_pt = applied_map.get("button", [11])[0]

        button_vpad, button_hpad = scale_padding(
            base_vertical=14,
            base_horizontal=20,
            scale=scale,
            min_vertical=6,
            min_horizontal=10,
        )

        item_vpad, item_hpad = scale_padding(
            base_vertical=14,
            base_horizontal=12,
            scale=scale,
            min_vertical=8,
            min_horizontal=8,
        )

        dynamic_style = f"""
            QWidget#albumScreen QLabel#albumTitle {{
                font-size: {title_pt}pt;
            }}

            QWidget#albumScreen QLabel#infoLabel {{
                font-size: {caption_pt}pt;
            }}

            QWidget#albumScreen QPushButton {{
                font-size: {button_pt}pt;
                padding: {button_vpad}px {button_hpad}px;
            }}

            QWidget#albumScreen QListWidget#albumsList {{
                font-size: {list_pt}pt;
            }}

            QWidget#albumScreen QListWidget#albumsList::item {{
                padding: {item_vpad}px {item_hpad}px;
            }}
        """

        self.setStyleSheet(self._base_style + dynamic_style)

    def resizeEvent(self, event):
        """창 크기 변경 대응"""
        super().resizeEvent(event)
        self.adjust_layout()

    def showEvent(self, event):
        """화면 표시시 자동 로드"""
        super().showEvent(event)
        self.adjust_layout()
        if not self.albums:
            self.load_albums()
