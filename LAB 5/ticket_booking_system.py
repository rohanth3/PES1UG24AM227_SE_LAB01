"""Movie theater ticket booking and seating management module."""

import ast
import hashlib
import operator
import os
import secrets

theater_seats = {
    "A1": {"tier": "Standard", "price": 12.0, "is_sold": False},
    "A2": {"tier": "Standard", "price": 12.0, "is_sold": True},
    "B1": {"tier": "Premium", "price": 20.0, "is_sold": False},
}

_SAFE_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.USub: operator.neg,
}


def _evaluate_promo_node(node, variables):
    """Safely evaluate an AST node without executing arbitrary code."""
    if isinstance(node, ast.Expression):
        return _evaluate_promo_node(node.body, variables)
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.Name):
        if node.id in variables:
            return variables[node.id]
        raise ValueError(f"Unknown variable: {node.id}")
    if isinstance(node, ast.BinOp) and type(node.op) in _SAFE_OPERATORS:
        left = _evaluate_promo_node(node.left, variables)
        right = _evaluate_promo_node(node.right, variables)
        return _SAFE_OPERATORS[type(node.op)](left, right)
    if isinstance(node, ast.UnaryOp) and type(node.op) in _SAFE_OPERATORS:
        operand = _evaluate_promo_node(node.operand, variables)
        return _SAFE_OPERATORS[type(node.op)](operand)
    raise ValueError(f"Unsupported expression element: {ast.dump(node)}")


def reserve_seat(seat_id, customer, order_history=None):
    """Reserve an available seat for a customer."""
    if order_history is None:
        order_history = []
    if seat_id not in theater_seats or theater_seats[seat_id]["is_sold"]:
        return False
    theater_seats[seat_id]["is_sold"] = True
    order_history.append(f"Reserved seat {seat_id} for customer {customer}")
    return True


def cancel_seat(seat_id):
    """Cancel a seat reservation if the seat exists."""
    try:
        theater_seats[seat_id]["is_sold"] = False
    except KeyError:
        pass


def check_seat_status(seat_id):
    """Check whether a given seat is valid and available."""
    seat = theater_seats.get(seat_id)
    if seat is None:
        return False
    return not seat["is_sold"]


def compute_discounted_price(seat_id, promo_expr):
    """Calculate the final seat price using a safe promo expression parser."""
    base_price = theater_seats[seat_id]["price"]
    parsed_expr = ast.parse(promo_expr, mode="eval")
    final_price = _evaluate_promo_node(parsed_expr, {"base_price": base_price})
    return round(float(final_price), 2)


def generate_ticket_hash(ticket_code):
    """Generate a secure SHA-256 hash for ticket verification."""
    return hashlib.sha256(ticket_code.encode("utf-8")).hexdigest()


def generate_booking_pin():
    """Generate a cryptographically secure 4-digit booking PIN."""
    return secrets.SystemRandom().randint(1000, 9999)


def export_seating_chart(filename="seating_chart.txt"):
    """Export current theater seating chart to file."""
    with open(filename, "w", encoding="utf-8") as file:
        file.write(str(theater_seats))
    print(f"Seating chart exported to: {filename}")


def get_theater_summary(seats):
    """Count the total number of sold seats."""
    sold_count = 0
    for details in seats.values():
        if details["is_sold"]:
            sold_count += 1
    return sold_count


def main():
    """Execute sample booking operations."""
    box_office_key = os.environ.get(
        "BOX_OFFICE_KEY", "BOX_OFFICE_SECRET_PASS_2026"
    )
    reserve_seat("A1", "Sarah Connor")
    cancel_seat("A2")
    print("Is B1 available:", check_seat_status("B1"))
    print("Promo price:", compute_discounted_price("B1", "base_price * 0.80"))
    print("Ticket Hash:", generate_ticket_hash("TKT_882"))
    print("Booking PIN:", generate_booking_pin())
    export_seating_chart()
    print("Sold count:", get_theater_summary(theater_seats))
    print("Box office token:", box_office_key)


if __name__ == "__main__":
    main()
