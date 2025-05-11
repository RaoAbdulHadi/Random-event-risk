import pygame
import sys
# from typing import Dict, Any, Optional, Tuple

class MenuGUI:
    def __init__(self):
        pygame.init()
        self.screen_width = 800
        self.screen_height = 600
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("Risk Game Menu")
        
        # Colors
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.GRAY = (200, 200, 200)
        self.BUTTON_COLOR = (100, 100, 100)
        self.HOVER_COLOR = (150, 150, 150)
        self.SELECTED_COLOR = (0, 255, 0)
        
        # Fonts
        self.font = pygame.font.Font(None, 36)
        self.title_font = pygame.font.Font(None, 48)
        
        # Game settings
        self.settings = {
            'num_players': 2,
            'ai_players': 1,
            'max_cards': 5,
            'random_events': True,
            'victory_condition': 'elimination'
        }
        
        # Menu state
        self.current_menu = 'main'  # main, settings, load
        self.selected_option = 0
        self.button_rects = []
        
    def draw_button(self, text: str, x: int, y: int, width: int, height: int, 
                   is_selected: bool = False, is_hovered: bool = False):
        # Draw button background
        color = self.SELECTED_COLOR if is_selected else (self.HOVER_COLOR if is_hovered else self.BUTTON_COLOR)
        pygame.draw.rect(self.screen, color, (x, y, width, height))
        pygame.draw.rect(self.screen, self.WHITE, (x, y, width, height), 2)
        
        # Draw button text
        text_surface = self.font.render(text, True, self.WHITE)
        text_rect = text_surface.get_rect(center=(x + width//2, y + height//2))
        self.screen.blit(text_surface, text_rect)
        
        return pygame.Rect(x, y, width, height)
    
    def draw_main_menu(self):
        self.screen.fill(self.BLACK)
        
        # Draw title
        title = self.title_font.render("Risk Game", True, self.WHITE)
        title_rect = title.get_rect(center=(self.screen_width//2, 100))
        self.screen.blit(title, title_rect)
        
        # Draw buttons
        button_width = 200
        button_height = 50
        spacing = 20
        start_y = 250
        
        self.button_rects = []
        
        # New Game button
        self.button_rects.append(self.draw_button(
            "New Game",
            self.screen_width//2 - button_width//2,
            start_y,
            button_width,
            button_height,
            self.selected_option == 0
        ))
        
        # Settings button
        self.button_rects.append(self.draw_button(
            "Settings",
            self.screen_width//2 - button_width//2,
            start_y + button_height + spacing,
            button_width,
            button_height,
            self.selected_option == 1
        ))
        
        # Quit button
        self.button_rects.append(self.draw_button(
            "Quit",
            self.screen_width//2 - button_width//2,
            start_y + (button_height + spacing) * 3,
            button_width,
            button_height,
            self.selected_option == 3
        ))
    
    def draw_settings_menu(self):
        self.screen.fill(self.BLACK)
        
        # Draw title
        title = self.title_font.render("Settings", True, self.WHITE)
        title_rect = title.get_rect(center=(self.screen_width//2, 100))
        self.screen.blit(title, title_rect)
        
        # Draw settings
        button_width = 300
        button_height = 50
        spacing = 20
        start_y = 200
        
        self.button_rects = []
        
        # Number of Players
        self.button_rects.append(self.draw_button(
            f"Number of Players: {self.settings['num_players']}",
            self.screen_width//2 - button_width//2,
            start_y,
            button_width,
            button_height,
            self.selected_option == 0
        ))
        
        # Number of AI Players
        self.button_rects.append(self.draw_button(
            f"Number of AI Players: {self.settings['ai_players']}",
            self.screen_width//2 - button_width//2,
            start_y + button_height + spacing,
            button_width,
            button_height,
            self.selected_option == 1
        ))
        
        # Random Events
        self.button_rects.append(self.draw_button(
            f"Random Events: {'On' if self.settings['random_events'] else 'Off'}",
            self.screen_width//2 - button_width//2,
            start_y + (button_height + spacing) * 2,
            button_width,
            button_height,
            self.selected_option == 2
        ))
        
        # Back button
        self.button_rects.append(self.draw_button(
            "Back",
            self.screen_width//2 - button_width//2,
            start_y + (button_height + spacing) * 3,
            button_width,
            button_height,
            self.selected_option == 3
        ))
    
    def handle_click(self, pos):
        for i, rect in enumerate(self.button_rects):
            if rect.collidepoint(pos):
                self.selected_option = i
                if self.current_menu == 'main':
                    if i == 0:  # New Game
                        return self.settings
                    elif i == 1:  # Settings
                        self.current_menu = 'settings'
                        self.selected_option = 0
                    elif i == 2:  # Quit game
                        return None
                elif self.current_menu == 'settings':
                    if i == 0:  # Number of Players
                        self.settings['num_players'] = (self.settings['num_players'] % 5) + 1
                    elif i == 1:  # Number of AI Players
                        self.settings['ai_players'] = (self.settings['ai_players'] % self.settings['num_players']) + 1
                    elif i == 2:  # Random Events
                        self.settings['random_events'] = not self.settings['random_events']
                    elif i == 3:  # Back
                        self.current_menu = 'main'
                        self.selected_option = 0
                break
    
    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return None
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Left click
                        result = self.handle_click(event.pos)
                        if result is not None:
                            return result
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        self.selected_option = (self.selected_option - 1) % len(self.button_rects)
                    elif event.key == pygame.K_DOWN:
                        self.selected_option = (self.selected_option + 1) % len(self.button_rects)
                    elif event.key == pygame.K_RETURN:
                        result = self.handle_click(self.button_rects[self.selected_option].center)
                        if result is not None:
                            return result
                    elif event.key == pygame.K_ESCAPE:
                        if self.current_menu != 'main':
                            self.current_menu = 'main'
                            self.selected_option = 0
                        else:
                            return None
            
            # Draw current menu
            if self.current_menu == 'main':
                self.draw_main_menu()
            elif self.current_menu == 'settings':
                self.draw_settings_menu()
            
            pygame.display.flip()
        
        pygame.quit()
        return None 