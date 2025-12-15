from google import genai
from google.genai import types
from typing import List, Dict
from dotenv import load_dotenv
import json
import re
import os

load_dotenv()

class ValorantScoreboardParser:
    def __init__(self, image_path: str):
        self.image_path = image_path
        self.client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    
    def parse_scoreboard(self) -> List[Dict[str, any]]:
        prompt = """Analyze this image. If it's a Valorant scoreboard, extract player data in JSON format: [{"name": "player", "score": 123, "kills": 12}]. 
        Only include name, score (ACS), and kills for each player. If not a Valorant scoreboard, return empty array []."""
        
        with open(self.image_path, 'rb') as f:
            image_data = f.read()
        
        response = self.client.models.generate_content(
            model="gemini-2.5-flash-live",
            contents=[
                types.Part.from_bytes(data=image_data, mime_type="image/png"),
                prompt
            ]
        )
        
        text = response.text
        json_match = re.search(r'\[.*\]', text, re.DOTALL)
        if json_match:
            players = json.loads(json_match.group())
            return players
        return []

    
    def find_scoreboarding(self) -> List[tuple]:
        players = self.parse_scoreboard()
        print(players)
        mismatches = []
        
        for i in range(len(players)):
            for j in range(i + 1, len(players)):
                p1, p2 = players[i], players[j]
                if p1['score'] > p2['score'] and p1['kills'] < p2['kills']:
                    mismatches.append((p1, p2))
                elif p2['score'] > p1['score'] and p2['kills'] < p1['kills']:
                    mismatches.append((p2, p1))
        
        return mismatches

if __name__ == "__main__":
    path = "image.png"
    scoreboard = ValorantScoreboardParser(path)
    print(scoreboard.parse_scoreboard())
    print(scoreboard.find_scoreboarding())
