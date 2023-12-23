import sys
import pygame

from settings import Settings
from ship import Ship

class AlienInvasion:
    """Overal class to manage game assets and behavior"""

    def __init__(self):
        """Initialize the game, and create game resources"""
        pygame.init()
        
        # Attribute that will hold the controller if present
        self.joycon = None

        # Add clock for framerate
        self.clock = pygame.time.Clock()

        self.settings = Settings()
        # Create display window
        self.screen = pygame.display.set_mode((self.settings.screen_width, self.settings.screen_height))
        pygame.display.set_caption("Alien Invasion")

        self.ship = Ship(self)



    def run_game(self):
        """Start the main loop for the game"""
        while True:
            self._check_events()
            self.ship.update()
            self._update_screen()
            self.clock.tick(60)
    
    def _update_screen(self):
        """Update images on the screen, and flip to the new screen."""
        self.screen.fill(self.settings.bg_color)
        self.ship.blitme()

        # Make the most recently drawn screen visible
        pygame.display.flip()    

    def _check_events(self):
        """Respond to keyboard and mouse events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RIGHT:
                    self.ship.moving_right = True
                elif event.key == pygame.K_LEFT:
                    self.ship.moving_left = True
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_RIGHT:
                    self.ship.moving_right = False
                elif event.key == pygame.K_LEFT:
                    self.ship.moving_left = False
            # Handle joystick hotplugging
            elif event.type == pygame.JOYDEVICEADDED:
                # From the pygame offical docs:
                # This event will be generated when the program starts for every
                # joystick, filling up the list without needing to create them manually.
                self.joycon = pygame.joystick.Joystick(event.device_index)
                print(f"Joystick {self.joycon.get_instance_id()} connencted")
            elif event.type == pygame.JOYDEVICEREMOVED:
                self.joycon = None
                print(f"Joystick {event.instance_id} disconnected")
            elif event.type == pygame.JOYHATMOTION and self.joycon:
                # hat contains a touple with values depending on which dpad button was pressed:
                # (1, 0)  -> dpad right
                # (-1, 0) -> dpad left
                # (0, 1)  -> dpad up
                # (0, -1) -> dpad down
                # Also, hat comes from the physical hat switch the dpad uses on xbox and ps controllers
                # xbox and ps controllers only have on dpad, hence get_hat(0)
                hat_x, hat_y = self.joycon.get_hat(0)
                if hat_x == 1:
                    self.ship.moving_right = True
                if hat_x == -1:
                    self.ship.moving_left = True
                if hat_x == 0:
                    self.ship.moving_right = False
                    self.ship.moving_left = False
            else:
                print(event)


if __name__ == '__main__':
    # Make a game instance, and run the game
    ai = AlienInvasion()
    ai.run_game()