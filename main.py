import random
import sys
import os
from kivy.app import App
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.floatlayout import FloatLayout
from kivy.core.audio import SoundLoader
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.config import Config
from kivmob import KivMob  # Import KivMob for ads

# Set screen size for Android devices
Config.set('graphics', 'width', '289')
Config.set('graphics', 'height', '511')
Window.size = (289, 511)


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)


class FluffyHopGame(FloatLayout):
    def __init__(self, ad_instance, **kwargs):
        super().__init__(**kwargs)
        self.ad_instance = ad_instance  # Reference to the KivMob instance
        self.screen_width = 289
        self.screen_height = 511
        self.groundy = self.screen_height * 0.8
        self.gravity = -0.15  # Further lowered gravity
        self.bird_velocity = 0
        self.pipe_velocity = -2
        self.is_flapped = False
        self.game_started = False  # Game starts paused
        self.score = 0
        self.playerFlapAccv = 3  # Reduced flap acceleration
        self.playerMaxVelY = 10
        self.playerAccY = 1
        self.playerFlapped = False

        # Load resources
        self.background = Image(source=resource_path('gallery/sprites/background.jpg'), size_hint=(None, None),
                                size=(self.screen_width, self.screen_height), pos=(0, 0))
        self.add_widget(self.background)
        self.bird = Image(source=resource_path('gallery/sprites/bird.png'), size_hint=(None, None), size=(44, 34),
                          pos=(self.screen_width / 5, self.screen_height / 2))
        self.add_widget(self.bird)
        self.pipe_up = Image(source=resource_path('gallery/sprites/pipe.png'), size_hint=(None, None), size=(52, 320),
                             pos=(self.screen_width, random.randint(200, 450)))  # Increased randomness
        self.pipe_down = Image(source=resource_path('gallery/sprites/pipe.png'), size_hint=(None, None), size=(52, 320),
                               pos=(self.screen_width, self.pipe_up.y - random.randint(400, 500)))  # Wider gap
        self.add_widget(self.pipe_up)
        self.add_widget(self.pipe_down)
        self.base = Image(source=resource_path('gallery/sprites/base.png'), size_hint=(None, None),
                          size=(self.screen_width, 100), pos=(0, 0))
        self.add_widget(self.base)
        self.score_label = Label(text="0", font_size=40, size_hint=(None, None), size=(100, 50),
                                 pos=(self.screen_width / 2 - 50, self.screen_height * 0.85))
        self.add_widget(self.score_label)

        # Load sounds
        self.wing_sound = SoundLoader.load(resource_path('gallery/audio/wing.wav'))
        self.point_sound = SoundLoader.load(resource_path('gallery/audio/point.wav'))
        self.hit_sound = SoundLoader.load(resource_path('gallery/audio/hit.wav'))
        self.die_sound = SoundLoader.load(resource_path('gallery/audio/die.wav'))

        # Schedule update
        Clock.schedule_interval(self.update, 1 / 60.0)

        # Show welcome screen
        self.message = Image(source=resource_path('gallery/sprites/message.png'), size_hint=(None, None),
                             size=(200, 200), pos=(self.screen_width / 2 - 100, self.screen_height / 2 - 100))
        self.add_widget(self.message)

    def update(self, dt):
        if not self.game_started:
            return

        # Increase speed every 10 points
        if self.score %10 == 0 and self.score != 0:
            self.pipe_velocity = -2 - (self.score //10)  # Increase speed as score increases

        if self.is_flapped:
            self.bird_velocity = self.playerFlapAccv
            self.is_flapped = False
        else:
            self.bird_velocity += self.gravity

        # Update bird position
        self.bird.y += self.bird_velocity

        # Update pipe positions
        self.pipe_up.x += self.pipe_velocity
        self.pipe_down.x += self.pipe_velocity

        # Reset pipes and update score
        if self.pipe_up.right < 0:
            self.pipe_up.x = self.screen_width
            self.pipe_down.x = self.screen_width
            self.pipe_up.y = random.randint(200, 450)  # Increased randomness
            self.pipe_down.y = self.pipe_up.y - random.randint(400, 500)  # Wider gap
            self.score += 1
            self.score_label.text = str(self.score)
            self.point_sound.play()

        # Check for collisions
        if (self.bird.collide_widget(self.pipe_up) or self.bird.collide_widget(self.pipe_down) or
                self.bird.y < self.base.top or self.bird.y > self.screen_height):
            self.hit_sound.play()
            self.die_sound.play()
            self.reset_game()

    def reset_game(self):
        # Show ad only if the score is greater than 5
        if self.score > 5:
            self.show_ad()  # Display the ad

        # Reset game parameters
        self.bird.y = self.screen_height / 2
        self.bird_velocity = 0  # Reset bird velocity
        self.pipe_up.x = self.screen_width
        self.pipe_down.x = self.screen_width
        self.pipe_up.y = random.randint(200, 450)  # Increased randomness
        self.pipe_down.y = self.pipe_up.y - random.randint(400, 500)  # Wider gap
        self.score = 0
        self.score_label.text = "0"

        # Reset pipe velocity
        self.pipe_velocity = -2  # Reset the speed to its initial value

        self.game_started = False
        self.add_widget(self.message)

    def show_ad(self):
        # Placeholder for ad integration
        print("Displaying ad...")  # Replace this with your ad library's ad display function

    def on_touch_down(self, touch):
        if not self.game_started:
            self.game_started = True
            self.remove_widget(self.message)
        else:
            self.wing_sound.play()
            self.is_flapped = True


class FluffyHopApp(App):
    def build(self):
        # Initialize the KivMob instance with your AdMob App ID
        self.ads = KivMob("ca-app-pub-4667440476303357~4219111913")  # Replace with your AdMob App ID
        self.ads.new_interstitial("ca-app-pub-4667440476303357/9614344176")  # Replace with your Interstitial Ad Unit ID
        self.ads.request_interstitial()
        return FluffyHopGame(self.ads)


if __name__ == '__main__':
    FluffyHopApp().run()
