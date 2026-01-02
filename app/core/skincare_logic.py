def check_compatibility(ingredient_a: str, ingredient_b: str):
    conflicts = {
        "Retinol": ["AHA", "BHA", "Benzoyl Peroxide", "Vitamin C", "Adapalene"],
        "Vitamin C": ["AHA", "BHA", "Retinol", "Benzoyl Peroxide"],
        "AHA": ["Retinol", "Vitamin C", "BHA", "Adapalene"],
        "BHA": ["Retinol", "Vitamin C", "AHA", "Benzoyl Peroxide"],
        "Benzoyl Peroxide": ["Retinol", "Vitamin C", "BHA"],
        "Adapalene": ["AHA", "BHA", "Retinol"]
    }
    
    a = ingredient_a.strip()
    b = ingredient_b.strip()
    
    if a in conflicts and b in conflicts[a]:
        return False, f"Tidak Disarankan: {a} dan {b}."
    
    if b in conflicts and a in conflicts[b]:
        return False, f"Tidak Disarankan: {b} dan {a}."
    
    return True, "Aman digunakan bersamaan."