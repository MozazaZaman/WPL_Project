from __future__ import annotations

import json
import uuid
import hashlib
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from enum import Enum, auto
from typing import Optional, List, Dict, Callable
from collections import defaultdict


# ---------------------------------------------------------------------------
# Enums & Constants
# ---------------------------------------------------------------------------

class Category(Enum):
    ROAD = "Road"
    WATER = "Water"
    GAS = "Gas"
    POWER = "Power"
    SANITATION = "Sanitation"


class Department(Enum):
    WASA = "WASA"           # Water issues
    LGED = "LGED"           # Roads
    DESA = "DESA"           # Electricity
    TITAS_GAS = "Titas Gas" # Gas leaks
    CITY_CORP = "City Corp" # Sanitation


class Status(Enum):
    SUBMITTED = auto()
    VERIFYING = auto()
    REJECTED = auto()
    CLASSIFIED = auto()
    CHECKING_DUPLICATE = auto()
    MERGED = auto()
    RANKED = auto()
    ROUTED = auto()
    ASSIGNED = auto()
    IN_PROGRESS = auto()
    RESOLVED = auto()


class Severity(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


# ---------------------------------------------------------------------------
# Data Models
# ---------------------------------------------------------------------------

@dataclass
class GPSLocation:
    lat: float
    lon: float

    def distance_km(self, other: GPSLocation) -> float:
        """Haversine distance between two GPS points."""
        from math import radians, sin, cos, sqrt, atan2
        R = 6371.0
        lat1, lon1 = radians(self.lat), radians(self.lon)
        lat2, lon2 = radians(other.lat), radians(other.lon)
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))
        return R * c


@dataclass
class Complaint:
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    citizen_id: str = ""
    photo_url: str = ""
    description: str = ""
    gps: Optional[GPSLocation] = None
    submitted_at: datetime = field(default_factory=datetime.now)

    # Pipeline outputs
    status: Status = Status.SUBMITTED
    category: Optional[Category] = None
    department: Optional[Department] = None
    priority_score: float = 0.0
    severity: Severity = Severity.LOW
    vote_count: int = 1
    merged_into: Optional[str] = None
    rejection_reason: str = ""
    assigned_staff_id: Optional[str] = None
    resolved_at: Optional[datetime] = None
    resolution_notes: str = ""

    def to_dict(self) -> dict:
        d = asdict(self)
        d["status"] = self.status.name
        d["category"] = self.category.value if self.category else None
        d["department"] = self.department.value if self.department else None
        d["severity"] = self.severity.name
        d["submitted_at"] = self.submitted_at.isoformat()
        d["resolved_at"] = self.resolved_at.isoformat() if self.resolved_at else None
        return d


@dataclass
class Notification:
    citizen_id: str
    message: str
    channel: str = "app"  # "sms" | "app" | "email"
    sent_at: Optional[datetime] = None


# ---------------------------------------------------------------------------
# Agent 1 — Photo Verifier
# ---------------------------------------------------------------------------

class PhotoVerifier:
    """
    Checks if the submitted image is:
      - Real (not AI-generated)
      - Relevant to civic issues
      - Not fake / misleading

    EDITABLE: Replace stub logic with real ML model calls.
    """
    def __init__(self):
        # Stub: in production, load a vision classifier here
        self.fake_keywords = {"stock photo", "meme", "selfie", "party"}

    def verify(self, complaint: Complaint) -> tuple[bool, str]:
        """Returns (is_valid, reason_if_rejected)."""
        # Stub heuristics — replace with actual image analysis
        desc_lower = complaint.description.lower()

        if any(kw in desc_lower for kw in self.fake_keywords):
            return False, "Image appears irrelevant or fake."

        if not complaint.photo_url:
            return False, "No photo attached."

        # Simulate 5% random rejection rate for demo
        # hash_val = int(hashlib.md5(complaint.id.encode()).hexdigest(), 16)
        # if hash_val % 100 < 5:
        #     return False, "AI-generated image detected."

        return True, ""


# ---------------------------------------------------------------------------
# Agent 2 — Classifier
# ---------------------------------------------------------------------------

