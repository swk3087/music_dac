"""
Player Screen
음악 재생 화면
"""

from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QSlider,
    QFrame,
    QScrollArea,
    QSizePolicy,
)
from PyQt6.QtCore import Qt, QTimer
import config
from ui_styles import (
    BASE_STYLESHEET,
    apply_font_scaling,
    compute_responsive_scale,
    scale_padding,
)


class PlayerScreen(QWidget):
    """플레이어 화면 클래스"""
    
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.current_track = None
        self.is_playing = False
        self.buttons = []
        self.setup_ui()
        self.setup_timer()
        
    def setup_ui(self):
        """UI 구성"""
        self.setObjectName("playerScreen")

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

        header_layout = QHBoxLayout()
        header_layout.setSpacing(14)

        back_btn = QPushButton("← Back")
        back_btn.setProperty("variant", "ghost")
        back_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        back_btn.clicked.connect(self.parent.go_back)
        back_btn.setObjectName("playerBackButton")
        header_layout.addWidget(back_btn)
        self.back_btn = back_btn
        self.buttons.append(back_btn)
        header_layout.addStretch()
        self.content_layout.addLayout(header_layout)

        self.card = QFrame()
        self.card.setObjectName("card")
        self.card.setFrameShape(QFrame.Shape.NoFrame)

        self.card.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        self.card_layout = QVBoxLayout(self.card)
        self.card_layout.setContentsMargins(28, 28, 28, 28)
        self.card_layout.setSpacing(18)
        self.card_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.album_art = QLabel("🎧")
        self.album_art.setObjectName("albumArt")
        self.album_art.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.album_art.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.card_layout.addWidget(self.album_art, alignment=Qt.AlignmentFlag.AlignCenter)

        info_layout = QVBoxLayout()
        info_layout.setSpacing(6)
        info_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.info_layout = info_layout

        self.track_name = QLabel("No track playing")
        self.track_name.setObjectName("trackTitle")
        self.track_name.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.track_name.setWordWrap(True)
        self.track_name.setProperty("role", "title")
        info_layout.addWidget(self.track_name)

        self.artist_name = QLabel("Start music from search or library")
        self.artist_name.setObjectName("artistLabel")
        self.artist_name.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.artist_name.setWordWrap(True)
        self.artist_name.setProperty("role", "subtitle")
        info_layout.addWidget(self.artist_name)

        self.album_name = QLabel("")
        self.album_name.setObjectName("albumLabel")
        self.album_name.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.album_name.setWordWrap(True)
        self.album_name.setProperty("role", "caption")
        info_layout.addWidget(self.album_name)

        self.card_layout.addLayout(info_layout)

        self.progress_slider = QSlider(Qt.Orientation.Horizontal)
        self.progress_slider.setObjectName("progressSlider")
        self.progress_slider.setMinimum(0)
        self.progress_slider.setMaximum(100)
        self.progress_slider.setValue(0)
        self.progress_slider.sliderPressed.connect(self.slider_pressed)
        self.progress_slider.sliderReleased.connect(self.slider_released)
        self.card_layout.addWidget(self.progress_slider)

        time_layout = QHBoxLayout()
        time_layout.setSpacing(10)

        self.time_current = QLabel("0:00")
        self.time_current.setObjectName("timeCurrent")
        self.time_current.setProperty("role", "caption")

        self.time_total = QLabel("0:00")
        self.time_total.setObjectName("timeTotal")
        self.time_total.setProperty("role", "caption")

        time_layout.addWidget(self.time_current)
        time_layout.addStretch()
        time_layout.addWidget(self.time_total)
        self.card_layout.addLayout(time_layout)

        controls = QHBoxLayout()
        controls.setSpacing(18)

        self.prev_btn = QPushButton("⏮")
        self.prev_btn.setProperty("variant", "roundSurface")
        self.prev_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.prev_btn.clicked.connect(self.previous_track)

        self.play_pause_btn = QPushButton("▶")
        self.play_pause_btn.setProperty("variant", "roundAccent")
        self.play_pause_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.play_pause_btn.clicked.connect(self.toggle_playback)

        self.next_btn = QPushButton("⏭")
        self.next_btn.setProperty("variant", "roundSurface")
        self.next_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.next_btn.clicked.connect(self.next_track)

        for btn in (self.prev_btn, self.play_pause_btn, self.next_btn):
            btn.setMinimumSize(0, 0)
            btn.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

        self.control_buttons = (self.prev_btn, self.play_pause_btn, self.next_btn)

        controls.addStretch()
        controls.addWidget(self.prev_btn)
        controls.addWidget(self.play_pause_btn)
        controls.addWidget(self.next_btn)
        controls.addStretch()
        self.card_layout.addLayout(controls)
        self.controls_layout = controls

        self.content_layout.addWidget(self.card, alignment=Qt.AlignmentFlag.AlignHCenter)
        self.content_layout.addStretch(1)
        self.content_layout.setStretch(0, 1)
        self.content_layout.setStretch(1, 0)

        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.addWidget(self.scroll_area)

        self.setup_styles()
        self.adjust_layout()

        # Slider tracking
        self.slider_being_dragged = False
        
    def setup_timer(self):
        """타이머 설정 - 재생 상태 업데이트"""
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_playback)
        self.timer.start(config.PLAYBACK_UPDATE_INTERVAL)
        
    def update_playback(self):
        """재생 상태 업데이트"""
        playback = self.parent.spotify.get_current_playback()
        
        if not playback or not playback.get('item'):
            # No track playing
            if self.current_track is not None:
                self.track_name.setText("No track playing")
                self.artist_name.setText("Start playing music from search or library")
                self.album_name.setText("")
                self.play_pause_btn.setText("▶")
                self.current_track = None
            return
        
        track = playback['item']
        self.current_track = track
        
        # Update track info
        self.track_name.setText(track.get('name', 'Unknown'))
        
        artists = track.get('artists', [])
        artist_text = ', '.join([a.get('name', 'Unknown') for a in artists]) if artists else 'Unknown Artist'
        self.artist_name.setText(artist_text)
        
        album = track.get('album', {})
        self.album_name.setText(album.get('name', ''))
        
        # Update progress
        progress_ms = playback.get('progress_ms', 0)
        duration_ms = track.get('duration_ms', 1)
        
        if duration_ms > 0 and not self.slider_being_dragged:
            progress_percent = int((progress_ms / duration_ms) * 100)
            self.progress_slider.setMaximum(duration_ms)
            self.progress_slider.setValue(progress_ms)
            
            self.time_current.setText(self.format_time(progress_ms))
            self.time_total.setText(self.format_time(duration_ms))
        
        # Update play/pause button
        self.is_playing = playback.get('is_playing', False)
        self.play_pause_btn.setText("⏸" if self.is_playing else "▶")
        
    def toggle_playback(self):
        """재생/일시정지 토글"""
        if self.is_playing:
            self.parent.spotify.pause()
            print("⏸ Paused")
        else:
            self.parent.spotify.resume()
            print("▶ Resumed")
        
        # Immediate UI update
        self.is_playing = not self.is_playing
        self.play_pause_btn.setText("⏸" if self.is_playing else "▶")
        
    def previous_track(self):
        """이전 트랙"""
        self.parent.spotify.previous_track()
        print("⏮ Previous track")
        
    def next_track(self):
        """다음 트랙"""
        self.parent.spotify.next_track()
        print("⏭ Next track")
        
    def slider_pressed(self):
        """슬라이더 드래그 시작"""
        self.slider_being_dragged = True
        
    def slider_released(self):
        """슬라이더 드래그 종료 - 위치 이동"""
        self.slider_being_dragged = False
        position_ms = self.progress_slider.value()
        self.parent.spotify.seek_to_position(position_ms)
        print(f"⏩ Seek to {position_ms}ms")
        
    def format_time(self, ms):
        """밀리초를 MM:SS 형식으로 변환"""
        if not ms:
            return "0:00"
        
        seconds = ms // 1000
        minutes = seconds // 60
        seconds = seconds % 60
        
        return f"{minutes}:{seconds:02d}"
    
    def setup_styles(self):
        """기본 스타일 템플릿 저장"""
        self._base_style = (
            BASE_STYLESHEET
            + f"""
            QWidget#playerScreen {{
                background: {config.GRADIENT_NIGHTFALL};
            }}

            QWidget#playerScreen QLabel#albumArt {{
                background: qradialgradient(
                    cx:0.5, cy:0.45, radius:0.9,
                    stop:0 rgba(102, 255, 224, 0.25),
                    stop:1 rgba(17, 22, 30, 0.95)
                );
                border-radius: 22px;
                border: 1px solid rgba(255, 255, 255, 0.07);
                color: {config.COLOR_TEXT};
            }}

            QWidget#playerScreen QLabel#trackTitle {{
                font-weight: 800;
            }}

            QWidget#playerScreen QLabel#artistLabel {{
                color: {config.COLOR_TEXT_SECONDARY};
            }}

            QWidget#playerScreen QLabel#albumLabel {{
                color: rgba(255, 255, 255, 0.65);
                letter-spacing: 0.4px;
            }}

            QWidget#playerScreen QLabel#timeCurrent,
            QWidget#playerScreen QLabel#timeTotal {{
                color: rgba(255, 255, 255, 0.6);
            }}

            QWidget#playerScreen QPushButton[variant="roundSurface"] {{
                background-color: rgba(255, 255, 255, 0.08);
                border-radius: 18px;
            }}

            QWidget#playerScreen QPushButton[variant="roundSurface"]:hover {{
                background-color: rgba(255, 255, 255, 0.18);
            }}
            """
        )

    def adjust_layout(self):
        """현재 창 크기에 맞춰 레이아웃 요소 조정"""
        width = max(320, self.width())
        margin_side = max(10, int(width * 0.045))
        margin_top = max(6, int(width * 0.015))
        margin_bottom = max(10, int(width * 0.035))
        self.content_layout.setContentsMargins(margin_side, margin_top, margin_side, margin_bottom)

        if self.card:
            max_width = int(width * 0.92)
            self.card.setMaximumWidth(max_width)
            self.card.setMinimumWidth(min(max_width, width - (margin_side * 2)))

        current_height = self.height()
        height = current_height if current_height > 0 else config.SCREEN_HEIGHT

        available_height = max(260, height - (margin_top + margin_bottom))

        base_scale = compute_responsive_scale(width, height)
        height_scale = available_height / 580.0
        effective_scale = max(0.25, min(base_scale, height_scale))

        self.content_layout.setSpacing(max(8, int(round(18 * effective_scale))))

        if hasattr(self, "card_layout"):
            card_margin = max(12, int(round(24 * effective_scale)))
            self.card_layout.setContentsMargins(card_margin, card_margin, card_margin, card_margin)
            self.card_layout.setSpacing(max(6, int(round(16 * effective_scale))))

        if hasattr(self, "info_layout"):
            self.info_layout.setSpacing(max(3, int(round(6 * effective_scale))))

        if hasattr(self, "controls_layout"):
            self.controls_layout.setSpacing(max(6, int(round(14 * effective_scale))))

        self.progress_slider.setFixedHeight(max(8, int(round(14 * effective_scale))))

        if hasattr(self, "back_btn"):
            self.back_btn.setMinimumHeight(max(36, int(round(64 * effective_scale))))
            min_back_width = max(96, int(round(160 * effective_scale)))
            max_back_width = max(120, int(width * 0.45))
            self.back_btn.setMinimumWidth(min(min_back_width, max_back_width))

        # Album art scales with available width and height
        art_base = self.card.width() if self.card.width() > 0 else width
        art_height_cap = max(90, int(available_height * 0.48))
        base_art_width = min(int(art_base * 0.4), int(width * 0.42))
        art_size = max(
            72,
            min(
                int(round(240 * effective_scale)),
                base_art_width,
                art_height_cap,
            ),
        )
        self.album_art.setFixedSize(art_size, art_size)

        # Control buttons adjust proportionally but stay compact
        side_btn = max(28, min(int(round(52 * effective_scale)), art_size - 12))
        center_btn = max(32, min(int(round(64 * effective_scale)), art_size - 8))

        self.prev_btn.setFixedSize(side_btn, side_btn)
        self.next_btn.setFixedSize(side_btn, side_btn)
        self.play_pause_btn.setFixedSize(center_btn, center_btn)

        self.update_dynamic_style(width, height, art_size=art_size, scale_override=effective_scale)

    def update_dynamic_style(self, width, height, art_size=None, scale_override=None):
        """화면 크기에 맞춰 텍스트와 패딩 조정"""
        scale = scale_override if scale_override is not None else compute_responsive_scale(width, height)

        scaling_config = []
        if hasattr(self, "back_btn"):
            scaling_config.append(("back", self.back_btn, 12, 9))
        if hasattr(self, "track_name"):
            scaling_config.append(("title", self.track_name, 18, 12))
        if hasattr(self, "artist_name"):
            scaling_config.append(("subtitle", self.artist_name, 14, 10))
        if hasattr(self, "album_name"):
            scaling_config.append(("caption", self.album_name, 11, 9))
        if hasattr(self, "time_current"):
            scaling_config.append(("time", self.time_current, 10, 9))
        if hasattr(self, "time_total"):
            scaling_config.append(("time", self.time_total, 10, 9))
        if hasattr(self, "prev_btn"):
            scaling_config.append(("control_small", self.prev_btn, 15, 11))
        if hasattr(self, "next_btn"):
            scaling_config.append(("control_small", self.next_btn, 15, 11))
        if hasattr(self, "play_pause_btn"):
            scaling_config.append(("control_primary", self.play_pause_btn, 18, 14))
        if hasattr(self, "album_art"):
            scaling_config.append(("art", self.album_art, 52, 36))

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

        back_pt = applied_map.get("back", [11])[0]
        title_pt = applied_map.get("title", [16])[0]
        subtitle_pt = applied_map.get("subtitle", [13])[0]
        caption_pt = applied_map.get("caption", [11])[0]
        time_pt = applied_map.get("time", [10])[0]
        control_small_pt = applied_map.get("control_small", [15])[0]
        control_primary_pt = applied_map.get("control_primary", [18])[0]
        art_pt = applied_map.get("art", [48])[0]

        back_vpad, back_hpad = scale_padding(
            base_vertical=12,
            base_horizontal=20,
            scale=scale,
            min_vertical=6,
            min_horizontal=10,
        )

        art_dimension = art_size if art_size else max(200, int(240 * scale))
        art_padding = max(12, int(round(art_dimension * 0.08)))

        dynamic_style = f"""
            QWidget#playerScreen QPushButton#playerBackButton {{
                font-size: {back_pt}pt;
                padding: {back_vpad}px {back_hpad}px;
            }}

            QWidget#playerScreen QLabel#trackTitle {{
                font-size: {title_pt}pt;
            }}

            QWidget#playerScreen QLabel#artistLabel {{
                font-size: {subtitle_pt}pt;
            }}

            QWidget#playerScreen QLabel#albumLabel {{
                font-size: {caption_pt}pt;
            }}

            QWidget#playerScreen QLabel#timeCurrent,
            QWidget#playerScreen QLabel#timeTotal {{
                font-size: {time_pt}pt;
            }}

            QWidget#playerScreen QLabel#albumArt {{
                font-size: {art_pt}pt;
                padding: {art_padding}px;
            }}

            QWidget#playerScreen QPushButton[variant="roundSurface"] {{
                font-size: {control_small_pt}pt;
            }}

            QWidget#playerScreen QPushButton[variant="roundAccent"] {{
                font-size: {control_primary_pt}pt;
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
        # Immediately update playback
        self.update_playback()
        self.adjust_layout()
