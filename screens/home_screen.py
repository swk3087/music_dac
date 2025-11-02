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
        self.card_layout.setContentsMargins(18, 18, 18, 18)
        self.card_layout.setSpacing(12)

        search_section = self.build_section(
            "Search",
            [("🔍 General Search", 1), ("🤖 AI Search", 2)],
        )
        self.card_layout.addWidget(search_section)

        library_section = self.build_section(
            "Library",
            [("📝 Playlists", 3), ("💿 Albums", 4), ("🎤 Artists", 5)],
        )
        self.card_layout.addWidget(library_section)

        now_playing_btn = self.create_button("▶ Now Playing", 6)
        now_playing_btn.setObjectName("nowPlayingButton")
        self.card_layout.addWidget(now_playing_btn)

        self.content_layout.addWidget(self.card, alignment=Qt.AlignmentFlag.AlignHCenter)
        self.content_layout.addStretch(1)

        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.addWidget(self.scroll_area)

        self.apply_styles()
        self.adjust_layout()

    def create_button(self, text, target_index):
        """버튼 생성 및 스타일 적용"""
        button = QPushButton(text)
        button.setProperty("variant", "surface")
        button.setCursor(Qt.CursorShape.PointingHandCursor)
        button.clicked.connect(lambda _, idx=target_index: self.parent.navigate_to(idx))
        self.buttons.append(button)
        return button

    def build_section(self, title_text, buttons):
        """섹션 카드 생성"""
        section = QFrame()
        section.setObjectName("section")

        layout = QVBoxLayout(section)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)

        title = QLabel(title_text)
        title.setProperty("role", "subtitle")
        title.setObjectName("sectionTitle")
        layout.addWidget(title)

        grid = self.create_button_grid(buttons)
        layout.addLayout(grid)

        return section

    def create_button_grid(self, buttons, columns=2):
        """버튼을 그리드 형태로 배치"""
        grid = QGridLayout()
        grid.setSpacing(12)

        for index, (text, screen_index) in enumerate(buttons):
            button = self.create_button(text, screen_index)
            button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            row = index // columns
            col = index % columns
            grid.addWidget(button, row, col)

        return grid

    def apply_styles(self):
        """스타일시트 적용"""
        self.setStyleSheet(
            BASE_STYLESHEET
            + f"""
            QWidget#homeScreen {{
                background: {config.GRADIENT_NIGHTFALL};
            }}

            QWidget#homeScreen QLabel#homeTitle {{
                font-size: 200%;
                font-weight: 800;
                color: {config.COLOR_TEXT};
            }}

            QWidget#homeScreen QFrame#section {{
                background: rgba(255, 255, 255, 0.035);
                border: 1px solid rgba(255, 255, 255, 0.05);
            }}

            QWidget#homeScreen QFrame#section QLabel#sectionTitle {{
                color: {config.COLOR_TEXT};
                font-weight: 700;
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
        margin_side = max(8, int(width * 0.035))
        margin_top = max(4, int(width * 0.01))
        margin_bottom = max(8, int(width * 0.03))
        self.content_layout.setContentsMargins(margin_side, margin_top, margin_side, margin_bottom)

        if self.card:
            max_width = int(width * 0.9)
            self.card.setMaximumWidth(max_width)
            self.card.setMinimumWidth(min(max_width, width - (margin_side * 2)))

        # Update button sizing proportionally
        button_height = max(36, int(width * 0.075))
        for btn in self.buttons:
            btn.setMinimumHeight(button_height)

    def resizeEvent(self, event):
        """창 크기 변경 대응"""
        super().resizeEvent(event)
        self.adjust_layout()

    def showEvent(self, event):
        """화면이 표시될 때 호출"""
        super().showEvent(event)
