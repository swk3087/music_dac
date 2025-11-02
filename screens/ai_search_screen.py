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
    QSizePolicy,
)
from PyQt6.QtCore import Qt, pyqtSignal, QThread
import config
from ui_styles import (
    BASE_STYLESHEET,
    apply_font_scaling,
    compute_responsive_scale,
    compute_effective_scale,
    scale_padding,
)


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
        self.scroll_container = container

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
        self.title_label = title

        header.addStretch()
        self.content_layout.addLayout(header)

        self.card = QFrame()
        self.card.setObjectName("card")
        self.card.setFrameShape(QFrame.Shape.NoFrame)
        self.card.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        self.card_layout = QVBoxLayout(self.card)
        self.card_layout.setContentsMargins(24, 24, 24, 24)
        self.card_layout.setSpacing(18)

        desc = QLabel("Describe the mood or type of music you want and AI will craft suggestions.")
        desc.setObjectName("descriptionLabel")
        desc.setProperty("role", "caption")
        desc.setWordWrap(True)
        self.card_layout.addWidget(desc)
        self.description_label = desc

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
        self.suggestions_label = suggestions_label

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
        self.results_label = results_label

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

        self.setup_styles()
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

        normalized_suggestions = []
        for item in suggestions:
            if isinstance(item, dict):
                raw_query = (
                    item.get("query")
                    or item.get("text")
                    or item.get("title")
                    or item.get("suggestion")
                )
                query = str(raw_query).strip() if raw_query else ""
                raw_description = item.get("description") or item.get("details") or ""
                description = str(raw_description).strip()
                if query:
                    normalized_suggestions.append({"query": query, "description": description})
            elif isinstance(item, str):
                query = item.strip()
                if query:
                    normalized_suggestions.append({"query": query, "description": ""})

        if not normalized_suggestions:
            self.results_info.setText("AI suggestions were invalid. Try again or refine your prompt.")
            self.results_info.setStyleSheet(f"color: {config.COLOR_ERROR};")
            return

        self.current_suggestions = normalized_suggestions
        self.results_info.setText("Pick a suggestion to explore matching tracks.")
        self.results_info.setStyleSheet(f"color: {config.COLOR_TEXT_SECONDARY};")

        for idx, suggestion in enumerate(normalized_suggestions):
            if idx >= len(self.suggestion_buttons):
                break

            text = suggestion.get("query") or f"Suggestion {idx + 1}"
            btn = self.suggestion_buttons[idx]
            btn.setText(text)
            btn.show()

        for idx in range(len(normalized_suggestions), len(self.suggestion_buttons)):
            self.suggestion_buttons[idx].hide()

    def select_suggestion(self, index):
        """AI 추천 선택"""
        if index >= len(self.current_suggestions):
            return

        suggestion = self.current_suggestions[index]
        if isinstance(suggestion, dict):
            query = suggestion.get("query")
            description = suggestion.get("description", "")
        else:
            query = str(suggestion).strip()
            description = ""

        if not query:
            self.results_info.setText("Suggestion is missing a search query.")
            self.results_info.setStyleSheet(f"color: {config.COLOR_WARNING};")
            return

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

    def setup_styles(self):
        """기본 스타일 템플릿 저장"""
        self._base_style = (
            BASE_STYLESHEET
            + f"""
            QWidget#aiSearchScreen {{
                background: {config.GRADIENT_NIGHTFALL};
            }}

            QWidget#aiSearchScreen QLabel#aiTitle {{
                font-weight: 820;
                color: {config.COLOR_TEXT};
            }}

            QWidget#aiSearchScreen QPushButton#suggestionButton {{
                text-align: left;
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
            card_margin = max(16, int(round(28 * effective_scale)))
            card_spacing = max(10, int(round(18 * effective_scale)))
            self.card_layout.setContentsMargins(card_margin, card_margin, card_margin, card_margin)
            self.card_layout.setSpacing(card_spacing)

        if hasattr(self, "suggestions_grid"):
            grid_spacing = max(8, int(round(14 * effective_scale)))
            self.suggestions_grid.setHorizontalSpacing(grid_spacing)
            self.suggestions_grid.setVerticalSpacing(grid_spacing)

        search_field_height = max(36, int(round(54 * effective_scale)))
        self.search_input.setMinimumHeight(search_field_height)

        button_height = max(36, int(round(56 * effective_scale)))
        for btn in self.buttons:
            btn.setMinimumHeight(button_height)

        if hasattr(self, "search_btn"):
            self.search_btn.setMinimumWidth(max(120, int(round(180 * effective_scale))))

        for btn in self.suggestion_buttons:
            btn.setMinimumHeight(max(40, int(round(58 * effective_scale))))

        if hasattr(self, "results_list"):
            list_height = max(180, int(available_height * 0.35))
            self.results_list.setMinimumHeight(list_height)

        if hasattr(self, "scroll_container"):
            self.scroll_container.setMinimumHeight(available_height)
            self.scroll_container.setMaximumHeight(available_height)

        if self.card:
            self.card.setMinimumHeight(available_height)
            self.card.setMaximumHeight(available_height)

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
        if hasattr(self, "description_label"):
            scaling_config.append(("body", self.description_label, 12, 9))
        if hasattr(self, "suggestions_label"):
            scaling_config.append(("subtitle", self.suggestions_label, 15, 11))
        if hasattr(self, "results_label"):
            scaling_config.append(("subtitle", self.results_label, 15, 11))
        if hasattr(self, "results_info"):
            scaling_config.append(("caption", self.results_info, 11, 9))
        if hasattr(self, "loading_label"):
            scaling_config.append(("caption", self.loading_label, 11, 9))
        if hasattr(self, "search_input"):
            scaling_config.append(("input", self.search_input, 12, 10))
        if hasattr(self, "results_list"):
            scaling_config.append(("list", self.results_list, 11, 9))

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
        body_pt = applied_map.get("body", [11])[0]
        subtitle_pt = applied_map.get("subtitle", [13])[0]
        caption_pt = applied_map.get("caption", [10])[0]
        input_pt = applied_map.get("input", [11])[0]
        list_pt = applied_map.get("list", [11])[0]
        button_pt = applied_map.get("button", [11])[0]

        button_vpad, button_hpad = scale_padding(
            base_vertical=14,
            base_horizontal=20,
            scale=scale,
            min_vertical=6,
            min_horizontal=10,
        )

        suggestion_vpad, suggestion_hpad = scale_padding(
            base_vertical=16,
            base_horizontal=22,
            scale=scale,
            min_vertical=8,
            min_horizontal=12,
        )

        input_vpad, input_hpad = scale_padding(
            base_vertical=14,
            base_horizontal=18,
            scale=scale,
            min_vertical=6,
            min_horizontal=12,
        )

        dynamic_style = f"""
            QWidget#aiSearchScreen QLabel#aiTitle {{
                font-size: {title_pt}pt;
            }}

            QWidget#aiSearchScreen QLabel#descriptionLabel {{
                font-size: {body_pt}pt;
            }}

            QWidget#aiSearchScreen QLabel#suggestionsLabel,
            QWidget#aiSearchScreen QLabel#resultsLabel {{
                font-size: {subtitle_pt}pt;
            }}

            QWidget#aiSearchScreen QLabel#resultsInfo,
            QWidget#aiSearchScreen QLabel#loadingLabel {{
                font-size: {caption_pt}pt;
            }}

            QWidget#aiSearchScreen QPushButton {{
                font-size: {button_pt}pt;
                padding: {button_vpad}px {button_hpad}px;
            }}

            QWidget#aiSearchScreen QPushButton#suggestionButton {{
                padding: {suggestion_vpad}px {suggestion_hpad}px;
            }}

            QLineEdit#aiSearchField {{
                font-size: {input_pt}pt;
                padding: {input_vpad}px {input_hpad}px;
            }}

            QWidget#aiSearchScreen QListWidget#resultsList {{
                font-size: {list_pt}pt;
            }}
        """

        self.setStyleSheet(self._base_style + dynamic_style)

    def resizeEvent(self, event):
        """창 크기 변경 대응"""
        super().resizeEvent(event)
        self.adjust_layout()

    def showEvent(self, event):
        """화면 표시시 호출"""
        super().showEvent(event)
        self.search_input.setFocus()
        self.adjust_layout()

    def hideEvent(self, event):
        """화면 숨김시 호출"""
        super().hideEvent(event)
        # 필요 시 상태 초기화 가능
