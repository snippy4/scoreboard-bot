import base64
import json
import os
import re
from typing import List, Dict
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

class ValorantScoreboardParser:
    def __init__(self, image_path: str):
        self.image_path = image_path
        self.client = OpenAI(
            api_key=os.getenv("DEEPSEEK_API_KEY"),
            base_url="https://api.deepseek.com"
        )

    def _encode_image(self) -> str:
        with open(self.image_path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")

    def parse_scoreboard(self) -> List[Dict[str, any]]:
        prompt = (
            "Analyze this image. If it's a Valorant scoreboard, extract player data "
            "in valid JSON format ONLY:\n\n"
            '[{"name": "player", "score": 123, "kills": 12}]\n\n'
            "Only include name, score (ACS), and kills.\n"
            "If not a Valorant scoreboard, return []."
        )

        image_base64 = self._encode_image()

        response = self.client.chat.completions.create(
            model="deepseek-vl",  # vision model
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{image_base64}"
                            }
                        },
                    ],
                }
            ],
            temperature=0,
        )

        text = response.choices[0].message.content

        # Extract JSON safely
        json_match = re.search(r"\[.*\]", text, re.DOTALL)
        if json_match:
            return json.loads(json_match.group())

        return []

    def find_scoreboarding(self) -> List[tuple]:
        players = self.parse_scoreboard()
        print(players)

        mismatches = []

        for i in range(len(players)):
            for j in range(i + 1, len(players)):
                p1, p2 = players[i], players[j]
                if p1["score"] > p2["score"] and p1["kills"] < p2["kills"]:
                    mismatches.append((p1, p2))
                elif p2["score"] > p1["score"] and p2["kills"] < p1["kills"]:
                    mismatches.append((p2, p1))

        return mismatches


if __name__ == "__main__":
    path = "image.png"
    scoreboard = ValorantScoreboardParser(path)
    print(scoreboard.parse_scoreboard())
    print(scoreboard.find_scoreboarding())
