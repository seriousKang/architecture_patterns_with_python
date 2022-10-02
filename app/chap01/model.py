from typing import Optional, Set, List
from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class OrderLine:
    order_id: str
    sku: str
    qty: int


class Batch:
    def __init__(self,
                 reference: str,
                 sku: str,
                 eta: Optional[date],
                 available_quantity: int):
        self.reference = reference
        self.sku = sku
        self.eta = eta
        self._available_quantity = available_quantity
        self.allocations: Set[OrderLine] = set()

    def allocate(self,
                 line: OrderLine):
        if self.can_allocate(line):
            self.allocations.add(line)

    def deallocate(self,
                   line: OrderLine):
        if line in self.allocations:
            self.allocations.remove(line)

    @property
    def allocated_quantity(self) -> int:
        return sum(line.qty for line in self.allocations)

    @property
    def available_quantity(self) -> int:
        return self._available_quantity - self.allocated_quantity

    def can_allocate(self,
                     line: OrderLine) -> bool:
        return self.sku == line.sku and \
               self.available_quantity >= line.qty

    def __eq__(self, other):
        if not isinstance(other, Batch):
            return False
        return other.reference == self.reference

    def __hash__(self):
        return hash(self.reference)

    def __gt__(self,
               other):
        if self.eta is None:
            return False
        elif other.eta is None:
            return True
        else:
            return self.eta > other.eta


class OutOfStock(Exception):
    pass


def allocate(line: OrderLine,
             batches: List[Batch]) -> str:
    try:
        batch = next(
            b for b in sorted(batches) if b.can_allocate(line)
        )
        batch.allocate(line)
        return batch.reference
    except StopIteration:
        raise OutOfStock(f'Out of stock for sku {line.sku}')
