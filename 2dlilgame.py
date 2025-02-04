import random
import time

# Global list of elements
ELEMENTS = ["fire", "water", "air", "light", "earth", "dark"]

# Define each element's advantages (elements it is strong against)
ADVANTAGES = {
    "fire":  ["air", "dark"],
    "water": ["fire", "earth"],
    "air":   ["water", "light"],
    "light": ["air", "dark"],
    "earth": ["light", "fire"],
    "dark":  ["earth", "water"]
}

# Utility function: determine elemental multiplier
def get_element_multiplier(attacker_element, defender_element):
    if defender_element in ADVANTAGES.get(attacker_element, []):
        # Attacker has advantage
        return 1.5
    elif attacker_element in ADVANTAGES.get(defender_element, []):
        # Attacker is at disadvantage
        return 0.75
    else:
        return 1.0

# Function to generate lore events based on context
def generate_lore_event(event_type, player, **kwargs):
    if event_type == "quest":
        events = [
            f"As you complete your quest, ancient scrolls whisper of a hero whose {player.element} spirit alters fate.",
            f"The winds carry tales of your {player.element} mastery—legends once forgotten now stir anew.",
            f"A shimmering aura of {player.element} energy surrounds you, as if destiny itself takes note."
        ]
    elif event_type == "combat":
        enemy = kwargs.get('enemy')
        events = [
            f"The clash of your {player.element} power against {enemy.element} fury sends sparks into the night.",
            f"In the heat of battle, the forces of {player.element} and {enemy.element} collide in a dazzling display.",
            f"Your {player.element} strike meets the enemy’s {enemy.element} might—an encounter written in the stars."
        ]
    elif event_type == "npc":
        events = [
            f"A mysterious sage appears, hinting at prophecies of a hero with the rare {player.element} gift.",
            f"An old wanderer murmurs legends of forgotten realms where the power of {player.element} once reigned supreme.",
            f"In a quiet moment, a voice speaks of ancient lore tied to the {player.element} element, urging you onward."
        ]
    else:
        events = ["The world seems to whisper secrets of its ancient past."]
    
    print("\n" + random.choice(events) + "\n")

# Character Classes
class Character:
    def __init__(self, name, health, attack, defense, magic_power, element):
        self.name = name
        self.health = health
        self.max_health = health
        self.attack = attack
        self.defense = defense
        self.magic_power = magic_power
        self.element = element  # New element attribute
        self.inventory = []
        self.gold = 0
        self.exp = 0
        self.level = 1
        self.next_level_exp = 100

    def take_damage(self, damage):
        damage -= self.defense
        if damage < 0:
            damage = 0
        self.health -= int(damage)
        if self.health < 0:
            self.health = 0

    def is_alive(self):
        return self.health > 0

    def gain_exp(self, exp):
        self.exp += exp
        print(f"You gained {exp} EXP!")
        while self.exp >= self.next_level_exp:
            self.level_up()

    def level_up(self):
        self.level += 1
        self.exp -= self.next_level_exp
        self.next_level_exp = int(self.next_level_exp * 1.5)
        self.max_health += 10
        self.health = self.max_health
        self.attack += 5
        self.defense += 2
        self.magic_power += 3
        print(f"\nCongratulations! You leveled up to level {self.level}!")
        print("Max Health: +10, Attack: +5, Defense: +2, Magic Power: +3")

    def __str__(self):
        return (f"{self.name} (Level: {self.level}, HP: {self.health}/{self.max_health}, "
                f"Attack: {self.attack}, Defense: {self.defense}, Magic: {self.magic_power}, "
                f"Element: {self.element}, EXP: {self.exp}/{self.next_level_exp})")

class Warrior(Character):
    def __init__(self, name, element):
        super().__init__(name, 100, 20, 10, 5, element)

class Mage(Character):
    def __init__(self, name, element):
        super().__init__(name, 80, 10, 5, 20, element)

