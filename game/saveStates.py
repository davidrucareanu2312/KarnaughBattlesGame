import pygame
import sys
import os
import json

class SaveManager:
    def __init__(self):
        game_dir = os.path.dirname(os.path.abspath(__file__))
        root_dir = os.path.join(game_dir, "..")
        self.save_dir = os.path.join(root_dir, "configs", "SaveStates")
        
        if not os.path.exists(self.save_dir):
            os.makedirs(self.save_dir)

    def is_slot_written(self, slot_id):
        """Verifica rapid daca un slot are date salvate (written: true)"""
        path = os.path.join(self.save_dir, f"save_{slot_id}.json")
        if os.path.exists(path):
            try:
                with open(path, 'r') as f:
                    data = json.load(f)
                    return data.get("written", False)
            except:
                return False
        return False

    def get_save_info(self, slot_id):
        path = os.path.join(self.save_dir, f"save_{slot_id}.json")
        if os.path.exists(path):
            try:
                with open(path, 'r') as f:
                    data = json.load(f)
                    if not data.get("written", False):
                        return f"Slot {slot_id}: GOL (Joc Nou)"
                    
                    bosses = 0
                    if data.get("beaten_boss1"): bosses += 1
                    if data.get("beaten_boss2"): bosses += 1
                    if data.get("beaten_boss3"): bosses += 1
                    if data.get("beaten_boss4"): bosses += 1
                    if data.get("beaten_boss5"): bosses += 1
                    return f"Slot {slot_id}: PROGRES (Bossi: {bosses}/5)"
            except:
                return f"Slot {slot_id}: EROARE FISIER"
        return f"Slot {slot_id}: GOL (Joc Nou)"

    def load_game(self, slot_id, session, player):
        """Incarca datele in sesiune. Returneaza True daca a reusit."""
        path = os.path.join(self.save_dir, f"save_{slot_id}.json")
        
        session.reset()
        session.current_slot = slot_id

        if os.path.exists(path):
            try:
                with open(path, 'r') as f:
                    data = json.load(f)
                    
                    session.beaten_boss1 = data.get("beaten_boss1", False)
                    session.beaten_boss2 = data.get("beaten_boss2", False)
                    session.beaten_boss3 = data.get("beaten_boss3", False)
                    session.beaten_boss4 = data.get("beaten_boss4", False)
                    session.beaten_boss5 = data.get("beaten_boss5", False)
                    
                    pos = data.get("position")
                    if pos:
                        player.rect.x = pos["x"]
                        player.rect.y = pos["y"]
                    
                    return True
            except Exception as e:
                print(f"[ERROR] Load failed: {e}")
                return False
        return False

    def save_game(self, session, player):
        if session.current_slot is None: return
        data = {
            "written": True,
            "position": {"x": player.rect.x, "y": player.rect.y},
            "beaten_boss1": session.beaten_boss1,
            "beaten_boss2": session.beaten_boss2,
            "beaten_boss3": session.beaten_boss3,
            "beaten_boss4": session.beaten_boss4,
            "beaten_boss5": session.beaten_boss5
        }
        path = os.path.join(self.save_dir, f"save_{session.current_slot}.json")
        try:
            with open(path, 'w') as f:
                json.dump(data, f, indent=4)
            print(f"[SYSTEM] Salvat in Slot {session.current_slot}")
        except Exception as e:
            print(f"[ERROR] Save failed: {e}")