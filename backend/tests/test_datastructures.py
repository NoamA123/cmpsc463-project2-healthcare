from __future__ import annotations

import random

import pytest

from fairsched.datastructures import HashTable, MinHeap, Slot, SlotTree


def test_min_heap_sorts():
    rng = random.Random(0)
    xs = [rng.randrange(1000) for _ in range(500)]
    h: MinHeap[int] = MinHeap()
    for x in xs:
        h.push(x)
    assert len(h) == len(xs)
    assert h.peek() == min(xs)
    assert [h.pop() for _ in range(len(xs))] == sorted(xs)
    with pytest.raises(IndexError):
        h.pop()


def test_min_heap_heapify():
    xs = [(5, "D2"), (1, "D3"), (5, "D1")]
    h = MinHeap(list(xs))
    assert [h.pop() for _ in xs] == sorted(xs)


def test_hash_table_roundtrip():
    t: HashTable[str, int] = HashTable(capacity=2)
    for i in range(200):
        t.put(f"P{i}", i)
    t.put("P5", -5)
    assert len(t) == 200
    assert t.get("P5") == -5 and t.get("P199") == 199
    assert "P7" in t and "nope" not in t
    assert t.remove("P7") == 7 and "P7" not in t
    assert sorted(t.keys()) == sorted(f"P{i}" for i in range(200) if i != 7)
    with pytest.raises(KeyError):
        t.get("P7")


def test_slot_tree_queries():
    tree = SlotTree()
    slots = [Slot(s, s + length, "D01") for s, length in [(50, 10), (10, 5), (30, 20), (80, 40)]]
    for s in slots:
        tree.insert(s)
    assert tree.in_order() == sorted(slots)
    assert tree.earliest_at_or_after(0) == Slot(10, 15, "D01")
    assert tree.earliest_at_or_after(11) == Slot(30, 50, "D01")
    assert tree.earliest_at_or_after(0, min_length=15) == Slot(30, 50, "D01")
    assert tree.earliest_at_or_after(81) is None
    tree.delete(Slot(30, 50, "D01"))
    assert tree.earliest_at_or_after(11) == Slot(50, 60, "D01")
    with pytest.raises(KeyError):
        tree.delete(Slot(30, 50, "D01"))
