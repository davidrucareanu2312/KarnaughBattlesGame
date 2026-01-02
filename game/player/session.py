class Session:
    def __init__(self, max_health=100):
        self.max_health = max_health
        self.current_health = max_health
        self.battles_won = 0
        self.is_alive = True
        
        self.beaten_boss1 = False
        self.beaten_boss2 = False
        self.beaten_boss3 = False
        self.beaten_boss4 = False
        self.beaten_boss5 = False
        
    def take_damage(self, amount):
        self.current_health -= amount
        if self.current_health <= 0:
            self.current_health = 0
            self.is_alive = False
            print("SESSION: Player has died.")

    def heal(self, amount):
        if not self.is_alive:
            return 
            
        self.current_health += amount
        if self.current_health > self.max_health:
            self.current_health = self.max_health

    def reset(self):

        self.current_health = self.max_health
        self.is_alive = True
        print("SESSION: Player stats reset (Progress kept).")

    def full_reset(self):

        self.current_health = self.max_health
        self.is_alive = True
        self.battles_won = 0
        self.beaten_boss1 = False
        self.beaten_boss2 = False
        self.beaten_boss3 = False
        self.beaten_boss4 = False
        self.beaten_boss5 = False