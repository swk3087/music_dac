"""
Detail Screen
플레이리스트/앨범/아티스트의 트랙 상세 목록 화면
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
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
import config
from ui_styles import BASE_STYLESHEET


class TrackLoadWorker(QThread):
    """트랙 데이터 로딩 Worker"""
    finished = pyqtSignal(list)
    
    def __init__(self, spotify_manager, item_type, item_id):
        super().__init__()
        self.spotify = spotify_manager
        self.item_type = item_type
        self.item_id = item_id
        
    def run(self):
        tracks = []
        try:
            if self.item_type == 'playlist':
                results = self.spotify.get_playlist_tracks(self.item_id)
                tracks = [item['track'] for item in results if item.get('track')]
            elif self.item_type == 'album':
                tracks = self.spotify.get_album_tracks(self.item_id)
            elif self.item_type == 'artist':
                tracks = self.spotify.get_artist_top_tracks(self.item_id)
        except Exception as e:
            print(f"Failed to load tracks: {e}")
        
        self.finished.emit(tracks)


class DetailScreen(QWidget):
    """상세 화면 클래스"""
    
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.current_item = None
        self.current_type = None
        self.tracks = []
        self.worker = None
        self.buttons = []
        self.setup_ui()
        
    def setup_ui(self):
        """UI 구성"""
        self.setObjectName("detailScreen")

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
        self.back_btn.clicked.connect(self.go_back)
        header.addWidget(self.back_btn)
        self.buttons.append(self.back_btn)

        header.addStretch()

        self.play_all_btn = QPushButton("▶ Play All")
        self.play_all_btn.setProperty("variant", "accent")
        self.play_all_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.play_all_btn.clicked.connect(self.play_all)
        header.addWidget(self.play_all_btn)
        self.buttons.append(self.play_all_btn)

        self.content_layout.addLayout(header)

        self.card = QFrame()
        self.card.setObjectName("card")
        self.card.setFrameShape(QFrame.Shape.NoFrame)

        self.card_layout = QVBoxLayout(self.card)
        self.card_layout.setContentsMargins(24, 24, 24, 24)
        self.card_layout.setSpacing(16)

        self.title_label = QLabel("Title")
        self.title_label.setObjectName("titleLabel")
        self.title_label.setProperty("role", "title")
        self.title_label.setWordWrap(True)
        self.card_layout.addWidget(self.title_label)

        self.subtitle_label = QLabel("")
        self.subtitle_label.setObjectName("subtitleLabel")
        self.subtitle_label.setProperty("role", "subtitle")
        self.subtitle_label.setWordWrap(True)
        self.card_layout.addWidget(self.subtitle_label)

        self.stats_label = QLabel("")
        self.stats_label.setObjectName("statsLabel")
        self.stats_label.setProperty("role", "caption")
        self.card_layout.addWidget(self.stats_label)

        self.loading_label = QLabel("Loading tracks…")
        self.loading_label.setObjectName("loadingLabel")
        self.loading_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.loading_label.hide()
        self.card_layout.addWidget(self.loading_label)

        tracks_section = QFrame()
        tracks_section.setObjectName("section")

        tracks_layout = QVBoxLayout(tracks_section)
        tracks_layout.setContentsMargins(20, 20, 20, 20)
        tracks_layout.setSpacing(12)

        tracks_label = QLabel("Tracks")
        tracks_label.setObjectName("tracksLabel")
        tracks_label.setProperty("role", "subtitle")
        tracks_layout.addWidget(tracks_label)

        self.tracks_list = QListWidget()
        self.tracks_list.setObjectName("tracksList")
        self.tracks_list.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.tracks_list.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.tracks_list.itemDoubleClicked.connect(self.play_track)
        tracks_layout.addWidget(self.tracks_list)

        self.card_layout.addWidget(tracks_section)

        self.content_layout.addWidget(self.card, alignment=Qt.AlignmentFlag.AlignHCenter)
        self.content_layout.addStretch(1)

        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.addWidget(self.scroll_area)

        self.apply_styles()
        self.adjust_layout()
        
    def load_playlist(self, playlist):
        """플레이리스트 로드"""
        self.current_item = playlist
        self.current_type = 'playlist'
        
        # Update info
        name = playlist.get('name', 'Unknown Playlist')
        self.title_label.setText(f"📝 {name}")
        
        owner = playlist.get('owner', {}).get('display_name', 'Unknown')
        self.subtitle_label.setText(f"by {owner}")
        
        track_count = playlist.get('tracks', {}).get('total', 0)
        self.stats_label.setText(f"🎵 {track_count} tracks")
        
        # Load tracks
        playlist_id = playlist.get('id')
        if playlist_id:
            self.load_tracks('playlist', playlist_id)
        
    def load_album(self, album):
        """앨범 로드"""
        self.current_item = album
        self.current_type = 'album'
        
        # Update info
        name = album.get('name', 'Unknown Album')
        self.title_label.setText(f"💿 {name}")
        
        artists = album.get('artists', [])
        artist_text = ', '.join([a.get('name', 'Unknown') for a in artists]) if artists else 'Unknown'
        self.subtitle_label.setText(f"by {artist_text}")
        
        track_count = album.get('total_tracks', 0)
        release_date = album.get('release_date', 'Unknown')[:4]
        self.stats_label.setText(f"🎵 {track_count} tracks | 📅 {release_date}")
        
        # Load tracks
        album_id = album.get('id')
        if album_id:
            self.load_tracks('album', album_id)
        
    def load_artist(self, artist):
        """아티스트 로드"""
        self.current_item = artist
        self.current_type = 'artist'
        
        # Update info
        name = artist.get('name', 'Unknown Artist')
        self.title_label.setText(f"🎤 {name}")
        
        genres = artist.get('genres', [])
        genre_text = ', '.join(genres[:3]) if genres else 'Various genres'
        self.subtitle_label.setText(f"🎵 {genre_text}")
        
        followers = artist.get('followers', {}).get('total', 0)
        if followers >= 1000000:
            followers_text = f"{followers / 1000000:.1f}M"
        elif followers >= 1000:
            followers_text = f"{followers / 1000:.1f}K"
        else:
            followers_text = str(followers)
        
        popularity = artist.get('popularity', 0)
        self.stats_label.setText(f"👥 {followers_text} followers | ⭐ {popularity}% popularity")
        
        # Load top tracks
        artist_id = artist.get('id')
        if artist_id:
            self.load_tracks('artist', artist_id)
        
    def load_tracks(self, item_type, item_id):
        """트랙 로드 시작"""
        if not item_id:
            self.tracks_list.addItem("Error: Invalid ID")
            return
        
        self.loading_label.show()
        self.tracks_list.clear()
        
        self.worker = TrackLoadWorker(self.parent.spotify, item_type, item_id)
        self.worker.finished.connect(self.display_tracks)
        self.worker.start()
        
    def display_tracks(self, tracks):
        """트랙 목록 표시"""
        self.loading_label.hide()
        self.tracks = tracks
        self.tracks_list.clear()
        
        if not tracks:
            self.tracks_list.addItem("No tracks found")
            self.play_all_btn.setEnabled(False)
            return
        
        self.play_all_btn.setEnabled(True)
        
        for idx, track in enumerate(tracks, 1):
            if not track:
                continue
            
            track_name = track.get('name', 'Unknown')
            
            # Artist names
            artists = track.get('artists', [])
            if artists:
                artist_names = ', '.join([a.get('name', 'Unknown') for a in artists])
            else:
                artist_names = 'Unknown'
            
            # Duration
            duration_ms = track.get('duration_ms', 0)
            duration_min = duration_ms // 60000
            duration_sec = (duration_ms % 60000) // 1000
            
            # Display format
            item_text = f"{idx}. {track_name}\n   👤 {artist_names} | ⏱ {duration_min}:{duration_sec:02d}"
            
            item = QListWidgetItem(item_text)
            item.setData(Qt.ItemDataRole.UserRole, track)
            self.tracks_list.addItem(item)
    
    def play_track(self, item):
        """선택한 트랙 재생"""
        track = item.data(Qt.ItemDataRole.UserRole)
        
        if track and track.get('uri'):
            uri = track['uri']
            self.parent.spotify.play_track(uri)
            # Navigate to player screen
            self.parent.navigate_to(6)
        else:
            print("❌ No valid track URI")
    
    def play_all(self):
        """모든 트랙 재생"""
        if not self.tracks or len(self.tracks) == 0:
            print("❌ No tracks to play")
            return
        
        # Get all valid URIs
        uris = []
        for track in self.tracks:
            if track and track.get('uri'):
                uris.append(track['uri'])
        
        if not uris:
            print("❌ No valid track URIs")
            return
        
        try:
            self.parent.spotify.play_tracks(uris)
            print(f"▶ Playing {len(uris)} tracks")
            # Navigate to player screen
            self.parent.navigate_to(6)
        except Exception as e:
            print(f"❌ Failed to play all: {e}")
    
    def go_back(self):
        """뒤로 가기"""
        if self.current_type == 'playlist':
            self.parent.navigate_to(3)
        elif self.current_type == 'album':
            self.parent.navigate_to(4)
        elif self.current_type == 'artist':
            self.parent.navigate_to(5)
        else:
            self.parent.go_back()
    
    def apply_styles(self):
        """스타일 시트 적용"""
        self.setStyleSheet(
            BASE_STYLESHEET
            + f"""
            QWidget#detailScreen {{
                background: {config.GRADIENT_NIGHTFALL};
            }}

            QWidget#detailScreen QLabel#titleLabel {{
                font-size: 205%;
                font-weight: 820;
                color: {config.COLOR_TEXT};
            }}

            QWidget#detailScreen QLabel#subtitleLabel {{
                color: {config.COLOR_TEXT_SECONDARY};
            }}

            QWidget#detailScreen QLabel#statsLabel {{
                color: rgba(255, 255, 255, 0.65);
            }}

            QWidget#detailScreen QLabel#loadingLabel {{
                padding: 1.1em;
                color: {config.COLOR_PRIMARY};
            }}

            QWidget#detailScreen QPushButton[variant="accent"]:disabled {{
                background: rgba(255, 255, 255, 0.22);
                color: rgba(14, 17, 23, 0.55);
            }}

            QWidget#detailScreen QListWidget#tracksList {{
                font-size: 105%;
                line-height: 1.45em;
            }}

            QWidget#detailScreen QListWidget#tracksList::item {{
                padding: 12px 12px;
                border-radius: 10px;
                margin: 2px 0;
                border: 1px solid transparent;
            }}

            QWidget#detailScreen QListWidget#tracksList::item:selected {{
                border-color: rgba(102, 255, 224, 0.35);
                background-color: rgba(102, 255, 224, 0.18);
            }}

            QWidget#detailScreen QListWidget#tracksList::item:hover {{
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

        button_height = max(44, int(width * 0.085))
        for btn in self.buttons:
            btn.setMinimumHeight(button_height)
            btn.setMinimumWidth(max(110, int(width * 0.24)))

    def resizeEvent(self, event):
        """창 크기 변경 대응"""
        super().resizeEvent(event)
        self.adjust_layout()
