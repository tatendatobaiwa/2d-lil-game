import random
import time
from enum import Enum
from dataclasses import dataclass
from typing import Dict, List, Optional

# Enums and Constants
class Element(Enum):
    FIRE = "Fire"
    WATER = "Water"
    AIR = "Air"
    LIGHT = "Light"
    EARTH = "Earth"
    DARK = "Dark"

class Alignment(Enum):
    LAWFUL_GOOD = "Lawful Good"
    NEUTRAL_GOOD = "Neutral Good"
    CHAOTIC_GOOD = "Chaotic Good"
    LAWFUL_NEUTRAL = "Lawful Neutral"
    TRUE_NEUTRAL = "True Neutral"
    CHAOTIC_NEUTRAL = "Chaotic Neutral"
    LAWFUL_EVIL = "Lawful Evil"
    NEUTRAL_EVIL = "Neutral Evil"
    CHAOTIC_EVIL = "Chaotic Evil"

class RelationshipLevel(Enum):
    HATED = -2
    DISLIKED = -1
    NEUTRAL = 0
    LIKED = 1
    LOVED = 2

ELEMENTS = [e.value for e in Element]
ADVANTAGES = {
    Element.FIRE.value: [Element.AIR.value, Element.DARK.value],
    Element.WATER.value: [Element.FIRE.value, Element.EARTH.value],
    Element.AIR.value: [Element.WATER.value, Element.LIGHT.value],
    Element.LIGHT.value: [Element.AIR.value, Element.DARK.value],
    Element.EARTH.value: [Element.LIGHT.value, Element.FIRE.value],
    Element.DARK.value: [Element.EARTH.value, Element.WATER.value]
}

# Core Data Structures
@dataclass
class Relationship:
    level: RelationshipLevel = RelationshipLevel.NEUTRAL
    progress: int = 0
    history: List[str] = dataclass.field(default_factory=list)

class Character:
    def __init__(self, name: str, health: int, attack: int, defense: int, 
                 magic: int, element: Element, alignment: Alignment):
        self.name = name
        self.health = health
        self.max_health = health
        self.attack = attack
        self.defense = defense
        self.magic_power = magic
        self.element = element
        self.alignment = alignment
        self.inventory: List['Item'] = []
        self.gold: int = 0
        self.exp: int = 0
        self.level: int = 1
        self.relationships: Dict[str, Relationship] = {}
        self.personality: Dict[str, int] = {
            'bravery': random.randint(1, 10),
            'loyalty': random.randint(1, 10),
            'greed': random.randint(1, 10)
        }
        self.alive: bool = True

    def update_relationship(self, other: 'Character', change: int, reason: str):
        if other.name not in self.relationships:
            self.relationships[other.name] = Relationship()
        
        rel = self.relationships[other.name]
        rel.progress += change
        rel.history.append(f"{reason} ({'+' if change >0 else ''}{change})")
        
        # Update relationship level
        if rel.progress >= 100:
            rel.level = RelationshipLevel(rel.level.value + 1)
            rel.progress = 0
        elif rel.progress <= -100:
            rel.level = RelationshipLevel(rel.level.value - 1)
            rel.progress = 0

class Player(Character):
    def __init__(self, name: str, char_class: str, element: Element, alignment: Alignment):
        base_stats = {
            'Warrior': (120, 15, 10, 5),
            'Mage': (80, 5, 5, 20),
            'Rogue': (90, 10, 8, 12)
        }
        super().__init__(name, *base_stats[char_class], element, alignment)
        self.party: List['NPC'] = []
        self.completed_quests: int = 0

class NPC(Character):
    def __init__(self, name: str, element: Element, alignment: Alignment):
        super().__init__(
            name=name,
            health=random.randint(80, 120),
            attack=random.randint(8, 15),
            defense=random.randint(5, 10),
            magic=random.randint(5, 15),
            element=element,
            alignment=alignment
        )
        self.quest_interest: Dict[str, int] = {
            'combat': random.randint(0, 10),
            'exploration': random.randint(0, 10),
            'social': random.randint(0, 10)
        }

