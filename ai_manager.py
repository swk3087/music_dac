"""
Gemini AI Manager
Gemini AI를 활용한 음악 추천 및 검색 제안
"""

import google.generativeai as genai
from PyQt6.QtCore import QObject, pyqtSignal
import config
import json
import re


class AIManager(QObject):
    """Gemini AI 관리 클래스"""
    
    # Signals
    suggestion_ready = pyqtSignal(list)
    error_occurred = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.model = None
        self.setup_ai()
        
    def setup_ai(self):
        """Gemini AI 초기화"""
        try:
            genai.configure(api_key=config.GEMINI_API_KEY)
            self.model = genai.GenerativeModel('gemini-2.5-flash')
            print("✅ Gemini AI initialized successfully")
            
        except Exception as e:
            error_msg = f"Gemini AI initialization failed: {e}"
            print(f"❌ {error_msg}")
            self.error_occurred.emit(error_msg)
    
    def generate_music_suggestions(self, user_input):
        """
        사용자 입력을 기반으로 음악 검색 제안 생성
        
        Args:
            user_input (str): 사용자 입력 (예: "비오는 날 듣기 좋은 음악")
            
        Returns:
            list: 4개의 검색 제안
        """
        if not self.model:
            print("❌ AI model not initialized")
            return self._get_default_suggestions()
        
        try:
            prompt = self._create_prompt(user_input)
            
            print(f"🤖 Generating AI suggestions for: '{user_input}'")
            response = self.model.generate_content(prompt)
            
            suggestions = self._parse_suggestions(response.text)
            
            if suggestions and len(suggestions) >= 4:
                print(f"✅ Generated {len(suggestions)} suggestions")
                self.suggestion_ready.emit(suggestions)
                return suggestions
            else:
                print("⚠️  Invalid AI response, using defaults")
                return self._get_default_suggestions()
                
        except Exception as e:
            error_msg = f"AI suggestion generation failed: {e}"
            print(f"❌ {error_msg}")
            self.error_occurred.emit(error_msg)
            return self._get_default_suggestions()
    
    def _create_prompt(self, user_input):
        """프롬프트 생성"""
        prompt = f"""You are a music recommendation expert. Based on the user's input, generate 4 specific Spotify search queries.

User input: "{user_input}"

Requirements:
- Generate exactly 4 search queries
- Each query should be specific and searchable on Spotify
- Queries should be diverse but related to the user's mood/preference
- Use English or keep the original language if appropriate
- Format as a JSON array: ["query1", "query2", "query3", "query4"]

Examples:
Input: "비오는 날 듣기 좋은 음악"
Output: ["rainy day jazz", "melancholic indie", "acoustic rain songs", "lo-fi chill beats"]

Input: "운동할 때 신나는 노래"
Output: ["workout motivation", "high energy EDM", "gym pump up", "running beats"]

Input: "잠들기 전 편안한 음악"
Output: ["sleep meditation music", "calm piano", "relaxing ambient", "bedtime classical"]

Now generate 4 search queries for the user's input. Return ONLY the JSON array, nothing else.
"""
        return prompt
    
    def _parse_suggestions(self, response_text):
        """AI 응답 파싱"""
        try:
            # Remove markdown code blocks if present
            response_text = response_text.strip()
            response_text = re.sub(r'```json\s*', '', response_text)
            response_text = re.sub(r'```\s*', '', response_text)
            response_text = response_text.strip()
            
            # Try to find JSON array
            match = re.search(r'\[.*?\]', response_text, re.DOTALL)
            if match:
                json_str = match.group(0)
                suggestions = json.loads(json_str)
                
                if isinstance(suggestions, list) and len(suggestions) >= 4:
                    # Take first 4 suggestions
                    return suggestions[:4]
            
            return None
            
        except json.JSONDecodeError as e:
            print(f"❌ Failed to parse AI response: {e}")
            print(f"Response text: {response_text}")
            return None
        except Exception as e:
            print(f"❌ Error parsing suggestions: {e}")
            return None
    
    def _get_default_suggestions(self):
        """기본 제안 (AI 실패시)"""
        defaults = [
            "popular tracks",
            "new releases",
            "top hits 2024",
            "trending now"
        ]
        self.suggestion_ready.emit(defaults)
        return defaults
    
    def generate_playlist_description(self, playlist_name, tracks):
        """
        플레이리스트 설명 생성 (추가 기능)
        
        Args:
            playlist_name (str): 플레이리스트 이름
            tracks (list): 트랙 리스트
            
        Returns:
            str: 생성된 설명
        """
        if not self.model:
            return f"A collection of {len(tracks)} tracks"
        
        try:
            # Get track info
            track_info = []
            for track in tracks[:5]:  # First 5 tracks
                if track:
                    name = track.get('name', 'Unknown')
                    artist = track.get('artists', [{}])[0].get('name', 'Unknown')
                    track_info.append(f"{name} by {artist}")
            
            prompt = f"""Generate a short, engaging description for a music playlist.

Playlist name: {playlist_name}
Sample tracks: {', '.join(track_info)}
Total tracks: {len(tracks)}

Generate a 1-2 sentence description that captures the mood and style of this playlist.
"""
            
            response = self.model.generate_content(prompt)
            return response.text.strip()
            
        except Exception as e:
            print(f"❌ Failed to generate description: {e}")
            return f"A collection of {len(tracks)} tracks"
    
    def analyze_mood(self, track_name, artist_name):
        """
        트랙의 분위기 분석 (추가 기능)
        
        Args:
            track_name (str): 트랙 이름
            artist_name (str): 아티스트 이름
            
        Returns:
            dict: 분석 결과
        """
        if not self.model:
            return {'mood': 'neutral', 'energy': 'medium'}
        
        try:
            prompt = f"""Analyze the mood of this song:
Track: {track_name}
Artist: {artist_name}

Return a JSON object with these fields:
- mood: (happy/sad/energetic/calm/melancholic/upbeat)
- energy: (low/medium/high)
- tags: [list of 3-5 descriptive tags]

Example output:
{{"mood": "upbeat", "energy": "high", "tags": ["dance", "summer", "party"]}}

Return ONLY the JSON object.
"""
            
            response = self.model.generate_content(prompt)
            result = json.loads(response.text.strip())
            return result
            
        except Exception as e:
            print(f"❌ Mood analysis failed: {e}")
            return {'mood': 'neutral', 'energy': 'medium', 'tags': []}