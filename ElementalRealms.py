from dataclasses import dataclass, field
from typing import List, Dict, Optional
import random
import time
from enum import Enum

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
    history: List[str] = field(default_factory=list)

@dataclass
class Item:
    name: str
    attack: int = 0
    defense: int = 0
    magic: int = 0
    value: int = 0

    def __post_init__(self):
        self.value = (self.attack + self.defense + self.magic) * 10 + random.randint(10, 50)

    def __str__(self):
        stats = []
        if self.attack > 0: stats.append(f"ATK +{self.attack}")
        if self.defense > 0: stats.append(f"DEF +{self.defense}")
        if self.magic > 0: stats.append(f"MAG +{self.magic}")
        return f"{self.name} ({', '.join(stats)})"

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
        self.inventory: List[Item] = []
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
        rel.history.append(f"{reason} ({'+' if change > 0 else ''}{change})")
        
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
        self.char_class = char_class  # Store class for later reference
        self.party: List['NPC'] = []  # Starts empty; recruit via travel events.
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
                f"Escort the {random.choice(['diplomat', 'scholar', 'priest'])} through dangerous territory"
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
    def generate_item(level: int) -> Item:
        prefixes = ["Ancient", "Forgotten", "Divine", "Cursed", "Enchanted"]
        suffixes = ["Power", "Wisdom", "the Ages", "Destiny", "Elements"]
        item_types = ["Sword", "Amulet", "Ring", "Tome", "Armor", "Shield"]
        
        return Item(
            name=f"{random.choice(prefixes)} {random.choice(item_types)} of {random.choice(suffixes)}",
            attack=random.randint(1, max(1, level//2)),
            defense=random.randint(1, max(1, level//3)),
            magic=random.randint(1, max(1, level//2))
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
        base_damage = max(1, (attacker.attack - defender.defense))
        return int(base_damage * element_multiplier)

    @staticmethod
    def party_vs_enemies(player_party: List[Character], enemies: List[Character]):
        print("\n--- COMBAT BEGINS ---")
        while any(c.alive for c in player_party) and any(e.alive for e in enemies):
            for char in player_party:
                if char.alive:
                    target = random.choice([e for e in enemies if e.alive])
                    damage = CombatSystem.calculate_damage(char, target)
                    target.health = max(0, target.health - damage)
                    print(f"{char.name} hits {target.name} for {damage} damage!")
            
            for enemy in enemies:
                if enemy.alive:
                    target = random.choice([c for c in player_party if c.alive])
                    damage = CombatSystem.calculate_damage(enemy, target)
                    target.health = max(0, target.health - damage)
                    print(f"{enemy.name} attacks {target.name} for {damage} damage!")
            
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
        return sum(npc.personality['loyalty'] for npc in party) / len(party) if party else 0

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
        if char_class not in ['Warrior', 'Mage', 'Rogue']:
            print("Invalid class! Defaulting to Warrior.")
            char_class = 'Warrior'
        
        print("\nChoose element: Fire, Water, Air, Light, Earth, Dark")
        element_input = input("Enter element: ").strip().capitalize()
        try:
            element = Element(element_input)
        except ValueError:
            print("Invalid element! Defaulting to Fire.")
            element = Element.FIRE
        
        print("\nChoose alignment:")
        print("Options: Lawful Good, Neutral Good, Chaotic Good, Lawful Neutral, True Neutral, Chaotic Neutral, Lawful Evil, Neutral Evil, Chaotic Evil")
        alignment_input = input("Enter alignment: ").strip().replace(' ', '_').upper()
        
        try:
            alignment = Alignment[alignment_input]
        except KeyError:
            print("Invalid alignment! Defaulting to True Neutral.")
            alignment = Alignment.TRUE_NEUTRAL
        
        self.player = Player(name, char_class, element, alignment)
        print(f"\nWelcome {self.player.name}, {self.player.alignment.value} {char_class} of {element.value}!")
    
    def estimate_success_probability(self, quest: Quest) -> int:
        # Simple estimation formula:
        # Base chance 50%, modified by (player level - quest difficulty)*5 and (player.attack - 11)*2.
        base = 50
        level_factor = (self.player.level - quest.difficulty) * 5
        attack_factor = (self.player.attack - 11) * 2  # assuming average enemy attack around 11
        chance = base + level_factor + attack_factor
        return max(5, min(95, chance))
    
    def handle_recruitment(self):
        # Recruitment from travel: 40% chance to meet a recruitable NPC.
        if random.random() < 0.4:
            npc = WorldGenerator.generate_npc()
            print(f"\nYou encountered {npc.name} during your journey.")
            if input("Would you like to recruit them? (y/n): ").lower() == 'y':
                self.player.party.append(npc)
                print(f"{npc.name} has joined your party!")
            else:
                print(f"You decided not to recruit {npc.name}.")
    
    def main_loop(self):
        while True:
            print("\n=== MAIN MENU ===")
            print("1. Quest Board")
            print("2. Manage Party")
            print("3. Relationships")
            print("4. Inventory")
            print("5. Travel")
            print("6. View Stats")
            print("7. Quit")
            
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
                self.view_stats()
            elif choice == '7':
                print("Thanks for playing!")
                return
            else:
                print("Invalid option. Try again.")
    
    def quest_system(self):
        self.current_quest = WorldGenerator.generate_quest(self.player.level)
        print(f"\nNew Quest: {self.current_quest.description}")
        print(f"Difficulty: {self.current_quest.difficulty}")
        est = self.estimate_success_probability(self.current_quest)
        print(f"Estimated Success Chance: {est}%")
        
        if self.player.party:
            print("\nYour party:")
            for npc in self.player.party:
                interest = npc.quest_interest.get(self.current_quest.type, 0)
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
        for npc in self.player.party.copy():
            RelationshipSystem.handle_shared_quest(self.player, npc, self.current_quest)
            if not npc.alive:
                print(f"{npc.name} perished during the quest...")
                self.player.party.remove(npc)
        
        # After a quest, offer a chance to recruit an NPC (via travel) if none is recruited already.
        if not self.player.party:
            self.handle_recruitment()
    
    def party_management(self):
        if not self.player.party:
            print("\nYou currently have no party members.")
            return
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
                print(f"{npc.name} has left the party")
    
    def relationship_browser(self):
        print("\n=== RELATIONSHIPS ===")
        combined_npcs = self.world_npcs + self.player.party
        if not combined_npcs:
            print("No NPCs to display.")
            return
        for npc in combined_npcs:
            rel = self.player.relationships.get(npc.name, Relationship())
            print(f"{npc.name}: {rel.level.name} ({rel.progress}%)")
            if input("Show history? (y/n): ").lower() == 'y':
                for event in rel.history[-3:]:
                    print(f"- {event}")
    
    def inventory_management(self):
        print("\n=== INVENTORY ===")
        if not self.player.inventory:
            print("Your inventory is empty.")
            return
        for i, item in enumerate(self.player.inventory, 1):
            print(f"{i}. {item}")
        
        choice = input("(u)se, (d)rop, (b)ack: ")
        if choice == 'd':
            index = input("Enter item number to drop: ")
            if index.isdigit():
                index = int(index) - 1
                if 0 <= index < len(self.player.inventory):
                    dropped_item = self.player.inventory.pop(index)
                    print(f"Dropped {dropped_item.name}")
    
    def travel_system(self):
        print("\nYou set out to travel to a new area...")
        print("Choose your travel action:")
        print("1. Help Someone")
        print("2. Solve a Mystery")
        print("3. Farm Experience")
        print("4. Explore a Dungeon")
        print("5. Meet Travelers")
        choice = input("Your choice: ")
        
        if choice == '1':
            self.travel_help_someone()
        elif choice == '2':
            self.travel_solve_mystery()
        elif choice == '3':
            self.travel_farm_exp()
        elif choice == '4':
            self.travel_explore_dungeon()
        elif choice == '5':
            self.handle_recruitment()
        else:
            print("Unrecognized action. You wander without incident.")
    
    def travel_help_someone(self):
        print("\nYou come across a villager in distress!")
        # Simulate a small non-combat scenario.
        success = random.random() < 0.8
        if success:
            print("You help resolve the problem, earning gratitude and a small reward.")
            self.player.gold += random.randint(10, 30)
            self.player.exp += random.randint(20, 40)
        else:
            print("Despite your efforts, the situation didn't improve much.")
    
    def travel_solve_mystery(self):
        print("\nYou investigate strange happenings in a nearby forest.")
        # Mystery outcome based on a chance influenced by player's level.
        chance = 0.5 + (self.player.level / 100)
        if random.random() < chance:
            print("Your keen senses uncover vital clues!")
            self.player.exp += random.randint(30, 50)
        else:
            print("The mystery remains unsolved.")
    
    def travel_farm_exp(self):
        print("\nYou head to a training area to farm experience.")
        # Define farming locations with specific mobs and multipliers.
        farming_locations = {
            "Glistening Grove": {
                "mob_name": "Slime",
                "difficulty_multiplier": 0.8,
                "base_exp": 20
            },
            "Crimson Cavern": {
                "mob_name": "Goblin",
                "difficulty_multiplier": 1.0,
                "base_exp": 40
            },
            "Darkened Depths": {
                "mob_name": "Shadow Beast",
                "difficulty_multiplier": 1.2,
                "base_exp": 60
            }
        }
        location_name = random.choice(list(farming_locations.keys()))
        location_data = farming_locations[location_name]
        print(f"\nYou arrive at {location_name}.")
        
        # Calculate enemy level based on player's level and location difficulty.
        enemy_level = max(1, int(self.player.level * location_data['difficulty_multiplier']))
        mob_name = location_data['mob_name']
        
        # Create enemy stats based on mob type.
        if mob_name == "Slime":
            enemy_health = 30 * enemy_level
            enemy_attack = 3 * enemy_level
            enemy_defense = 1 * enemy_level
            enemy_magic = 1 * enemy_level
        elif mob_name == "Goblin":
            enemy_health = 50 * enemy_level
            enemy_attack = 5 * enemy_level
            enemy_defense = 3 * enemy_level
            enemy_magic = 2 * enemy_level
        elif mob_name == "Shadow Beast":
            enemy_health = 70 * enemy_level
            enemy_attack = 7 * enemy_level
            enemy_defense = 4 * enemy_level
            enemy_magic = 3 * enemy_level
        else:
            enemy_health = 40 * enemy_level
            enemy_attack = 4 * enemy_level
            enemy_defense = 2 * enemy_level
            enemy_magic = 2 * enemy_level
        
        # Create a custom enemy. Here, we use a dummy NPC with fixed element and alignment.
        enemy = NPC(name=mob_name, element=Element.DARK, alignment=Alignment.CHAOTIC_EVIL)
        enemy.health = enemy_health
        enemy.max_health = enemy_health
        enemy.attack = enemy_attack
        enemy.defense = enemy_defense
        enemy.magic_power = enemy_magic
        
        print(f"A wild {mob_name} (Level {enemy_level}) appears! (HP: {enemy.health}, ATK: {enemy.attack}, DEF: {enemy.defense})")
        
        # Simulate combat with the enemy.
        victory = CombatSystem.party_vs_enemies([self.player] + self.player.party, [enemy])
        if victory:
            print("You defeat the enemy!")
            # Scale exp reward: if enemy is much weaker than the player, reward is lower.
            exp_reward = int(location_data['base_exp'] * (enemy_level / self.player.level))
            exp_reward = max(10, exp_reward)
            self.player.exp += exp_reward
            print(f"You gain {exp_reward} experience!")
        else:
            print("You were overwhelmed by the enemy and had to retreat.")
    
    def travel_explore_dungeon(self):
        print("\nYou explore a mysterious dungeon filled with dangers and treasures.")
        enemies = [WorldGenerator.generate_npc() for _ in range(2)]
        victory = CombatSystem.party_vs_enemies([self.player] + self.player.party, enemies)
        if victory:
            print("You clear the dungeon and find valuable items!")
            self.player.exp += random.randint(40, 60)
            self.player.gold += random.randint(30, 50)
            self.player.inventory.append(ItemGenerator.generate_item(self.player.level))
        else:
            print("The dungeon proved too perilous, and you barely escape.")
    
    def view_stats(self):
        print("\n=== YOUR STATS ===")
        print(f"Name: {self.player.name}")
        print(f"Class: {self.player.char_class}")
        print(f"Element: {self.player.element.value}")
        print(f"Alignment: {self.player.alignment.value}")
        print(f"Level: {self.player.level}")
        print(f"EXP: {self.player.exp}")
        print(f"Gold: {self.player.gold}")
        print(f"Health: {self.player.health}/{self.player.max_health}")
        print(f"Attack: {self.player.attack}")
        print(f"Defense: {self.player.defense}")
        print(f"Magic: {self.player.magic_power}")
        print(f"Party Members: {len(self.player.party)}")
        print(f"Inventory Items: {len(self.player.inventory)}")
    
if __name__ == "__main__":
    game = Game()
    game.character_creation()
    game.main_loop()
