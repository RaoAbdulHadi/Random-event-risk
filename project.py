import random
import numpy as np
import pygame
import networkx as nx
from typing import List, Dict, Tuple, Optional
import json
import pickle
from datetime import datetime

class Territory:
    def __init__(self, name: str, continent: str):
        self.name = name
        self.continent = continent
        self.owner = None
        self.troops = 0
        self.connections = []

class Card:
    def __init__(self, territory: str, type: str):
        self.territory = territory
        self.type = type  # "infantry", "cavalry", "artillery", "wild"

class Player:
    def __init__(self, name: str, color: Tuple[int, int, int]):
        self.name = name
        self.color = color
        self.territories = []
        self.cards = []
        self.num_cards = 0
        self.num_reinforcements = 0
        self.reinforcements = 0
        self.sets_traded = 0  # Track number of sets traded
        self.max_cards = 5  # Maximum cards a player can hold
        self.battle_stats = {
            'attacks_won': 0,
            'attacks_lost': 0,
            'territories_conquered': 0,
            'continents_controlled': 0
        }

    def can_trade_cards(self) -> bool:
        # Check if player has 3 or more cards
        if len(self.cards) < 3:
            return False
        
        # Check for valid card combinations
        types = [card.type for card in self.cards]
        
        # Three of a kind
        if types.count(types[0]) >= 3:
            return True
        
        # One of each type
        if "infantry" in types and "cavalry" in types and "artillery" in types:
            return True
        
        # Two of one type and a wild
        if types.count(types[0]) >= 2 and "wild" in types:
            return True
        
        return False

    def trade_cards(self) -> int:
        if not self.can_trade_cards():
            return 0
        
        # Calculate reinforcements based on number of trades
        self.sets_traded += 1
        base_reinforcements = self._calculate_trade_bonus()
        
        # Check for territory matching bonus
        territory_bonus = 0
        for card in self.cards[:3]:  # Only check first 3 cards being traded
            if card.territory != "wild" and any(t.name == card.territory for t in self.territories):
                territory_bonus += 2
        
        total_reinforcements = base_reinforcements + territory_bonus
        
        # Remove traded cards
        self.cards = self.cards[3:]
        
        return total_reinforcements

    def _calculate_trade_bonus(self) -> int:
        # Get the types of the first 3 cards being traded
        types = [card.type for card in self.cards[:3]]
        
        # Three of a kind
        if types.count(types[0]) >= 3:
            if types[0] == "infantry":
                return 4
            elif types[0] == "cavalry":
                return 6
            elif types[0] == "artillery":
                return 8
        
        # One of each type
        if "infantry" in types and "cavalry" in types and "artillery" in types:
            return 10
        
        # Two of one type and a wild
        if types.count(types[0]) >= 2 and "wild" in types:
            if types[0] == "infantry":
                return 4
            elif types[0] == "cavalry":
                return 6
            elif types[0] == "artillery":
                return 8
        
        return 0  # Default case if no valid combination

    def add_card(self, card: Card):
        self.cards.append(card)
        if len(self.cards) > self.max_cards:
            print(f"Warning: {self.name} has more than {self.max_cards} cards and must trade!")

class RandomEvent:
    def __init__(self, name: str, description: str, effect: callable):
        self.name = name
        self.description = description
        self.effect = effect
        self.chosen_values = {}  # Store random values chosen for this event

