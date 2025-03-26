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


# Helper function to list available cheats
def help():
    return """
           Available cheats:
           - set_coins(amount): Set the global coin count
           - help(): Display this help message
           """