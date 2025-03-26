from app.database import DatabaseManager, Coins


# Main cheat functions
def set_coins(amount_of_coins):
    if not isinstance(amount_of_coins, int) or amount_of_coins < 0:
        return "Error: Coin amount must be a positive integer"

    db = DatabaseManager()
    session = db.Session()

    try:
        coins = session.query(Coins).first()
        old_amount = coins.total_count
        coins.total_count = amount_of_coins
        session.commit()
        return f"Coins updated: {old_amount} → {amount_of_coins}"
    except Exception as e:
        session.rollback()
        return f"Error setting coins: {str(e)}"
    finally:
        session.close()


def infinite_nitro(game, enable=True):
    """Toggle infinite nitro for player"""
    try:
        player = game.current_display.p
        player.nitroAmount = 9999 if enable else 0
        player.infiNitro = enable
        return f"Infinite nitro {'enabled' if enable else 'disabled'}"
    except:
        return "Failed to modify nitro settings"


def repair_tires(game):
    """Repair all tires to full health"""
    try:
        player = game.current_display.p
        player.deadTires = 0
        player.tireHealth = 1
        return "All tires repaired"
    except:
        return "Failed to repair tires"


def super_speed(game, multiplier=2.0):
    """Increase player's speed parameters"""
    try:
        player = game.current_display.p
        player.normalMaxSpeed *= multiplier
        player.normalAcceleration *= multiplier
        player.currentMaxSpeed = player.normalMaxSpeed
        player.currentAcceleration = player.normalAcceleration
        return f"Speed increased by {multiplier}x"
    except:
        return "Failed to modify speed"


def invincible(game, duration=60):
    """Give temporary invincibility to player"""
    try:
        player = game.current_display.p
        player.invincibility = duration
        return f"Invincibility activated for {duration} seconds"
    except:
        return "Failed to activate invincibility"


def fill_nitro(game):
    """Fill nitro to maximum"""
    try:
        player = game.current_display.p
        player.nitroAmount = 100
        return "Nitro tank filled to 100%"
    except:
        return "Failed to refill nitro"

#not working for some reason
# def add_powerups(game):
#     """Add all powerups to inventory"""
#     try:
#         player = game.current_display.p
#         # Clear inventory first to avoid overflow
#         game.current_display.p.inventory = []
#         # Add powerups: 1=strength, 2=barrier, 3=spikes, 4=heal
#         for i in range(1, 5):
#             if len(game.current_display.p.inventory) < game.current_display.p.inventory_size:
#                 game.current_display.p.inventory.append(i)
#         return f"Added powerups to inventory"
#     except:
#         return "Failed to add powerups"


def teleport_checkpoint(game, checkpoint_number=None):
    """Teleport to specified checkpoint or next checkpoint"""
    try:
        player = game.current_display.p
        display = game.current_display

        if checkpoint_number is None:
            # Go to next checkpoint
            next_cp = (player.current_checkpoint + 1) % display.amount_of_checkpoints
        else:
            next_cp = max(0, min(checkpoint_number, display.amount_of_checkpoints - 1))

        checkpoint = display.checkpoints[next_cp]
        x = (checkpoint.start_pos[0] + checkpoint.end_pos[0]) / 2
        y = (checkpoint.start_pos[1] + checkpoint.end_pos[1]) / 2
        player.teleport((x, y))

        return f"Teleported to checkpoint {next_cp}"
    except:
        return "Failed to teleport"


def fast_win(game):
    """Teleport to next checkpoint until game is won"""
    try:
        player = game.current_display.p
        display = game.current_display

        while True:
            teleport_checkpoint(game)
            display.mainloop()
            if player.lap > display.map_data['laps']:
                break
        return "Fast win cheat activated"
    except Exception as e:
        return "Failed to activate fast win cheat, error: " + str(e)



def reset_cheats(game):
    """Reset all cheats to default values"""
    try:
        player = game.current_display.p
        player.infiNitro = False
        player.tireHealth = 1
        player.deadTires = 0
        player.invincibility = 0
        player.inventory = []
        player.change_model(player.model)  # Reset car parameters
        return "All cheats reset to default"
    except:
        return "Failed to reset cheats"


def help():
    """Show available cheat commands"""
    commands = [


    ]
    return """
           Available cheats:
           - set_coins(amount): Set the global coin count
           - infinite_nitro(game) - Toggle infinite nitro,
           - repair_tires(game) - Repair all tires,
           - super_speed(game, multiplier) - Increase speed,
           - invincible(game, duration) - Temporary invincibility,
           - fill_nitro(game) - Fill nitro to 100%,
           - teleport_checkpoint(game, checkpoint_number) - Teleport to target_checkpoint or next checkpoint,
           - fast_win(game) - Teleport to next checkpoint until game is won,
           - reset_cheats(game) - Reset all cheats to default,
           - help(): Display this help message
           """