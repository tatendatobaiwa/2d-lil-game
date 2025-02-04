from dataclasses import dataclass, field
from typing import List, Dict, Optional
import random
import time
from enum import Enum

# --- Extended Enums and Constants ---
class Element(Enum):
    FIRE = "Fire"
    WATER = "Water"
    EARTH = "Earth"
    AIR = "Air"
    LIGHT = "Light"
    DARK = "Dark"
    NATURE = "Nature"
    LIGHTNING = "Lightning"
    ICE = "Ice"
    POISON = "Poison"

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

class QuestRank(Enum):
    F = 1
    E = 2
    D = 3
    C = 4
    B = 5
    A = 6
    S = 7
    SS = 8
    SSS = 9

# Basic elemental advantages – adjust as needed.
ADVANTAGES = {
    Element.FIRE.value: [Element.ICE.value, Element.POISON.value, Element.NATURE.value],
    Element.WATER.value: [Element.FIRE.value, Element.LIGHTNING.value],
    Element.EARTH.value: [Element.LIGHTNING.value, Element.POISON.value],
    Element.AIR.value: [Element.EARTH.value, Element.NATURE.value],
    Element.LIGHT.value: [Element.DARK.value],
    Element.DARK.value: [Element.LIGHT.value, Element.ICE.value],
    Element.NATURE.value: [Element.WATER.value, Element.EARTH.value],
    Element.LIGHTNING.value: [Element.AIR.value, Element.FIRE.value],
    Element.ICE.value: [Element.LIGHTNING.value, Element.DARK.value],
    Element.POISON.value: [Element.NATURE.value, Element.EARTH.value]
}

# --- Core Data Structures ---
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
    effect: Optional[str] = None  # For example: "Bleed", "Stun"
    effect_chance: float = 0.0  # Extra chance (in decimal) to trigger the effect

    def __post_init__(self):
        self.value = (self.attack + self.defense + self.magic) * 10 + random.randint(10, 50)

    def __str__(self):
        stats = []
        if self.attack > 0:
            stats.append(f"ATK +{self.attack}")
        if self.defense > 0:
            stats.append(f"DEF +{self.defense}")
        if self.magic > 0:
            stats.append(f"MAG +{self.magic}")
        extra = ""
        if self.effect:
            extra = f", Effect: {self.effect} ({int(self.effect_chance*100)}% chance)"
        return f"{self.name} ({', '.join(stats)}{extra})"

class Consumable(Item):
    def __init__(self, name: str, heal_value: int = 0, throw_damage: int = 0):
        super().__init__(name)
        self.heal_value = heal_value
        self.throw_damage = throw_damage

    def __str__(self):
        if self.heal_value > 0:
            return f"{self.name} (Heals {self.heal_value} HP)"
        elif self.throw_damage > 0:
            return f"{self.name} (Throw Damage {self.throw_damage})"
        else:
            return self.name

# Helper: determine equipment slot from item name.
def determine_slot(item: Item) -> Optional[str]:
    name = item.name.lower()
    if "sword" in name or "wand" in name or "tome" in name:
        return "weapon"
    elif "armor" in name:
        return "armor"
    elif "shield" in name:
        return "shield"
    elif "ring" in name or "amulet" in name:
        return "accessory"
    return None

# --- Status Effects System ---
# Effects are stored as entries in a dictionary (key: effect name).
# Each effect has a "turns" counter and may have "damage_per_turn".
# Some effects modify multipliers (e.g., Empowered, Cursed) or prevent actions (Frozen, Stun).

# --- Base Character Classes ---
class Character:
    def __init__(self, name: str, health: int, attack: int, defense: int, magic: int, element: Element, alignment: Alignment):
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
        # Status effects: keys are effect names, values are dicts with effect data.
        self.status_effects: Dict[str, Dict] = {}

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

    def process_status_effects(self):
        # Process each active effect.
        for effect_name in list(self.status_effects.keys()):
            effect = self.status_effects[effect_name]
            # Effects that deal damage each turn.
            if effect_name in ["Burn", "Poisoned", "Shocked"]:
                self.health -= effect["damage_per_turn"]
                print(f"{self.name} suffers {effect['damage_per_turn']} damage from {effect_name} (turns left: {effect['turns']-1}).")
            # Decrement turns for every effect.
            effect["turns"] -= 1
            if effect["turns"] <= 0:
                print(f"{self.name} is no longer affected by {effect_name}.")
                del self.status_effects[effect_name]

