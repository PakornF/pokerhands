import csv
import os

class DataLogger:
    def __init__(self):
        self.games = []
        self.headers = ['Game', 'Duration (s)', 'Player0 Cards', 'Player1 Cards', 'Winner', 'Community Cards', 'Bets']
        self.csv_file = "game_data.csv"
        # Create the CSV file if it doesn't exist
        if not os.path.exists(self.csv_file):
            with open(self.csv_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(self.headers)

    def log_game(self, game_data):
        game_data['game'] = len(self.games) + 1
        self.games.append(game_data)

        # Append to CSV file
        with open(self.csv_file, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            row = [
                game_data['game'],
                f"{game_data['duration']:.2f}",
                game_data['player0_cards'],
                game_data['player1_cards'],
                game_data['winner'],
                game_data['community_cards'],
                game_data['bets'],
            ]
            writer.writerow(row)

    def get_csv(self):
        # Create a CSV string from the logged games
        csv_lines = [','.join(self.headers)]
        for game in self.games:
            line = [
                str(game['game']),
                f"{game['duration']:.2f}",
                game['player0_cards'],
                game['player1_cards'],
                str(game['winner']),
                game['community_cards'],
                game['bets']
            ]
            csv_lines.append(','.join(line))
        return '\n'.join(csv_lines)