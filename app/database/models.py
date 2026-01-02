import enum
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Date, Time, Boolean, Float, JSON, Table, Enum, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class RoutineType(enum.Enum):
    MORNING = "morning"
    NIGHT = "night"

class RiskLevel(enum.Enum):
    HIGH = "high_risk"
    MEDIUM = "medium_risk"
    LOW = "low_risk"

product_ingredients_map = Table(
    "product_ingredients_map",
    Base.metadata,
    Column("product_id", Integer, ForeignKey("products.id"), primary_key=True),
    Column("ingredient_id", Integer, ForeignKey("active_ingredients.id"), primary_key=True),
)

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    
    full_name = Column(String, nullable=False)
    alias = Column(String, nullable=True)
    date_of_birth = Column(Date, nullable=True) 
    gender = Column(String, nullable=True)
    
    skin_type = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    products = relationship("Product", back_populates="owner")
    routines = relationship("Routine", back_populates="owner")
    logs = relationship("SkinLog", back_populates="owner")


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)

    products = relationship("Product", back_populates="category")


class ActiveIngredient(Base):
    __tablename__ = "active_ingredients"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(Text, nullable=True)

class IngredientConflict(Base):
    __tablename__ = "ingredient_conflicts"

    id = Column(Integer, primary_key=True, index=True)
    ingredient_id_1 = Column(Integer, ForeignKey("active_ingredients.id"))
    ingredient_id_2 = Column(Integer, ForeignKey("active_ingredients.id"))
    risk_level = Column(Enum(RiskLevel), default=RiskLevel.LOW)
    description = Column(String, nullable=True)


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    category_id = Column(Integer, ForeignKey("categories.id"))
    product_name = Column(String, nullable=False)
    brand = Column(String, nullable=True)
    opened_at = Column(Date, nullable=True)
    pao_months = Column(Integer, default=12)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    owner = relationship("User", back_populates="products")
    category = relationship("Category", back_populates="products")
    ingredients = relationship("ActiveIngredient", secondary=product_ingredients_map)


class Routine(Base):
    __tablename__ = "routines"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    routine_type = Column(Enum(RoutineType), nullable=False)
    scheduled_time = Column(Time, nullable=False)

    owner = relationship("User", back_populates="routines")
    items = relationship("RoutineItem", back_populates="routine", cascade="all, delete-orphan")


class RoutineItem(Base):
    __tablename__ = "routine_items"

    id = Column(Integer, primary_key=True, index=True)
    routine_id = Column(Integer, ForeignKey("routines.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    order_index = Column(Integer)

    routine = relationship("Routine", back_populates="items")
    product = relationship("Product")


class SkinLog(Base):
    __tablename__ = "skin_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    photo_url = Column(String, nullable=True)
    ai_analysis_result = Column(JSON, nullable=True)
    stress_level = Column(Integer, nullable=True)
    sleep_hours = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    owner = relationship("User", back_populates="logs")