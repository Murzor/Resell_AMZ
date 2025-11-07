import pytest
from app.workers.tasks import scrape_store, clean_price
from app.models.store import Store
from decimal import Decimal


def test_clean_price():
    """Test de nettoyage des prix"""
    assert clean_price("10,99 €") == Decimal("10.99")
    assert clean_price("15.50") == Decimal("15.50")
    assert clean_price("€ 20,00") == Decimal("20.00")
    assert clean_price("invalid") == Decimal("0")


def test_scrape_store_dry_run(db):
    """Test du scraping en mode dry-run"""
    # Créer une boutique de test
    store = Store(
        name="Test Store",
        url="https://example.com",
        selectors={
            "product_selector": ".product",
            "price_selector": ".price",
            "title_selector": ".title"
        },
        is_active=True
    )
    db.add(store)
    db.commit()
    db.refresh(store)
    
    # Tester en mode dry-run
    result = scrape_store(store.id, dry_run=True)
    
    assert result["store_id"] == store.id
    assert result["store_name"] == "Test Store"
    assert result["dry_run"] is True
    assert "products_scraped" in result
    assert "offers_found" in result


def test_scrape_store_invalid_store(db):
    """Test avec une boutique inexistante"""
    with pytest.raises(ValueError, match="Boutique .* introuvable"):
        scrape_store(999, dry_run=True)


def test_scrape_store_inactive_store(db):
    """Test avec une boutique inactive"""
    store = Store(
        name="Inactive Store",
        url="https://example.com",
        selectors={},
        is_active=False
    )
    db.add(store)
    db.commit()
    db.refresh(store)
    
    with pytest.raises(ValueError, match="Boutique .* inactive"):
        scrape_store(store.id, dry_run=True)