class RiskGame:
    def __init__(self):
        self.territories = {}
        self.players = []
        self.current_player = None
        self.events = self._initialize_events()
        self.game_map = nx.Graph()
        self.continent_bonus = {
            "North America": 5,
            "South America": 2,
            "Europe": 5,
            "Africa": 3,
            "Asia": 7,
            "Australia": 2
        }
        self.card_deck = self._initialize_card_deck()
        self.game_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        
    def _initialize_events(self) -> List[RandomEvent]:
        events = [
            RandomEvent(
                "Natural Disaster",
                "A natural disaster strikes! All territories in a random continent lose 1 troop.",
                self._natural_disaster_effect
            ),
            RandomEvent(
                "Reinforcement",
                "A friendly nation sends reinforcements! Add 2 troops to a random territory.",
                self._reinforcement_effect
            ),
            RandomEvent(
                "Disease",
                "A disease outbreak! All territories with more than 3 troops lose 1 troop.",
                self._disease_effect
            ),
            RandomEvent(
                "Territory Swap",
                "A diplomatic agreement forces two random territories to swap owners!",
                self._territory_swap_effect
            ),
            RandomEvent(
                "Border Dispute",
                "A border dispute breaks out! Two random connected territories lose 1 troop each.",
                self._border_dispute_effect
            ),
            RandomEvent(
                "Alliance",
                "An alliance is formed! All territories in a random continent gain 1 troop.",
                self._alliance_effect
            ),
            RandomEvent(
                "Civil War",
                "A civil war breaks out! All territories with more than 2 troops lose 1 troop.",
                self._civil_war_effect
            ),
            RandomEvent(
                "Economic Boom",
                "An economic boom occurs! All territories gain 1 troop.",
                self._economic_boom_effect
            )
        ]
        return events

    def _natural_disaster_effect(self, player: Player):
        continent = random.choice(list(set(t.continent for t in self.territories.values())))
        self.events[-1].chosen_values['continent'] = continent
        for territory in self.territories.values():
            if territory.continent == continent and territory.owner == player:
                territory.troops = max(0, territory.troops - 1)

    def _reinforcement_effect(self, player: Player):
        player_territories = [t for t in self.territories.values() if t.owner == player]
        if player_territories:
            territory = random.choice(player_territories)
            self.events[-1].chosen_values['territory'] = territory.name
            territory.troops += 2

    def _disease_effect(self, player: Player):
        for territory in self.territories.values():
            if territory.owner == player and territory.troops > 3:
                territory.troops -= 1

    def _territory_swap_effect(self, player: Player):
        # Get two random territories
        territories = list(self.territories.values())
        if len(territories) >= 2:
            territory1, territory2 = random.sample(territories, 2)
            # Swap owners
            owner1 = territory1.owner
            owner2 = territory2.owner
            if owner1 and owner2:
                territory1.owner.territories.remove(territory1)
                territory2.owner.territories.remove(territory2)
                territory1.owner = owner2
                territory2.owner = owner1
                owner2.territories.append(territory1)
                owner1.territories.append(territory2)

    def _border_dispute_effect(self, player: Player):
        # Find two random connected territories
        territories = list(self.territories.values())
        if len(territories) >= 2:
            territory1 = random.choice(territories)
            connected = [t for t in territories if t.name in territory1.connections]
            if connected:
                territory2 = random.choice(connected)
                territory1.troops = max(0, territory1.troops - 1)
                territory2.troops = max(0, territory2.troops - 1)

    def _alliance_effect(self, player: Player):
        # Choose a random continent
        continent = random.choice(list(set(t.continent for t in self.territories.values())))
        # Add 1 troop to all territories in that continent
        for territory in self.territories.values():
            if territory.continent == continent:
                territory.troops += 1

    def _civil_war_effect(self, player: Player):
        # All territories with more than 2 troops lose 1 troop
        for territory in self.territories.values():
            if territory.troops > 2:
                territory.troops -= 1

    def _economic_boom_effect(self, player: Player):
        # All territories gain 1 troop
        for territory in self.territories.values():
            territory.troops += 1

    def trigger_random_event(self):
        event = random.choice(self.events)
        print(f"\nRandom Event: {event.name}")
        print(f"Description: {event.description}")
        event.effect(self.current_player)

    def initialize_game(self):
        # Initialize territories
        territories_data = {
            "North America": ["Alaska", "Northwest Territory", "Greenland", "Alberta", "Ontario", "Quebec", "Western United States", "Eastern United States", "Central America"],
            "South America": ["Venezuela", "Peru", "Brazil", "Argentina"],
            "Europe": ["Iceland", "Scandinavia", "Great Britain", "Northern Europe", "Western Europe", "Southern Europe", "Ukraine"],
            "Africa": ["North Africa", "Egypt", "East Africa", "Congo", "South Africa", "Madagascar"],
            "Asia": ["Ural", "Siberia", "Yakutsk", "Kamchatka", "Afghanistan", "China", "Mongolia", "Japan", "Middle East", "India", "Southeast Asia"],
            "Australia": ["Indonesia", "New Guinea", "Western Australia", "Eastern Australia"]
        }
        
        for continent, territories in territories_data.items():
            for territory_name in territories:
                self.territories[territory_name] = Territory(territory_name, continent)
                self.game_map.add_node(territory_name)

        # Add complete territory connections
        self._add_territory_connections()

    def _add_territory_connections(self):
        # North America connections
        self._connect_territories("Alaska", ["Northwest Territory", "Alberta", "Kamchatka"])
        self._connect_territories("Northwest Territory", ["Alaska", "Alberta", "Ontario", "Greenland"])
        self._connect_territories("Greenland", ["Northwest Territory", "Ontario", "Quebec", "Iceland"])
        self._connect_territories("Alberta", ["Alaska", "Northwest Territory", "Ontario", "Western United States"])
        self._connect_territories("Ontario", ["Northwest Territory", "Greenland", "Quebec", "Alberta", "Western United States", "Eastern United States"])
        self._connect_territories("Quebec", ["Greenland", "Ontario", "Eastern United States"])
        self._connect_territories("Western United States", ["Alberta", "Ontario", "Eastern United States", "Central America"])
        self._connect_territories("Eastern United States", ["Ontario", "Quebec", "Western United States", "Central America"])
        self._connect_territories("Central America", ["Western United States", "Eastern United States", "Venezuela"])

        # South America connections
        self._connect_territories("Venezuela", ["Central America", "Peru", "Brazil"])
        self._connect_territories("Peru", ["Venezuela", "Brazil", "Argentina"])
        self._connect_territories("Brazil", ["Venezuela", "Peru", "Argentina", "North Africa"])
        self._connect_territories("Argentina", ["Peru", "Brazil"])

        # Europe connections
        self._connect_territories("Iceland", ["Greenland", "Great Britain", "Scandinavia"])
        self._connect_territories("Scandinavia", ["Iceland", "Great Britain", "Northern Europe", "Ukraine"])
        self._connect_territories("Great Britain", ["Iceland", "Scandinavia", "Northern Europe", "Western Europe"])
        self._connect_territories("Northern Europe", ["Scandinavia", "Great Britain", "Western Europe", "Southern Europe", "Ukraine"])
        self._connect_territories("Western Europe", ["Great Britain", "Northern Europe", "Southern Europe", "North Africa"])
        self._connect_territories("Southern Europe", ["Northern Europe", "Western Europe", "Ukraine", "Middle East", "North Africa", "Egypt"])
        self._connect_territories("Ukraine", ["Scandinavia", "Northern Europe", "Southern Europe", "Ural", "Afghanistan", "Middle East"])

        # Africa connections
        self._connect_territories("North Africa", ["Brazil", "Western Europe", "Southern Europe", "Egypt", "East Africa", "Congo"])
        self._connect_territories("Egypt", ["Southern Europe", "North Africa", "East Africa", "Middle East"])
        self._connect_territories("East Africa", ["North Africa", "Egypt", "Congo", "South Africa", "Madagascar", "Middle East"])
        self._connect_territories("Congo", ["North Africa", "East Africa", "South Africa"])
        self._connect_territories("South Africa", ["Congo", "East Africa", "Madagascar"])
        self._connect_territories("Madagascar", ["East Africa", "South Africa"])

        # Asia connections
        self._connect_territories("Ural", ["Ukraine", "Afghanistan", "Siberia"])
        self._connect_territories("Siberia", ["Ural", "Yakutsk", "Mongolia", "China"])
        self._connect_territories("Yakutsk", ["Siberia", "Kamchatka"])
        self._connect_territories("Kamchatka", ["Alaska", "Yakutsk", "Mongolia", "Japan"])
        self._connect_territories("Mongolia", ["Siberia", "Kamchatka", "Japan", "China"])
        self._connect_territories("Japan", ["Kamchatka", "Mongolia"])
        self._connect_territories("Afghanistan", ["Ukraine", "Ural", "China", "India", "Middle East"])
        self._connect_territories("China", ["Siberia", "Mongolia", "Southeast Asia", "India", "Afghanistan"])
        self._connect_territories("Middle East", ["Ukraine", "Southern Europe", "Egypt", "East Africa", "India", "Afghanistan"])
        self._connect_territories("India", ["Afghanistan", "China", "Southeast Asia", "Middle East"])
        self._connect_territories("Southeast Asia", ["China", "India", "Indonesia"])

        # Australia connections
        self._connect_territories("Indonesia", ["Southeast Asia", "New Guinea", "Western Australia"])
        self._connect_territories("New Guinea", ["Indonesia", "Western Australia", "Eastern Australia"])
        self._connect_territories("Western Australia", ["Indonesia", "New Guinea", "Eastern Australia"])
        self._connect_territories("Eastern Australia", ["New Guinea", "Western Australia"])

    def _connect_territories(self, territory: str, connections: List[str]):
        for connection in connections:
            self.game_map.add_edge(territory, connection)
            self.territories[territory].connections.append(connection)
            self.territories[connection].connections.append(territory)

    def calculate_reinforcements(self, player: Player) -> int:
        # Base reinforcements (territories / 3, rounded down)
        base = len(player.territories) // 3
        if base < 3:
            base = 3  # Minimum of 3 reinforcements

        # Continent bonus
        continent_bonus = 0
        for continent, bonus in self.continent_bonus.items():
            # Check if player owns all territories in this continent
            continent_territories = [t for t in self.territories.values() if t.continent == continent]
            if all(t.owner == player for t in continent_territories):
                continent_bonus += bonus

        total_reinforcements = base + continent_bonus
        print(f"Calculating reinforcements for {player.name}:")
        print(f"Base reinforcements (territories/3): {base}")
        print(f"Continent bonus: {continent_bonus}")
        print(f"Total reinforcements: {total_reinforcements}")
        return total_reinforcements

    def roll_dice(self, num_dice: int) -> List[int]:
        return sorted([random.randint(1, 6) for _ in range(num_dice)], reverse=True)

    def resolve_combat(self, attacker: Territory, defender: Territory) -> Tuple[int, int]:
        # Determine number of dice
        attacker_dice = min(3, attacker.troops - 1)
        defender_dice = min(2, defender.troops)

        # Roll dice
        attacker_rolls = self.roll_dice(attacker_dice)
        defender_rolls = self.roll_dice(defender_dice)

        # Compare dice and determine losses
        attacker_losses = 0
        defender_losses = 0

        for a_roll, d_roll in zip(attacker_rolls, defender_rolls):
            if a_roll > d_roll:
                defender_losses += 1
            else:
                attacker_losses += 1

        return attacker_losses, defender_losses

    def attack(self, attacker: Territory, defender: Territory) -> bool:
        if attacker.owner != self.current_player:
            raise ValueError("Not your territory")
        if defender.owner == self.current_player:
            raise ValueError("Cannot attack your own territory")
        if defender.name not in attacker.connections:
            raise ValueError("Territories are not connected")
        if attacker.troops < 2:
            raise ValueError("Not enough troops to attack")

        attacker_losses, defender_losses = self.resolve_combat(attacker, defender)
        
        # Apply losses
        attacker.troops -= attacker_losses
        defender.troops -= defender_losses

        # Update battle statistics
        if defender.troops <= 0:
            self.current_player.battle_stats['attacks_won'] += 1
            defender.owner.battle_stats['attacks_lost'] += 1
            self.current_player.battle_stats['territories_conquered'] += 1
        else:
            self.current_player.battle_stats['attacks_lost'] += 1
            defender.owner.battle_stats['attacks_won'] += 1

        # If defender is defeated, transfer ownership
        if defender.troops <= 0:
            defender.owner.territories.remove(defender)
            defender.owner = attacker.owner
            defender.owner.territories.append(defender)
            defender.troops = attacker.troops - 1
            attacker.troops = 1
            
            # Draw a card when conquering a territory
            if self.card_deck:
                card = self.card_deck.pop()
                self.current_player.add_card(card)
                print(f"{self.current_player.name} drew a {card.type} card for conquering {defender.name}")
            
            # Update continent control statistics
            self._update_continent_control()
            
            return True

        return False

    def _update_continent_control(self):
        for player in self.players:
            player.battle_stats['continents_controlled'] = 0
            for continent in self.continent_bonus.keys():
                continent_territories = [t for t in self.territories.values() if t.continent == continent]
                if all(t.owner == player for t in continent_territories):
                    player.battle_stats['continents_controlled'] += 1

    def fortify(self, from_territory: Territory, to_territory: Territory, num_troops: int):
        if from_territory.owner != self.current_player or to_territory.owner != self.current_player:
            raise ValueError("Not your territory")
        if to_territory.name not in from_territory.connections:
            raise ValueError("Territories are not connected")
        if num_troops >= from_territory.troops:
            raise ValueError("Not enough troops to move")

        from_territory.troops -= num_troops
        to_territory.troops += num_troops

    def reinforce(self, territory: Territory):
        if territory.owner != self.current_player:
            raise ValueError("Not your territory")

        territory.troops += 1
        self.current_player.reinforcements -= 1

    def start_turn(self):
        # Calculate reinforcements for the current player
        self.current_player.reinforcements = self.calculate_reinforcements(self.current_player)
        
        # Draw a card if player conquered a territory last turn
        if self.current_player.territories:
            self.draw_card(self.current_player)
        
        print(f"\n{self.current_player.name}'s turn")
        print(f"Available reinforcements: {self.current_player.reinforcements}")
        print(f"Cards: {[card.type for card in self.current_player.cards]}")

    def end_turn(self):
        # Trigger random event
        self.trigger_random_event()
        
        # Move to next player
        current_index = self.players.index(self.current_player)
        next_index = (current_index + 1) % len(self.players)
        self.current_player = self.players[next_index]

    def check_win_condition(self) -> bool:
        # Check if any player has been eliminated
        active_players = [p for p in self.players if len(p.territories) > 0]
        if len(active_players) == 1:
            winner = active_players[0]
            print(f"\n{winner.name} has won the game!")
            self._print_game_statistics(winner)
            return True
            
        # Check if any player controls all territories
        for player in self.players:
            if len(player.territories) == len(self.territories):
                print(f"\n{player.name} has won by controlling all territories!")
                self._print_game_statistics(player)
                return True
                
        return False

    def _print_game_statistics(self, winner: Player):
        print("\nGame Statistics:")
        print(f"Winner: {winner.name}")
        print("\nPlayer Statistics:")
        for player in self.players:
            print(f"\n{player.name}:")
            print(f"Territories controlled: {len(player.territories)}")
            print(f"Attacks won: {player.battle_stats['attacks_won']}")
            print(f"Attacks lost: {player.battle_stats['attacks_lost']}")
            print(f"Territories conquered: {player.battle_stats['territories_conquered']}")
            print(f"Continents controlled: {player.battle_stats['continents_controlled']}")
            print(f"Card sets traded: {player.sets_traded}")

    def play_turn(self):
        self.start_turn()
        
        # Reinforcement phase
        print("\nReinforcement Phase")
        # Check for card trading at the start of reinforcement phase
        if self.current_player.can_trade_cards():
            print("\nYou can trade cards for reinforcements!")
            print("Your cards:", [card.type for card in self.current_player.cards])
            if input("Would you like to trade cards? (y/n): ").lower() == 'y':
                reinforcements = self.current_player.trade_cards()
                self.current_player.reinforcements += reinforcements
                print(f"Received {reinforcements} reinforcements from card trade")
        
        while self.current_player.reinforcements > 0:
            print(f"\nAvailable reinforcements: {self.current_player.reinforcements}")
            print("Your territories:")
            for territory in self.current_player.territories:
                print(f"{territory.name}: {territory.troops} troops")
            
            # Get player input for reinforcement
            territory_name = input("Enter territory name to reinforce (or 'done' to end phase): ")
            if territory_name.lower() == 'done':
                break
                
            if territory_name in self.territories:
                territory = self.territories[territory_name]
                if territory.owner == self.current_player:
                    try:
                        num_troops = int(input("Enter number of troops to add: "))
                        self.reinforce(territory, num_troops)
                    except ValueError:
                        print("Invalid number of troops")
                else:
                    print("Not your territory")
            else:
                print("Invalid territory name")
        
        # Attack phase
        print("\nAttack Phase")
        while True:
            print("\nYour territories:")
            for territory in self.current_player.territories:
                if territory.troops > 1:  # Can only attack with more than 1 troop
                    print(f"{territory.name}: {territory.troops} troops")
            
            # Get player input for attack
            attacker_name = input("Enter attacking territory name (or 'done' to end phase): ")
            if attacker_name.lower() == 'done':
                break
                
            if attacker_name in self.territories:
                attacker = self.territories[attacker_name]
                if attacker.owner == self.current_player and attacker.troops > 1:
                    print("Connected enemy territories:")
                    for connection in attacker.connections:
                        defender = self.territories[connection]
                        if defender.owner != self.current_player:
                            print(f"{defender.name}: {defender.troops} troops")
                    
                    defender_name = input("Enter defending territory name: ")
                    if defender_name in self.territories:
                        defender = self.territories[defender_name]
                        if defender.name in attacker.connections:
                            try:
                                self.attack(attacker, defender)
                                print(f"Attack result: {attacker.troops} troops remaining in {attacker.name}, {defender.troops} troops remaining in {defender.name}")
                            except ValueError as e:
                                print(f"Invalid attack: {e}")
                        else:
                            print("Territories are not connected")
                    else:
                        print("Invalid territory name")
                else:
                    print("Invalid attacking territory")
            else:
                print("Invalid territory name")
        
        # Fortify phase
        print("\nFortify Phase")
        while True:
            print("\nYour territories:")
            for territory in self.current_player.territories:
                if territory.troops > 1:  # Can only fortify with more than 1 troop
                    print(f"{territory.name}: {territory.troops} troops")
            
            # Get player input for fortification
            from_territory_name = input("Enter territory to move troops from (or 'done' to end phase): ")
            if from_territory_name.lower() == 'done':
                break
                
            if from_territory_name in self.territories:
                from_territory = self.territories[from_territory_name]
                if from_territory.owner == self.current_player and from_territory.troops > 1:
                    print("Connected friendly territories:")
                    for connection in from_territory.connections:
                        to_territory = self.territories[connection]
                        if to_territory.owner == self.current_player:
                            try:
                                num_troops = int(input("Enter number of troops to move: "))
                                self.fortify(from_territory, to_territory, num_troops)
                                print(f"Fortification complete: {from_territory.troops} troops in {from_territory.name}, {to_territory.troops} troops in {to_territory.name}")
                            except ValueError as e:
                                print(f"Invalid fortification: {e}")
                        else:
                            print("Territories are not connected")
                    else:
                        print("Invalid territory name")
                else:
                    print("Invalid territory")
            else:
                print("Invalid territory name")
        
        self.end_turn()

    def add_player(self, name: str, color: Tuple[int, int, int]):
        player = Player(name, color)
        self.players.append(player)
        return player

    def start_game(self):
        if len(self.players) < 2:
            raise ValueError("Need at least 2 players to start the game")
        
        # Reinitialize the card deck
        self.card_deck = self._initialize_card_deck()
        
        self.current_player = self.players[0]
        
        # Get all territories and shuffle them
        territories = list(self.territories.values())
        random.shuffle(territories)
        
        # Initial territory distribution
        print("\nInitial Territory Distribution Phase")
        current_player_idx = 0
        for territory in territories:
            player = self.players[current_player_idx]
            territory.owner = player
            territory.troops = 1  # Start with 1 troop each
            player.territories.append(territory)
            print(f"{player.name} claims {territory.name}")
            
            # Move to next player
            current_player_idx = (current_player_idx + 1) % len(self.players)
        
        # Calculate total troops to distribute (40, 35, 30, 25 for 2, 3, 4, 5 players respectively)
        troops_per_player = 40 - (len(self.players) - 2) * 5
        
        # Randomly distribute remaining troops for each player
        for player in self.players:
            remaining_troops = troops_per_player
            player_territories = player.territories.copy()
            random.shuffle(player_territories)
            
            # Distribute troops randomly
            while remaining_troops > 0 and player_territories:
                # Choose a random territory
                territory = random.choice(player_territories)
                # Add 1-3 troops randomly
                troops_to_add = min(random.randint(1, 3), remaining_troops)
                territory.troops += troops_to_add
                remaining_troops -= troops_to_add
                
                # If we've used all troops for this territory, remove it from the list
                if remaining_troops == 0:
                    player_territories.remove(territory)
            
            print(f"{player.name} has {troops_per_player} troops distributed across their territories")
            for territory in player.territories:
                print(f"  {territory.name}: {territory.troops} troops")
            
            # Initialize reinforcements for the first turn
            player.reinforcements = self.calculate_reinforcements(player)
            print(f"{player.name} starts with {player.reinforcements} reinforcements for their first turn")

    def _initialize_card_deck(self) -> List[Card]:
        deck = []
        # Add territory cards with types based on continents
        for territory in self.territories.values():
            # Assign card types based on continents
            if territory.continent in ["North America", "South America"]:
                card_type = "infantry"
            elif territory.continent in ["Europe", "Africa"]:
                card_type = "cavalry"
            elif territory.continent in ["Asia", "Australia"]:
                card_type = "artillery"
            else:
                card_type = "infantry"  # Default fallback
                
            deck.append(Card(territory.name, card_type))
        
        # Add wild cards
        for _ in range(2):
            deck.append(Card("wild", "wild"))
        
        random.shuffle(deck)
        return deck
    
    def draw_card(self, player: Player):
        if self.card_deck:
            card = self.card_deck.pop()
            player.cards.append(card)
            print(f"DEBUG: {player.name} drew a {card.type} card for territory {card.territory}")
            return card
        return None
        