# Procedural Generation Systems
class WorldGenerator:
    @staticmethod
    def generate_npc() -> NPC:
        name = random.choice([
            "Aelien", "Branwen", "Caelum", "Drystan", "Eirian", 
            "Faelar", "Gwyneth", "Haelia", "Ithilien", "Kyros"
        ])
        return NPC(
            name=name,
            element=Element(random.choice(ELEMENTS)),
            alignment=Alignment(random.choice(list(Alignment)))
        )

    @staticmethod
    def generate_quest(player_level: int) -> 'Quest':
        quest_types = ['combat', 'gather', 'rescue', 'diplomacy']
        quest_type = random.choices(quest_types, weights=[40, 30, 20, 10])[0]
        
        templates = {
            'combat': [
                f"Defeat the {random.choice(['Corrupted', 'Fallen'])} {random.choice(['Knight', 'Mage', 'Titan'])}",
                f"Clear {random.randint(3,6)} {random.choice(['bandit', 'goblin', 'undead'])} camps"
            ],
            'gather': [
                f"Recover {random.randint(5,8)} {random.choice(['artifacts', 'relics', 'crystals'])}",
                f"Collect {random.randint(10,15)} {random.choice(['herbs', 'ores', 'components'])}"
            ],
            'rescue': [
                f"Save the {random.choice(['merchant', 'blacksmith', 'elder'])} from {random.choice(['bandits', 'monsters', 'cultists'])}",
                f"Escort the {random.choice('diplomat|scholar|priest').split('|')} through dangerous territory"
            ],
            'diplomacy': [
                f"Negotiate peace between {random.choice(['nobles', 'guilds', 'villages'])}",
                f"Convince the {random.choice(['mages', 'druids', 'mercenaries'])} to join the cause"
            ]
        }
        
        return Quest(
            description=random.choice(templates[quest_type]),
            difficulty=min(max(player_level + random.randint(-2,2), 1), 20),
            quest_type=quest_type,
            rewards={
                'exp': player_level * 50,
                'gold': player_level * 25,
                'items': [ItemGenerator.generate_item(player_level)] if random.random() > 0.7 else []
            }
        )

