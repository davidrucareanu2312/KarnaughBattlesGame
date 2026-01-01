class Session:
    def __init__(self, max_health=100):
        self.max_health = max_health
        self.current_health = max_health
        self.is_alive = True

        self.beaten_boss = False

        self.beaten_boss1 = False
        self.beaten_boss2 = False
        self.beaten_boss3 = False
        self.beaten_boss4 = False
        self.beaten_boss5 = False
        
        self.total_score = 0.0
        self.battles_won = 0
        
    def take_damage(self, amount):
        self.current_health -= amount
        if self.current_health <= 0:
            self.current_health = 0
            self.is_alive = False

    def add_score(self, points):
        self.total_score += points

    def reset(self):
        self.current_health = self.max_health
        self.total_score = 0.0
        self.battles_won = 0
        self.is_alive = True