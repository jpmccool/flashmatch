import pygame
import math
import random
import itertools
import argparse

# A two dimensional vector over the real numbers
class Vector () :
    
    # Initialize with coordinates (x, y)
    def __init__ (self, x = 0.0, y = 0.0) :
        self.x = x
        self.y = y
    
    def __str__ (self) :
        return "(" + str(self.x) + ", " + str(self.y) + ")"
    
    def __len__ (self) :
        return math.sqrt(self.x ** 2 + self.y ** 2)
        
    def __iter__ (self) :
        for element in self.x, self.y :
            yield element
    
    # Vector addition and subtraction
    def __add__ (self, vector) :
        return Vector(self.x + vector.x, self.y + vector.y)
    def __iadd__ (self, vector) :
        self.x += vector.x
        self.y += vector.y
        return self
    def __sub__ (self, vector) :
        return Vector(self.x - vector.x, self.y - vector.y)
    def __isub__ (self, vector) :
        self.x -= vector.x
        self.y -= vector.y
        return self
    
    # Scalar multiplication
    def __mul__ (self, scalar) :
        return Vector(self.x * scalar, self.y * scalar)
    def __imul__ (self, scalar) :
        self.x *= scalar
        self.y *= scalar
        return self
    def __rmul__ (self, scalar) :
        return Vector(scalar * self.x, scalar * self.y)
    def __truediv__ (self, scalar) :
        return Vector(self.x / scalar, self.y / scalar)
    def __idiv__ (self, scalar) :
        self.x /= scalar
        self.y /= scalar
        return self
    def __floordiv__ (self, scalar) :
        return Vector(math.floor(self.x / scalar), math.floor(self.y / scalar))
    def __ifloordiv__ (self, scalar) :
        self.x //= scalar
        self.y //= scalar
        return self
    def __neg__ (self) :
        return Vector(- self.x, - self.y)