class AIPlayer(Player):
    def __init__(self, name: str, color: Tuple[int, int, int]):
        super().__init__(name, color)
        self.target_continent = None
        self.defensive_territories = set()
        self.offensive_territories = set()
        self.monte_carlo_simulations = 1000  # Increased for better accuracy
        self.heuristic_weights = {
            'territory_count': 1.0,      # +1 per territory
            'continent_control': 5.0,     # +5 for full continent
            'border_troops': 1.0,         # +1 per troop on border
            'enemy_neighbors': -2.0,      # -2 per weak region
            'army_strength': 0.5         # ± based on total count
        }

    def evaluate_territory(self, territory: Territory, game: 'RiskGame') -> float:
        """Evaluate a territory's strategic value"""
        score = 0.0
        
        # Base territory value
        score += self.heuristic_weights['territory_count']
        
        # Continent control value
        continent_territories = [t for t in game.territories.values() if t.continent == territory.continent]
        if all(t.owner == self for t in continent_territories):
            score += self.heuristic_weights['continent_control']
        
        # Border troops value
        enemy_neighbors = sum(1 for c in territory.connections 
                            if game.territories[c].owner != self)
        if enemy_neighbors > 0:
            score += territory.troops * self.heuristic_weights['border_troops']
        
        # Enemy neighbors penalty
        score += enemy_neighbors * self.heuristic_weights['enemy_neighbors']
        
        # Army strength comparison
        total_enemy_troops = sum(t.troops for t in game.territories.values() 
                               if t.owner != self and t.name in territory.connections)
        if total_enemy_troops > 0:
            strength_diff = territory.troops - total_enemy_troops
            score += strength_diff * self.heuristic_weights['army_strength']
        
        return score

    def _update_strategy(self, game: 'RiskGame'):
        """Update AI's strategic targets and territory classifications"""
        # Choose target continent based on current holdings and potential
        continent_scores = {}
        for continent, bonus in game.continent_bonus.items():
            continent_territories = [t for t in game.territories.values() if t.continent == continent]
            owned = sum(1 for t in continent_territories if t.owner == self)
            potential = sum(1 for t in continent_territories 
                          if t.owner != self and 
                          any(c.owner == self for c in [game.territories[conn] for conn in t.connections]))
            # Score based on ownership percentage and potential for expansion
            continent_scores[continent] = (owned / len(continent_territories)) * (1 + potential/len(continent_territories))
        
        self.target_continent = max(continent_scores.items(), key=lambda x: x[1])[0]
        
        # Classify territories as defensive or offensive
        self.defensive_territories.clear()
        self.offensive_territories.clear()
        
        for territory in self.territories:
            # Check if territory is on border with enemy
            is_border = any(t.owner != self for t in [game.territories[c] for c in territory.connections])
            
            if is_border:
                if territory.continent == self.target_continent:
                    self.defensive_territories.add(territory)
                else:
                    self.offensive_territories.add(territory)

    def _reinforcement_phase(self, game: 'RiskGame'):
        """Place reinforcements strategically"""
        while self.reinforcements > 0:
            # Evaluate all territories
            territory_scores = {}
            for territory in self.territories:
                score = self.evaluate_territory(territory, game)
                territory_scores[territory] = score
            
            # Reinforce the territory with highest score
            best_territory = max(territory_scores.items(), key=lambda x: x[1])[0]
            game.reinforce(best_territory)

    def monte_carlo_simulate_attack(self, attacker: Territory, defender: Territory) -> float:
        """Simulate attack multiple times using Monte Carlo method"""
        wins = 0
        total_troops_lost = 0
        
        for _ in range(self.monte_carlo_simulations):
            # Create copies of territories for simulation
            sim_attacker = Territory(attacker.name, attacker.continent)
            sim_attacker.troops = attacker.troops
            sim_defender = Territory(defender.name, defender.continent)
            sim_defender.troops = defender.troops
            
            # Simulate combat until one side is defeated
            while sim_attacker.troops > 1 and sim_defender.troops > 0:
                # Roll dice
                attacker_dice = min(3, sim_attacker.troops - 1)
                defender_dice = min(2, sim_defender.troops)
                attacker_rolls = sorted([random.randint(1, 6) for _ in range(attacker_dice)], reverse=True)
                defender_rolls = sorted([random.randint(1, 6) for _ in range(defender_dice)], reverse=True)
                
                # Compare dice and apply losses
                for a_roll, d_roll in zip(attacker_rolls, defender_rolls):
                    if a_roll > d_roll:
                        sim_defender.troops -= 1
                    else:
                        sim_attacker.troops -= 1
            
            if sim_defender.troops <= 0:
                wins += 1
                total_troops_lost += (attacker.troops - sim_attacker.troops)
        
        win_rate = wins / self.monte_carlo_simulations
        avg_troops_lost = total_troops_lost / self.monte_carlo_simulations if wins > 0 else float('inf')
        
        # Return a score that considers both win rate and troop loss
        return win_rate * (1 - (avg_troops_lost / attacker.troops))

    def _attack_phase(self, game: 'RiskGame'):
        """Execute attacks based on Monte Carlo simulation results"""
        # Get all possible attacks and evaluate them
        possible_attacks = []
        for attacker in self.territories:
            if attacker.troops > 1:
                for connection in attacker.connections:
                    defender = game.territories[connection]
                    if defender.owner != self:
                        # Calculate attack score using Monte Carlo
                        attack_score = self.monte_carlo_simulate_attack(attacker, defender)
                        
                        # Add strategic value for target continent
                        if defender.continent == self.target_continent:
                            attack_score *= 1.5
                        
                        # Only consider attacks with good chances of success
                        if attack_score > 0.4:  # Lowered threshold to be more aggressive
                            possible_attacks.append((attacker, defender, attack_score))
        
        # Sort attacks by score
        possible_attacks.sort(key=lambda x: x[2], reverse=True)
        
        # Execute attacks
        attacks_made = 0
        max_attacks = 5  # Limit number of attacks per turn
        
        while attacks_made < max_attacks and possible_attacks:
            attacker, defender, _ = possible_attacks[0]
            try:
                if game.attack(attacker, defender):
                    attacks_made += 1
                    # Update strategy after successful attack
                    self._update_strategy(game)
                    # Recalculate possible attacks
                    possible_attacks = [a for a in possible_attacks 
                                      if a[0].troops > 1 and a[1].troops > 0]
            except ValueError:
                possible_attacks.pop(0)

    def _fortify_phase(self, game: 'RiskGame'):
        """Move troops to improve defensive position"""
        # Find territories that can fortify
        can_fortify = [t for t in self.territories if t.troops > 1]
        if not can_fortify:
            return
        
        # Evaluate fortification moves
        best_move = None
        best_score = float('-inf')
        
        for source in can_fortify:
            # Skip territories on enemy borders
            if any(game.territories[c].owner != self for c in source.connections):
                continue
                
            for connection in source.connections:
                target = game.territories[connection]
                if target.owner == self and target != source:
                    # Calculate how many troops to move
                    troops_to_move = source.troops // 2
                    if troops_to_move > 0:
                        # Evaluate the move
                        current_score = self.evaluate_territory(target, game)
                        new_score = self.evaluate_territory(target, game) + (troops_to_move * 0.5)
                        
                        if new_score > best_score:
                            best_score = new_score
                            best_move = (source, target, troops_to_move)
        
        if best_move:
            source, target, troops = best_move
            try:
                game.fortify(source, target, troops)
            except ValueError:
                pass