class ItemGenerator:
    @staticmethod
    def generate_item(level: int) -> 'Item':
        prefixes = ["Ancient", "Forgotten", "Divine", "Cursed", "Enchanted"]
        suffixes = ["Power", "Wisdom", "the Ages", "Destiny", "Elements"]
        return Item(
            name=f"{random.choice(prefixes)} {random.choice(['Sword', 'Amulet', 'Ring', 'Tome'])} of {random.choice(suffixes)}",
            attack=random.randint(1, level//2),
            defense=random.randint(1, level//3),
            magic=random.randint(1, level//2)
        )

# Game Systems
class Quest:
    def __init__(self, description: str, difficulty: int, quest_type: str, rewards: dict):
        self.description = description
        self.difficulty = difficulty
        self.type = quest_type
        self.rewards = rewards
        self.success: Optional[bool] = None

class CombatSystem:
    @staticmethod
    def calculate_damage(attacker: Character, defender: Character) -> int:
        element_multiplier = 1.5 if defender.element.value in ADVANTAGES[attacker.element.value] else 1.0
        return max(0, int((attacker.attack - defender.defense) * element_multiplier))

    @staticmethod
    def party_vs_enemies(player_party: List[Character], enemies: List[Character]):
        print("\n--- COMBAT BEGINS ---")
        while any(c.alive for c in player_party) and any(e.alive for e in enemies):
            # Player party attacks
            for char in player_party:
                if char.alive:
                    target = random.choice([e for e in enemies if e.alive])
                    damage = CombatSystem.calculate_damage(char, target)
                    target.health = max(0, target.health - damage)
                    print(f"{char.name} hits {target.name} for {damage} damage!")
            
            # Enemies attack
            for enemy in enemies:
                if enemy.alive:
                    target = random.choice([c for c in player_party if c.alive])
                    damage = CombatSystem.calculate_damage(enemy, target)
                    target.health = max(0, target.health - damage)
                    print(f"{enemy.name} attacks {target.name} for {damage} damage!")
            
            # Check deaths
            for char in player_party + enemies:
                if char.health <= 0 and char.alive:
                    print(f"{char.name} has died!")
                    char.alive = False

        return any(c.alive for c in player_party)

class RelationshipSystem:
    @staticmethod
    def handle_shared_quest(player: Player, npc: NPC, quest: Quest):
        relationship_change = random.randint(10, 25)
        if quest.success:
            npc.update_relationship(player, relationship_change, 
                                   f"Successfully completed {quest.description}")
            player.update_relationship(npc, relationship_change//2, 
                                      "Worked well together")
        else:
            npc.update_relationship(player, -relationship_change, 
                                   f"Failed {quest.description}")
            player.update_relationship(npc, -relationship_change//2, 
                                      "Let them down")

    @staticmethod
    def check_party_morale(party: List[NPC]) -> float:
        return sum(npc.personality['loyalty'] for npc in party) / len(party)

# Main Game Loop
class Game:
    def __init__(self):
        self.player: Optional[Player] = None
        self.world_npcs: List[NPC] = [WorldGenerator.generate_npc() for _ in range(20)]
        self.current_quest: Optional[Quest] = None
    
    def character_creation(self):
        print("Welcome to Elemental Realms!\n")
        name = input("Enter your character's name: ")
        char_class = input("Choose class (Warrior/Mage/Rogue): ").capitalize()
        element = Element(input("Choose element: ").capitalize())
        alignment = Alignment(input("Choose alignment: ").replace(' ', '_').capitalize())
        
        self.player = Player(name, char_class, element, alignment)
        print(f"\nWelcome {self.player.name}, {self.player.alignment.value} {char_class} of {element.value}!")
    
    def handle_recruitment(self):
        available_npcs = [npc for npc in self.world_npcs 
                         if npc.relationships.get(self.player.name, Relationship()).level.value >= 1]
        
        if available_npcs:
            print("\nAvailable companions:")
            for i, npc in enumerate(available_npcs, 1):
                rel = npc.relationships.get(self.player.name, Relationship())
                print(f"{i}. {npc.name} ({npc.element.value} {type(npc).__name__}, Relationship: {rel.level.name})")
            
            choice = input("Recruit someone? (number or skip): ")
            if choice.isdigit() and 0 < int(choice) <= len(available_npcs):
                npc = available_npcs[int(choice)-1]
                self.player.party.append(npc)
                self.world_npcs.remove(npc)
                print(f"{npc.name} has joined your party!")
    
    def main_loop(self):
        while True:
            print("\n=== MAIN MENU ===")
            print("1. Quest Board\n2. Manage Party\n3. Relationships\n4. Inventory\n5. Travel\n6. Quit")
            
            choice = input("Choose: ")
            if choice == '1':
                self.quest_system()
            elif choice == '2':
                self.party_management()
            elif choice == '3':
                self.relationship_browser()
            elif choice == '4':
                self.inventory_management()
            elif choice == '5':
                self.travel_system()
            elif choice == '6':
                print("Thanks for playing!")
                return
    
    def quest_system(self):
        self.current_quest = WorldGenerator.generate_quest(self.player.level)
        print(f"\nNew Quest: {self.current_quest.description}")
        print(f"Difficulty: {self.current_quest.difficulty}")
        
        if self.player.party:
            print("\nYour party:")
            for npc in self.player.party:
                interest = npc.quest_interest[self.current_quest.type]
                print(f"- {npc.name} ({interest}/10 interest)")
        
        if input("Accept quest? (y/n): ").lower() == 'y':
            success = self.run_quest()
            self.current_quest.success = success
            self.handle_quest_outcome()
    
    def run_quest(self) -> bool:
        enemies = [WorldGenerator.generate_npc() for _ in range(3)]
        print("\nYour party encounters enemies!")
        party = [self.player] + self.player.party
        victory = CombatSystem.party_vs_enemies(
            [c for c in party if c.alive],
            enemies
        )
        
        if victory:
            print("\nQuest successful!")
            self.player.completed_quests += 1
            self.player.gold += self.current_quest.rewards['gold']
            self.player.exp += self.current_quest.rewards['exp']
            for item in self.current_quest.rewards['items']:
                self.player.inventory.append(item)
            return True
        else:
            print("\nQuest failed...")
            return False
    
    def handle_quest_outcome(self):
        for npc in self.player.party:
            RelationshipSystem.handle_shared_quest(self.player, npc, self.current_quest)
            if not npc.alive:
                print(f"{npc.name} perished during the quest...")
                self.player.party.remove(npc)
        
        if random.random() < 0.3:
            self.handle_recruitment()
    
    def party_management(self):
        print("\n=== PARTY MANAGEMENT ===")
        for i, npc in enumerate(self.player.party, 1):
            print(f"{i}. {npc.name} (HP: {npc.health}/{npc.max_health})")
        
        choice = input("Manage party member (number) or (b)ack: ")
        if choice.isdigit() and 0 < int(choice) <= len(self.player.party):
            npc = self.player.party[int(choice)-1]
            print(f"\n{npc.name}'s Status:")
            print(f"Element: {npc.element.value}")
            print(f"Alignment: {npc.alignment.value}")
            print(f"Relationship: {npc.relationships.get(self.player.name, Relationship()).level.name}")
            
            action = input("(e)quip, (d)ismiss, (b)ack: ").lower()
            if action == 'd':
                self.world_npcs.append(npc)
                self.player.party.remove(npc)
                print(f"{npc.name} left the party")
    
    def relationship_browser(self):
        print("\n=== RELATIONSHIPS ===")
        for npc in self.world_npcs + self.player.party:
            rel = self.player.relationships.get(npc.name, Relationship())
            print(f"{npc.name}: {rel.level.name} ({rel.progress}%)")
            if input("Show history? (y/n): ").lower() == 'y':
                for event in rel.history[-3:]:
                    print(f"- {event}")
    
    def inventory_management(self):
        print("\n=== INVENTORY ===")
        for i, item in enumerate(self.player.inventory, 1):
            print(f"{i}. {item}")
        
        choice = input("(u)se, (d)rop, (b)ack: ")
        # Implement item usage logic
    
    def travel_system(self):
        print("\nYou travel to a new area...")
        event = random.choice([
            self.random_encounter,
            self.find_item,
            self.social_interaction
        ])
        event()
    
    def random_encounter(self):
        print("\nRandom encounter!")
        # Implement encounter logic
    
    def social_interaction(self):
        npc = random.choice(self.world_npcs)
        print(f"\nYou meet {npc.name} ({npc.element.value} {npc.alignment.value})")
        # Implement dialogue system

if __name__ == "__main__":
    game = Game()
    game.character_creation()
    game.main_loop()