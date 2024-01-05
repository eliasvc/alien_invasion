import sys
import pygame

from settings import Settings
from ship import Ship
from bullet import Bullet
from alien import Alien

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
        self.bullets = pygame.sprite.Group()
        self.aliens = pygame.sprite.Group()

        self._create_fleet()



    def run_game(self):
        """Start the main loop for the game"""
        while True:
            self._check_events()
            self.ship.update()
            self._update_bullets()
            self._update_aliens()
            self._update_screen()
            self.clock.tick(60)

    def _update_bullets(self):
        """Update position of bullets and get rid of old bullets."""
        # Update bullet positions.
        self.bullets.update()

        # Get rid of bullets that have dissapeared
        for bullet in self.bullets.copy():
            if bullet.rect.bottom <= 0:
                self.bullets.remove(bullet)
        print(len(self.bullets))

        # Check for any bullets that have hit aliens.
        # If so, get rid of the bullet and the alien.
        collisions = pygame.sprite.groupcollide(self.bullets, self.aliens, dokilla=True, dokillb=True)

        if not self.aliens:
            # Destroy existing bullets and create new fleet.
            self.bullets.empty()
            self._create_fleet()
    def _create_fleet(self):
        """Create a fleet of aliens."""
        # Create an alien and keep adding aliens until there's no room left
        # Spacing between aliens is one alien width and one alien height
        alien = Alien(self)
        alien_width, alien_height = alien.rect.size

        current_x, current_y =alien_width, alien_height
        # We need to know when to stop drawing aliens and it can't be the very edge of the screen.
        # Otherwise, the last alien screen is going to get drawn off-screen. So we need a buffer.
        horizontal_screen_buffer = 2 * alien_width
        vertical_screen_buffer = 3 * alien_width

        while current_y < (self.settings.screen_height - vertical_screen_buffer):
            while current_x < (self.settings.screen_width - horizontal_screen_buffer):
                self._create_alien(current_x, current_y)
                # The next alien will have to be drawn past the last alien + the space between them.
                current_x += 2 * alien_width
            
            # Finished a row; reset x value, and increment y value
            current_x = alien_width
            current_y += 2 * alien_height

    def _create_alien(self, x_position, y_position):
        """Create an alien and place it in the row."""
        new_alien = Alien(self)
        new_alien.x = x_position
        new_alien.rect.x = x_position
        new_alien.rect.y = y_position
        self.aliens.add(new_alien)    
    
    def _update_aliens(self):
        """Check if the fleet is at an edge, then update positions."""
        self._check_fleet_edges()
        self.aliens.update()

    def _check_fleet_edges(self):
        """Respond appropriately if any aleans have reached an edge."""
        for alien in self.aliens.sprites():
            if alien.check_edges():
                self._change_fleet_direction()
                break
    
    def _change_fleet_direction(self):
        """Drop the entire fleet and change the fleet's direction."""
        for alien in self.aliens.sprites():
            alien.rect.y += self.settings.fleet_drop_speed
        self.settings.fleet_direction *= -1
        
    def _update_screen(self):
        """Update images on the screen, and flip to the new screen."""
        self.screen.fill(self.settings.bg_color)
        for bullet in self.bullets.sprites():
            bullet.draw_bullet()
        self.ship.blitme()
        self.aliens.draw(self.screen)

        # Make the most recently drawn screen visible
        pygame.display.flip()    

    def _check_events(self):
        """Respond to keyboard and mouse events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                self._check_keydown_events(event)
            elif event.type == pygame.KEYUP:
                self._check_keyup_events(event)
            # Handle joystick hotplugging
            elif event.type == pygame.JOYDEVICEADDED:
                self._check_joystick_connection_events(event)
            elif event.type == pygame.JOYDEVICEREMOVED:
                self._check_joystick_disconnection_events(event)
            elif event.type == pygame.JOYHATMOTION and self.joycon:
                self._check_hat_events(event)
            elif event.type == pygame.JOYBUTTONDOWN and self.joycon:
                if event.button == 0:
                    self._fire_bullet() 
            else:
                print(event)
    
    def _check_keydown_events(self, event):
        """Respond to key presses."""
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = True
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = True
        elif event.key == pygame.K_q:
            sys.exit()
        elif event.key == pygame.K_SPACE:
            self._fire_bullet()
    
    def _check_keyup_events(self, event):
        """Respond to key releases."""
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = False
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = False

    def _fire_bullet(self):
        """Create a new bullet and add it to the bullets group."""
        if len(self.bullets) < self.settings.bullets_allowed:
            new_bullet = Bullet(self)
            self.bullets.add(new_bullet)

    def _check_joystick_connection_events(self, event):
        """Register joystick device when connected."""
        # From the pygame offical docs:
        # This event will be generated when the program starts for every
        # joystick, filling up the list without needing to create them manually.
        self.joycon = pygame.joystick.Joystick(event.device_index)
        print(f"Joystick {self.joycon.get_instance_id()} connencted")
    
    def _check_joystick_disconnection_events(self, event):
        """Remove joystick device from game when disconnected."""
        self.joycon = None
        print(f"Joystick {event.instance_id} disconnected")
    
    def _check_hat_events(self, event):
        """Respond to hat (d-pad) presses."""
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

if __name__ == '__main__':
    # Make a game instance, and run the game
    ai = AlienInvasion()
    ai.run_game()