class Drawable () :
    
    def contrast (color) :
        r, g, b = int(color[1:3], 16), int(color[3:5], 16), int(color[5:7], 16)
        luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255;
        return "#000000" if luminance > 0.5 else "#ffffff"
    
    box_factor = 1.6
    
    def __init__ (self, position, offset, angle, speed, color, text, onclick) :
        
        self.position = position
        self.offset = offset
        self.velocity = Vector(math.cos(math.radians(angle)) * speed, math.sin(math.radians(angle)) * speed)
        
        self.color = color
        self.text = text
        self.text_color = Drawable.contrast(color)
        self.onclick = onclick
                
        self.font = pygame.font.SysFont("FreeSans.ttf", 32, bold = True, italic = False)
        self.text_surface = self.font.render(self.text, True, self.text_color)
        
        text_size = Vector( self.text_surface.get_width(), self.text_surface.get_height() )
        self.size = text_size + Vector(text_size.y * Drawable.box_factor // 1, text_size.y * Drawable.box_factor // 1)
        self.text_offset = text_size.y * Drawable.box_factor // 2
        self.text_position = self.position + Vector(self.text_offset, self.text_offset)
        
    def draw (self, parent, bound, size) :
        pygame.draw.rect(parent, self.color, pygame.Rect(*tuple(self.position + self.offset), *tuple(self.size)), border_radius = 10)
        parent.blit(self.text_surface, tuple(self.text_position + self.offset))
        self.update(bound, size)
    
    def update (self, bound, size) :
        pos = self.position + self.velocity
        fx, fy = 1.0, 1.0
        if pos.x < bound.x :
            fx = (bound.x - self.position.x) / self.velocity.x
        if pos.x + self.size.x > bound.x + size.x :
            fx = (bound.x + size.x - self.position.x - self.size.x) / self.velocity.x
        if pos.y < bound.y :
            fy = (bound.y - self.position.y) / self.velocity.y
        if pos.y + self.size.y > bound.y + size.y :
            fy = (bound.y + size.y - self.position.y - self.size.y) / self.velocity.y
                
        
        if fx <= fy :
            pos = self.position + fx * self.velocity
            if fx < 1 :
                self.velocity.x *= -1
                pos += (fy - fx) * self.velocity
            if fy < 1 :
                self.velocity.y *= -1
                pos += (1 - fy) * self.velocity
        else :
            pos = self.position + fy * self.velocity
            if fy < 1 :
                self.velocity.y *= -1
                pos += (fx - fy) * self.velocity
            if fx < 1 :
                self.velocity.x *= -1
                pos += (1 - fx) * self.velocity
        self.position = pos
        self.text_position = self.position + Vector(self.text_offset, self.text_offset)

    '''
    def scale (self, factor) :
        self.size = self.size ** factor
        self.image = pygame.transform.scale(self.image, (int(self.size.x), int(self.size.y)))
    '''
    def collides_with (self, position) :
        if position.x - self.offset.x < self.position.x :
            return False
        if position.x - self.offset.x >= self.position.x + self.size.x :
            return False
        if position.y - self.offset.y < self.position.y :
            return False
        if position.y - self.offset.y >= self.position.y + self.size.y :
            return False
        return True


def luminance (r, g, b) :
    return (0.299 * int(r, 16) + 0.587 * int(g, 16) + 0.114 * int(b, 16)) / 255

class Card (Drawable) :
    
    available_colors = [ "#" + r + g + b for (r, g, b) in itertools.product([ "00", "33", "66", "99", "cc", "ff" ], repeat = 3) ] # 216 Colors
    available_angles = [ 2 * a for a in range(180) ] # 180 angles
    def random_color () :
        if len(Card.available_colors) == 0 :
            raise NotImplementedError("Oops! Ran out of colors while making a new card.")
        return Card.available_colors.pop(random.randrange(len(Card.available_colors))) 
    def random_angle () :
        if len(Card.available_angles) == 0 :
            raise NotImplementedError("Oops! Ran out of angles while making a new card.")
        return Card.available_angles.pop(random.randrange(len(Card.available_angles)))
    
    
    # Call this function once before making any Card objects
    def set_parameters (window_size, speed, offset = Vector(0, 0)) :
        Card.window_size = window_size
        Card.speed = speed
        Card.offset = offset
    
    def __init__ (self, key, value) :
        self.key = key
        self.value = value
        Drawable.__init__(self, Card.window_size // 2, Card.offset, Card.random_angle(), Card.speed, Card.random_color(), self.key, onclick = lambda : print(self.key, self.value))

class Menu () :
    
    # Call this function once before making any Menu objects
    def set_parameters (chances, wait, noclear, colorhint) :
        Menu.chances = chances
        Menu.wait = wait
        Menu.noclear = noclear
        Menu.colorhint = colorhint
        
    def __init__ (self, window, menu_size, offset, cards) :
        self.window = window
        self.size = menu_size
        self.offset = offset
        self.cards = [ [card.value, card.color, self.chances] for card in cards ]
        
        self.font = pygame.font.Font(["FressSans.ttf", "bitstream-cyberbit.ttf"], 32, bold = True, italic = False)        
        #font_file = pygame.font.match_font(unifont-15.1.05.ttf)  # Select and 
        #self.font = pygame.font.Font(font_file, 30)          # open the font
        
        self.box_size = Vector( self.size.x * 4 // 5, self.size.x * 4 // 5 )
        self.box_offset = Vector( self.size.x // 10, self.size.x // 10)
        
        self.score_font = pygame.font.SysFont("FreeSans.ttf", 24, bold = True, italic = False)
        self.score_label_surface = self.score_font.render("Score", True, "#ffffff")
        self.score_label_size = Vector( self.score_label_surface.get_width(), self.score_label_surface.get_height() )
        self.score_label_offset = Vector(0, self.size.x) + Vector((self.size.x - self.score_label_size.x) // 2, self.score_label_size.y // 10)
        self.changed = True
        
        self.progress = 0
        self.score = 0
        
        self.new_card(True)
    
    def new_card (self, discard) :
        if len(self.cards) == 0 :
            self.goal = None
            self.text = "DONE!"
            self.box_color = "#000000"
        else :
            if not discard :
                self.cards.append(self.goal)
            self.goal = self.cards.pop(random.randrange(len(self.cards)))
            self.text = self.goal[0]
            if Menu.colorhint :
                self.box_color = self.goal[1]
            else :
                self.box_color = "#000000"
        self.text_surface = self.font.render(self.text, True, "#ffffff")
        self.text_size = Vector( self.text_surface.get_width(), self.text_surface.get_height() )
    
    def draw (self) :
        
        if not self.changed :
            return
        
        else :
            pygame.draw.rect(self.window, "#000000", pygame.Rect(*tuple(self.offset), *tuple(self.size)))
            
            pygame.draw.rect(self.window, self.box_color, pygame.Rect(*tuple(self.offset + self.box_offset), *tuple(self.box_size)), border_radius = 10)
            text_offset = (self.box_size - self.text_size) // 2
            self.window.blit(self.text_surface, tuple(self.offset + text_offset + self.box_offset))
            self.window.blit(self.score_label_surface, tuple(self.offset + self.score_label_offset)) 
            
            self.score_surface = self.score_font.render(str(self.score), True, "#ffffff")
            self.score_size = Vector( self.score_surface.get_width(), self.score_surface.get_height() )
            self.score_offset = Vector((self.size.x - self.score_size.x) // 2, self.size.x + self.score_label_size.y + 2 * self.score_label_size.y // 10)
            self.window.blit(self.score_surface, tuple(self.offset + self.score_offset))
            
            self.changed = False
    
    def register_click (self, value, cards) :
        if self.goal == None :
            return
        if value == self.goal[0] : # Correct match
            if not Menu.noclear :  # Clear the match from the board if noclear is off
                cards.remove([card for card in cards if card.value == value][-1])
            self.progress += 1
            self.score += 100
            self.new_card(True) # Get a new card, discarding this one
        else : # Incorrect match
            self.score -= 10
            if self.goal[2] <= 0 : # Unlimited chances
                if not Menu.wait : # Try a new card, without discarding the current one, if wait is off
                    self.new_card(False)
            else :                 # Guesses are finite, and this one had at least one remaining
                self.goal[2] -= 1  # Decrement guesses
                if self.goal[2] == 0 : # If no guesses remain, get a new card, discarding this one
                    self.score -= 100
                    if not Menu.noclear :  # Clear the failed card from the board if noclear is off
                        cards.remove([card for card in cards if card.value == self.goal[0]][-1])
                    self.new_card(True)
                else :                 # There are still guesses available
                    if not Menu.wait : # True a new card, without discarding the current one, if wait is off
                        self.new_card(False)
        self.changed = True



parser = argparse.ArgumentParser(description = "Play a new game of FlashMatch")
parser.add_argument("deck", metavar = "deck_file",                        help = "A file with key-value pairs, one pair per line, separated by whitespace, with optional notes afterward.")
parser.add_argument("--speed", metavar = "x", type = int, default = 1,    help = "The speed of pieces on the board. Default is x = 1.")
parser.add_argument("--chances", metavar = "n", type = int, default = -1, help = "The number of guesses allowed for each card. Default is n = -1 (unlimited guesses).")
parser.add_argument("--wait", action = "store_true",                      help = "Wait until the correct match is found, or guesses exhausted, before moving on to the next card. Off by default.")
parser.add_argument("--noclear", action = "store_true",                   help = "Do not clear correct matches from the board. Off by default.")
parser.add_argument("--colorhint", action = "store_true",                 help = "Show the correct match's background color. Off by default.")
args = parser.parse_args()
print(args)









# Program parameters
# Menu and field sizes are calculated assuming window_size is 16:9
window_size = Vector(1368, 768) # 16:9
fps = 60
menu_size = Vector(window_size.x / 4, window_size.y)
field_size = Vector(3 * window_size.x / 4, window_size.y)

# Set up the window and clock
pygame.init()
window = pygame.display.set_mode(tuple(window_size), pygame.SCALED)
pygame.display.set_caption("Flash Match")
clock = pygame.time.Clock()
paused = False

# Load flashcards
fname = args.deck
cards = [ ]
Card.set_parameters(field_size, args.speed, Vector(menu_size.x, 0))
with open(fname, encoding = "utf-8") as f:
    for line in f:
       (key, val) = line.split()
       cards.append(Card(key, val))
       print(key, val)
n_cards = len(cards)

# Create menu
Menu.set_parameters(args.chances, args.wait, args.noclear, args.colorhint)
menu = Menu(window, menu_size, Vector(0, 0), cards)

while True:
    for event in pygame.event.get():
        match event.type :
            case pygame.QUIT :
                pygame.quit()
                exit()
            case pygame.KEYDOWN :
                if event.key == pygame.K_SPACE :
                    paused = not paused
            case pygame.MOUSEBUTTONUP :
                pos = Vector(*(pygame.mouse.get_pos()))
                clicked = [card for card in cards if card.collides_with(pos) ]
                if len(clicked) > 0 :
                    menu.register_click(clicked[-1].value, cards) # Only register a click on the top-most card
                    print(menu.progress, "/", n_cards, "=", round(100*(menu.progress / n_cards), 2), "% - score =", menu.score)
    
    if not paused :
        window.fill("#000000", pygame.Rect(*tuple(Vector(menu_size.x, 0)), *tuple(field_size)))
        for card in cards :
            card.draw(window, Vector(0, 0), field_size)
        menu.draw()
        
    pygame.display.flip()
    clock.tick(fps)
