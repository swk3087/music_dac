"""
Artist Screen
아티스트 목록 화면
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
    compute_effective_scale,
    scale_padding,
)


class ArtistLoadWorker(QThread):
    """아티스트 로딩 Worker Thread"""

    finished = pyqtSignal(list)

    def __init__(self, spotify_manager):
        super().__init__()
        self.spotify = spotify_manager

    def run(self):
        artists = self.spotify.get_followed_artists()
        self.finished.emit(artists)


class ArtistScreen(QWidget):
    """아티스트 화면 클래스"""

    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.artists = []
        self.worker = None
        self.buttons = []
        self.setup_ui()

    def setup_ui(self):
        """UI 구성"""
        self.setObjectName("artistScreen")

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        container = QWidget()
        self.scroll_area.setWidget(container)
        self.scroll_container = container

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

        title = QLabel("Followed Artists")
        title.setObjectName("artistTitle")
        title.setProperty("role", "title")
        header.addWidget(title)
        self.title_label = title

        header.addStretch()

        refresh_btn = QPushButton("Refresh")
        refresh_btn.setProperty("variant", "surface")
        refresh_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        refresh_btn.clicked.connect(self.load_artists)
        header.addWidget(refresh_btn)
        self.buttons.append(refresh_btn)
        self.refresh_btn = refresh_btn

        self.content_layout.addLayout(header)

        self.card = QFrame()
        self.card.setObjectName("card")
        self.card.setFrameShape(QFrame.Shape.NoFrame)
        self.card.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        self.card_layout = QVBoxLayout(self.card)
        self.card_layout.setContentsMargins(24, 24, 24, 24)
        self.card_layout.setSpacing(16)

        self.info_label = QLabel("Loading artists…")
        self.info_label.setObjectName("infoLabel")
        self.info_label.setProperty("role", "caption")
        self.card_layout.addWidget(self.info_label)

        self.artists_list = QListWidget()
        self.artists_list.setObjectName("artistsList")
        self.artists_list.setMinimumHeight(220)
        self.artists_list.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.artists_list.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.artists_list.itemClicked.connect(self.open_artist)
        self.card_layout.addWidget(self.artists_list)

        self.content_layout.addWidget(self.card, alignment=Qt.AlignmentFlag.AlignHCenter)
        self.content_layout.addStretch(1)

        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.addWidget(self.scroll_area)

        self.setup_styles()
        self.adjust_layout()

    def load_artists(self):
        """아티스트 로드"""
        self.info_label.setText("Loading artists…")
        self.info_label.setStyleSheet(f"color: {config.COLOR_PRIMARY};")
        self.artists_list.clear()

        self.worker = ArtistLoadWorker(self.parent.spotify)
        self.worker.finished.connect(self.display_artists)
        self.worker.start()

    def display_artists(self, artists):
        """아티스트 표시"""
        self.artists = artists or []
        self.artists_list.clear()

        if not self.artists:
            self.info_label.setText("No followed artists found")
            self.info_label.setStyleSheet(f"color: {config.COLOR_TEXT_SECONDARY};")
            self.artists_list.addItem("You're not following any artists yet.")
            return

        self.info_label.setText(f"Following {len(self.artists)} artists")
        self.info_label.setStyleSheet(f"color: {config.COLOR_TEXT_SECONDARY};")

        for artist in self.artists:
            if not artist:
                continue

            name = artist.get("name", "Unknown Artist")
            genres = artist.get("genres", [])
            genre_text = ", ".join(genres[:2]) if genres else "Various genres"

            followers = artist.get("followers", {}).get("total", 0)
            if followers >= 1_000_000:
                followers_text = f"{followers / 1_000_000:.1f}M"
            elif followers >= 1_000:
                followers_text = f"{followers / 1_000:.1f}K"
            else:
                followers_text = str(followers)

            popularity = artist.get("popularity", 0)

            item_text = (
                f"🎤 {name}\n   🎵 {genre_text}  ·  👥 {followers_text} followers  ·  ⭐ {popularity}% popular"
            )

            item = QListWidgetItem(item_text)
            item.setData(Qt.ItemDataRole.UserRole, artist)
            self.artists_list.addItem(item)

    def open_artist(self, item):
        """아티스트 열기"""
        artist = item.data(Qt.ItemDataRole.UserRole)

        if artist:
            self.parent.detail_screen.load_artist(artist)
            self.parent.navigate_to(7)

    def setup_styles(self):
        """기본 스타일 템플릿 저장"""
        self._base_style = (
            BASE_STYLESHEET
            + f"""
            QWidget#artistScreen {{
                background: {config.GRADIENT_NIGHTFALL};
            }}

            QWidget#artistScreen QLabel#artistTitle {{
                font-weight: 800;
                color: {config.COLOR_TEXT};
            }}

            QWidget#artistScreen QListWidget#artistsList {{
                line-height: 1.5em;
            }}

            QWidget#artistScreen QListWidget#artistsList::item {{
                padding: 14px 12px;
                border-radius: 12px;
                margin: 2px 0;
                border: 1px solid transparent;
            }}

            QWidget#artistScreen QListWidget#artistsList::item:selected {{
                border-color: rgba(102, 255, 224, 0.35);
                background-color: rgba(102, 255, 224, 0.18);
            }}

            QWidget#artistScreen QListWidget#artistsList::item:hover {{
                background-color: rgba(255, 255, 255, 0.08);
            }}
            """
        )

    def adjust_layout(self):
        """화면 크기에 따라 여백/카드 폭 조정"""
        width = max(320, self.width())
        margin_side = max(10, int(width * 0.045))
        margin_top = max(6, int(width * 0.015))
        margin_bottom = max(10, int(width * 0.035))
        self.content_layout.setContentsMargins(margin_side, margin_top, margin_side, margin_bottom)

        if self.card:
            max_width = int(width * 0.94)
            self.card.setMaximumWidth(max_width)
            self.card.setMinimumWidth(min(max_width, width - (margin_side * 2)))

        current_height = self.height()
        height = current_height if current_height > 0 else config.SCREEN_HEIGHT
        available_height = max(320, height - (margin_top + margin_bottom))

        effective_scale = compute_effective_scale(
            width,
            height,
            available_height=available_height,
            base_height=640,
            min_scale=0.28,
        )

        self.content_layout.setSpacing(max(10, int(round(20 * effective_scale))))

        if hasattr(self, "card_layout"):
            card_margin = max(16, int(round(26 * effective_scale)))
            card_spacing = max(10, int(round(18 * effective_scale)))
            self.card_layout.setContentsMargins(card_margin, card_margin, card_margin, card_margin)
            self.card_layout.setSpacing(card_spacing)

        if hasattr(self, "scroll_container"):
            self.scroll_container.setMinimumHeight(available_height)
            self.scroll_container.setMaximumHeight(available_height)

        if self.card:
            self.card.setMinimumHeight(available_height)
            self.card.setMaximumHeight(available_height)

        button_height = max(36, int(round(58 * effective_scale)))
        for btn in self.buttons:
            btn.setMinimumHeight(button_height)

        if hasattr(self, "back_btn"):
            self.back_btn.setMinimumWidth(max(90, int(round(150 * effective_scale))))
        if hasattr(self, "refresh_btn"):
            self.refresh_btn.setMinimumWidth(max(90, int(round(150 * effective_scale))))

        if hasattr(self, "artists_list"):
            list_height = max(220, int(available_height * 0.45))
            self.artists_list.setMinimumHeight(list_height)

        self.update_dynamic_style(width, height, scale_override=effective_scale)

    def update_dynamic_style(self, width, height, scale_override=None):
        """화면 크기에 맞춰 글꼴 및 패딩 조정"""
        scale = (
            scale_override
            if scale_override is not None
            else compute_responsive_scale(width, height)
        )

        scaling_config = []
        if hasattr(self, "title_label"):
            scaling_config.append(("title", self.title_label, 20, 12))
        if hasattr(self, "info_label"):
            scaling_config.append(("caption", self.info_label, 11, 9))
        if hasattr(self, "artists_list"):
            scaling_config.append(("list", self.artists_list, 11, 9))

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
            QWidget#artistScreen QLabel#artistTitle {{
                font-size: {title_pt}pt;
            }}

            QWidget#artistScreen QLabel#infoLabel {{
                font-size: {caption_pt}pt;
            }}

            QWidget#artistScreen QPushButton {{
                font-size: {button_pt}pt;
                padding: {button_vpad}px {button_hpad}px;
            }}

            QWidget#artistScreen QListWidget#artistsList {{
                font-size: {list_pt}pt;
            }}

            QWidget#artistScreen QListWidget#artistsList::item {{
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
        if not self.artists:
            self.load_artists()
