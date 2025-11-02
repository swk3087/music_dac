"""
Spotify API Manager
Spotify API 관리 및 음악 재생 제어
"""

import spotipy
from spotipy.oauth2 import SpotifyOAuth
from PyQt6.QtCore import QObject, pyqtSignal
import config


class SpotifyManager(QObject):
    """Spotify API 관리 클래스"""
    
    # Signals
    playback_changed = pyqtSignal(dict)
    error_occurred = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.sp = None
        self.current_playback = None
        self.authenticate()
        
    def authenticate(self):
        """Spotify 인증"""
        try:
            auth_manager = SpotifyOAuth(
                client_id=config.SPOTIFY_CLIENT_ID,
                client_secret=config.SPOTIFY_CLIENT_SECRET,
                redirect_uri=config.SPOTIFY_REDIRECT_URI,
                scope=config.SPOTIFY_SCOPE,
                open_browser=True
            )
            
            self.sp = spotipy.Spotify(auth_manager=auth_manager)
            
            # Test connection
            user = self.sp.current_user()
            print(f"✅ Spotify authenticated as: {user['display_name']}")
            
        except Exception as e:
            error_msg = f"Spotify authentication failed: {e}"
            print(f"❌ {error_msg}")
            self.error_occurred.emit(error_msg)
            
    # ==============================================
    # Search Functions
    # ==============================================
    
    def search(self, query, search_type='track', limit=20):
        """
        검색 수행
        
        Args:
            query (str): 검색어
            search_type (str): 'track', 'album', 'artist', 'playlist'
            limit (int): 결과 개수
            
        Returns:
            dict: 검색 결과
        """
        try:
            if not query or not query.strip():
                return None
                
            results = self.sp.search(
                q=query,
                type=search_type,
                limit=limit,
                market='KR'
            )
            return results
            
        except Exception as e:
            print(f"❌ Search failed: {e}")
            self.error_occurred.emit(f"Search failed: {e}")
            return None
    
    # ==============================================
    # Library Functions
    # ==============================================
    
    def get_user_playlists(self, limit=50):
        """사용자 플레이리스트 가져오기"""
        try:
            playlists = self.sp.current_user_playlists(limit=limit)
            return playlists['items']
        except Exception as e:
            print(f"❌ Failed to get playlists: {e}")
            self.error_occurred.emit(f"Failed to get playlists: {e}")
            return []
    
    def get_playlist_tracks(self, playlist_id):
        """플레이리스트의 트랙 가져오기"""
        try:
            results = self.sp.playlist_tracks(playlist_id)
            return results['items']
        except Exception as e:
            print(f"❌ Failed to get playlist tracks: {e}")
            self.error_occurred.emit(f"Failed to get playlist tracks: {e}")
            return []
    
    def get_saved_albums(self, limit=50):
        """저장된 앨범 가져오기"""
        try:
            albums = self.sp.current_user_saved_albums(limit=limit)
            return albums['items']
        except Exception as e:
            print(f"❌ Failed to get albums: {e}")
            self.error_occurred.emit(f"Failed to get albums: {e}")
            return []
    
    def get_album_tracks(self, album_id):
        """앨범의 트랙 가져오기"""
        try:
            results = self.sp.album_tracks(album_id)
            return results['items']
        except Exception as e:
            print(f"❌ Failed to get album tracks: {e}")
            self.error_occurred.emit(f"Failed to get album tracks: {e}")
            return []
    
    def get_followed_artists(self, limit=50):
        """팔로우한 아티스트 가져오기"""
        try:
            artists = self.sp.current_user_followed_artists(limit=limit)
            return artists['artists']['items']
        except Exception as e:
            print(f"❌ Failed to get artists: {e}")
            self.error_occurred.emit(f"Failed to get artists: {e}")
            return []
    
    def get_artist_top_tracks(self, artist_id):
        """아티스트의 인기 트랙 가져오기"""
        try:
            results = self.sp.artist_top_tracks(artist_id, country='KR')
            return results['tracks']
        except Exception as e:
            print(f"❌ Failed to get artist top tracks: {e}")
            self.error_occurred.emit(f"Failed to get artist top tracks: {e}")
            return []
    
    # ==============================================
    # Playback Control Functions
    # ==============================================
    
    def play_track(self, uri):
        """
        트랙 재생
        
        Args:
            uri (str): Spotify URI (예: 'spotify:track:...')
        """
        try:
            # Check if URI is valid
            if not uri or not uri.startswith('spotify:'):
                print(f"❌ Invalid URI: {uri}")
                return
            
            self.sp.start_playback(uris=[uri])
            print(f"▶️  Playing: {uri}")
            
        except Exception as e:
            error_msg = f"Playback failed: {e}"
            print(f"❌ {error_msg}")
            self.error_occurred.emit(error_msg)
    
    def play_tracks(self, uris):
        """
        여러 트랙 재생
        
        Args:
            uris (list): Spotify URI 리스트
        """
        try:
            if not uris or len(uris) == 0:
                return
            
            self.sp.start_playback(uris=uris)
            print(f"▶️  Playing {len(uris)} tracks")
            
        except Exception as e:
            error_msg = f"Playback failed: {e}"
            print(f"❌ {error_msg}")
            self.error_occurred.emit(error_msg)
    
    def pause(self):
        """재생 일시정지"""
        try:
            self.sp.pause_playback()
            print("⏸️  Paused")
        except Exception as e:
            print(f"❌ Pause failed: {e}")
            self.error_occurred.emit(f"Pause failed: {e}")
    
    def resume(self):
        """재생 재개"""
        try:
            self.sp.start_playback()
            print("▶️  Resumed")
        except Exception as e:
            print(f"❌ Resume failed: {e}")
            self.error_occurred.emit(f"Resume failed: {e}")
    
    def next_track(self):
        """다음 트랙"""
        try:
            self.sp.next_track()
            print("⏭️  Next track")
        except Exception as e:
            print(f"❌ Next track failed: {e}")
            self.error_occurred.emit(f"Next track failed: {e}")
    
    def previous_track(self):
        """이전 트랙"""
        try:
            self.sp.previous_track()
            print("⏮️  Previous track")
        except Exception as e:
            print(f"❌ Previous track failed: {e}")
            self.error_occurred.emit(f"Previous track failed: {e}")
    
    def seek_to_position(self, position_ms):
        """
        특정 위치로 이동
        
        Args:
            position_ms (int): 위치 (밀리초)
        """
        try:
            self.sp.seek_track(position_ms)
            print(f"⏩ Seek to {position_ms}ms")
        except Exception as e:
            print(f"❌ Seek failed: {e}")
            self.error_occurred.emit(f"Seek failed: {e}")
    
    def set_volume(self, volume_percent):
        """
        볼륨 설정
        
        Args:
            volume_percent (int): 볼륨 (0-100)
        """
        try:
            volume_percent = max(0, min(100, volume_percent))
            self.sp.volume(volume_percent)
            print(f"🔊 Volume set to {volume_percent}%")
        except Exception as e:
            print(f"❌ Volume change failed: {e}")
            self.error_occurred.emit(f"Volume change failed: {e}")
    
    # ==============================================
    # Playback State Functions
    # ==============================================
    
    def get_current_playback(self):
        """
        현재 재생 상태 가져오기
        
        Returns:
            dict: 재생 상태 정보
        """
        try:
            playback = self.sp.current_playback()
            
            if playback:
                self.current_playback = playback
                self.playback_changed.emit(playback)
            
            return playback
            
        except Exception as e:
            if config.DEBUG_MODE:
                print(f"❌ Failed to get playback: {e}")
            return None
    
    def is_playing(self):
        """현재 재생 중인지 확인"""
        playback = self.get_current_playback()
        if playback:
            return playback.get('is_playing', False)
        return False
    
    def get_current_track(self):
        """현재 재생 중인 트랙 정보"""
        playback = self.get_current_playback()
        if playback and playback.get('item'):
            return playback['item']
        return None
    
    # ==============================================
    # Device Functions
    # ==============================================
    
    def get_available_devices(self):
        """사용 가능한 재생 장치 목록"""
        try:
            devices = self.sp.devices()
            return devices['devices']
        except Exception as e:
            print(f"❌ Failed to get devices: {e}")
            return []
    
    def transfer_playback(self, device_id):
        """재생을 다른 장치로 전환"""
        try:
            self.sp.transfer_playback(device_id)
            print(f"📱 Playback transferred to device: {device_id}")
        except Exception as e:
            print(f"❌ Transfer failed: {e}")
            self.error_occurred.emit(f"Transfer failed: {e}")