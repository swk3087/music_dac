"""
Search Screen
일반 검색 화면
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
    QFrame,
    QScrollArea,
    QSizePolicy,
)
from PyQt6.QtCore import Qt
import config
from ui_styles import (
    BASE_STYLESHEET,
    apply_font_scaling,
    compute_responsive_scale,
    scale_padding,
)


class SearchScreen(QWidget):
    """검색 화면 클래스"""
    
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.current_results = []
        self.buttons = []
        self.setup_ui()
        
    def setup_ui(self):
        """UI 구성"""
        self.setObjectName("searchScreen")
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
        header.addWidget(back_btn, alignment=Qt.AlignmentFlag.AlignVCenter)
        self.buttons.append(back_btn)
        self.back_btn = back_btn

        title = QLabel("Search")
        title.setObjectName("searchTitle")
        title.setProperty("role", "title")
        header.addWidget(title)
        self.title_label = title
        header.addStretch()
        self.content_layout.addLayout(header)

        self.card = QFrame()
        self.card.setObjectName("card")
        self.card.setFrameShape(QFrame.Shape.NoFrame)

        self.card_layout = QVBoxLayout(self.card)
        self.card_layout.setContentsMargins(24, 24, 24, 24)
        self.card_layout.setSpacing(16)

        search_row = QHBoxLayout()
        search_row.setSpacing(12)

        self.search_input = QLineEdit()
        self.search_input.setObjectName("searchField")
        self.search_input.setPlaceholderText("Search tracks, albums, or artists…")
        self.search_input.returnPressed.connect(self.perform_search)
        self.search_input.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        search_row.addWidget(self.search_input)

        search_btn = QPushButton("Search")
        search_btn.setProperty("variant", "primary")
        search_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        search_btn.clicked.connect(self.perform_search)
        search_row.addWidget(search_btn)
        self.buttons.append(search_btn)
        self.search_btn = search_btn

        self.card_layout.addLayout(search_row)

        self.results_info = QLabel("Enter a search query to get started")
        self.results_info.setObjectName("resultsInfo")
        self.results_info.setProperty("role", "caption")
        self.results_info.setWordWrap(True)
        self.card_layout.addWidget(self.results_info)

        self.results_list = QListWidget()
        self.results_list.setObjectName("resultsList")
        self.results_list.setMinimumHeight(200)
        self.results_list.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.results_list.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.results_list.itemDoubleClicked.connect(self.play_selected)
        self.card_layout.addWidget(self.results_list)

        self.content_layout.addWidget(self.card, alignment=Qt.AlignmentFlag.AlignHCenter)
        self.content_layout.addStretch(1)

        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.addWidget(self.scroll_area)

        self.setup_styles()
        self.adjust_layout()
        
    def perform_search(self):
        """검색 수행"""
        query = self.search_input.text().strip()

        if not query:
            self.results_info.setText("Please enter a search query")
            self.results_info.setStyleSheet(f"color: {config.COLOR_WARNING};")
            return
        
        self.results_info.setText(f"Searching for '{query}'...")
        self.results_info.setStyleSheet(f"color: {config.COLOR_PRIMARY};")
        self.results_list.clear()
        
        # Perform search
        results = self.parent.spotify.search(query, search_type='track', limit=config.MAX_SEARCH_RESULTS)
        self.display_results(results, query)
        
    def display_results(self, results, query):
        """검색 결과 표시"""
        self.results_list.clear()
        self.current_results = []
        
        if not results or 'tracks' not in results:
            self.results_info.setText("Search failed. Please try again.")
            self.results_info.setStyleSheet(f"color: {config.COLOR_ERROR};")
            return
        
        tracks = results['tracks']['items']
        
        if not tracks:
            self.results_info.setText(f"No results found for '{query}'")
            self.results_info.setStyleSheet(f"color: {config.COLOR_TEXT_SECONDARY};")
            self.results_list.addItem("No tracks found. Try a different search term.")
            return
        
        self.results_info.setText(f"Found {len(tracks)} tracks for '{query}'")
        self.results_info.setStyleSheet(f"color: {config.COLOR_TEXT_SECONDARY};")
        
        for track in tracks:
            if not track:
                continue
            
            # Track info
            track_name = track.get('name', 'Unknown')
            artists = track.get('artists', [])
            artist_names = ', '.join([a.get('name', 'Unknown') for a in artists]) if artists else 'Unknown'
            album_name = track.get('album', {}).get('name', 'Unknown')
            
            # Duration
            duration_ms = track.get('duration_ms', 0)
            duration_min = duration_ms // 60000
            duration_sec = (duration_ms % 60000) // 1000
            
            # Create item
            item_text = f"🎵 {track_name}\n   👤 {artist_names} | 💿 {album_name} | ⏱ {duration_min}:{duration_sec:02d}"
            
            item = QListWidgetItem(item_text)
            item.setData(Qt.ItemDataRole.UserRole, track)
            self.results_list.addItem(item)
            
            self.current_results.append(track)
    
    def play_selected(self, item):
        """선택한 트랙 재생"""
        track = item.data(Qt.ItemDataRole.UserRole)
        
        if track and track.get('uri'):
            uri = track['uri']
            self.parent.spotify.play_track(uri)
            
            # Navigate to player screen
            self.parent.navigate_to(6)
        else:
            print("❌ No valid track URI")
    
    def setup_styles(self):
        """기본 스타일 템플릿 저장"""
        self._base_style = (
            BASE_STYLESHEET
            + f"""
            QWidget#searchScreen {{
                background: {config.GRADIENT_NIGHTFALL};
            }}

            QWidget#searchScreen QLabel#searchTitle {{
                font-weight: 800;
                color: {config.COLOR_TEXT};
            }}

            QWidget#searchScreen QLabel#resultsInfo {{
                padding: 4px 0;
            }}

            QWidget#searchScreen QListWidget#resultsList {{
                line-height: 1.4em;
            }}

            QWidget#searchScreen QListWidget#resultsList::item {{
                border: 1px solid transparent;
            }}

            QWidget#searchScreen QListWidget#resultsList::item:selected {{
                border-color: rgba(102, 255, 224, 0.4);
            }}
            """
        )

    def adjust_layout(self):
        """현재 창 크기에 맞게 여백 및 카드 폭 조정"""
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
        if hasattr(self, "search_btn"):
            self.search_btn.setMinimumWidth(max(110, int(width * 0.24)))

        current_height = self.height()
        height = current_height if current_height > 0 else config.SCREEN_HEIGHT
        self.update_dynamic_style(width, height)

    def update_dynamic_style(self, width, height):
        """화면 크기에 맞춰 글꼴 및 패딩 조정"""
        scale = compute_responsive_scale(width, height)

        scaling_config = []
        if hasattr(self, "title_label"):
            scaling_config.append(("title", self.title_label, 20, 12))
        if hasattr(self, "results_info"):
            scaling_config.append(("caption", self.results_info, 11, 9))
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

        title_pt = applied_map.get("title", [14])[0]
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

        input_vpad, input_hpad = scale_padding(
            base_vertical=14,
            base_horizontal=18,
            scale=scale,
            min_vertical=6,
            min_horizontal=12,
        )

        dynamic_style = f"""
            QWidget#searchScreen QLabel#searchTitle {{
                font-size: {title_pt}pt;
            }}

            QWidget#searchScreen QLabel#resultsInfo {{
                font-size: {caption_pt}pt;
            }}

            QWidget#searchScreen QPushButton {{
                font-size: {button_pt}pt;
                padding: {button_vpad}px {button_hpad}px;
            }}

            QLineEdit#searchField {{
                font-size: {input_pt}pt;
                padding: {input_vpad}px {input_hpad}px;
            }}

            QWidget#searchScreen QListWidget#resultsList {{
                font-size: {list_pt}pt;
            }}
        """

        self.setStyleSheet(self._base_style + dynamic_style)
    
    def showEvent(self, event):
        """화면 표시시 호출"""
        super().showEvent(event)
        self.search_input.setFocus()
        self.adjust_layout()

    def hideEvent(self, event):
        """화면 숨김시 호출"""
        super().hideEvent(event)
        # Clear search when leaving screen
        # self.search_input.clear()
        # self.results_list.clear()

    def resizeEvent(self, event):
        """창 크기 변경 대응"""
        super().resizeEvent(event)
        self.adjust_layout()