class Rogue(Character):
    def __init__(self, name, element):
        super().__init__(name, 70, 15, 8, 10, element)

# Adventurer Guilds
class Guild:
    def __init__(self, name, quests):
        self.name = name
        self.quests = quests

    def get_quest(self):
        if self.quests:
            return self.quests.pop(0)
        return None

# Quests
class Quest:
    def __init__(self, description, exp_reward, gold_reward, reward_item=None):
        self.description = description
        self.exp_reward = exp_reward
        self.gold_reward = gold_reward
        self.reward_item = reward_item

    def complete(self, player):
        player.gain_exp(self.exp_reward)
        player.gold += self.gold_reward
        if self.reward_item:
            player.inventory.append(self.reward_item)
        print(f"Quest completed! You received {self.exp_reward} EXP and {self.gold_reward} gold.")
        if self.reward_item:
            print(f"You received {self.reward_item}.")
        generate_lore_event("quest", player)

# Monsters
class Monster:
    def __init__(self, name, health, attack, defense, element):
        self.name = name
        self.health = health
        self.attack = attack
        self.defense = defense
        self.element = element

    def take_damage(self, damage):
        damage -= self.defense
        if damage < 0:
            damage = 0
        self.health -= int(damage)
        if self.health < 0:
            self.health = 0

    def is_alive(self):
        return self.health > 0

    def __str__(self):
        return (f"{self.name} (HP: {self.health}, Attack: {self.attack}, "
                f"Defense: {self.defense}, Element: {self.element})")

# NPC Class for lore encounters
class NPC:
    def __init__(self, name, element):
        self.name = name
        self.element = element

    def speak(self, player):
        dialogues = [
            f"Greetings, traveler. I sense the power of {self.element} within you.",
            f"Ah, a brave soul touched by {self.element}. The old legends speak of such strength.",
            f"Beware, for the balance of {self.element} is delicate in these troubled times."
        ]
        print(f"{self.name}: {random.choice(dialogues)}")
        generate_lore_event("npc", player)

# Combat System
def combat(player, monster):
    print(f"\nA wild {monster.name} appears with a {monster.element} aura!")
    while player.is_alive() and monster.is_alive():
        print(f"\n{player}")
        print(f"{monster}")
        action = input("\nDo you want to (a)ttack or (r)un? ").strip().lower()
        if action == 'a':
            # Player attacks
            base_damage = player.attack
            multiplier = get_element_multiplier(player.element, monster.element)
            damage = int(base_damage * multiplier)
            monster.take_damage(damage)
            print(f"You attack the {monster.name} for {damage} damage! (Multiplier: {multiplier}x)")
            if monster.is_alive():
                # Monster counterattacks
                base_damage = monster.attack
                multiplier = get_element_multiplier(monster.element, player.element)
                damage = int(base_damage * multiplier)
                player.take_damage(damage)
                print(f"The {monster.name} strikes back for {damage} damage! (Multiplier: {multiplier}x)")
                generate_lore_event("combat", player, enemy=monster)
        elif action == 'r':
            print("You run away!")
            return False
        else:
            print("Invalid action. Please choose (a)ttack or (r)un.")
    
    if not monster.is_alive():
        print(f"\nYou defeated the {monster.name}!")
        return True
    elif not player.is_alive():
        print("You have been defeated!")
        return False

# Lore and Storyline Introduction
def display_lore():
    print("\nWelcome to the Dungeons of Eldoria!")
    print("In a realm where elemental forces shape destiny, brave adventurers seek fortune and glory.")
    print("Join a guild, embark on daring quests, and witness the unfolding lore as your choices echo through time.")
    print("Choose from the elements: fire, water, air, light, earth, and dark.")
    print("The adventure begins now...")

