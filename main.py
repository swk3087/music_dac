"""
Music Streaming DAC - Main Application
메인 애플리케이션 진입점
"""

import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QStackedWidget
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

# Import screens
from screens.home_screen import HomeScreen
from screens.search_screen import SearchScreen
from screens.ai_search_screen import AISearchScreen
from screens.playlist_screen import PlaylistScreen
from screens.album_screen import AlbumScreen
from screens.artist_screen import ArtistScreen
from screens.player_screen import PlayerScreen
from screens.detail_screen import DetailScreen

# Import managers
from spotify_manager import SpotifyManager
from ai_manager import AIManager

# Import config
import config


class MusicDACApp(QMainWindow):
    """메인 애플리케이션 클래스"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Music Streaming DAC")
        self.setGeometry(100, 100, config.SCREEN_WIDTH, config.SCREEN_HEIGHT)
        
        # Set application font
        font = QFont("Arial", config.FONT_SIZE_MEDIUM)
        QApplication.instance().setFont(font)
        
        # Initialize managers
        print("Initializing Spotify Manager...")
        self.spotify = SpotifyManager()
        
        print("Initializing AI Manager...")
        self.ai = AIManager()
        
        # Setup UI
        self.setup_ui()
        
        print("Application initialized successfully!")
        
    def setup_ui(self):
        """UI 초기화"""
        # Central widget with stacked layout
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)
        
        # Create screens
        print("Creating screens...")
        self.home_screen = HomeScreen(self)
        self.search_screen = SearchScreen(self)
        self.ai_search_screen = AISearchScreen(self)
        self.playlist_screen = PlaylistScreen(self)
        self.album_screen = AlbumScreen(self)
        self.artist_screen = ArtistScreen(self)
        self.player_screen = PlayerScreen(self)
        self.detail_screen = DetailScreen(self)
        
        # Add screens to stack
        self.stacked_widget.addWidget(self.home_screen)      # 0
        self.stacked_widget.addWidget(self.search_screen)    # 1
        self.stacked_widget.addWidget(self.ai_search_screen) # 2
        self.stacked_widget.addWidget(self.playlist_screen)  # 3
        self.stacked_widget.addWidget(self.album_screen)     # 4
        self.stacked_widget.addWidget(self.artist_screen)    # 5
        self.stacked_widget.addWidget(self.player_screen)    # 6
        self.stacked_widget.addWidget(self.detail_screen)    # 7
        
        # Set initial screen
        self.stacked_widget.setCurrentIndex(0)
        
    def navigate_to(self, screen_index):
        """
        특정 화면으로 이동
        
        Args:
            screen_index (int): 화면 인덱스 (0-7)
        """
        if 0 <= screen_index < self.stacked_widget.count():
            self.stacked_widget.setCurrentIndex(screen_index)
            print(f"Navigated to screen {screen_index}")
        
    def go_back(self):
        """홈 화면으로 돌아가기"""
        self.stacked_widget.setCurrentIndex(0)
        print("Navigated back to home")
        
    def closeEvent(self, event):
        """애플리케이션 종료 시 정리"""
        print("Closing application...")
        # Stop player timer if running
        if hasattr(self, 'player_screen'):
            self.player_screen.timer.stop()
        event.accept()


def main():
    """메인 함수"""
    print("=" * 50)
    print("Music Streaming DAC")
    print("=" * 50)
    
    # Create application
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle('Fusion')
    
    # Create and show main window
    try:
        window = MusicDACApp()
        window.show()
        
        print("\nApplication is running!")
        print("Press Ctrl+C to quit\n")
        
        # Run application
        sys.exit(app.exec())
        
    except Exception as e:
        print(f"\nError starting application: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()