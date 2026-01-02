from app.database.session import SessionLocal
from app.database.models import Category, ActiveIngredient, IngredientConflict, RiskLevel

def seed_data():
    db = SessionLocal()
    
    categories = ["Cleanser", "Toner", "Serum", "Moisturizer", "Sunscreen"]
    for cat_name in categories:
        if not db.query(Category).filter_by(name=cat_name).first():
            db.add(Category(name=cat_name))
    
    ingredients = ["Retinol", "Vitamin C", "AHA", "BHA", "Niacinamide"]
    for ing_name in ingredients:
        if not db.query(ActiveIngredient).filter_by(name=ing_name).first():
            db.add(ActiveIngredient(name=ing_name))
    
    db.commit()

    retinol = db.query(ActiveIngredient).filter_by(name="Retinol").first()
    aha = db.query(ActiveIngredient).filter_by(name="AHA").first()
    
    if retinol and aha:
        conflict = db.query(IngredientConflict).filter_by(
            ingredient_id_1=retinol.id, ingredient_id_2=aha.id
        ).first()
        if not conflict:
            db.add(IngredientConflict(
                ingredient_id_1=retinol.id,
                ingredient_id_2=aha.id,
                risk_level=RiskLevel.HIGH,
                description="Dapat menyebabkan iritasi parah dan kulit kering."
            ))
    
    db.commit()
    db.close()
    print("Seeding berhasil!")

if __name__ == "__main__":
    seed_data()