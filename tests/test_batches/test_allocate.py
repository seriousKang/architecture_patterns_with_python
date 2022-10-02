import pytest
from app.chap01.model import Batch, OrderLine, allocate, OutOfStock
from datetime import date, timedelta

today = date.today()
tomorrow = today + timedelta(days=1)
later = tomorrow + timedelta(days=10)


def test_prefers_current_stock_batches_to_shipments():
    in_stock_batch = Batch(reference="in-stock-batch",
                           sku="RETRO-CLOCK",
                           available_quantity=100,
                           eta=None)
    shipment_batch = Batch(reference="shipment-batch",
                           sku="RETRO-CLOCK",
                           available_quantity=100,
                           eta=tomorrow)
    line = OrderLine(order_id="oref",
                     sku="RETRO-CLOCK",
                     qty=10)

    allocate(line, [in_stock_batch, shipment_batch])

    assert in_stock_batch.available_quantity == 90
    assert shipment_batch.available_quantity == 100


def test_prefers_earlier_batches():
    earliest = Batch(reference="speedy-batch",
                     sku="MINIMALIST-SPOON",
                     available_quantity=100,
                     eta=today)
    medium = Batch(reference="speedy-batch",
                   sku="MINIMALIST-SPOON",
                   available_quantity=100,
                   eta=tomorrow)
    latest = Batch(reference="speedy-batch",
                   sku="MINIMALIST-SPOON",
                   available_quantity=100,
                   eta=later)
    line = OrderLine(order_id="order1",
                     sku="MINIMALIST-SPOON",
                     qty=10)

    allocate(line, [medium, earliest, latest])

    assert earliest.available_quantity == 90
    assert medium.available_quantity == 100
    assert latest.available_quantity == 100


def test_returns_allocated_batch_ref():
    in_stock_batch = Batch(reference="in-stock-batch-ref",
                           sku="HIGHBROW-POSTER",
                           available_quantity=100,
                           eta=None)
    shipment_batch = Batch(reference="shipment-batch-ref",
                           sku="HIGHBROW-POSTER",
                           available_quantity=100,
                           eta=tomorrow)
    line = OrderLine(order_id="oref",
                     sku="HIGHBROW-POSTER",
                     qty=10)

    allocation = allocate(line, [in_stock_batch, shipment_batch])

    assert allocation == in_stock_batch.reference


def test_raises_out_of_stock_exception_if_cannot_allocate():
    batch = Batch(reference="batch1",
                  sku="SMALL-FORK",
                  available_quantity=10,
                  eta=today)

    allocate(line=OrderLine(order_id="order1", sku="SMALL-FORK", qty=10),
             batches=[batch])

    with pytest.raises(OutOfStock, match="Out of stock for sku SMALL-FORK"):
        allocate(line=OrderLine(order_id="order2", sku="SMALL-FORK", qty=1),
                 batches=[batch])
