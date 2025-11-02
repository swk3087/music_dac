"""
Home Screen
메인 메뉴 화면
"""

from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QPushButton,
    QLabel,
    QFrame,
    QScrollArea,
    QSizePolicy,
    QGridLayout,
)
from PyQt6.QtCore import Qt

import config
from ui_styles import BASE_STYLESHEET


class HomeScreen(QWidget):
    """홈 화면 클래스"""

    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.buttons = []
        self.setup_ui()

    def setup_ui(self):
        """UI 구성"""
        self.setObjectName("homeScreen")

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        container = QWidget()
        self.scroll_area.setWidget(container)

        self.content_layout = QVBoxLayout(container)
        self.content_layout.setSpacing(14)
        self.content_layout.setContentsMargins(0, 0, 0, 0)

        header_layout = QVBoxLayout()
        header_layout.setSpacing(4)

        title = QLabel("Music DAC")
        title.setObjectName("homeTitle")
        title.setProperty("role", "title")
        header_layout.addWidget(title)

        self.content_layout.addLayout(header_layout)

        self.card = QFrame()
        self.card.setObjectName("card")
        self.card.setFrameShape(QFrame.Shape.NoFrame)

        self.card_layout = QVBoxLayout(self.card)
        self.card_layout.setContentsMargins(14, 14, 14, 14)
        self.card_layout.setSpacing(10)

        button_specs = [
            ("🔍 General Search", 1),
            ("🤖 AI Search", 2),
            ("📝 Playlists", 3),
            ("💿 Albums", 4),
            ("🎤 Artists", 5),
        ]

        button_grid = self.create_button_grid(button_specs, columns=2)
        self.card_layout.addLayout(button_grid)

        now_playing_btn = self.create_button("▶ Now Playing", 6)
        now_playing_btn.setObjectName("nowPlayingButton")
        self.card_layout.addWidget(now_playing_btn)

        self.content_layout.addWidget(self.card, alignment=Qt.AlignmentFlag.AlignHCenter)
        self.content_layout.addStretch(1)

        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.addWidget(self.scroll_area)

        self.setup_styles()
        self.adjust_layout()

    def create_button(self, text, target_index):
        """버튼 생성 및 스타일 적용"""
        button = QPushButton(text)
        button.setProperty("variant", "surface")
        button.setCursor(Qt.CursorShape.PointingHandCursor)
        button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        button.setObjectName("homeButton")
        button.clicked.connect(lambda _, idx=target_index: self.parent.navigate_to(idx))
        self.buttons.append(button)
        return button

    def create_button_grid(self, buttons, columns=2):
        """버튼을 그리드 형태로 배치"""
        grid = QGridLayout()
        grid.setSpacing(8)

        for index, (text, screen_index) in enumerate(buttons):
            button = self.create_button(text, screen_index)
            button.setMinimumHeight(0)
            row = index // columns
            col = index % columns
            grid.addWidget(button, row, col)

        return grid

    def setup_styles(self):
        """기본 스타일 템플릿"""
        self._base_style = (
            BASE_STYLESHEET
            + f"""
            QWidget#homeScreen {{
                background: {config.GRADIENT_NIGHTFALL};
            }}

            QWidget#homeScreen QLabel#homeTitle {{
                font-weight: 800;
                color: {config.COLOR_TEXT};
            }}

            QWidget#homeScreen QPushButton#nowPlayingButton {{
                text-align: center;
                font-weight: 700;
            }}
            """
        )

    def adjust_layout(self):
        """현재 창 크기에 맞게 여백 및 카드 폭 조정"""
        width = max(320, self.width())
        margin_side = max(6, int(width * 0.025))
        margin_top = max(2, int(width * 0.007))
        margin_bottom = max(6, int(width * 0.022))
        self.content_layout.setContentsMargins(margin_side, margin_top, margin_side, margin_bottom)

        if self.card:
            max_width = int(width * 0.9)
            self.card.setMaximumWidth(max_width)
            self.card.setMinimumWidth(min(max_width, width - (margin_side * 2)))

        self.update_dynamic_style(width)

    def update_dynamic_style(self, width):
        """화면 크기에 맞춰 텍스트 크기 조정"""
        scale = width / 640
        title_pct = min(220, max(140, int(200 * scale)))
        button_pct = min(150, max(95, int(110 * scale)))

        dynamic_style = f"""
            QWidget#homeScreen QLabel#homeTitle {{
                font-size: {title_pct}%;
            }}

            QPushButton#homeButton,
            QWidget#homeScreen QPushButton#nowPlayingButton {{
                font-size: {button_pct}%;
            }}
        """

        self.setStyleSheet(self._base_style + dynamic_style)

        # Scale typography relative to width
        scale_factor = width / 640  # baseline reference width
        title_size = min(220, max(140, int(200 * scale_factor)))
        button_font = min(140, max(100, int(110 * scale_factor)))

        style_overrides = f"""
            QLabel#homeTitle {{ font-size: {title_size}%; }}
            QPushButton#homeButton {{ font-size: {button_font}%; }}
        """
        self.setStyleSheet(BASE_STYLESHEET + f"""
            QWidget#homeScreen {{
                background: {config.GRADIENT_NIGHTFALL};
            }}

            QWidget#homeScreen QLabel#homeTitle {{
                font-size: {title_size}%;
                font-weight: 800;
                color: {config.COLOR_TEXT};
            }}

            QWidget#homeScreen QPushButton#nowPlayingButton {{
                text-align: center;
                font-weight: 700;
                font-size: {button_font}%;
            }}

            QPushButton#homeButton {{ font-size: {button_font}%; }}
        """ + style_overrides)

    def resizeEvent(self, event):
        """창 크기 변경 대응"""
        super().resizeEvent(event)
        self.adjust_layout()

    def showEvent(self, event):
        """화면이 표시될 때 호출"""
        super().showEvent(event)