class Player(Character):
    RANK_THRESHOLDS = {
        QuestRank.F: 100,
        QuestRank.E: 250,
        QuestRank.D: 500,
        QuestRank.C: 1000,
        QuestRank.B: 2000,
        QuestRank.A: 4000,
        QuestRank.S: 8000,
        QuestRank.SS: 16000,
        QuestRank.SSS: 32000
    }

    def __init__(self, name: str, char_class: str, element: Element, alignment: Alignment):
        base_stats = {
            'Warrior': (120, 15, 10, 5),
            'Mage': (80, 5, 5, 20),
            'Rogue': (90, 10, 8, 12)
        }
        super().__init__(name, *base_stats[char_class], element, alignment)
        self.char_class = char_class
        self.party: List['NPC'] = []
        self.completed_quests: int = 0
        self.base_health = self.max_health
        self.base_attack = self.attack
        self.base_defense = self.defense
        self.base_magic = self.magic_power
        self.equipment: Dict[str, Optional[Item]] = {"weapon": None, "armor": None, "shield": None, "accessory": None}
        self.current_rank: QuestRank = QuestRank.F
        self.rank_progress: int = 0
        self.rank_threshold: int = self.RANK_THRESHOLDS[QuestRank.F]

    def recalc_stats(self):
        self.attack = self.base_attack + sum(item.attack for item in self.equipment.values() if item)
        self.defense = self.base_defense + sum(item.defense for item in self.equipment.values() if item)
        self.magic_power = self.base_magic + sum(item.magic for item in self.equipment.values() if item)

    def check_level_up(self):
        required_exp = 100 + (self.level - 1) * 20
        leveled_up = False
        while self.exp >= required_exp:
            self.exp -= required_exp
            self.level += 1
            leveled_up = True
            if self.char_class == 'Warrior':
                self.base_health += 15
                self.base_attack += 3
                self.base_defense += 2
                self.base_magic += 1
            elif self.char_class == 'Mage':
                self.base_health += 8
                self.base_attack += 1
                self.base_defense += 1
                self.base_magic += 4
            elif self.char_class == 'Rogue':
                self.base_health += 10
                self.base_attack += 2
                self.base_defense += 2
                self.base_magic += 2
            self.max_health = self.base_health
            self.health = self.max_health
            print(f"\n*** Level up! Now Level {self.level}! ***")
            required_exp = 100 + (self.level - 1) * 20
        if leveled_up:
            print(f"EXP to next level: {self.exp}/{required_exp}")

    def update_rank_progress(self, difficulty: int):
        base_progress = difficulty * 10
        rank_modifier = (self.current_rank.value * 0.2) + 1
        self.rank_progress += int(base_progress * rank_modifier)
        print(f"\nRank Progress: {self.rank_progress}/{self.rank_threshold}")
        if self.rank_progress >= self.rank_threshold:
            if self.current_rank != QuestRank.SSS:
                self.current_rank = QuestRank(self.current_rank.value + 1)
                self.rank_threshold = self.RANK_THRESHOLDS[self.current_rank]
                self.rank_progress = 0
                print(f"\n*** Achieved {self.current_rank.name} Rank! ***")
            else:
                print("\n*** Maximum Rank (SSS) Achieved! ***")

    def equip_item(self, item: Item, slot: str):
        if self.equipment.get(slot):
            old_item = self.equipment[slot]
            self.inventory.append(old_item)
            print(f"Unequipped {old_item.name} from {slot} slot.")
        self.equipment[slot] = item
        self.recalc_stats()
        print(f"Equipped {item.name} in {slot} slot.")

    def check_level_up(self):
        required_exp = 100 + (self.level - 1) * 20
        leveled_up = False
        while self.exp >= required_exp:
            self.exp -= required_exp
            self.level += 1
            leveled_up = True
            if self.char_class == 'Warrior':
                self.base_health += 15
                self.base_attack += 3
                self.base_defense += 2
                self.base_magic += 1
            elif self.char_class == 'Mage':
                self.base_health += 8
                self.base_attack += 1
                self.base_defense += 1
                self.base_magic += 4
            elif self.char_class == 'Rogue':
                self.base_health += 10
                self.base_attack += 2
                self.base_defense += 2
                self.base_magic += 2
            self.max_health = self.base_health
            self.health = self.max_health
            print(f"\n*** Congratulations! You've leveled up to Level {self.level}! ***")
            required_exp = 100 + (self.level - 1) * 20
        if leveled_up:
            print(f"EXP remaining: {self.exp}/{required_exp}")

    def use_consumable(self, consumable: Consumable):
        if consumable.heal_value > 0:
            healed = min(consumable.heal_value, self.max_health - self.health)
            self.health += healed
            print(f"{self.name} uses {consumable.name} and restores {healed} HP!")

    def auto_use_consumables(self):
        if self.health < 0.3 * self.max_health:
            for item in self.inventory:
                if isinstance(item, Consumable) and item.heal_value > 0:
                    print(f"\n[Auto-Use] {self.name}'s health is low ({self.health}/{self.max_health}).")
                    self.use_consumable(item)
                    self.inventory.remove(item)
                    break

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