class Classifier:
    """
    Classifies complaint into: Road / Water / Gas / Power / Sanitation.

    EDITABLE: Replace keyword matching with an NLP model (BERT, etc.).
    """
    KEYWORDS: Dict[Category, List[str]] = {
        Category.ROAD:       ["pothole", "road", "street", "broken road", "crack"],
        Category.WATER:      ["water", "pipe", "leak", "flood", "drainage", "wasa"],
        Category.GAS:        ["gas", "gas leak", "pipeline", "titas", "smell gas"],
        Category.POWER:      ["electricity", "power", "line down", "transformer", "desa"],
        Category.SANITATION: ["garbage", "trash", "sewage", "toilet", "sanitation", "waste"],
    }

    def classify(self, complaint: Complaint) -> Category:
        desc_lower = complaint.description.lower()
        scores: Dict[Category, int] = defaultdict(int)

        for category, keywords in self.KEYWORDS.items():
            for kw in keywords:
                if kw in desc_lower:
                    scores[category] += 1

        if scores:
            return max(scores, key=scores.get)
        return Category.ROAD  # default fallback


# ---------------------------------------------------------------------------
# Agent 3 — Duplicate Checker
# ---------------------------------------------------------------------------

class DuplicateChecker:
    """
    Scans GPS radius for similar complaints.
    If duplicate found → merge (vote count +1).

    EDITABLE: Adjust DUPLICATE_RADIUS_KM and similarity logic.
    """
    DUPLICATE_RADIUS_KM = 0.3  # 300 meters

    def __init__(self, complaint_store: ComplaintStore):
        self.store = complaint_store

    def check(self, complaint: Complaint) -> Optional[str]:
        """
        Returns the ID of an existing duplicate complaint, or None if unique.
        """
        if not complaint.gps:
            return None

        for existing in self.store.get_active():
            if existing.id == complaint.id:
                continue
            if existing.category != complaint.category:
                continue
            if not existing.gps:
                continue

            dist = complaint.gps.distance_km(existing.gps)
            if dist <= self.DUPLICATE_RADIUS_KM:
                return existing.id
        return None


# ---------------------------------------------------------------------------
# Agent 4 — Priority Ranker
# ---------------------------------------------------------------------------

class PriorityRanker:
    """
    Ranks complaints by: Severity + vote count + time elapsed.
    Higher score = higher priority.

    EDITABLE: Tune weights and formula.
    """
    SEVERITY_WEIGHT = 10.0
    VOTE_WEIGHT = 2.0
    TIME_WEIGHT = 0.5  # per hour elapsed

    def rank(self, complaint: Complaint) -> float:
        hours_elapsed = (datetime.now() - complaint.submitted_at).total_seconds() / 3600
        score = (
            complaint.severity.value * self.SEVERITY_WEIGHT +
            complaint.vote_count * self.VOTE_WEIGHT +
            hours_elapsed * self.TIME_WEIGHT
        )
        complaint.priority_score = round(score, 2)
        return score


# ---------------------------------------------------------------------------
# Agent 5 — Department Router
# ---------------------------------------------------------------------------

class DepartmentRouter:
    """
    Maps complaint category → responsible department.

    EDITABLE: Add new categories or departments.
    """
    MAP: Dict[Category, Department] = {
        Category.WATER:      Department.WASA,
        Category.ROAD:       Department.LGED,
        Category.POWER:      Department.DESA,
        Category.GAS:        Department.TITAS_GAS,
        Category.SANITATION: Department.CITY_CORP,
    }

    def route(self, complaint: Complaint) -> Department:
        if complaint.category in self.MAP:
            return self.MAP[complaint.category]
        return Department.CITY_CORP  # fallback


# ---------------------------------------------------------------------------
# Data Store (in-memory for demo; swap for DB in production)
# ---------------------------------------------------------------------------

class ComplaintStore:
    def __init__(self):
        self._complaints: Dict[str, Complaint] = {}
        self._notifications: List[Notification] = []

    def save(self, complaint: Complaint):
        self._complaints[complaint.id] = complaint

    def get(self, complaint_id: str) -> Optional[Complaint]:
        return self._complaints.get(complaint_id)

    def get_active(self) -> List[Complaint]:
        """Returns complaints that are not rejected, merged, or resolved."""
        exclude = {Status.REJECTED, Status.MERGED, Status.RESOLVED}
        return [c for c in self._complaints.values() if c.status not in exclude]

    def get_by_department(self, dept: Department) -> List[Complaint]:
        return [
            c for c in self._complaints.values()
            if c.department == dept and c.status not in {Status.RESOLVED, Status.REJECTED, Status.MERGED}
        ]

    def list_all(self) -> List[Complaint]:
        return list(self._complaints.values())

    def add_notification(self, notification: Notification):
        self._notifications.append(notification)


