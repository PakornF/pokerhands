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
    
    def plot_betting_behavior(self):
        """Analyze and visualize betting actions by round for both players"""
        # Initialize data structures with all possible rounds (1-4)
        rounds_data = {1: {'P0': {'call': 0, 'raise': 0}, 'P1': {'call': 0, 'raise': 0}},
                    2: {'P0': {'call': 0, 'raise': 0}, 'P1': {'call': 0, 'raise': 0}},
                    3: {'P0': {'call': 0, 'raise': 0}, 'P1': {'call': 0, 'raise': 0}},
                    4: {'P0': {'call': 0, 'raise': 0}, 'P1': {'call': 0, 'raise': 0}}}
        
        # Parse betting data for each game
        for bets in self.df['Bets']:
            if not isinstance(bets, str):
                continue
                
            # Split into rounds
            rounds = bets.split(';')
            for round_data in rounds:
                if not round_data or 'Round' not in round_data:
                    continue

                try:
                    parts = round_data.split(':')
                    if len(parts) < 3:
                        continue

                    round_num = int(parts[0].replace('Round', ''))
                    actions = parts[1:]

                    for i in range(0, len(actions), 2):
                        if i + 1 >= len(actions):
                            continue
                        player = actions[i]
                        action = actions[i + 1]

                        if player in ['P0', 'P1'] and action in ['call', 'raise']:
                            rounds_data[round_num][player][action] += 1
                except Exception as e:
                    print(f"Error processing round data: {e}")


        # Prepare data for plotting
        rounds = sorted(rounds_data.keys())
        p0_calls = [rounds_data[r]['P0']['call'] for r in rounds]
        p0_raises = [rounds_data[r]['P0']['raise'] for r in rounds]
        p1_calls = [rounds_data[r]['P1']['call'] for r in rounds]
        p1_raises = [rounds_data[r]['P1']['raise'] for r in rounds]

        # Create a new figure with larger size
        plt.figure(figsize=(12, 8))
        
        # Set the positions and width for the bars
        width = 0.35
        x = range(len(rounds))
        
        # Plot Player 0 bars
        p0_total = [sum(x) for x in zip(p0_calls, p0_raises)]
        p0_bars = plt.bar(x, p0_calls, width, color='#3498db', label='Player 0 Calls')
        plt.bar(x, p0_raises, width, bottom=p0_calls, color='#2980b9', label='Player 0 Raises')
        
        # Plot Player 1 bars (shifted right)
        p1_total = [sum(x) for x in zip(p1_calls, p1_raises)]
        p1_bars = plt.bar([i + width for i in x], p1_calls, width, color='#e74c3c', label='Player 1 Calls')
        plt.bar([i + width for i in x], p1_raises, width, bottom=p1_calls, color='#c0392b', label='Player 1 Raises')
        
        # Add labels and title
        plt.title('Betting Actions by Round and Player', fontsize=14, pad=20)
        plt.xlabel('Round Number', fontsize=12)
        plt.ylabel('Number of Actions', fontsize=12)
        plt.xticks([i + width/2 for i in x], rounds)
        
        # Add legend outside the plot
        plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        
        # Add grid lines
        plt.grid(True, axis='y', linestyle='--', alpha=0.7)
        
        # Set y-axis limits with some padding
        max_actions = max(p0_total + p1_total)
        plt.ylim(0, max_actions + 5)
        
        # Add value labels on top of bars
        def add_labels(bars):
            for bar in bars:
                height = bar.get_height()
                if height > 0:
                    plt.text(bar.get_x() + bar.get_width()/2., bar.get_y() + height,
                            f'{int(height)}', ha='center', va='bottom', fontsize=9)
        
        add_labels(p0_bars)
        add_labels(p1_bars)
        
        # Adjust layout and save
        plt.tight_layout()
        
        # Print debug information
        print("Plot data:")
        print(f"Rounds: {rounds}")
        print(f"Player 0 Calls: {p0_calls}")
        print(f"Player 0 Raises: {p0_raises}")
        print(f"Player 1 Calls: {p1_calls}")
        print(f"Player 1 Raises: {p1_raises}")
        
        # Save the figure
        output_path = os.path.abspath('betting_actions_by_round.png')
        plt.savefig(output_path)
        print(f"Graph saved to: {output_path}")
        
    def convert_cards_to_numerical(self):
        # Define the mapping for suits
        suit_mapping = {'♣': 0.1, '♦': 0.3, '♥': 0.5, '♠': 0.9}

        def card_to_value(card):
            # Extract the rank and suit
            rank = card[:-1]  # All characters except the last one
            suit = card[-1]  # The last character

            # Convert rank to numerical value
            if rank == 'A':
                rank_value = 14
            elif rank == 'K':
                rank_value = 13
            elif rank == 'Q':
                rank_value = 12
            elif rank == 'J':
                rank_value = 11
            else:
                rank_value = int(rank)

            # Add the suit value
            return rank_value + suit_mapping[suit]

        # Process Player0 Cards and Player1 Cards
        self.df['Player0 Cards'] = self.df['Player0 Cards'].apply(
            lambda cards: sum([card_to_value(card.strip()) for card in cards.split(',')])
        )
        self.df['Player1 Cards'] = self.df['Player1 Cards'].apply(
            lambda cards: sum([card_to_value(card.strip()) for card in cards.split(',')])
        )
        self.df['Community Cards'] = self.df['Community Cards'].apply(
            lambda cards: sum([card_to_value(card.strip()) for card in cards.split(',')])
        )
        self.df['Player0 Cards'] = self.df['Player0 Cards'].astype('float64')
        self.df['Player1 Cards'] = self.df['Player1 Cards'].astype('float64')
        print(self.df.dtypes)
        # print(self.df[['Player0 Cards', 'Player1 Cards']])
        # Save the updated DataFrame to a new CSV file
        # self.df.to_csv('game_data_numerical.csv', index=False)
        plt.figure(figsize=(10, 6))
        sns.heatmap(self.df[['Player0 Cards', 'Player1 Cards', 'Community Cards', 'Duration (s)']].corr(), annot=True, cmap='coolwarm')
        self.save_graph('correlation.png')
    
    def summarize_game_duration_table(self):
        duration_series = self.df['Duration (s)']
        summary = {
            'Mean': duration_series.mean(),
            'Median': duration_series.median(),
            'Min': duration_series.min(),
            'Max': duration_series.max(),
            'Standard Deviation (SD)': duration_series.std()
        }

        summary_df = pd.DataFrame([summary], index=['Duration'])

        # Plotting the table
        fig, ax = plt.subplots(figsize=(10, 8))
        ax.axis('off')  # Hide the axes

        # Create the table
        table = plt.table(cellText=summary_df.values,
                        colLabels=summary_df.columns,
                        rowLabels=summary_df.index,
                        loc='center',
                        cellLoc='center')

        table.scale(1.2, 1.5)
        table.auto_set_font_size(False)
        table.set_fontsize(12)

        plt.title('Summary Statistics of Game Duration', fontsize=14, pad=20)
        plt.tight_layout()
        plt.savefig('duration_summary_table.png', bbox_inches='tight')

# visualizer = PokerVisualizer('game_data.csv')
# visualizer.summarize_game_duration_table()