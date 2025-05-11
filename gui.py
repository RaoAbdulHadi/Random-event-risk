import pygame
import math
import random
from pygame.locals import *
from typing import Dict, Tuple, List
from project import RiskGame, Territory, Player, AIPlayer

# Initialize Pygame
pygame.init()

class RiskGUI:
    def __init__(self, game: RiskGame):
        self.game = game
        self.screen_width = 1366  # Standard laptop width
        self.screen_height = 720
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("Random Event Risk")
        
        # Colors
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.GRAY = (200, 200, 200)
        self.BUTTON_COLOR = (100, 100, 100)
        self.BUTTON_HOVER_COLOR = (150, 150, 150)
        self.POPUP_COLOR = (50, 50, 50)
        self.OCEAN_BLUE = (135, 206, 235)  # A lighter ocean blue color
        
        # Continent colors (more visible)
        self.continent_colors = {
            "North America": (255, 200, 200),  # Light red
            "South America": (200, 255, 200),  # Light green
            "Europe": (200, 200, 255),        # Light blue
            "Africa": (255, 255, 200),        # Light yellow
            "Asia": (255, 200, 255),          # Light purple
            "Australia": (200, 255, 255)      # Light cyan
        }
        
        # Territory positions (simplified for now)
        self.territory_positions = self._initialize_territory_positions()
        
        # Fonts
        self.font = pygame.font.Font(None, 20)  # Slightly smaller font
        self.title_font = pygame.font.Font(None, 32)
        self.event_font = pygame.font.Font(None, 40)
        self.continent_font = pygame.font.Font(None, 36)  # New font for continent names
        
        # Game state
        self.selected_territory = None
        self.target_territory = None
        self.phase = "reinforcement"  # reinforcement, attack, fortify
        self.current_player = game.current_player
        
        # Button properties
        self.button_rect = pygame.Rect(self.screen_width - 150, 20, 120, 40)
        self.button_hovered = False
        
        # Player info button properties
        self.info_button_rect = pygame.Rect(self.screen_width - 150, 70, 120, 40)
        self.infoClosure = pygame.Rect(self.screen_width - 150, 70, 120, 40)
        self.info_button_hovered = False
        self.showing_info = False
        
        # Event popup properties
        self.showing_event = False
        self.current_event = None
        self.event_button_rect = pygame.Rect(self.screen_width//2 - 60, self.screen_height//2 + 50, 120, 40)
        self.event_button_hovered = False
        
        # Card trading popup properties
        self.showing_card_prompt = False
        self.card_button_rect = pygame.Rect(self.screen_width//2 - 60, self.screen_height//2 + 50, 120, 40)
        self.card_button_hovered = False
        self.card_yes_rect = pygame.Rect(self.screen_width//2 - 100, self.screen_height//2 + 50, 80, 40)
        self.card_no_rect = pygame.Rect(self.screen_width//2 + 20, self.screen_height//2 + 50, 80, 40)
        self.card_yes_hovered = False
        self.card_no_hovered = False

    def _initialize_territory_positions(self) -> Dict[str, Tuple[int, int]]:
        # Define positions for each continent
        positions = {
            # North America
            "Alaska": (150, 100),
            "Northwest Territory": (250, 100),
            "Greenland": (400, 100),
            "Alberta": (175, 175),
            "Ontario": (325, 175),
            "Quebec": (425, 175),
            "Western United States": (175, 250),
            "Eastern United States": (325, 250),
            "Central America": (250, 325),
            
            # South America
            "Venezuela": (250, 400),
            "Peru": (325, 475),
            "Brazil": (400, 475),
            "Argentina": (375, 550),
            
            # Europe (adjusted positions)
            "Iceland": (550, 100),
            "Scandinavia": (650, 150),
            "Great Britain": (550, 200),
            "Northern Europe": (650, 200),
            "Western Europe": (550, 250),
            "Southern Europe": (650, 275),
            "Ukraine": (750, 200),
            
            # Africa (adjusted positions)
            "North Africa": (550, 375),
            "Egypt": (630, 350),
            "East Africa": (700, 400),
            "Congo": (625, 475),
            "South Africa": (550, 550),
            "Madagascar": (700, 550),
            
            # Asia (adjusted positions)
            "Ural": (825, 150),
            "Siberia": (900, 150),
            "Yakutsk": (975, 100),
            "Kamchatka": (1050, 100),
            "Afghanistan": (825, 225),
            "China": (900, 225),
            "Mongolia": (975, 225),
            "Japan": (1050, 250),
            "Middle East": (825, 300),
            "India": (900, 325),
            "Southeast Asia": (970, 325),
            
            # Australia
            "Indonesia": (1000, 400),
            "New Guinea": (1075, 400),
            "Western Australia": (975, 500),
            "Eastern Australia": (1075, 475)
        }
        
        # Scale positions to fit the screen
        scale_x = self.screen_width / 1200
        scale_y = self.screen_height / 650
        
        scaled_positions = {}
        for territory, (x, y) in positions.items():
            scaled_positions[territory] = (int(x * scale_x), int(y * scale_y))
            
        return scaled_positions
    
    def draw_territory(self, territory: Territory, pos: Tuple[int, int]):
        x, y = pos
        color = territory.owner.color if territory.owner else self.GRAY
        
        # Draw territory circle (smaller size)
        pygame.draw.circle(self.screen, color, (x, y), 20)  # Reduced from 30 to 20
        pygame.draw.circle(self.screen, self.BLACK, (x, y), 20, 2)  # Reduced from 30 to 20
        
        # Draw territory name
        name_text = self.font.render(territory.name, True, self.BLACK)
        self.screen.blit(name_text, (x - 30, y - 35))  # Adjusted position
        
        # Draw troop count
        troop_text = self.font.render(str(territory.troops), True, self.BLACK)
        self.screen.blit(troop_text, (x - 5, y - 7))  # Adjusted position
        
        # Draw selection highlight
        if self.selected_territory == territory:
            pygame.draw.circle(self.screen, (0,200,0), (x, y), 25, 3)  # Reduced from 35 to 25
        elif self.target_territory == territory:
            pygame.draw.circle(self.screen, (0, 50, 0), (x, y), 25, 3)
    
    def draw_connections(self):
        for territory in self.game.territories.values():
            start_pos = self.territory_positions[territory.name]
            for connection in territory.connections:
                end_pos = self.territory_positions[connection]
                
                # Special case for Alaska-Kamchatka connection
                if (territory.name == "Alaska" and connection == "Kamchatka") or \
                   (territory.name == "Kamchatka" and connection == "Alaska"):
                    # Draw a curved line that wraps around the screen
                    points = []
                    # Start from Alaska
                    points.append(start_pos)
                    # Add control points for the curve
                    if territory.name == "Alaska":
                        points.append((0, start_pos[1]))  # Left edge
                        points.append((0, end_pos[1]))    # Left edge at Kamchatka's height
                    else:
                        points.append((self.screen_width, start_pos[1]))  # Right edge
                        points.append((self.screen_width, end_pos[1]))    # Right edge at Alaska's height
                    # End at Kamchatka
                    points.append(end_pos)
                    
                    # Draw the curved line
                    pygame.draw.lines(self.screen, self.BLACK, False, points, 2)
                else:
                    # Regular straight line for other connections
                    pygame.draw.line(self.screen, self.BLACK, start_pos, end_pos, 2)
    
    def draw_game_info(self):
        # Calculate bottom left position
        bottom_margin = 80  # Increased from 20 to 100
        left_margin = 20
        
        # Draw current player
        player_text = self.title_font.render(
            f"Current Player: {self.current_player.name}", 
            True, 
            self.current_player.color
        )
        self.screen.blit(player_text, (left_margin, self.screen_height - bottom_margin - 80))
        
        # Draw phase
        phase_text = self.title_font.render(
            f"Phase: {self.phase.capitalize()}", 
            True, 
            self.BLACK
        )
        self.screen.blit(phase_text, (left_margin, self.screen_height - bottom_margin - 40))
        
        # Draw reinforcements
        if self.phase == "reinforcement":
            reinforce_text = self.font.render(
                f"Available Reinforcements: {self.current_player.reinforcements}",
                True,
                self.BLACK
            )
            self.screen.blit(reinforce_text, (left_margin, self.screen_height - bottom_margin))
        
        # Draw cards
        cards_text = self.font.render(
            f"Cards: {[card.type for card in self.current_player.cards]}",
            True,
            self.BLACK
        )
        self.screen.blit(cards_text, (left_margin, self.screen_height - bottom_margin + 20))
        
        # Draw Next Phase button
        button_color = self.BUTTON_HOVER_COLOR if self.button_hovered else self.BUTTON_COLOR
        pygame.draw.rect(self.screen, button_color, self.button_rect)
        pygame.draw.rect(self.screen, self.BLACK, self.button_rect, 2)
        
        button_text = self.font.render("Next Phase", True, self.WHITE)
        text_rect = button_text.get_rect(center=self.button_rect.center)
        self.screen.blit(button_text, text_rect)
        
        # Draw Player Info button
        info_button_color = self.BUTTON_HOVER_COLOR if self.info_button_hovered else self.BUTTON_COLOR
        pygame.draw.rect(self.screen, info_button_color, self.info_button_rect)
        pygame.draw.rect(self.screen, self.BLACK, self.info_button_rect, 2)
        
        info_button_text = self.font.render("Player Info", True, self.WHITE)
        info_text_rect = info_button_text.get_rect(center=self.info_button_rect.center)
        self.screen.blit(info_button_text, info_text_rect)
    
    def handle_click(self, pos: Tuple[int, int]):
        x, y = pos
        for territory_name, territory_pos in self.territory_positions.items():
            tx, ty = territory_pos
            if math.sqrt((x - tx)**2 + (y - ty)**2) < 20:  # Reduced from 30 to 20
                territory = self.game.territories[territory_name]
                self.handle_territory_click(territory)
                break

    def handle_player_reinforcement(self, territory: Territory):
        """Handle reinforcement for human players"""
        if territory.owner == self.current_player:
            if self.current_player.reinforcements > 0:
                # Place one troop
                territory.troops += 1
                self.current_player.reinforcements -= 1
                # Highlight the territory being reinforced
                self.selected_territory = territory
                pygame.time.delay(500)  # Short delay for visual feedback
                self.selected_territory = None

    
    def handle_territory_click(self, territory: Territory):
        if self.phase == "reinforcement":
            if isinstance(self.current_player, AIPlayer):
                self.handle_ai_reinforcement()
            else:
                self.handle_player_reinforcement(territory)
        elif self.phase == "attack":
            if self.selected_territory is None:
                if territory.owner == self.current_player and territory.troops > 1:
                    self.selected_territory = territory
            else:
                if territory.owner != self.current_player:
                    try:
                        self.game.attack(self.selected_territory, territory)
                    except ValueError as e:
                        print(f"Invalid attack: {e}")
                self.selected_territory = None
        elif self.phase == "fortify":
            if self.selected_territory is None:
                if territory.owner == self.current_player and territory.troops > 1:
                    self.selected_territory = territory
            else:
                if territory.owner == self.current_player:
                    try:
                        # Calculate maximum troops that can be moved
                        max_troops = self.selected_territory.troops - 1
                        # Move all but one troop
                        self.game.fortify(self.selected_territory, territory, max_troops)
                    except ValueError as e:
                        print(f"Invalid fortification: {e}")
                self.selected_territory = None
    
    def show_event_popup(self, event):
        self.showing_event = True
        self.current_event = event
        
        # Create semi-transparent overlay
        overlay = pygame.Surface((self.screen_width, self.screen_height))
        overlay.fill(self.BLACK)
        overlay.set_alpha(128)
        self.screen.blit(overlay, (0, 0))
        
        # Draw popup box (wider)
        popup_rect = pygame.Rect(self.screen_width//2 - 300, self.screen_height//2 - 100, 600, 200)
        pygame.draw.rect(self.screen, self.POPUP_COLOR, popup_rect)
        pygame.draw.rect(self.screen, self.WHITE, popup_rect, 2)
        
        # Draw event title
        title_text = self.event_font.render("Random Event!", True, self.WHITE)
        title_rect = title_text.get_rect(center=(self.screen_width//2, self.screen_height//2 - 60))
        self.screen.blit(title_text, title_rect)
        
        # Draw event name
        name_text = self.font.render(event.name, True, self.WHITE)
        name_rect = name_text.get_rect(center=(self.screen_width//2, self.screen_height//2 - 20))
        self.screen.blit(name_text, name_rect)
        
        # Draw event description with specific values
        description = event.description
        if event.name == "Natural Disaster":
            continent = random.choice(list(set(t.continent for t in self.game.territories.values())))
            description = description.replace("a random continent", f"the continent of {continent}")
            # Apply effect
            for territory in self.game.territories.values():
                if territory.continent == continent and territory.owner == self.current_player:
                    territory.troops = max(0, territory.troops - 1)
        elif event.name == "Reinforcement":
            player_territories = [t for t in self.game.territories.values() if t.owner == self.current_player]
            if player_territories:
                territory = random.choice(player_territories)
                description = description.replace("a random territory", f"the territory of {territory.name}")
                # Apply effect
                territory.troops += 2
        elif event.name == "Territory Swap":
            territories = list(self.game.territories.values())
            if len(territories) >= 2:
                territory1, territory2 = random.sample(territories, 2)
                description = description.replace("two random territories", f"{territory1.name} and {territory2.name}")
                # Apply effect
                owner1 = territory1.owner
                owner2 = territory2.owner
                if owner1 and owner2:
                    territory1.owner.territories.remove(territory1)
                    territory2.owner.territories.remove(territory2)
                    territory1.owner = owner2
                    territory2.owner = owner1
                    owner2.territories.append(territory1)
                    owner1.territories.append(territory2)
        elif event.name == "Border Dispute":
            territories = list(self.game.territories.values())
            if len(territories) >= 2:
                territory1 = random.choice(territories)
                connected = [t for t in territories if t.name in territory1.connections]
                if connected:
                    territory2 = random.choice(connected)
                    description = description.replace("Two random connected territories", f"{territory1.name} and {territory2.name}")
                    # Apply effect
                    territory1.troops = max(0, territory1.troops - 1)
                    territory2.troops = max(0, territory2.troops - 1)
        elif event.name == "Alliance":
            continent = random.choice(list(set(t.continent for t in self.game.territories.values())))
            description = description.replace("a random continent", f"the continent of {continent}")
            # Apply effect
            for territory in self.game.territories.values():
                if territory.continent == continent:
                    territory.troops += 1
        elif event.name == "Civil War":
            affected_territories = [t.name for t in self.game.territories.values() if t.owner == self.current_player and t.troops > 2]
            if affected_territories:
                description = description.replace("All territories", f"Territories {', '.join(affected_territories)}")
                # Apply effect
                for territory in self.game.territories.values():
                    if territory.owner == self.current_player and territory.troops > 2:
                        territory.troops -= 1
        elif event.name == "Disease":
            # Apply effect
            for territory in self.game.territories.values():
                if territory.owner == self.current_player and territory.troops > 3:
                    territory.troops -= 1
        elif event.name == "Economic Boom":
            # Apply effect
            for territory in self.game.territories.values():
                territory.troops += 1
        
        # Split description into multiple lines if needed
        words = description.split()
        lines = []
        current_line = []
        for word in words:
            current_line.append(word)
            test_line = ' '.join(current_line)
            if self.font.size(test_line)[0] > 550:  # Width limit for text
                current_line.pop()
                lines.append(' '.join(current_line))
                current_line = [word]
        if current_line:
            lines.append(' '.join(current_line))
        
        # Draw each line of the description
        for i, line in enumerate(lines):
            desc_text = self.font.render(line, True, self.WHITE)
            desc_rect = desc_text.get_rect(center=(self.screen_width//2, self.screen_height//2 + 20 + i*25))
            self.screen.blit(desc_text, desc_rect)
        
        # Draw continue button
        button_color = self.BUTTON_HOVER_COLOR if self.event_button_hovered else self.BUTTON_COLOR
        pygame.draw.rect(self.screen, button_color, self.event_button_rect)
        pygame.draw.rect(self.screen, self.WHITE, self.event_button_rect, 2)
        
        continue_text = self.font.render("Continue", True, self.WHITE)
        text_rect = continue_text.get_rect(center=self.event_button_rect.center)
        self.screen.blit(continue_text, text_rect)
        
        pygame.display.flip()

    def draw_continent_boundaries(self):
        # Define continent regions (x, y, width, height)
        continent_regions = {
            "North America": (50, 50, 470, 350),
            "South America": (220, 400, 300, 250),
            "Europe": (560, 50, 350, 300),
            "Africa": (550, 350, 300, 300),
            "Asia": (890, 50, 350, 350),
            "Australia": (1050, 400, 300, 200)
        }
        
        # Draw each continent's region
        for continent, region in continent_regions.items():
            # Draw the continent region
            pygame.draw.rect(self.screen, self.continent_colors[continent], region)
            # Draw the border
            pygame.draw.rect(self.screen, self.BLACK, region, 2)
            
            # Draw continent name with the new font
            name_text = self.continent_font.render(continent, True, self.BLACK)
            x = region[0] + region[2]//2 - name_text.get_width()//2
            
            # Position Africa, Australia, and South America's names below their regions, others above
            if continent in ["Africa", "Australia", "South America"]:
                y = region[1] + region[3] + 25  # Position below the region
            else:
                y = region[1] - 25  # Position above the region
                
            self.screen.blit(name_text, (x, y))

    def show_card_prompt(self):
        self.showing_card_prompt = True
        
        # Create semi-transparent overlay
        overlay = pygame.Surface((self.screen_width, self.screen_height))
        overlay.fill(self.BLACK)
        overlay.set_alpha(128)
        self.screen.blit(overlay, (0, 0))
        
        # Draw popup box
        popup_rect = pygame.Rect(self.screen_width//2 - 300, self.screen_height//2 - 100, 600, 200)
        pygame.draw.rect(self.screen, self.POPUP_COLOR, popup_rect)
        pygame.draw.rect(self.screen, self.WHITE, popup_rect, 2)
        
        # Draw title
        title_text = self.event_font.render("Trade Cards?", True, self.WHITE)
        title_rect = title_text.get_rect(center=(self.screen_width//2, self.screen_height//2 - 60))
        self.screen.blit(title_text, title_rect)
        
        # Draw card information
        card_text = self.font.render(f"Your cards: {[card.type for card in self.current_player.cards]}", True, self.WHITE)
        card_rect = card_text.get_rect(center=(self.screen_width//2, self.screen_height//2 - 20))
        self.screen.blit(card_text, card_rect)
        
        # Draw reinforcement information
        reinforce_text = self.font.render("Trade cards for reinforcements?", True, self.WHITE)
        reinforce_rect = reinforce_text.get_rect(center=(self.screen_width//2, self.screen_height//2 + 20))
        self.screen.blit(reinforce_text, reinforce_rect)
        
        # Draw Yes/No buttons
        pygame.draw.rect(self.screen, self.BUTTON_HOVER_COLOR if self.card_yes_hovered else self.BUTTON_COLOR, self.card_yes_rect)
        pygame.draw.rect(self.screen, self.WHITE, self.card_yes_rect, 2)
        yes_text = self.font.render("Yes", True, self.WHITE)
        yes_rect = yes_text.get_rect(center=self.card_yes_rect.center)
        self.screen.blit(yes_text, yes_rect)
        
        pygame.draw.rect(self.screen, self.BUTTON_HOVER_COLOR if self.card_no_hovered else self.BUTTON_COLOR, self.card_no_rect)
        pygame.draw.rect(self.screen, self.WHITE, self.card_no_rect, 2)
        no_text = self.font.render("No", True, self.WHITE)
        no_rect = no_text.get_rect(center=self.card_no_rect.center)
        self.screen.blit(no_text, no_rect)
        
        pygame.display.flip()

    def show_player_info(self):
        self.showing_info = True
        
        # Create semi-transparent overlay
        overlay = pygame.Surface((self.screen_width, self.screen_height))
        overlay.fill(self.BLACK)
        overlay.set_alpha(128)
        self.screen.blit(overlay, (0, 0))
        
        # Draw popup box
        popup_width = 400
        popup_height = 300
        popup_rect = pygame.Rect(
            self.screen_width//2 - popup_width//2,
            self.screen_height//2 - popup_height//2,
            popup_width,
            popup_height
        )
        pygame.draw.rect(self.screen, self.POPUP_COLOR, popup_rect)
        pygame.draw.rect(self.screen, self.WHITE, popup_rect, 2)
        
        # Draw title
        title_text = self.title_font.render("Player Information", True, self.WHITE)
        title_rect = title_text.get_rect(center=(self.screen_width//2, popup_rect.top + 40))
        self.screen.blit(title_text, title_rect)
        
        # Draw player information
        y_offset = popup_rect.top + 80
        for player in self.game.players:
            # Player name and color
            name_text = self.font.render(f"{player.name}:", True, player.color)
            self.screen.blit(name_text, (popup_rect.left + 20, y_offset))
            
            # Territories count
            territory_text = self.font.render(
                f"Territories: {len(player.territories)}",
                True,
                self.WHITE
            )
            self.screen.blit(territory_text, (popup_rect.left + 20, y_offset + 30))
            
            # Card count
            card_text = self.font.render(
                f"Cards: {len(player.cards)}",
                True,
                self.WHITE
            )
            self.screen.blit(card_text, (popup_rect.left + 20, y_offset + 60))
            
            y_offset += 100
        
        # Draw close button
        close_button_rect = pygame.Rect(
            self.screen_width//2 - 40,
            popup_rect.bottom - 60,
            80,
            40
        )
        pygame.draw.rect(self.screen, self.BUTTON_COLOR, close_button_rect)
        pygame.draw.rect(self.screen, self.WHITE, close_button_rect, 2)
        
        close_text = self.font.render("Close", True, self.WHITE)
        close_rect = close_text.get_rect(center=close_button_rect.center)
        self.screen.blit(close_text, close_rect)
        
        self.infoClosure = close_button_rect

        pygame.display.flip()

    def handle_ai_reinforcement(self):
        """Handle reinforcement for AI players"""
        if self.current_player.reinforcements > 0:
            # Call AI's reinforcement strategy
            
            self.current_player._reinforcement_phase(self.game, self)
            pygame.time.delay(1000)  # 1 second delay between reinforcements

    def handle_ai_attack(self):
        print('fourmulating attack')
        self.current_player._attack_phase(self.game, self)
        print('fourmulating attack onde')

    def handle_ai_fortify(self):
        self.current_player._fortify_phase(self.game, self)

    def render(self):
        # Clear screen with ocean blue background
        self.screen.fill(self.OCEAN_BLUE)
        
        # Draw continent boundaries first
        self.draw_continent_boundaries()
        
        # Draw game elements
        self.draw_connections()
        for territory_name, pos in self.territory_positions.items():
            self.draw_territory(self.game.territories[territory_name], pos)
        self.draw_game_info()
        
        # Show player info if active
        if self.showing_info:
            self.show_player_info()
        # else:
        #     print('showing info')
        
        # Update display
        pygame.display.flip()

    def run(self):
        running = True
        while running:

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                # Handle mouse motion for button hover effects
                if event.type == pygame.MOUSEMOTION:
                    mouse_pos = pygame.mouse.get_pos()
                    self.button_hovered = self.button_rect.collidepoint(mouse_pos)
                    self.card_yes_hovered = self.card_yes_rect.collidepoint(mouse_pos)
                    self.card_no_hovered = self.card_no_rect.collidepoint(mouse_pos)
                
                # Handle mouse clicks
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    
                    # Handle card trading prompt
                    if self.showing_card_prompt:
                        if self.card_yes_rect.collidepoint(mouse_pos):
                            reinforcements = self.current_player.trade_cards()
                            self.current_player.reinforcements += reinforcements
                            self.showing_card_prompt = False
                        elif self.card_no_rect.collidepoint(mouse_pos):
                            self.showing_card_prompt = False
                        continue
                    
                    # Handle Next Phase button
                    if self.button_rect.collidepoint(mouse_pos):
                        if self.phase == "reinforcement":
                            self.phase = "attack"
                        elif self.phase == "attack":
                            self.phase = "fortify"
                        elif self.phase == "fortify":
                            self.phase = "reinforcement"
                            # Check for card trading at the start of reinforcement phase
                            if self.current_player.can_trade_cards():
                                self.showing_card_prompt = True

                            # Show event popup and end turn
                            # event = random.choice(self.game.events)
                            # self.show_event_popup(event)

                            event = self.game.end_turn()
                            self.show_event_popup(event)
                            
                            # Update current player after turn ends
                            self.current_player = self.game.current_player
                            self.selected_territory = None
                            self.target_territory = None

                            print(self.current_player.__class__)
                            print(AIPlayer)

                            print(self.current_player.__class__ is AIPlayer)
                            # if it’s the AI’s turn, play out its entire turn in one go
                            # if isinstance(self.current_player, AIPlayer):
                            if isinstance(self.current_player, AIPlayer) or 'AIPlayer' in str(self.current_player.__class__):
                                # 1) Reinforcement
                                print(' ****************** Ai player')
                                self.showing_event = False
                                
                                while self.current_player.reinforcements > 0:
                                    self.handle_ai_reinforcement()
                                print('reinforcement done')
                                self.phase = 'attack'

                                # 2) Attack phase
                                # you’ll need to write a small helper (e.g. self.handle_ai_attack())
                                # that chooses valid attacks until no more
                                self.handle_ai_attack()
                                print('attack done')

                                # 3) Fortify phase
                                # similarly, implement and call self.handle_ai_fortify()
                                self.phase = 'fortify'
                                self.handle_ai_fortify()
                                print('fortify done')
                                self.phase = 'reinforcement'

                                # 4) End its turn (invoke the same steps you do on human end-turn)
                                
                                # No effect on playerrrr *********************************************************************************************************************************************************************************************************************************************************



                                event = self.game.end_turn()
                                self.show_event_popup(event)

                                self.current_player = self.game.current_player

                            else:
                                print('*********** not ai player', type(self.current_player))

                    # Check if Player Info button was clicked
                    elif self.info_button_rect.collidepoint(mouse_pos):
                        self.showing_info = True
                    elif self.event_button_rect.collidepoint(mouse_pos):
                        self.showing_event = False
                    elif self.infoClosure.collidepoint(mouse_pos):
                        print('setting button false')
                        self.showing_info = False
                    else:
                        self.handle_click(mouse_pos)
            
            if not self.showing_event and not self.showing_card_prompt:
                self.render()
        
        pygame.quit() 