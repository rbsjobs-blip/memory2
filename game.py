import pygame
import random
import sys

# --- Constantes ---

# Configurações da tela
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800

# Cores (RGB)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (30, 144, 255)
GRAY = (200, 200, 200)
GREEN = (0, 200, 0) # CORRIGIDO: Cor adicionada

# Configurações do tabuleiro
CARD_WIDTH = 150
CARD_HEIGHT = 100
GAP = 20
FLIP_DELAY = 1200 # CORRIGIDO: Atraso adicionado

# --- Inicialização do Pygame ---
pygame.init()

# Criar a tela
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Jogo da Memória de Frases")

# --- Fontes --
main_font = pygame.font.Font(None, 28)
game_over_font = pygame.font.Font(None, 72) # CORRIGIDO: Fonte adicionada

# --- Classes --
class Card:
    def __init__(self, text, id, rect):
        self.text = text
        self.id = id
        self.rect = rect
        self.is_flipped = False
        self.is_matched = False

    def draw(self, screen):
        # A indentação aqui deve ser com espaços ou tabs padrão
        if self.is_flipped or self.is_matched:
            pygame.draw.rect(screen, WHITE, self.rect, border_radius=10)
            pygame.draw.rect(screen, BLUE, self.rect, 3, border_radius=10)

            # Lógica para quebrar o texto em múltiplas linhas se necessário
            words = self.text.split(' ')
            lines = []
            current_line = ""
            for word in words:
                test_line = current_line + word + " "
                if main_font.size(test_line)[0] < self.rect.width - 20:
                    current_line = test_line
                else:
                    lines.append(current_line)
                    current_line = word + " "
            lines.append(current_line)

            # Renderiza cada linha
            total_height = len(lines) * main_font.get_height()
            start_y = self.rect.centery - total_height // 2
            for i, line in enumerate(lines):
                text_surface = main_font.render(line.strip(), True, BLACK)
                text_rect = text_surface.get_rect(centerx=self.rect.centerx, y=start_y + i * main_font.get_height())
                screen.blit(text_surface, text_rect)
        else:
            pygame.draw.rect(screen, BLUE, self.rect, border_radius=10)
            
# --- Dados do Jogo ---
sentence_parts = [
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

# --- Funções ---
def create_board(data):
    card_list = []
    # Embaralha uma cópia para não modificar a lista original
    shuffled_data = data[:]
    random.shuffle(shuffled_data)

    cols, rows = 6, 4
    board_width = cols * (CARD_WIDTH + GAP) - GAP
    board_height = rows * (CARD_HEIGHT + GAP) - GAP
    start_x = (SCREEN_WIDTH - board_width) // 2
    start_y = (SCREEN_HEIGHT - board_height) // 2

    for i, item in enumerate(shuffled_data):
        col, row = i % cols, i // cols
        x = start_x + col * (CARD_WIDTH + GAP)
        y = start_y + row * (CARD_HEIGHT + GAP)
        rect = pygame.Rect(x, y, CARD_WIDTH, CARD_HEIGHT)
        card_list.append(Card(item['text'], item['id'], rect))

    return card_list

def reset_game():
    global card_list, first_card, second_card, lock_board, moves_count, game_over
    card_list = create_board(sentence_parts)
    first_card, second_card = None, None
    lock_board = False
    moves_count = 0
    game_over = False

# --- Configuração do Jogo ---
card_list, first_card, second_card = [], None, None
lock_board, game_over = False, False
unflip_time, moves_count = 0, 0
reset_game()
play_again_rect = pygame.Rect(SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 + 50, 300, 50)

# --- Loop Principal do Jogo ---
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            if game_over:
                if play_again_rect.collidepoint(mouse_pos):
                    reset_game()
            elif not lock_board:
                for card in card_list:
                    if card.rect.collidepoint(mouse_pos) and not card.is_matched and not card.is_flipped:
                        card.is_flipped = True
                        if first_card is None:
                            first_card = card
                        else:
                            second_card = card
                            moves_count += 1
                            
                            # Lógica de verificação movida para cá para ser imediata
                            if first_card.id == second_card.id:
                                first_card.is_matched = True
                                second_card.is_matched = True
                                first_card, second_card = None, None
                                if all(c.is_matched for c in card_list):
                                    game_over = True
                            else:
                                lock_board = True
                                unflip_time = pygame.time.get_ticks()

    if lock_board and (pygame.time.get_ticks() - unflip_time > FLIP_DELAY):
        if first_card and second_card:
            first_card.is_flipped = False
            second_card.is_flipped = False
        first_card, second_card = None, None
        lock_board = False

    screen.fill(BLACK)
    for card in card_list:
        card.draw(screen)

    moves_text = main_font.render(f"Movimentos: {moves_count}", True, WHITE)
    screen.blit(moves_text, (20, 20))

    if game_over:
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))

        end_text = game_over_font.render("Fim de Jogo!", True, WHITE)
        end_rect = end_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
        screen.blit(end_text, end_rect)

        pygame.draw.rect(screen, GREEN, play_again_rect, border_radius=15)
        again_text = main_font.render("Jogar Novamente", True, BLACK)
        again_rect = again_text.get_rect(center=play_again_rect.center)
        screen.blit(again_text, again_rect)
        
    pygame.display.flip()

pygame.quit()
sys.exit()