# --- Procedural Generation Systems ---
class WorldGenerator:
    TIER_QUESTS = {
        QuestRank.F: [
            ("Slime Extermination", "Defeat {n} Slimes in the forest", "slimes", 3, 5),
            ("Rat Patrol", "Clear {n} Giant Rats from the sewers", "rats", 2, 4),
            ("Herb Collection", "Gather {n} medicinal herbs for the apothecary", "herbs", 5, 8),
            ("Lost Package", "Recover {n} lost packages from the wilderness", "packages", 3, 5),
            ("Scout Duty", "Patrol the village outskirts for {n} hours", "hours", 4, 6)
        ],
        QuestRank.E: [
            ("Goblin Camp", "Clear {n} Goblin camps near the village", "camps", 2, 3),
            ("Spider Silk", "Collect {n} bundles of spider silk", "silk", 4, 6),
            ("Bandit Hunt", "Defeat {n} bandits harassing travelers", "bandits", 3, 5),
            ("Ancient Relics", "Recover {n} ancient relics from ruins", "relics", 2, 4),
            ("Wolves' Bane", "Protect livestock from {n} wolves", "wolves", 4, 6)
        ],
        QuestRank.D: [
            ("Orc Raid", "Defeat {n} Orc raiders in the mountains", "orcs", 3, 5),
            ("Mystic Crystal", "Find {n} Mystic Crystals in the Crystal Caverns", "crystals", 2, 4),
            ("Treasure Hunt", "Retrieve {n} treasure chests from the pirate ship", "treasures", 3, 5),
            ("Forest Fire", "Extinguish {n} forest fires", "fires", 4, 6),
            ("Desert Bandits", "Defeat {n} Desert Bandits", "bandits", 3, 5)
        ],
        QuestRank.C: [
            ("Troll Bridge", "Build a bridge over the river using {n} trolls", "trolls", 2, 3),
            ("Haunted Mansion", "Clear {n} ghosts from the haunted mansion", "ghosts", 4, 6),
            ("Mine Collapse", "Rescue miners trapped in the collapsing mine", "miners", 3, 5),
            ("Dragon Cave", "Defeat {n} baby dragons in the dragon cave", "dragons", 2, 4),
            ("Frozen Lake", "Break the ice on the frozen lake", "ice", 4, 6)
        ],
        QuestRank.B: [
            ("Golem Army", "Defeat {n} stone golems", "golems", 3, 5),
            ("Phoenix Nest", "Destroy {n} phoenix nests", "nests", 2, 4),
            ("Volcano Eruption", "Contain the volcano eruption", "volcano", 3, 5),
            ("Haunted Forest", "Clear the haunted forest", "forest", 4, 6),
            ("Ice Troll", "Defeat {n} ice trolls", "trolls", 3, 5)
        ],
        QuestRank.A: [
            ("Lich Tower", "Defeat the lich in the tower", "lich", 1, 1),
            ("Demon Gate", "Seal the demon gate", "gate", 1, 1),
            ("Mystical Dragon", "Capture the mystical dragon", "dragon", 1, 1),
            ("Dark Wizard", "Defeat the dark wizard", "wizard", 1, 1),
            ("Undead Army", "Defeat the undead army", "army", 1, 1)
        ],
        QuestRank.S: [
            ("Dragon Queen", "Defeat the dragon queen", "queen", 1, 1),
            ("Devil's Lair", "Destroy the devil's lair", "lair", 1, 1),
            ("Celestial Being", "Summon a celestial being", "being", 1, 1),
            ("Eldritch Horror", "Banish the eldritch horror", "horror", 1, 1),
            ("Time Guardian", "Defeat the time guardian", "guardian", 1, 1)
        ],
        QuestRank.SS: [
            ("Ancient God", "Defeat the ancient god", "god", 1, 1),
            ("Primordial Chaos", "Seal primordial chaos", "chaos", 1, 1),
            ("Cosmic Anomaly", "Contain the cosmic anomaly", "anomaly", 1, 1),
            ("Dimensional Rift", "Close the dimensional rift", "rift", 1, 1),
            ("Planar Invader", "Defeat the planar invader", "invader", 1, 1)
        ],
        QuestRank.SSS: [
            ("DemiGod Slayer", "Defeat {n} Demi-Humans from the Astral Plane", "demihumans", 1, 1),
            ("Worldbreaker", "Stop {n} Reality Collapse Events", "collapses", 1, 2),
            ("Titan's Fall", "Slay {n} Primordial Titans", "titans", 1, 1),
            ("Void Walker", "Close {n} Corrupted Dimension Rifts", "rifts", 1, 3),
            ("Eternal Champion", "Win {n} Trials of the Infinite Arena", "trials", 3, 5)
        ]
    }

    @staticmethod
    def generate_npc() -> NPC:
        name = random.choice([
            "Aelien", "Branwen", "Caelum", "Drystan", "Eirian",
            "Faelar", "Gwyneth", "Haelia", "Ithilien", "Kyros"
        ])
        return NPC(
            name=name,
            element=Element(random.choice(list(Element))),
            alignment=Alignment(random.choice(list(Alignment)))
        )

    @staticmethod
    def generate_quest(player_rank: QuestRank) -> 'Quest':
        templates = WorldGenerator.TIER_QUESTS[player_rank]
        name, desc_template, target, min_count, max_count = random.choice(templates)
        count = random.randint(min_count, max_count)
        difficulty = player_rank.value * 10 + random.randint(-2, 2)
        return Quest(
            name=name,
            description=desc_template.replace("{n}", str(count)),
            difficulty=difficulty,
            target=target,
            target_count=count,
            rewards={
                'exp': 50 * player_rank.value,
                'gold': 25 * player_rank.value,
                'items': [ItemGenerator.generate_item(player_rank.value)] if random.random() > 0.7 else []
            }
        )

