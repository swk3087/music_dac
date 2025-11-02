"""
AI Search Screen
Gemini AI 기반 음악 검색 및 추천 화면
"""

from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLineEdit,
    QListWidget,
    QLabel,
    QListWidgetItem,
    QGridLayout,
    QFrame,
    QScrollArea,
)
from PyQt6.QtCore import Qt, pyqtSignal, QThread
import config
from ui_styles import BASE_STYLESHEET


class AISearchWorker(QThread):
    """AI 검색을 백그라운드에서 처리하는 Worker Thread"""

    finished = pyqtSignal(list)

    def __init__(self, ai_manager, query):
        super().__init__()
        self.ai_manager = ai_manager
        self.query = query

    def run(self):
        suggestions = self.ai_manager.generate_music_suggestions(self.query)
        self.finished.emit(suggestions)


class AISearchScreen(QWidget):
    """AI 검색 화면 클래스"""

    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.current_suggestions = []
        self.worker = None
        self.buttons = []
        self.setup_ui()

    def setup_ui(self):
        """UI 구성"""
        self.setObjectName("aiSearchScreen")

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

        self.back_btn = QPushButton("← Back")
        self.back_btn.setProperty("variant", "ghost")
        self.back_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.back_btn.clicked.connect(self.parent.go_back)
        header.addWidget(self.back_btn)
        self.buttons.append(self.back_btn)

        title = QLabel("AI Smart Search")
        title.setObjectName("aiTitle")
        title.setProperty("role", "title")
        header.addWidget(title)

        header.addStretch()
        self.content_layout.addLayout(header)

        self.card = QFrame()
        self.card.setObjectName("card")
        self.card.setFrameShape(QFrame.Shape.NoFrame)

        self.card_layout = QVBoxLayout(self.card)
        self.card_layout.setContentsMargins(24, 24, 24, 24)
        self.card_layout.setSpacing(18)

        desc = QLabel("Describe the mood or type of music you want and AI will craft suggestions.")
        desc.setObjectName("descriptionLabel")
        desc.setProperty("role", "caption")
        desc.setWordWrap(True)
        self.card_layout.addWidget(desc)

        search_row = QHBoxLayout()
        search_row.setSpacing(12)

        self.search_input = QLineEdit()
        self.search_input.setObjectName("aiSearchField")
        self.search_input.setPlaceholderText("e.g., 'rainy day music', 'workout songs', 'chill evening'…")
        self.search_input.returnPressed.connect(self.start_ai_search)
        search_row.addWidget(self.search_input)

        self.search_btn = QPushButton("Get AI Suggestions")
        self.search_btn.setProperty("variant", "accent")
        self.search_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.search_btn.clicked.connect(self.start_ai_search)
        search_row.addWidget(self.search_btn)
        self.buttons.append(self.search_btn)

        self.card_layout.addLayout(search_row)

        self.loading_label = QLabel("AI is generating suggestions…")
        self.loading_label.setObjectName("loadingLabel")
        self.loading_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.loading_label.hide()
        self.card_layout.addWidget(self.loading_label)

        suggestions_section = QFrame()
        suggestions_section.setObjectName("section")

        suggestions_layout = QVBoxLayout(suggestions_section)
        suggestions_layout.setContentsMargins(20, 20, 20, 20)
        suggestions_layout.setSpacing(12)

        suggestions_label = QLabel("AI Suggestions")
        suggestions_label.setObjectName("suggestionsLabel")
        suggestions_label.setProperty("role", "subtitle")
        suggestions_layout.addWidget(suggestions_label)

        self.suggestions_grid = QGridLayout()
        self.suggestions_grid.setSpacing(12)
        self.suggestion_buttons = []

        for i in range(4):
            btn = QPushButton(f"Suggestion {i + 1}")
            btn.setObjectName("suggestionButton")
            btn.setProperty("variant", "surface")
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda _, idx=i: self.select_suggestion(idx))
            btn.setMinimumHeight(68)
            btn.hide()
            self.suggestion_buttons.append(btn)
            self.buttons.append(btn)

            row = i // 2
            col = i % 2
            self.suggestions_grid.addWidget(btn, row, col)

        suggestions_layout.addLayout(self.suggestions_grid)
        self.card_layout.addWidget(suggestions_section)

        results_section = QFrame()
        results_section.setObjectName("section")

        results_layout = QVBoxLayout(results_section)
        results_layout.setContentsMargins(20, 20, 20, 20)
        results_layout.setSpacing(12)

        results_label = QLabel("Search Results")
        results_label.setObjectName("resultsLabel")
        results_label.setProperty("role", "subtitle")
        results_layout.addWidget(results_label)

        self.results_info = QLabel("Select an AI suggestion to see results.")
        self.results_info.setObjectName("resultsInfo")
        self.results_info.setProperty("role", "caption")
        results_layout.addWidget(self.results_info)

        self.results_list = QListWidget()
        self.results_list.setObjectName("resultsList")
        self.results_list.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.results_list.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.results_list.itemDoubleClicked.connect(self.play_selected)
        results_layout.addWidget(self.results_list)

        self.card_layout.addWidget(results_section)

        self.content_layout.addWidget(self.card, alignment=Qt.AlignmentFlag.AlignHCenter)
        self.content_layout.addStretch(1)

        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.addWidget(self.scroll_area)

        self.apply_styles()
        self.adjust_layout()

    def start_ai_search(self):
        """AI 검색 시작"""
        query = self.search_input.text().strip()

        if not query:
            self.results_info.setText("Please enter a description to guide AI.")
            self.results_info.setStyleSheet(f"color: {config.COLOR_WARNING};")
            return

        self.loading_label.show()
        self.loading_label.setStyleSheet(f"color: {config.COLOR_PRIMARY};")

        self.search_btn.setEnabled(False)
        self.search_btn.setText("Generating…")

        for btn in self.suggestion_buttons:
            btn.hide()

        self.results_list.clear()
        self.results_info.setText("Waiting for AI suggestions…")
        self.results_info.setStyleSheet(f"color: {config.COLOR_PRIMARY};")

        self.worker = AISearchWorker(self.parent.ai, query)
        self.worker.finished.connect(self.handle_ai_results)
        self.worker.start()

    def handle_ai_results(self, suggestions):
        """AI 검색 결과 처리"""
        self.loading_label.hide()
        self.search_btn.setEnabled(True)
        self.search_btn.setText("Get AI Suggestions")

        if not suggestions:
            self.results_info.setText("AI could not generate suggestions. Try refining your prompt.")
            self.results_info.setStyleSheet(f"color: {config.COLOR_ERROR};")
            return

        self.current_suggestions = suggestions
        self.results_info.setText("Pick a suggestion to explore matching tracks.")
        self.results_info.setStyleSheet(f"color: {config.COLOR_TEXT_SECONDARY};")

        for idx, suggestion in enumerate(suggestions):
            if idx >= len(self.suggestion_buttons):
                break

            text = suggestion.get("query", f"Suggestion {idx + 1}")
            btn = self.suggestion_buttons[idx]
            btn.setText(text)
            btn.show()

        for idx in range(len(suggestions), len(self.suggestion_buttons)):
            self.suggestion_buttons[idx].hide()

    def select_suggestion(self, index):
        """AI 추천 선택"""
        if index >= len(self.current_suggestions):
            return

        suggestion = self.current_suggestions[index]
        query = suggestion.get("query")

        if not query:
            self.results_info.setText("Suggestion is missing a search query.")
            self.results_info.setStyleSheet(f"color: {config.COLOR_WARNING};")
            return

        description = suggestion.get("description", "")
        if description:
            self.results_info.setText(f"Suggestion: {description}")
        else:
            self.results_info.setText(f"Searching for '{query}'")
        self.results_info.setStyleSheet(f"color: {config.COLOR_PRIMARY};")

        self.perform_search(query)

    def perform_search(self, query):
        """Spotify 검색 수행"""
        self.results_list.clear()

        try:
            results = self.parent.spotify.search(query, search_type="track", limit=config.MAX_AI_SUGGESTIONS * 5)
        except Exception as exc:
            print(f"❌ AI search failed: {exc}")
            self.results_info.setText("Search failed. Please try again.")
            self.results_info.setStyleSheet(f"color: {config.COLOR_ERROR};")
            return

        if not results or "tracks" not in results:
            self.results_info.setText("Search failed. Please try again.")
            self.results_info.setStyleSheet(f"color: {config.COLOR_ERROR};")
            return

        tracks = results["tracks"]["items"]

        if not tracks:
            self.results_info.setText(f"No results found for '{query}'")
            self.results_info.setStyleSheet(f"color: {config.COLOR_TEXT_SECONDARY};")
            self.results_list.addItem("No tracks found. Try another suggestion.")
            return

        self.results_info.setText(f"Found {len(tracks)} tracks for '{query}'")
        self.results_info.setStyleSheet(f"color: {config.COLOR_TEXT_SECONDARY};")

        for track in tracks:
            if not track:
                continue

            track_name = track.get("name", "Unknown")
            artists = track.get("artists", [])
            artist_names = ", ".join([a.get("name", "Unknown") for a in artists]) if artists else "Unknown"
            album_name = track.get("album", {}).get("name", "Unknown")

            duration_ms = track.get("duration_ms", 0)
            duration_min = duration_ms // 60000
            duration_sec = (duration_ms % 60000) // 1000

            item_text = f"🎵 {track_name}\n   👤 {artist_names}  ·  💿 {album_name}  ·  ⏱ {duration_min}:{duration_sec:02d}"

            item = QListWidgetItem(item_text)
            item.setData(Qt.ItemDataRole.UserRole, track)
            self.results_list.addItem(item)

    def play_selected(self, item):
        """선택한 트랙 재생"""
        track = item.data(Qt.ItemDataRole.UserRole)

        if track and track.get("uri"):
            uri = track["uri"]
            self.parent.spotify.play_track(uri)
            self.parent.navigate_to(6)
        else:
            print("❌ No valid track URI")

    def apply_styles(self):
        """스타일 시트 적용"""
        self.setStyleSheet(
            BASE_STYLESHEET
            + f"""
            QWidget#aiSearchScreen {{
                background: {config.GRADIENT_NIGHTFALL};
            }}

            QWidget#aiSearchScreen QLabel#aiTitle {{
                font-size: 210%;
                font-weight: 820;
                color: {config.COLOR_TEXT};
            }}

            QWidget#aiSearchScreen QPushButton#suggestionButton {{
                text-align: left;
                padding: 1em;
                font-size: 105%;
                font-weight: 600;
            }}

            QWidget#aiSearchScreen QPushButton#suggestionButton:hover {{
                border-color: rgba(102, 255, 224, 0.45);
            }}

            QWidget#aiSearchScreen QLabel#loadingLabel {{
                padding: 1em;
                background-color: rgba(255, 255, 255, 0.06);
                border-radius: 14px;
                color: {config.COLOR_PRIMARY};
            }}

            QWidget#aiSearchScreen QListWidget#resultsList {{
                font-size: 105%;
                line-height: 1.45em;
            }}

            QWidget#aiSearchScreen QListWidget#resultsList::item {{
                padding: 12px 12px;
                border-radius: 10px;
                margin: 2px 0;
                border: 1px solid transparent;
            }}

            QWidget#aiSearchScreen QListWidget#resultsList::item:selected {{
                border-color: rgba(102, 255, 224, 0.35);
                background-color: rgba(102, 255, 224, 0.18);
            }}

            QWidget#aiSearchScreen QListWidget#resultsList::item:hover {{
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

        button_height = max(42, int(width * 0.08))
        for btn in self.buttons:
            btn.setMinimumHeight(button_height)

        if hasattr(self, "back_btn"):
            self.back_btn.setMinimumWidth(max(90, int(width * 0.2)))
        if hasattr(self, "search_btn"):
            self.search_btn.setMinimumWidth(max(120, int(width * 0.28)))
        for btn in self.suggestion_buttons:
            btn.setMinimumHeight(max(48, int(width * 0.085)))

    def resizeEvent(self, event):
        """창 크기 변경 대응"""
        super().resizeEvent(event)
        self.adjust_layout()

    def showEvent(self, event):
        """화면 표시시 호출"""
        super().showEvent(event)
        self.search_input.setFocus()

    def hideEvent(self, event):
        """화면 숨김시 호출"""
        super().hideEvent(event)
        # 필요 시 상태 초기화 가능
