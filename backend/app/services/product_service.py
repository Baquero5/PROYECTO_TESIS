from app.repositories.product_repository import ProductRepository
from app.models.product import Product
from sqlalchemy.ext.asyncio import AsyncSession


class ProductService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = ProductRepository(db)

    async def create_product(self, product_data: dict) -> Product:
        product = Product(**product_data)
        return await self.repo.create(product)

    async def get_product(self, product_id: int) -> Product | None:
        return await self.repo.get_by_id(product_id)

    async def get_product_by_code(self, code: str) -> Product | None:
        return await self.repo.get_by_code(code)

    async def get_all_products(self, skip: int = 0, limit: int = 100):
        return await self.repo.get_all(skip, limit)

    async def update_product(self, product_id: int, product_data: dict) -> Product | None:
        return await self.repo.update(product_id, **product_data)

    async def delete_product(self, product_id: int) -> bool:
        return await self.repo.delete(product_id)

    async def check_stock_levels(self) -> list[dict]:
        low_stock = await self.repo.get_low_stock()
        return [
            {
                "id": p.id,
                "code": p.code,
                "name": p.name,
                "stock": p.stock,
                "min_stock": p.min_stock,
                "status": "critical" if p.stock <= p.min_stock else "warning"
            }
            for p in low_stock
        ]

    async def get_inventory_stats(self) -> dict:
        products = await self.repo.get_all()
        total_products = len(products)
        total_value = sum(p.stock * p.cost_price for p in products)
        low_stock_count = sum(1 for p in products if p.stock <= p.min_stock)
        
        return {
            "total_products": total_products,
            "total_inventory_value": round(total_value, 2),
            "low_stock_count": low_stock_count,
            "in_stock_count": total_products - low_stock_count
        }