class ItemGenerator:
    @staticmethod
    def generate_item(tier: int) -> Item:
        prefixes = ["Rusty", "Basic", "Sharp", "Sturdy", "Enchanted", "Epic", "Legendary", "Mythic"]
        suffixes = ["Power", "Wisdom", "the Ages", "Destiny", "Elements"]
        item_types = ["Sword", "Amulet", "Ring", "Tome", "Armor", "Shield"]
        return Item(
            name=f"{random.choice(prefixes)} {random.choice(item_types)} of {random.choice(suffixes)}",
            attack=random.randint(1, tier*2),
            defense=random.randint(1, tier*2),
            magic=random.randint(1, tier*2)
        )

# --- Combat System with Status Effects and Weapon-based Effects ---
class CombatSystem:
    @staticmethod
    def calculate_damage(attacker: Character, defender: Character) -> int:
        base_damage = max(1, (attacker.attack * random.uniform(0.8, 1.2)) -
                          (defender.defense * random.uniform(0.7, 1.0)))
        multiplier = 1.0
        if "Empowered" in attacker.status_effects:
            multiplier *= 1.2
        if "Cursed" in attacker.status_effects:
            multiplier *= 0.5
        return int(base_damage * multiplier)

    @staticmethod
    def party_vs_enemies(player_party: List[Character], enemies: List[Character]) -> bool:
        print("\n--- COMBAT BEGINS ---")
        round_counter = 1
        while any(c.alive for c in player_party) and any(e.alive for e in enemies):
            print(f"\n--- Round {round_counter} ---")
            for char in player_party + enemies:
                if char.alive:
                    char.process_status_effects()
                    if char.health <= 0:
                        print(f"{char.name} has died from status effects!")
                        char.alive = False
            # Player party turn
            for char in player_party:
                if not char.alive:
                    continue
                if "Frozen" in char.status_effects or "Stunned" in char.status_effects:
                    print(f"{char.name} is unable to act this round!")
                    continue
                if isinstance(char, Player):
                    char.auto_use_consumables()
                living_enemies = [e for e in enemies if e.alive]
                if not living_enemies:
                    break
                target = random.choice(living_enemies)
                damage = CombatSystem.calculate_damage(char, target)
                target.health = max(0, target.health - damage)
                print(f"{char.name} hits {target.name} for {damage} damage! (HP: {target.health}/{target.max_health})")
                # --- Elemental Effects (as before) ---
                chance = 0.10 + (char.attack / 1000)
                if char.element == Element.FIRE and random.random() < chance and "Burn" not in target.status_effects:
                    burn_damage = max(5, int(0.05 * target.max_health))
                    target.status_effects["Burn"] = {"turns": 5, "damage_per_turn": burn_damage}
                    print(f"{target.name} is burned! (5 turns, {burn_damage} damage per turn)")
                elif char.element == Element.DARK and random.random() < chance and "Cursed" not in target.status_effects:
                    target.status_effects["Cursed"] = {"turns": 5}
                    print(f"{target.name} is cursed! (Damage output halved for 5 turns)")
                elif char.element == Element.LIGHT and random.random() < chance and "Empowered" not in char.status_effects:
                    char.status_effects["Empowered"] = {"turns": 5}
                    print(f"{char.name} is empowered! (Damage increased by 20% for 5 turns)")
                elif char.element == Element.ICE and random.random() < chance and "Frozen" not in target.status_effects:
                    target.status_effects["Frozen"] = {"turns": 5}
                    print(f"{target.name} is frozen and cannot attack for 5 turns!")
                elif char.element == Element.POISON and random.random() < chance and "Poisoned" not in target.status_effects:
                    poison_damage = max(5, int(0.05 * target.max_health))
                    target.status_effects["Poisoned"] = {"turns": 5, "damage_per_turn": poison_damage}
                    print(f"{target.name} is poisoned! (5 turns, {poison_damage} damage per turn)")
                elif char.element == Element.LIGHTNING and random.random() < chance and "Shocked" not in target.status_effects:
                    shock_damage = max(5, int(0.05 * target.max_health))
                    target.status_effects["Shocked"] = {"turns": 5, "damage_per_turn": shock_damage}
                    print(f"{target.name} is shocked! (5 turns, {shock_damage} damage per turn)")
                # --- Weapon-based Extra Effects (if attacker is a Player) ---
                if isinstance(char, Player):
                    weapon = char.equipment.get("weapon")
                    if weapon and weapon.effect and random.random() < (weapon.effect_chance + chance):
                        if weapon.effect == "Bleed" and "Bleed" not in target.status_effects:
                            bleed_damage = max(5, int(0.05 * target.max_health))
                            target.status_effects["Bleed"] = {"turns": 5, "damage_per_turn": bleed_damage}
                            print(f"{target.name} is bleeding! (5 turns, {bleed_damage} damage per turn)")
                        elif weapon.effect == "Stun" and "Stunned" not in target.status_effects:
                            target.status_effects["Stunned"] = {"turns": 1}
                            print(f"{target.name} is stunned and loses its next turn!")
            # Enemies turn
            for enemy in enemies:
                if not enemy.alive:
                    continue
                if "Frozen" in enemy.status_effects or "Stunned" in enemy.status_effects:
                    print(f"{enemy.name} is unable to act this round!")
                    continue
                living_players = [c for c in player_party if c.alive]
                if not living_players:
                    break
                target = random.choice(living_players)
                damage = CombatSystem.calculate_damage(enemy, target)
                target.health = max(0, target.health - damage)
                print(f"{enemy.name} attacks {target.name} for {damage} damage! (HP: {target.health}/{target.max_health})")
            # Check for deaths
            for char in player_party + enemies:
                if char.health <= 0 and char.alive:
                    print(f"{char.name} has died!")
                    char.alive = False
            round_counter += 1
        return any(c.alive for c in player_party)

