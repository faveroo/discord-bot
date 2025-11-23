def parse_bet_type(bet: str):
    bet = bet.lower()

    # Cor
    if bet in ["red", "vermelho"]:
        return ("color", "red")
    if bet in ["black", "preto"]:
        return ("color", "black")

    # Faixas
    ranges = ["1-12", "13-24", "25-36", "1-18", "19-36"]
    if bet in ranges:
        start, end = map(int, bet.split("-"))
        return ("range", (start, end))

    # Número
    if bet.isdigit() and 0 <= int(bet) <= 36:
        return ("number", int(bet))

    return None
