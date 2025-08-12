import pygame
import random
import sys
from pathlib import Path

# --- Constantes ---

# Configurações da tela
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800

# Cores (RGB)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (30, 144, 255)       # Dodger Blue
GREEN = (60, 179, 113)      # Medium Sea Green
GRAY = (40, 40, 40)         # Fundo do menu
YELLOW = (255, 193, 7)      # Amarelo para o botão Peek

# Path to the assets directory
ASSETS_DIR = Path(__file__).parent / "assets"

# Configurações do tabuleiro
CARD_WIDTH = 150
CARD_HEIGHT = 100
GAP = 20
FLIP_DELAY = 1000 # Tempo em milissegundos para desvirar
PEEK_DURATION = 2000 # Tempo em milissegundos para espiar

# Níveis de dificuldade (colunas, linhas, número de pares)
DIFFICULTY_LEVELS = {
    'Easy':   {'cols': 4, 'rows': 3, 'pairs': 6},
    'Normal': {'cols': 6, 'rows': 4, 'pairs': 12},
}

# Dados do Jogo (poderiam ficar em um arquivo separado no futuro)
SENTENCE_PARTS = [
    {'text': 'She works', 'id': 1}, {'text': 'at a technology company.', 'id': 1},
    {'text': 'They play soccer', 'id': 2}, {'text': 'in the park every Sunday.', 'id': 2},
    {'text': "He doesn't like", 'id': 3}, {'text': 'to wake up early.', 'id': 3},
    {'text': "We don't watch", 'id': 4}, {'text': 'TV during the week.', 'id': 4},
    {'text': 'Do you speak', 'id': 5}, {'text': 'French?', 'id': 5},
    {'text': 'Does your brother live', 'id': 6}, {'text': 'in Rio de Janeiro?', 'id': 6},
    {'text': 'She is working', 'id': 7}, {'text': 'on an important project right now.', 'id': 7},
    {'text': 'They are playing', 'id': 8}, {'text': 'soccer at this moment.', 'id': 8},
    {'text': "He isn't listening", 'id': 9}, {'text': 'to music.', 'id': 9},
    {'text': "We aren't watching", 'id': 10}, {'text': 'a movie tonight.', 'id': 10},
    {'text': 'Are you studying', 'id': 11}, {'text': 'for the test?', 'id': 11},
    {'text': 'Is your brother traveling', 'id': 12}, {'text': 'this month?', 'id': 12}
]

# --- Classes --

class Card:
    def __init__(self, text, id, rect):
        self.text = text
        self.id = id
        self.rect = rect
        self.is_flipped = False
        self.is_matched = False

    def draw(self, screen, font):
        border_color = GREEN if self.is_matched else BLUE
        
        if self.is_flipped or self.is_matched:
            pygame.draw.rect(screen, WHITE, self.rect, border_radius=10)
            pygame.draw.rect(screen, border_color, self.rect, 3, border_radius=10)

            words = self.text.split(' ')
            lines = []
            current_line = ""
            for word in words:
                test_line = f"{current_line} {word}".strip()
                if font.size(test_line)[0] < self.rect.width - 20:
                    current_line = test_line
                else:
                    lines.append(current_line)
                    current_line = word
            lines.append(current_line)

            total_height = len(lines) * font.get_height()
            start_y = self.rect.centery - total_height // 2
            for i, line in enumerate(lines):
                text_surface = font.render(line, True, BLACK)
                text_rect = text_surface.get_rect(centerx=self.rect.centerx, y=start_y + i * font.get_height())
                screen.blit(text_surface, text_rect)
        else:
            pygame.draw.rect(screen, BLUE, self.rect, border_radius=10)

