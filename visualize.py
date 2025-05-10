import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

class PokerVisualizer:
    def __init__(self, file_path):
        self.file_path = pd.read_csv(file_path) if isinstance(file_path, str) else file_path
        self.df = pd.DataFrame(self.file_path)

    def plot_game_duration(self):
        plt.figure(figsize=(10, 6))
        sns.histplot(data=self.df, x='Duration (s)', bins=range(0, int(self.df['Duration (s)'].max()) + 20, 5), color='skyblue')
        plt.title('Game Duration Distribution')
        plt.xlabel('Duration (s)')
        plt.grid(True)
        plt.show()
    
    def plot_player_hands(self):
        plt.figure(figsize=(10, 6))
        sns.countplot(data=self.df, x='Player0 Cards', palette='pastel')
        plt.title('Distribution of Player 0 Hands')
        plt.xlabel('Player 0 Cards')
        plt.ylabel('Count')
        plt.xticks(rotation=45)
        # plt.grid(True)
        plt.show()
    
    def plot_win_ratio(self):
        win_counts = self.df['Winner'].value_counts()
        win_pct = win_counts / len(self.df) *100
        
        plt.figure(figsize=(10, 6))
        plt.pie(win_pct, labels=['Player1', 'Bot'], autopct='%1.1f%%', startangle=90, colors=['#66c2a5', '#fc8d62'])
        plt.title('Win Ratio of Players and Bot')
        plt.show()

visualize = PokerVisualizer('game_data.csv')
visualize.plot_game_duration()
visualize.plot_player_hands()
visualize.plot_win_ratio()