# ---------------------------------------------------------------------------
# Pipeline Orchestrator
# ---------------------------------------------------------------------------

class NagorikPipeline:
    """
    Runs the full complaint flow end-to-end.
    """
    def __init__(self, store: ComplaintStore):
        self.store = store
        self.verifier = PhotoVerifier()
        self.classifier = Classifier()
        self.duplicate_checker = DuplicateChecker(store)
        self.ranker = PriorityRanker()
        self.router = DepartmentRouter()

    def submit(self, citizen_id: str, photo_url: str, description: str,
               lat: float, lon: float, severity: Severity = Severity.MEDIUM) -> Complaint:
        """Entry point: citizen submits a complaint."""
        complaint = Complaint(
            citizen_id=citizen_id,
            photo_url=photo_url,
            description=description,
            gps=GPSLocation(lat, lon),
            severity=severity,
        )
        self.store.save(complaint)
        self._run_pipeline(complaint)
        return complaint

    def _run_pipeline(self, c: Complaint):
        # ---- Agent 1: Photo Verifier ----
        c.status = Status.VERIFYING
        is_valid, reason = self.verifier.verify(c)
        if not is_valid:
            c.status = Status.REJECTED
            c.rejection_reason = reason
            self._notify(c.citizen_id, f"Your complaint was rejected: {reason}")
            return

        # ---- Agent 2: Classifier ----
        c.category = self.classifier.classify(c)
        c.status = Status.CLASSIFIED

        # ---- Agent 3: Duplicate Checker ----
        c.status = Status.CHECKING_DUPLICATE
        duplicate_id = self.duplicate_checker.check(c)
        if duplicate_id:
            original = self.store.get(duplicate_id)
            if original:
                original.vote_count += 1
                c.status = Status.MERGED
                c.merged_into = duplicate_id
                self._notify(c.citizen_id, "Your complaint was merged with an existing one. Vote counted.")
                return

        # ---- Agent 4: Priority Ranker ----
        self.ranker.rank(c)
        c.status = Status.RANKED

        # ---- Agent 5: Department Router ----
        c.department = self.router.route(c)
        c.status = Status.ROUTED

        # ---- Auto-assign to staff dashboard ----
        c.status = Status.ASSIGNED

    def _notify(self, citizen_id: str, message: str, channel: str = "app"):
        notif = Notification(citizen_id=citizen_id, message=message, channel=channel)
        notif.sent_at = datetime.now()
        self.store.add_notification(notif)


# ---------------------------------------------------------------------------
# Staff Dashboard
# ---------------------------------------------------------------------------

class StaffDashboard:
    """
    Staff interface: view assigned complaints, track progress, resolve.
    """
    def __init__(self, store: ComplaintStore):
        self.store = store

    def get_department_queue(self, dept: Department) -> List[Complaint]:
        """View all complaints routed to a specific department."""
        complaints = self.store.get_by_department(dept)
        complaints.sort(key=lambda c: c.priority_score, reverse=True)
        return complaints

    def assign_to_staff(self, complaint_id: str, staff_id: str) -> bool:
        c = self.store.get(complaint_id)
        if c and c.status == Status.ASSIGNED:
            c.assigned_staff_id = staff_id
            c.status = Status.IN_PROGRESS
            return True
        return False

    def resolve(self, complaint_id: str, resolution_notes: str = "") -> bool:
        """Mark complaint as resolved and notify citizen."""
        c = self.store.get(complaint_id)
        if not c or c.status == Status.RESOLVED:
            return False

        c.status = Status.RESOLVED
        c.resolved_at = datetime.now()
        c.resolution_notes = resolution_notes

        msg = f"Your {c.category.value.lower() if c.category else 'complaint'} has been resolved."
        notif = Notification(citizen_id=c.citizen_id, message=msg, channel="sms")
        notif.sent_at = datetime.now()
        self.store.add_notification(notif)
        return True

    def generate_report(self, dept: Optional[Department] = None) -> dict:
        """Generate a summary report."""
        complaints = self.store.list_all() if dept is None else self.store.get_by_department(dept)
        total = len(complaints)
        resolved = sum(1 for c in complaints if c.status == Status.RESOLVED)
        pending = sum(1 for c in complaints if c.status in {Status.ASSIGNED, Status.IN_PROGRESS})
        avg_priority = sum(c.priority_score for c in complaints) / total if total else 0

        return {
            "department": dept.value if dept else "All",
            "total_complaints": total,
            "resolved": resolved,
            "pending": pending,
            "average_priority_score": round(avg_priority, 2),
        }