def main():
    try:
        # Initialize the menu GUI
        from menu_gui import MenuGUI
        menu = MenuGUI()
        result = menu.run()
        
        if result is None:
            return
        
        print("Received result from menu:", result)  # Debug print
        
        # Validate settings
        required_settings = ['num_players', 'ai_players', 'max_cards', 'random_events', 'victory_condition']
        if not all(key in result for key in required_settings):
            print("Error: Missing required settings")
            return
        
        # Close the menu GUI
        pygame.quit()
        
        # Initialize pygame again for the game GUI
        pygame.init()
        
        # Initialize the game
        game = RiskGame()
        game.initialize_game()
        
        # Handle load game
        if isinstance(result, dict) and 'load_game' in result:
            if not game.load_game(result['load_game']):
                return
        else:
            try:
                # Add players based on settings
                colors = [
                    (255, 0, 0),    # Red
                    (0, 0, 255),    # Blue
                    (0, 255, 0),    # Green
                    (255, 255, 0),  # Yellow
                    (255, 0, 255),  # Magenta
                    (0, 255, 255)   # Cyan
                ]
                
                print("Creating game with settings:", result)  # Debug print
                
                # Validate player counts
                num_players = int(result['num_players'])
                num_ai = int(result['ai_players'])
                
                if num_players < 2 or num_players > 6:
                    print("Error: Invalid number of players")
                    return
                
                if num_ai >= num_players:
                    print("Error: Too many AI players")
                    return
                
                # Add human players
                num_human_players = num_players - num_ai
                print(f"Adding {num_human_players} human players")  # Debug print
                
                for i in range(num_human_players):
                    name = f"Player {i+1}"
                    game.add_player(name, colors[i])
                    game.players[-1].max_cards = int(result['max_cards'])
                
                # Add AI players
                print(f"Adding {num_ai} AI players")  # Debug print
                for i in range(num_ai):
                    name = f"AI Player {i+1}"
                    ai_player = AIPlayer(name, colors[num_human_players + i])
                    ai_player.max_cards = int(result['max_cards'])
                    game.players.append(ai_player)
                
                # Start the game
                game.start_game()
                
            except Exception as e:
                print(f"Error during game initialization: {e}")
                return
        
        # Start the GUI
        from gui import RiskGUI
        gui = RiskGUI(game)
        gui.run()
        
    except Exception as e:
        print(f"Error in main game loop: {e}")
        return

if __name__ == "__main__":
    main()