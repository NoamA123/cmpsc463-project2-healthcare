"""Cancellations and rebooking on top of a finished schedule. Owner: Noam.

Each provider's free time becomes Slots in a SlotTree. Cancelling an
appointment frees its slot; rebooking places a patient in the earliest slot
that starts at or after ``not_before`` and is long enough for the visit.
"""

from __future__ import annotations

from fairsched.schema import Appointment, Dataset, Schedule


class SlotManager:
    def __init__(self, dataset: Dataset, schedule: Schedule) -> None:
        """Build one SlotTree per provider from the gaps in ``schedule``."""
        raise NotImplementedError

    def cancel(self, patient_id: str) -> Appointment:
        """Remove the patient's appointment and return its slot to the tree."""
        raise NotImplementedError

    def rebook(self, patient_id: str, not_before: int) -> Appointment | None:
        """Book the earliest fitting slot across all providers, or None if none fits."""
        raise NotImplementedError

    def schedule(self) -> Schedule:
        raise NotImplementedError
