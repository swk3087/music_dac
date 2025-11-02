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
from ui_styles import BASE_STYLESHEET


class PlayerScreen(QWidget):
    """플레이어 화면 클래스"""
    
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.current_track = None
        self.is_playing = False
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

        self.content_layout = QVBoxLayout(container)
        self.content_layout.setSpacing(20)
        self.content_layout.setContentsMargins(0, 0, 0, 0)

        header_layout = QHBoxLayout()
        header_layout.setSpacing(14)

        back_btn = QPushButton("← Back")
        back_btn.setProperty("variant", "ghost")
        back_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        back_btn.setFixedWidth(170)
        back_btn.clicked.connect(self.parent.go_back)
        header_layout.addWidget(back_btn)
        self.back_btn = back_btn
        header_layout.addStretch()
        self.content_layout.addLayout(header_layout)

        self.card = QFrame()
        self.card.setObjectName("card")
        self.card.setFrameShape(QFrame.Shape.NoFrame)

        self.card_layout = QVBoxLayout(self.card)
        self.card_layout.setContentsMargins(28, 28, 28, 28)
        self.card_layout.setSpacing(18)

        self.album_art = QLabel("🎧")
        self.album_art.setObjectName("albumArt")
        self.album_art.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.album_art.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.card_layout.addWidget(self.album_art, alignment=Qt.AlignmentFlag.AlignCenter)

        info_layout = QVBoxLayout()
        info_layout.setSpacing(6)
        info_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)

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

        controls.addStretch()
        controls.addWidget(self.prev_btn)
        controls.addWidget(self.play_pause_btn)
        controls.addWidget(self.next_btn)
        controls.addStretch()
        self.card_layout.addLayout(controls)

        self.content_layout.addWidget(self.card, alignment=Qt.AlignmentFlag.AlignHCenter)
        self.content_layout.addStretch(1)

        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.addWidget(self.scroll_area)

        self.apply_styles()
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
    
    def apply_styles(self):
        """스타일시트 적용"""
        self.setStyleSheet(
            BASE_STYLESHEET
            + f"""
            QWidget#playerScreen {{
                background: {config.GRADIENT_NIGHTFALL};
            }}

            QWidget#playerScreen QLabel#albumArt {{
                font-size: 680%;
                background: qradialgradient(
                    cx:0.5, cy:0.45, radius:0.9,
                    stop:0 rgba(102, 255, 224, 0.25),
                    stop:1 rgba(17, 22, 30, 0.95)
                );
                border-radius: 22px;
                border: 1px solid rgba(255, 255, 255, 0.07);
                padding: 2.4em;
            }}

            QWidget#playerScreen QLabel#trackTitle {{
                font-size: 170%;
                font-weight: 800;
            }}

            QWidget#playerScreen QLabel#artistLabel {{
                color: {config.COLOR_TEXT_SECONDARY};
                font-size: 120%;
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
                border-radius: 36px;
                font-size: 165%;
            }}

            QWidget#playerScreen QPushButton[variant="roundSurface"]:hover {{
                background-color: rgba(255, 255, 255, 0.18);
            }}

            QWidget#playerScreen QPushButton[variant="roundAccent"] {{
                font-size: 210%;
            }}
            """
        )

    def adjust_layout(self):
        """현재 창 크기에 맞춰 레이아웃 요소 조정"""
        width = max(320, self.width())
        margin_side = max(10, int(width * 0.045))
        margin_top = max(6, int(width * 0.015))
        margin_bottom = max(10, int(width * 0.04))
        self.content_layout.setContentsMargins(margin_side, margin_top, margin_side, margin_bottom)

        if self.card:
            max_width = int(width * 0.92)
            self.card.setMaximumWidth(max_width)
            self.card.setMinimumWidth(min(max_width, width - (margin_side * 2)))

        if hasattr(self, "back_btn"):
            self.back_btn.setMinimumHeight(max(44, int(width * 0.08)))

        # Album art scales with available width
        art_base = self.card.width() if self.card.width() > 0 else width
        art_size = max(160, min(320, int(art_base * 0.45)))
        self.album_art.setFixedSize(art_size, art_size)

        # Control buttons adjust proportionally
        side_btn = max(56, int(art_size * 0.26))
        center_btn = max(72, int(art_size * 0.32))

        self.prev_btn.setFixedSize(side_btn, side_btn)
        self.next_btn.setFixedSize(side_btn, side_btn)
        self.play_pause_btn.setFixedSize(center_btn, center_btn)

    def resizeEvent(self, event):
        """창 크기 변경 대응"""
        super().resizeEvent(event)
        self.adjust_layout()

    def showEvent(self, event):
        """화면 표시시 호출"""
        super().showEvent(event)
        # Immediately update playback
        self.update_playback()