# Main Game Loop
def main():
    display_lore()
    
    # Choose Class
    print("\nAre you a (w)arrior, (m)age, or (r)ogue?")
    class_choice = input("Choose your class: ").strip().lower()
    
    # Choose Element
    print("\nNow choose your element:")
    print("(f)ire, (w)ater, (a)ir, (l)ight, (e)arth, or (d)ark")
    element_choice = input("Choose your element: ").strip().lower()
    if element_choice == 'f':
        element = "fire"
    elif element_choice == 'w':
        element = "water"
    elif element_choice == 'a':
        element = "air"
    elif element_choice == 'l':
        element = "light"
    elif element_choice == 'e':
        element = "earth"
    elif element_choice == 'd':
        element = "dark"
    else:
        print("Invalid choice. Defaulting to fire.")
        element = "fire"
    
    # Create the player character with chosen class and element
    if class_choice == 'w':
        player = Warrior(input("Enter your warrior's name: "), element)
    elif class_choice == 'm':
        player = Mage(input("Enter your mage's name: "), element)
    elif class_choice == 'r':
        player = Rogue(input("Enter your rogue's name: "), element)
    else:
        print("Invalid class. Defaulting to Warrior.")
        player = Warrior(input("Enter your warrior's name: "), element)
    
    print(f"\nWelcome, {player.name} the {player.__class__.__name__} of {player.element}!")
    print("Joining the Adventurer's Guild...")

    # Create guilds with quests
    guilds = [
        Guild("Adventurer's Guild", [
            Quest("Defeat 3 goblins in the Dark Forest.", 50, 50),
            Quest("Retrieve the lost artifact from the Cursed Cave.", 100, 100, "Ancient Sword"),
            Quest("Clear the bandits from the Old Bridge.", 150, 150)
        ]),
        Guild("Mercenary Guild", [
            Quest("Escort the caravan to the market town.", 75, 75),
            Quest("Defend the village from the orc raid.", 120, 120),
            Quest("Find the missing merchant in the Whispering Woods.", 200, 200, "Enchanted Ring")
        ])
    ]
    
    current_guild = guilds[0]
    print(f"You have joined the {current_guild.name}!")
    
    # Main game loop options include: get quest, view inventory, check status, explore, or quit.
    while player.is_alive():
        print("\nWhat do you want to do?")
        print("(g)et quest, (i)nventory, (s)tatus, (e)xplore, (q)uit")
        action = input("Choose an action: ").strip().lower()
        
        if action == 'g':
            quest = current_guild.get_quest()
            if quest:
                print(f"\nQuest: {quest.description}")
                print("Starting the quest...")
                time.sleep(1)
                # Random chance for an encounter during the quest
                if random.choice([True, False]):
                    # Create a monster with a random element
                    monster_element = random.choice(ELEMENTS)
                    monster = Monster("Goblin", 30, 10, 5, monster_element)
                    if combat(player, monster):
                        quest.complete(player)
                else:
                    print("The quest proceeds without incident. You complete it swiftly.")
                    quest.complete(player)
            else:
                print("No quests available.")
        
        elif action == 'i':
            print("\nInventory:")
            if player.inventory:
                for item in player.inventory:
                    print(f"- {item}")
            else:
                print("Your inventory is empty.")
            print(f"Gold: {player.gold}")
        
        elif action == 's':
            print(f"\nStatus:\n{player}")
        
        elif action == 'e':
            # Explore: chance to encounter a wandering NPC with lore
            print("\nYou venture off the beaten path...")
            time.sleep(1)
            if random.random() < 0.5:
                npc_element = random.choice(ELEMENTS)
                npc_name = random.choice(["Eldon", "Maris", "Shade", "Lyra"])
                npc = NPC(npc_name, npc_element)
                npc.speak(player)
            else:
                print("You explore in solitude, and the silence of the wild stirs mysterious thoughts.")
                generate_lore_event("npc", player)
        
        elif action == 'q':
            print("Thanks for playing!")
            break
        
        else:
            print("Invalid action. Please choose (g)et quest, (i)nventory, (s)tatus, (e)xplore, or (q)uit.")

if __name__ == "__main__":
    main()