class RelationshipSystem:
    @staticmethod
    def handle_shared_quest(player: Player, npc: NPC, quest: Quest):
        relationship_change = random.randint(10, 25)
        if quest.success:
            npc.update_relationship(player, relationship_change, f"Successfully completed {quest.description}")
            player.update_relationship(npc, relationship_change // 2, "Worked well together")
        else:
            npc.update_relationship(player, -relationship_change, f"Failed {quest.description}")
            player.update_relationship(npc, -relationship_change // 2, "Let them down")

    @staticmethod
    def check_party_morale(party: List[NPC]) -> float:
        return sum(npc.personality['loyalty'] for npc in party) / len(party) if party else 0

# --- Extended Mob Properties and Creation Functions ---
def get_mob_properties(mob_name: str) -> Dict[str, List[Enum]]:
    mob_properties = {
        "Slime": {"elements": [Element.WATER, Element.POISON, Element.NATURE],
                  "alignments": [Alignment.TRUE_NEUTRAL, Alignment.CHAOTIC_NEUTRAL]},
        "Goblin": {"elements": [Element.EARTH, Element.FIRE, Element.DARK],
                   "alignments": [Alignment.CHAOTIC_NEUTRAL, Alignment.CHAOTIC_EVIL]},
        "Shadow Beast": {"elements": [Element.DARK],
                         "alignments": [Alignment.CHAOTIC_EVIL, Alignment.NEUTRAL_EVIL]},
        "Rat": {"elements": [Element.EARTH, Element.POISON],
                "alignments": [Alignment.TRUE_NEUTRAL, Alignment.CHAOTIC_NEUTRAL]},
        "Spider": {"elements": [Element.POISON, Element.DARK],
                   "alignments": [Alignment.NEUTRAL_EVIL, Alignment.CHAOTIC_NEUTRAL]},
        "Skeleton": {"elements": [Element.DARK],
                     "alignments": [Alignment.LAWFUL_EVIL, Alignment.NEUTRAL_EVIL]},
        "Dark Mage": {"elements": [Element.DARK, Element.FIRE, Element.ICE],
                      "alignments": [Alignment.NEUTRAL_EVIL, Alignment.CHAOTIC_EVIL]},
        "Stone Golem": {"elements": [Element.EARTH],
                        "alignments": [Alignment.LAWFUL_NEUTRAL, Alignment.TRUE_NEUTRAL]},
        "Harpy": {"elements": [Element.AIR, Element.LIGHTNING],
                  "alignments": [Alignment.CHAOTIC_NEUTRAL, Alignment.CHAOTIC_EVIL]},
        "Werewolf": {"elements": [Element.NATURE, Element.DARK],
                     "alignments": [Alignment.CHAOTIC_NEUTRAL, Alignment.CHAOTIC_EVIL]},
        "Dragon Wyrmling": {"elements": [Element.FIRE, Element.ICE, Element.LIGHTNING],
                           "alignments": [Alignment.LAWFUL_EVIL, Alignment.NEUTRAL_EVIL]},
        "Lich": {"elements": [Element.DARK, Element.ICE],
                 "alignments": [Alignment.LAWFUL_EVIL, Alignment.NEUTRAL_EVIL]},
        "Ancient Guardian": {"elements": [Element.LIGHT, Element.EARTH],
                             "alignments": [Alignment.LAWFUL_NEUTRAL, Alignment.LAWFUL_EVIL]}
    }
    default_properties = {"elements": [Element.DARK], "alignments": [Alignment.NEUTRAL_EVIL]}
    return mob_properties.get(mob_name, default_properties)

def create_enemy(mob_name: str, enemy_health: int, enemy_attack: int, enemy_defense: int, enemy_magic: int) -> NPC:
    properties = get_mob_properties(mob_name)
    element = random.choice(properties["elements"])
    alignment = random.choice(properties["alignments"])
    enemy = NPC(name=mob_name, element=element, alignment=alignment)
    enemy.health = enemy_health
    enemy.max_health = enemy_health
    enemy.attack = enemy_attack
    enemy.defense = enemy_defense
    enemy.magic_power = enemy_magic
    for stat in ['health', 'max_health', 'attack', 'defense', 'magic_power']:
        variation = random.uniform(0.9, 1.1)
        current_value = getattr(enemy, stat)
        setattr(enemy, stat, int(current_value * variation))
    return enemy

# --- Shop System ---
class Shop:
    def __init__(self):
        self.inventory = [
            {"item": Item("Iron Sword", attack=5), "price": 100},
            {"item": Item("Steel Armor", defense=5), "price": 150},
            {"item": Item("Magic Wand", magic=7), "price": 120},
            {"item": Consumable("Health Potion", heal_value=50), "price": 50},
            {"item": Item("Enchanted Shield", defense=4), "price": 130},
            {"item": Item("Spell Tome", magic=5), "price": 110},
            # New weapons with extra effects:
            {"item": Item("Crimson Sword", attack=7, effect="Bleed", effect_chance=0.15), "price": 150},
            {"item": Item("Thunder Hammer", attack=8, effect="Stun", effect_chance=0.15), "price": 180},
        ]

    def enter_shop(self, player: Player):
        print("\n*** Welcome to the Shop! ***")
        print(f"Your Gold: {player.gold}")
        while True:
            for i, entry in enumerate(self.inventory, 1):
                item = entry["item"]
                price = entry["price"]
                print(f"{i}. {item} - Price: {price} gold")
            print(f"{len(self.inventory)+1}. Exit Shop")
            choice = input("Choose an item to buy (number): ")
            if not choice.isdigit():
                print("Invalid input.")
                continue
            choice = int(choice)
            if choice == len(self.inventory)+1:
                print("Exiting shop.")
                break
            if 1 <= choice <= len(self.inventory):
                entry = self.inventory[choice - 1]
                price = entry["price"]
                item = entry["item"]
                if player.gold >= price:
                    player.gold -= price
                    player.inventory.append(item)
                    print(f"You purchased {item.name}!")
                else:
                    print("Not enough gold!")
            else:
                print("Invalid selection.")

# --- Game Systems ---
@dataclass
class Quest:
    name: str
    description: str
    difficulty: int
    target: str
    target_count: int
    rewards: dict
    success: Optional[bool] = None

# --- Main Game Loop ---
class Game:
    def __init__(self):
        self.player: Optional[Player] = None
        self.world_npcs: List[NPC] = [WorldGenerator.generate_npc() for _ in range(20)]
        self.current_quest: Optional[Quest] = None
        self.shop = Shop()

    def character_creation(self):
        print("Welcome to Elemental Realms!\n")
        name = input("Enter your character's name: ")
        char_class = input("Choose class (Warrior/Mage/Rogue): ").capitalize()
        if char_class not in ['Warrior', 'Mage', 'Rogue']:
            print("Invalid class! Defaulting to Warrior.")
            char_class = 'Warrior'
        print("\nChoose element: " + ", ".join([e.value for e in Element]))
        element_input = input("Enter element: ").strip().capitalize()
        try:
            element = Element(element_input)
        except ValueError:
            print("Invalid element! Defaulting to Fire.")
            element = Element.FIRE
        print("\nChoose alignment:")
        print(", ".join([a.value for a in Alignment]))
        alignment_input = input("Enter alignment: ").strip().replace(' ', '_').upper()
        try:
            alignment = Alignment[alignment_input]
        except KeyError:
            print("Invalid alignment! Defaulting to True Neutral.")
            alignment = Alignment.TRUE_NEUTRAL
        self.player = Player(name, char_class, element, alignment)
        print(f"\nWelcome {self.player.name}, {self.player.alignment.value} {char_class} of {element.value}!")
        self.player.gold = 200
        self.player.inventory.append(Consumable("Health Potion", heal_value=50))

    def estimate_success_probability(self, quest: Quest) -> int:
        base = 50
        level_factor = (self.player.level - quest.difficulty) * 5
        attack_factor = (self.player.attack - 11) * 2
        chance = base + level_factor + attack_factor
        return max(5, min(95, chance))

    def handle_recruitment(self):
        if random.random() < 0.4:
            npc = WorldGenerator.generate_npc()
            print(f"\nYou encountered {npc.name} during your journey.")
            if input("Recruit them? (y/n): ").lower() == 'y':
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
            print("7. Shop")
            print("8. Quit")
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
                self.shop.enter_shop(self.player)
            elif choice == '8':
                print("Thanks for playing!")
                return
            else:
                print("Invalid option. Try again.")

    def quest_system(self):
        self.current_quest = WorldGenerator.generate_quest(self.player.current_rank)
        print(f"\n[{self.player.current_rank.name}] {self.current_quest.name}")
        print(f"Description: {self.current_quest.description}")
        print(f"Difficulty: {self.current_quest.difficulty}")
        if input("Accept quest? (y/n): ").lower() == 'y':
            success = self.run_quest()
            self.current_quest.success = success
            self.handle_quest_outcome()
            if success:
                self.player.update_rank_progress(self.current_quest.difficulty)

    def run_quest(self) -> bool:
        enemies = [WorldGenerator.generate_npc() for _ in range(3)]
        print("\nYour party encounters enemies!")
        party = [self.player] + self.player.party
        victory = CombatSystem.party_vs_enemies([c for c in party if c.alive], enemies)
        if victory:
            print("\nQuest successful!")
            self.player.completed_quests += 1
            self.player.gold += self.current_quest.rewards['gold']
            self.player.exp += self.current_quest.rewards['exp']
            for item in self.current_quest.rewards['items']:
                self.player.inventory.append(item)
            self.player.check_level_up()
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
            npc = self.player.party[int(choice) - 1]
            print(f"\n{npc.name}'s Status:")
            print(f"Element: {npc.element.value}")
            print(f"Alignment: {npc.alignment.value}")
            print(f"Relationship: {npc.relationships.get(self.player.name, Relationship()).level.name}")
            action = input("(e)quip, (d)ismiss, (b)ack: ").lower()
            if action == 'd':
                self.world_npcs.append(npc)
                self.player.party.remove(npc)
                print(f"{npc.name} has left the party.")

    def relationship_browser(self):
        print("\n=== RELATIONSHIPS ===")
        combined = self.world_npcs + self.player.party
        if not combined:
            print("No NPCs to display.")
            return
        for npc in combined:
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
        print("(u)se, (d)rop, (e)quip, (b)ack")
        choice = input("Your choice: ").lower()
        if choice == 'u':
            index = input("Enter item number to use: ")
            if index.isdigit():
                index = int(index) - 1
                if 0 <= index < len(self.player.inventory):
                    item = self.player.inventory[index]
                    if isinstance(item, Consumable):
                        self.player.use_consumable(item)
                        self.player.inventory.pop(index)
                    else:
                        print("That item cannot be used right now.")
        elif choice == 'd':
            index = input("Enter item number to drop: ")
            if index.isdigit():
                index = int(index) - 1
                if 0 <= index < len(self.player.inventory):
                    dropped_item = self.player.inventory.pop(index)
                    print(f"Dropped {dropped_item.name}")
        elif choice == 'e':
            index = input("Enter item number to equip: ")
            if index.isdigit():
                index = int(index) - 1
                if 0 <= index < len(self.player.inventory):
                    item = self.player.inventory[index]
                    slot = determine_slot(item)
                    if slot:
                        self.player.equip_item(item, slot)
                        self.player.inventory.pop(index)
                    else:
                        print("This item cannot be equipped.")
        elif choice == 'b':
            return
        else:
            print("Invalid option.")

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
        success = random.random() < 0.8
        if success:
            print("You help resolve the problem, earning gratitude and a small reward.")
            self.player.gold += random.randint(10, 30)
            self.player.exp += random.randint(20, 40)
            self.player.check_level_up()
        else:
            print("Despite your efforts, the situation didn't improve much.")

    def travel_solve_mystery(self):
        print("\nYou investigate strange happenings in a nearby forest.")
        chance = 0.5 + (self.player.level / 100)
        if random.random() < chance:
            print("Your keen senses uncover vital clues!")
            self.player.exp += random.randint(30, 50)
            self.player.check_level_up()
        else:
            print("The mystery remains unsolved.")

    def travel_farm_exp(self):
        print("\nYou head to a training area to farm experience.")
        farming_locations = {
            "Glistening Grove": {"mob_name": "Slime", "difficulty_multiplier": 0.8, "base_exp": 20},
            "Crimson Cavern": {"mob_name": "Goblin", "difficulty_multiplier": 1.0, "base_exp": 40},
            "Darkened Depths": {"mob_name": "Shadow Beast", "difficulty_multiplier": 1.2, "base_exp": 60},
            "Abandoned Sewers": {"mob_name": "Rat", "difficulty_multiplier": 0.6, "base_exp": 15},
            "Webbed Forest": {"mob_name": "Spider", "difficulty_multiplier": 0.7, "base_exp": 25},
            "Ancient Catacombs": {"mob_name": "Skeleton", "difficulty_multiplier": 1.1, "base_exp": 45},
            "Forbidden Library": {"mob_name": "Dark Mage", "difficulty_multiplier": 1.3, "base_exp": 55},
            "Crystal Mines": {"mob_name": "Stone Golem", "difficulty_multiplier": 1.4, "base_exp": 65},
            "Windswept Peaks": {"mob_name": "Harpy", "difficulty_multiplier": 1.2, "base_exp": 50},
            "Moonlit Grove": {"mob_name": "Werewolf", "difficulty_multiplier": 1.5, "base_exp": 70},
            "Dragon's Roost": {"mob_name": "Dragon Wyrmling", "difficulty_multiplier": 1.7, "base_exp": 80},
            "Cursed Sanctum": {"mob_name": "Lich", "difficulty_multiplier": 1.8, "base_exp": 85},
            "Temple Ruins": {"mob_name": "Ancient Guardian", "difficulty_multiplier": 1.9, "base_exp": 90}
        }
        print("\nAvailable Locations:")
        for i, (loc, data) in enumerate(farming_locations.items(), 1):
            print(f"{i}. {loc} - Mob: {data['mob_name']} | Multiplier: {data['difficulty_multiplier']} | Base EXP: {data['base_exp']}")
        choice = input("Enter the number of the location you want to visit: ")
        try:
            choice = int(choice)
            if 1 <= choice <= len(farming_locations):
                location_name = list(farming_locations.keys())[choice - 1]
            else:
                print("Invalid selection. Defaulting to a random location.")
                location_name = random.choice(list(farming_locations.keys()))
        except ValueError:
            print("Invalid input. Defaulting to a random location.")
            location_name = random.choice(list(farming_locations.keys()))
        location_data = farming_locations[location_name]
        print(f"\nYou arrive at {location_name}.")
        mob_name = location_data['mob_name']
        enemy_level = max(1, int(self.player.level * location_data['difficulty_multiplier']))
        if mob_name == "Slime":
            enemy_health = 30 * enemy_level; enemy_attack = 3 * enemy_level; enemy_defense = 1 * enemy_level; enemy_magic = 1 * enemy_level
        elif mob_name == "Goblin":
            enemy_health = 50 * enemy_level; enemy_attack = 5 * enemy_level; enemy_defense = 3 * enemy_level; enemy_magic = 2 * enemy_level
        elif mob_name == "Shadow Beast":
            enemy_health = 70 * enemy_level; enemy_attack = 7 * enemy_level; enemy_defense = 4 * enemy_level; enemy_magic = 3 * enemy_level
        elif mob_name == "Rat":
            enemy_health = 25 * enemy_level; enemy_attack = 4 * enemy_level; enemy_defense = 1 * enemy_level; enemy_magic = 0 * enemy_level
        elif mob_name == "Spider":
            enemy_health = 35 * enemy_level; enemy_attack = 3 * enemy_level; enemy_defense = 2 * enemy_level; enemy_magic = 3 * enemy_level
        elif mob_name == "Skeleton":
            enemy_health = 45 * enemy_level; enemy_attack = 6 * enemy_level; enemy_defense = 3 * enemy_level; enemy_magic = 1 * enemy_level
        elif mob_name == "Dark Mage":
            enemy_health = 40 * enemy_level; enemy_attack = 2 * enemy_level; enemy_defense = 2 * enemy_level; enemy_magic = 8 * enemy_level
        elif mob_name == "Stone Golem":
            enemy_health = 100 * enemy_level; enemy_attack = 4 * enemy_level; enemy_defense = 8 * enemy_level; enemy_magic = 0 * enemy_level
        elif mob_name == "Harpy":
            enemy_health = 45 * enemy_level; enemy_attack = 6 * enemy_level; enemy_defense = 2 * enemy_level; enemy_magic = 3 * enemy_level
        elif mob_name == "Werewolf":
            enemy_health = 65 * enemy_level; enemy_attack = 8 * enemy_level; enemy_defense = 4 * enemy_level; enemy_magic = 1 * enemy_level
        elif mob_name == "Dragon Wyrmling":
            enemy_health = 85 * enemy_level; enemy_attack = 7 * enemy_level; enemy_defense = 6 * enemy_level; enemy_magic = 6 * enemy_level
        elif mob_name == "Lich":
            enemy_health = 75 * enemy_level; enemy_attack = 4 * enemy_level; enemy_defense = 5 * enemy_level; enemy_magic = 10 * enemy_level
        elif mob_name == "Ancient Guardian":
            enemy_health = 120 * enemy_level; enemy_attack = 6 * enemy_level; enemy_defense = 9 * enemy_level; enemy_magic = 4 * enemy_level
        else:
            enemy_health = 40 * enemy_level; enemy_attack = 4 * enemy_level; enemy_defense = 2 * enemy_level; enemy_magic = 2 * enemy_level
        enemy = create_enemy(mob_name, enemy_health, enemy_attack, enemy_defense, enemy_magic)
        print(f"A wild {mob_name} (Level {enemy_level}) appears!")
        print(f"Stats -> HP: {enemy.health}, ATK: {enemy.attack}, DEF: {enemy.defense}, MAG: {enemy.magic_power}")
        victory = CombatSystem.party_vs_enemies([self.player] + self.player.party, [enemy])
        if victory:
            print("You defeat the enemy!")
            exp_reward = int(location_data['base_exp'] * (enemy_level / self.player.level))
            exp_reward = max(10, exp_reward)
            self.player.exp += exp_reward
            print(f"You gain {exp_reward} experience!")
            self.player.check_level_up()
        else:
            print("You were overwhelmed and had to retreat.")

    def travel_explore_dungeon(self):
        print("\nYou explore a mysterious dungeon filled with dangers and treasures.")
        enemies = [WorldGenerator.generate_npc() for _ in range(2)]
        victory = CombatSystem.party_vs_enemies([self.player] + self.player.party, enemies)
        if victory:
            print("You clear the dungeon and find valuable items!")
            self.player.exp += random.randint(40, 60)
            self.player.gold += random.randint(30, 50)
            self.player.inventory.append(ItemGenerator.generate_item(self.player.level))
            if random.random() < 0.5:
                potion = Consumable("Health Potion", heal_value=50)
                self.player.inventory.append(potion)
                print("You found a Health Potion!")
            self.player.check_level_up()
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
        required_exp = 100 + (self.player.level - 1) * 20
        print(f"Next Level in: {required_exp - self.player.exp} EXP")
        print(f"Gold: {self.player.gold}")
        print(f"Health: {self.player.health}/{self.player.max_health}")
        print(f"Attack: {self.player.attack}")
        print(f"Defense: {self.player.defense}")
        print(f"Magic: {self.player.magic_power}")
        print(f"Party Members: {len(self.player.party)}")
        print(f"Inventory Items: {len(self.player.inventory)}")
        if self.player.equipment:
            print("Equipped Items:")
            for slot, item in self.player.equipment.items():
                if item:
                    print(f"  {slot.capitalize()}: {item.name}")
                else:
                    print(f"  {slot.capitalize()}: None")

if __name__ == "__main__":
    game = Game()
    game.character_creation()
    game.main_loop()