class Game:
    def __init__(self, screen):
        self.screen = screen
        self.main_font = pygame.font.Font(None, 28)
        self.game_over_font = pygame.font.Font(None, 72)
        self.title_font = pygame.font.Font(None, 90)
        self.button_font = pygame.font.Font(None, 50)

        # Carrega os efeitos sonoros
        self.sounds = {}
        try:
            self.sounds['flip'] = pygame.mixer.Sound(ASSETS_DIR / 'flip.wav')
            self.sounds['match'] = pygame.mixer.Sound(ASSETS_DIR / 'match.wav')
            self.sounds['win'] = pygame.mixer.Sound(ASSETS_DIR / 'win.wav')
        except pygame.error as e:
            print(f"Warning: Could not load sound files. Error: {e}")
            # Create dummy sound objects so the game doesn't crash
            self.sounds = {key: pygame.mixer.Sound(buffer=b'') for key in ['flip', 'match', 'win']}

        # Estado inicial do jogo
        self.game_state = 'menu' # 'menu', 'playing'
        self.card_list = []
        self.current_difficulty = None

        # Estado para a funcionalidade "Peek"
        self.peek_used = False
        self.is_peeking = False
        self.peek_end_time = 0

        # Retângulos para os botões
        self.easy_button_rect = pygame.Rect(SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 - 60, 300, 60)
        self.normal_button_rect = pygame.Rect(SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 + 20, 300, 60)
        self.play_again_rect = pygame.Rect(SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 + 50, 300, 50)
        self.peek_button_rect = pygame.Rect(SCREEN_WIDTH - 220, 20, 200, 50)

    def create_board(self, data, cols, rows):
        card_list = []
        shuffled_data = data[:]
        random.shuffle(shuffled_data)

        board_width = cols * (CARD_WIDTH + GAP) - GAP
        board_height = rows * (CARD_HEIGHT + GAP) - GAP
        start_x = (SCREEN_WIDTH - board_width) // 2
        start_y = (SCREEN_HEIGHT - board_height) // 2

        # Garante que o tabuleiro não exceda a tela
        start_y = max(GAP, start_y)

        for i, item in enumerate(shuffled_data):
            col, row = i % cols, i // cols
            x = start_x + col * (CARD_WIDTH + GAP)
            y = start_y + row * (CARD_HEIGHT + GAP)
            rect = pygame.Rect(x, y, CARD_WIDTH, CARD_HEIGHT)
            card_list.append(Card(item['text'], item['id'], rect))
        return card_list

    def start_new_game(self, difficulty_key):
        self.current_difficulty = difficulty_key
        config = DIFFICULTY_LEVELS[difficulty_key]
        
        # Seleciona o número correto de pares de frases
        pairs_to_use = SENTENCE_PARTS[:config['pairs'] * 2]
        self.card_list = self.create_board(pairs_to_use, config['cols'], config['rows'])
        self.first_card = None
        self.second_card = None
        self.lock_board = False
        self.moves_count = 0
        self.game_over = False
        self.unflip_time = 0
        self.peek_used = False
        self.is_peeking = False

        self.game_state = 'playing'

    def handle_events(self, event):
        if event.type == pygame.QUIT:
            return False # Sinaliza para sair do jogo

        if event.type != pygame.MOUSEBUTTONDOWN:
            return True

        mouse_pos = pygame.mouse.get_pos()
        if self.game_state == 'menu':
            if self.easy_button_rect.collidepoint(mouse_pos):
                self.start_new_game('Easy')
            elif self.normal_button_rect.collidepoint(mouse_pos):
                self.start_new_game('Normal')
        
        elif self.game_state == 'playing':
            if self.game_over:
                if self.play_again_rect.collidepoint(mouse_pos):
                    self.start_new_game(self.current_difficulty) # Reinicia com a mesma dificuldade
            # Verifica clique no botão Peek
            elif self.peek_button_rect.collidepoint(mouse_pos) and not self.peek_used and not self.lock_board:
                self.activate_peek()
            # Verifica clique nas cartas
            elif not self.lock_board:
                for card in self.card_list:
                    if card.rect.collidepoint(mouse_pos) and not card.is_matched and not card.is_flipped:
                        card.is_flipped = True
                        self.sounds['flip'].play()
                        if self.first_card is None:
                            self.first_card = card
                        else:
                            self.second_card = card
                            self.moves_count += 1
                            self.check_for_match()
        return True

    def check_for_match(self):
        if self.first_card.id == self.second_card.id:
            self.first_card.is_matched = True
            self.sounds['match'].play()
            self.second_card.is_matched = True
            self.first_card, self.second_card = None, None
            if all(c.is_matched for c in self.card_list):
                self.sounds['win'].play()
                self.game_over = True
        else:
            self.lock_board = True
            self.unflip_time = pygame.time.get_ticks()

    def activate_peek(self):
        self.peek_used = True
        self.is_peeking = True
        self.lock_board = True
        self.peek_end_time = pygame.time.get_ticks() + PEEK_DURATION

        # Vira todas as cartas não combinadas
        for card in self.card_list:
            if not card.is_matched:
                card.is_flipped = True

    def deactivate_peek(self):
        self.is_peeking = False
        self.lock_board = False

        # Desvira todas as cartas, exceto as que já foram combinadas
        # ou as que estão sendo avaliadas pelo jogador
        for card in self.card_list:
            if not card.is_matched and card != self.first_card and card != self.second_card:
                card.is_flipped = False

    def update(self):
        if self.game_state != 'playing':
            return

        current_time = pygame.time.get_ticks()
        # Lógica para desativar o "peek"
        if self.is_peeking and current_time >= self.peek_end_time:
            self.deactivate_peek()
        # Lógica para desvirar cartas erradas
        elif self.lock_board and not self.is_peeking and not self.game_over:
            if current_time - self.unflip_time > FLIP_DELAY:
                if self.first_card and self.second_card:
                    self.first_card.is_flipped = False
                    self.second_card.is_flipped = False
                self.first_card, self.second_card = None, None
                self.lock_board = False

    def draw_menu_screen(self):
        self.screen.fill(GRAY)
        
        # Título
        title_text = self.title_font.render("Memory Game", True, WHITE)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 150))
        self.screen.blit(title_text, title_rect)

        # Botão Fácil
        pygame.draw.rect(self.screen, BLUE, self.easy_button_rect, border_radius=15)
        easy_text = self.button_font.render("Easy (4x3)", True, WHITE)
        easy_text_rect = easy_text.get_rect(center=self.easy_button_rect.center)
        self.screen.blit(easy_text, easy_text_rect)

        # Botão Normal
        pygame.draw.rect(self.screen, GREEN, self.normal_button_rect, border_radius=15)
        normal_text = self.button_font.render("Normal (6x4)", True, WHITE)
        normal_text_rect = normal_text.get_rect(center=self.normal_button_rect.center)
        self.screen.blit(normal_text, normal_text_rect)

    def draw_game_screen(self):
        self.screen.fill(BLACK) # Fundo do jogo
        for card in self.card_list:
            card.draw(self.screen, self.main_font)

        # Desenha o contador de movimentos
        moves_text = self.main_font.render(f"Movimentos: {self.moves_count}", True, WHITE)
        self.screen.blit(moves_text, (20, 20))

        # Desenha o botão "Peek"
        peek_button_color = GRAY if self.peek_used else YELLOW
        peek_text_color = WHITE if self.peek_used else BLACK
        pygame.draw.rect(self.screen, peek_button_color, self.peek_button_rect, border_radius=10)
        peek_text = self.main_font.render("Espiar (1 uso)", True, peek_text_color)
        peek_text_rect = peek_text.get_rect(center=self.peek_button_rect.center)
        self.screen.blit(peek_text, peek_text_rect)

        # Desenha a tela de fim de jogo
        if self.game_over:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            self.screen.blit(overlay, (0, 0))

            end_text = self.game_over_font.render("Fim de Jogo!", True, WHITE)
            end_rect = end_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
            self.screen.blit(end_text, end_rect)

            pygame.draw.rect(self.screen, GREEN, self.play_again_rect, border_radius=15)
            again_text = self.main_font.render("Jogar Novamente", True, BLACK)
            again_rect = again_text.get_rect(center=self.play_again_rect.center)
            self.screen.blit(again_text, again_rect)

    def run(self):
        running = True
        clock = pygame.time.Clock()
        while running:
            # Lida com eventos para todos os estados
            for event in pygame.event.get():
                running = self.handle_events(event)
                if not running:
                    break
            
            if self.game_state == 'menu':
                self.draw_menu_screen()
            elif self.game_state == 'playing':
                self.update()
                self.draw_game_screen()
            
            pygame.display.flip()

            clock.tick(60) # Limita o FPS para 60

        pygame.quit()
        sys.exit()

def main():
    pygame.init()
    pygame.mixer.init() # Inicializa o módulo de som
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Jogo da Memória de Frases")
    
    game = Game(screen)
    game.run()

if __name__ == "__main__":
    main()