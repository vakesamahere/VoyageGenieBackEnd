import pygame, sys, random, time
from pygame.locals import *
 
# Constant definitions
WINDOW_SIZE = WINDOW_WIDTH, WINDOW_HEIGHT = 640, 480
GRID_SIZE = GRID_WIDTH, GRID_HEIGHT = 20, 15
FPS = 5 # Game speed
 
# Directions definition

UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)
 
def draw_rect(surf, color, pos):
    # Draw a rectangle on the screen
    r = pygame.Rect((pos[0], pos[1]), (GRID_SIZE[0]-2, GRID_SIZE[1]-2))
    pygame.draw.rect(surf, color, r)
 
def draw_snake(win, snake):
    # Draw the body part of the snake
    for pos in snake[:-1]:
        draw_rect(win, (40, 40, 200), pos)
    
    # Draw the head of the snake with a different color
    head = snake[-1]
    draw_rect(win, (40, 200, 40), head)
 
def main():
    pygame.init()
    win = pygame.display.set_mode((WINDOW_SIZE))
 
    # Initialize variables
    direction = LEFT
    change_to = direction
    score = 0
    snake = [(200, 200), (210, 200), (220,200)]
    apple = (random.randint(0,9)*GRID_SIZE[0], random.randint(0,9)*GRID_SIZE[1])
    
    clock = pygame.time.Clock()
 
    while True: # Main game loop
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
 
            elif event.type == KEYDOWN:
                if (event.key==K_UP or event.key==K_w) and direction != DOWN:
                    change_to = UP
                if (event.key==K_DOWN or event.key==K_s) and direction != UP:
                    change_to = DOWN
                if (event.key==K_LEFT or event.key==K_a) and direction != RIGHT:
                    change_to = LEFT
                if (event.key==K_RIGHT or event.key==K_d) and direction != LEFT:
                    change_to = RIGHT
 
        # Avoid immediate reverse turns
        if change_to == UP and direction != DOWN:
            direction = UP
        if change_to == DOWN and direction != UP:
            direction = DOWN
        if change_to == LEFT and direction != RIGHT:
            direction = LEFT
        if change_to == RIGHT and direction != LEFT:
            direction = RIGHT
 
        # Move the snake head
        x, y = snake[-1]
        x += direction[0]*GRID_SIZE[0]
        y += direction[1]*GRID_SIZE[1]
 
        # If the snake hits the border or itself, game over
        if (x < 0 or x >= WINDOW_WIDTH) or (y < 0 or y >= WINDOW_HEIGHT) or ((x, y) in snake):
            pygame.quit()
            sys.exit()
 
        # Check if the snake ate the apple, if so, increase its length and score
        if (x, y) == apple:
            score += 1
            while apple in snake: # Make sure the apple does not appear on the snake
                apple = (random.randint(0,9)*GRID_SIZE[0], random.randint(0,9)*GRID_SIZE[1])
 
        snake.append((x, y)) # Increase the length of the snake
 
        del snake[0] # Remove one element from the beginning of the list when it's longer than score + 2 to keep its length equal to its score. This will make the snake shorter until it eats enough apple to grow again, just like in the original game.
            
        win.fill((0, 0, 0)) # Fill the screen with black color
        draw_snake(win, snake) # Draw the snake on the screen
        draw_rect(win, (200, 40, 40), apple) # Draw the apple on the screen
        
        pygame.display.flip() # Update the display to show the changes made above
        
        clock.tick(FPS) # Limit the FPS of the game
        
if __name__ == '__main__':
    main()
