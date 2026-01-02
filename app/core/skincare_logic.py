def check_compatibility(ingredient_a: str, ingredient_b: str):
    conflicts = {
        "Retinol": ["AHA", "BHA", "Benzoyl Peroxide", "Vitamin C"],
        "Vitamin C": ["AHA", "BHA", "Retinol"],
        "AHA": ["Retinol", "Vitamin C", "BHA"],
        "BHA": ["Retinol", "Vitamin C", "AHA"]
    }
    
    if ingredient_a in conflicts and ingredient_b in conflicts[ingredient_a]:
        return False, f"{ingredient_a} sebaiknya tidak digunakan bersamaan dengan {ingredient_b}."
    
    return True, "Aman untuk digunakan bersamaan."