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
        plt.savefig(file_name)

    def plot_game_duration(self):
        plt.figure(figsize=(10, 6))
        sns.histplot(data=self.df, x='Duration (s)', bins=range(0, int(self.df['Duration (s)'].max()) + 20, 5), color='skyblue')
        plt.title('Game Duration Distribution')
        plt.xlabel('Duration (s)')
        plt.grid(True)
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
        self.save_graph('player_card_distribution.png')
    
    def plot_win_ratio(self):
        win_counts = self.df['Winner'].value_counts()
        win_pct = win_counts / len(self.df) *100
        
        plt.figure(figsize=(10, 6))
        plt.pie(win_pct, labels=['Player1', 'Bot'], autopct='%1.1f%%', startangle=90, colors=['#66c2a5', '#fc8d62'])
        plt.title('Win Ratio of Players and Bot')
        self.save_graph('win_ratio.png')

    
    def _calculate_stats(self):
        """Calculate duration statistics for each game"""
        stats = {
            'Game': self.df['Game'],
            'Duration': self.df['Duration (s)'],
            'Min': self.df['Duration (s)'].min(),
            'Max': self.df['Duration (s)'].max(),
            'Mean': self.df['Duration (s)'].mean(),
            'Median': self.df['Duration (s)'].median(),
            'StDev': self.df['Duration (s)'].std()
        }
        return pd.DataFrame(stats)
    
    def plot_duration_table(self):
            """Create and save a table visualization of duration statistics"""
            stats_df = self._calculate_stats()
            
            fig, ax = plt.subplots(figsize=(12, 8))
            ax.axis('off')
            ax.axis('tight')
            
            # Create the table
            table = ax.table(
                cellText=stats_df.values,
                colLabels=stats_df.columns,
                loc='center',
                cellLoc='center'
            )
            
            # Style the table
            table.auto_set_font_size(False)
            table.set_fontsize(10)
            table.scale(1.2, 1.2)
            
            # Header styling
            for (row, col), cell in table.get_celld().items():
                if row == 0:  # Header row
                    cell.set_facecolor('#4C72B0')
                    cell.set_text_props(color='white', weight='bold')
                elif col == 0:  # First column (Game numbers)
                    cell.set_facecolor('#DDDDDD')
                else:  # Data cells
                    cell.set_facecolor('#F7F7F7')
            
            plt.title('Game Duration Statistics', pad=20, weight='bold')
            plt.tight_layout()
            self.save_graph('duration_statistics.png')

# visualize = PokerVisualizer('game_data.csv')
# visualize.plot_game_duration()
# visualize.plot_player_hands()
# visualize.plot_win_ratio()