import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
import seaborn as sns
import os

matplotlib.use('Agg')  # Use a non-interactive backend for matplotlib
# from matplotlib import pyplot as plt

class PokerVisualizer:
    def __init__(self, file_path):
        self.file_path = pd.read_csv(file_path) if isinstance(file_path, str) else file_path
        self.df = pd.DataFrame(self.file_path)
    
    def save_graph(self, file_name):
        if not os.path.exists('graphs'):
            os.makedirs('graphs')
        plt.savefig(os.path.join('graphs', file_name))

    def plot_game_duration(self):
        plt.figure(figsize=(10, 6))
        sns.histplot(data=self.df, x='Duration (s)', bins=range(0, int(self.df['Duration (s)'].max()) + 20, 5), color='skyblue')
        plt.title('Game Duration Distribution')
        plt.xlabel('Duration (s)')
        plt.grid(True)
        plt.show()
        self.save_graph('game_duration_distribution.png')
    
    def plot_player_hands(self):
        player0_hands = self.df[['Player0 Cards']].rename(columns={'Player0 Cards': 'Cards'})
        player1_hands = self.df[['Player1 Cards']].rename(columns={'Player1 Cards': 'Cards'})

        player0_hands['Player'] = 'Player 0'
        player1_hands['Player'] = 'Player 1'
        self.new_df = pd.concat([player0_hands, player1_hands], ignore_index=True)

        plt.figure(figsize=(10, 6))
        sns.countplot(data=self.new_df, x='Cards', hue='Player', palette='pastel')
        plt.title('Distribution of Player Hands')
        plt.xlabel('Cards')
        plt.ylabel('Count')
        plt.xticks(rotation=45, ha='right')
        plt.legend(title='Player')
        # plt.grid(True)
        plt.show()
        self.save_graph('player_card_distribution.png')
    
    def plot_win_ratio(self):
        win_counts = self.df['Winner'].value_counts()
        win_pct = win_counts / len(self.df) *100
        
        plt.figure(figsize=(10, 6))
        plt.pie(win_pct, labels=['Player1', 'Bot'], autopct='%1.1f%%', startangle=90, colors=['#66c2a5', '#fc8d62'])
        plt.title('Win Ratio of Players and Bot')
        plt.show()
        self.save_graph('win_ratio.png')

visualize = PokerVisualizer('game_data.csv')
visualize.plot_game_duration()
visualize.plot_player_hands()
visualize.plot_win_ratio()