# ---------------------------------------------------------------------------
# DEMO / USAGE
# ---------------------------------------------------------------------------

def demo():
    """Run a quick end-to-end demo of the pipeline."""
    store = ComplaintStore()
    pipeline = NagorikPipeline(store)
    dashboard = StaffDashboard(store)

    print("=" * 60)
    print("NAGORIK COMPLAINT SYSTEM — DEMO RUN")
    print("=" * 60)

    # 1. Citizen submits a water leak complaint
    c1 = pipeline.submit(
        citizen_id="citizen_001",
        photo_url="https://example.com/leak.jpg",
        description="Water pipe burst near Dhanmondi 32. Flooding the street.",
        lat=23.7461,
        lon=90.3742,
        severity=Severity.HIGH,
    )
    print(f"\n[1] Submitted: {c1.id} | Status: {c1.status.name} | Dept: {c1.department.value if c1.department else 'N/A'}")
    print(f"    Category: {c1.category.value if c1.category else 'N/A'} | Priority: {c1.priority_score}")

    # 2. Another citizen submits a similar complaint nearby (should merge)
    c2 = pipeline.submit(
        citizen_id="citizen_002",
        photo_url="https://example.com/leak2.jpg",
        description="Same water leak, different angle. Please fix!",
        lat=23.7463,  # Only ~22m away → within 300m radius
        lon=90.3744,
        severity=Severity.MEDIUM,
    )
    print(f"\n[2] Submitted: {c2.id} | Status: {c2.status.name}")
    if c2.status == Status.MERGED:
        print(f"    → Merged into {c2.merged_into}. Vote count on original is now {store.get(c2.merged_into).vote_count}")

    # 3. A road complaint
    c3 = pipeline.submit(
        citizen_id="citizen_003",
        photo_url="https://example.com/pothole.jpg",
        description="Huge pothole on Mirpur Road causing accidents.",
        lat=23.8103,
        lon=90.4125,
        severity=Severity.CRITICAL,
    )
    print(f"\n[3] Submitted: {c3.id} | Status: {c3.status.name} | Dept: {c3.department.value if c3.department else 'N/A'}")
    print(f"    Category: {c3.category.value if c3.category else 'N/A'} | Priority: {c3.priority_score}")

    # 4. Rejected complaint (fake/irrelevant)
    c4 = pipeline.submit(
        citizen_id="citizen_004",
        photo_url="https://example.com/meme.jpg",
        description="This is just a meme photo, not a real issue.",
        lat=23.7000,
        lon=90.4000,
        severity=Severity.LOW,
    )
    print(f"\n[4] Submitted: {c4.id} | Status: {c4.status.name} | Reason: {c4.rejection_reason}")

    # 5. Staff dashboard view
    print("\n" + "=" * 60)
    print("STAFF DASHBOARD — LGED Queue")
    print("=" * 60)
    lged_queue = dashboard.get_department_queue(Department.LGED)
    for c in lged_queue:
        print(f"  [{c.priority_score}] {c.id}: {c.description[:50]}...")

    # 6. Assign and resolve
    if lged_queue:
        top = lged_queue[0]
        dashboard.assign_to_staff(top.id, staff_id="staff_lged_01")
        print(f"\n  Assigned {top.id} to staff_lged_01 → {top.status.name}")

        dashboard.resolve(top.id, "Pothole filled with asphalt. Road reopened.")
        print(f"  Resolved {top.id} → {top.status.name}")

    # 7. Report
    print("\n" + "=" * 60)
    print("SYSTEM REPORT")
    print("=" * 60)
    print(json.dumps(dashboard.generate_report(), indent=2))

    # 8. Notifications log
    print("\n" + "=" * 60)
    print("NOTIFICATIONS SENT")
    print("=" * 60)
    for n in store._notifications:
        print(f"  [{n.channel}] To {n.citizen_id}: {n.message}")


if __name__ == "__main__":
    demo()
