import cv2
import pytesseract
import re
from typing import List, Dict

class ValorantScoreboardParser:
    def __init__(self, image_path: str):
        self.image_path = image_path
        self.image = cv2.imread(image_path)
    
    def preprocess_image(self):
        gray = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
        # Invert for light text on dark background
        inverted = 255 - gray
        # Apply threshold
        _, thresh = cv2.threshold(inverted, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        # Upscale for better OCR
        scaled = cv2.resize(thresh, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
        return scaled

    def extract_text(self) -> str:
        processed = self.preprocess_image()
        # Use PSM 6 for uniform block of text
        return pytesseract.image_to_string(processed, config='--psm 6')

    
    def parse_scoreboard(self) -> List[Dict[str, any]]:
        text = self.extract_text()
        print(text)
        players = []
        
        pattern = pattern = r'([A-Za-z0-9#_]+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)'

        matches = re.findall(pattern, text)
        
        for match in matches:
            player_data = {
                'name': match[0],
                'score': int(match[1]),
                'kills': int(match[2]),
                'deaths': int(match[3]),
                'assists': int(match[4])
            }
            players.append(player_data)
        
        return players
    
    def find_scoreboarding(self) -> List[tuple]:
        players = self.parse_scoreboard()
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
    path = "processed_image.png"
    scoreboard = ValorantScoreboardParser(path)
    print(scoreboard.parse_scoreboard())
    print(scoreboard.find_scoreboarding())
