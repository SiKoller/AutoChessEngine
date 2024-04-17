from AutoChessEngine import Arena, RectCollider, SimulationCreature, SimulationGame, SimulationProjectile, Game
import random
import math
import datetime
import uuid

def get_sniper_creature(position, i):
    return SimulationCreature(
        position=position,
        angle=random.randint(0, 360),
        health=100,
        speed=random.randint(5, 40),
        name=f"Sniper {i}",
        max_turn_rate=random.randint(8, 16),
        shoot_cooldown=random.randint(15, 30),
        bounding_box_size=(50, 100),
        damage=random.randint(50, 150), # Sniper damage range
        bullet_speed=random.randint(50, 100), # Sniper bullet speed range
        bullet_range=random.randint(500, 900), # Sniper bullet range
        # ... any other new attributes you want to initialize ...
    )

def get_machine_gun_creature(position, i):
    return SimulationCreature(
        position=position,
        angle=random.randint(0, 360),
        health=100,
        speed=random.randint(5, 40),
        name=f"Machine_Gun {i}",
        max_turn_rate=random.randint(5, 15),
        shoot_cooldown=random.randint(2, 5),
        bounding_box_size=(50, 100),
        damage=random.randint(15, 25), # Machine Gun damage range
        bullet_speed=random.randint(10, 50), # Machine Gun bullet speed range
        bullet_range=random.randint(200, 500), # Machine Gun bullet range
        # ... any other new attributes you want to initialize ...
    )

def get_mine_laying_creature(position, i):
    return SimulationCreature(
        position=position,
        angle=random.randint(0, 360),
        health=100,
        speed=random.randint(5, 40),
        name=f"Mine_Layer {i}",
        max_turn_rate=random.randint(1, 8),
        shoot_cooldown=random.randint(5, 30),
        bounding_box_size=(50, 100),
        damage=random.randint(80, 120), # Mine Layer damage range
        bullet_speed=0,
        bullet_range=random.randint(500, 700), # Mine Layer bullet range
        # ... any other new attributes you want to initialize ...
    )


def calculate_lattice_position(arena, n, i):

    # Calculate the number of rows and columns for the grid
    rows = int(n ** 0.5)
    cols = n if rows == 0 else (n // rows) + (n % rows > 0)

    # Calculate the row and column for the current creature
    row = i // cols
    col = i % cols

    # Calculate the size of each cell in the grid
    cell_width = arena.width / cols
    cell_height = arena.height / rows

    # Calculate the position of the creature within its cell
    # The creature is placed in the center of the cell
    x = (col * cell_width) + (cell_width / 2)
    y = (row * cell_height) + (cell_height / 2)

    return x, y

def calculate_lattice_position_with_jitter(arena, n, i, jitter_range=150, safe_zone=150):
    rows = int(math.sqrt(n))
    cols = n // rows
    cell_width = (arena.width - 2 * safe_zone) // cols
    cell_height = (arena.height - 2 * safe_zone) // rows
    row = i // cols
    col = i % cols
    x = col * cell_width + cell_width // 2 + safe_zone
    y = row * cell_height + cell_height // 2 + safe_zone

    # Calculate the maximum jitter range based on the cell dimensions
    max_jitter_x = min(jitter_range, cell_width // 2 - 50)  # Adjust the buffer value (50) as needed
    max_jitter_y = min(jitter_range, cell_height // 2 - 50)  # Adjust the buffer value (50) as needed

    # Apply jitter while ensuring the positions stay within the arena boundaries
    jittered_x = x + random.randint(-max_jitter_x, max_jitter_x)
    jittered_y = y + random.randint(-max_jitter_y, max_jitter_y)

    # Ensure the positions are within the arena boundaries, considering the safe zone
    jittered_x = max(safe_zone, min(jittered_x, arena.width - safe_zone))
    jittered_y = max(safe_zone, min(jittered_y, arena.height - safe_zone))

    return jittered_x, jittered_y

def initialize_game():
    arena = Arena(width=2000, height=2000)
    game = SimulationGame(arena, [])

    # Initialize a SimulationProjectile

    # Number of creatures in simulation
    n = 10

    # Randomly choose the type of creature to instantiate
    creature_types = [get_sniper_creature, get_machine_gun_creature, get_mine_laying_creature]

    # Initialize a dictionary to keep track of creature counts
    creature_counts = {
        'S': 0,
        'ML': 0,
        'MG': 0
        # Add more creature types and their counts as needed
    }

    creatures = []
    for i in range(n):
        creature_type = random.choice(creature_types)
        creature = creature_type(calculate_lattice_position_with_jitter(arena, n, i, jitter_range=150), i)
        creatures.append(creature)
        game.add_game_object(creature) # Add the creature to the game
        

        # Update the creature counts based on the creature type
        if creature_type == get_sniper_creature:
            creature_counts['S'] += 1
        elif creature_type == get_machine_gun_creature:
            creature_counts['MG'] += 1
        elif creature_type == get_mine_laying_creature:
            creature_counts['ML'] += 1
        # Add more conditions for other creature types as needed
    game.creature_counts = creature_counts
    return game

import uuid
from datetime import datetime

def generate_filename(creature_counts):
    timestamp = datetime.now().strftime("%Y-%m-%d--%H-%M-%S")
    unique_id = str(uuid.uuid4())[:8]  # Generate a unique identifier (first 8 characters of UUID)
    creature_counts_str = "--".join(f"{k}{v}" for k, v in creature_counts.items())
    return f"machine_gun_gauntlet--{timestamp}--{unique_id}--{creature_counts_str}--.json"





def main():
    game = initialize_game()
    creature_counts = game.creature_counts
    time_limit = 500 # Set your desired time limit here
    while True:
        game.simulate_turn()
        alive_creatures = [creature for creature in game.game_objects if isinstance(creature, SimulationCreature) and creature.health > 0]
        if len(alive_creatures) == 1: 
            game.winner = alive_creatures[0].name
            break
        if Game.get_time() >= time_limit or len(alive_creatures) == 0:
            game.winner = "Draw"
            break

    # Generate the filename based on the simulation parameters
    filename = generate_filename(creature_counts)

    # Save the simulation record with the generated filename
    game.record_game(f"playbacks/{filename}")
    print(f"Simulation saved to playbacks/{filename}")

if __name__ == "__main__":
    main()
