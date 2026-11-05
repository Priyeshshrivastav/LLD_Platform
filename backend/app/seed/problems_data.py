PROBLEMS = [
    {
        "title": "Parking Lot System",
        "difficulty": "Easy-Medium",
        "summary": "Design a multi-level parking lot that handles different vehicle types and calculates fees.",
        "requirements": (
            "- Support multiple vehicle types (motorcycle, car, bus) and multiple spot sizes.\n"
            "- Handle vehicle entry (find + assign a spot) and exit (free the spot).\n"
            "- Calculate a parking fee based on duration.\n"
            "- The lot has multiple levels, each with a fixed number of spots per size."
        ),
        "constraints": (
            "- A vehicle can only park in a spot of an appropriate size or larger.\n"
            "- The system should be able to report the number of free spots per level.\n"
            "- Assume single-entry/single-exit gate for MVP scope."
        ),
        "key_concepts": "entity modeling, strategy pattern (pricing), allocation strategy",
    },
    {
        "title": "Elevator System",
        "difficulty": "Medium",
        "summary": "Design the control logic for a bank of elevators serving external and internal requests.",
        "requirements": (
            "- Multiple elevators serve multiple floors.\n"
            "- Handle external requests (floor + direction) and internal requests (destination floor from inside a car).\n"
            "- Each elevator has a current floor, direction, and door state.\n"
            "- A dispatcher decides which elevator services a given request."
        ),
        "constraints": (
            "- Avoid unnecessary direction changes where possible.\n"
            "- The system should handle multiple simultaneous requests.\n"
            "- Concurrency can be reasoned about conceptually — no need to implement real threading."
        ),
        "key_concepts": "state machine design, scheduling/dispatch abstraction, request queueing",
    },
    {
        "title": "Library Management System",
        "difficulty": "Easy-Medium",
        "summary": "Design a system to manage a library's catalog, checkouts, holds, and overdue handling.",
        "requirements": (
            "- Maintain a catalog of books, where a title may have multiple physical copies.\n"
            "- Members can check out and return copies, and place holds on unavailable titles.\n"
            "- Track due dates and calculate overdue fines."
        ),
        "constraints": (
            "- A copy can only be checked out to one member at a time.\n"
            "- Holds should be served in the order they were placed.\n"
            "- Assume a fixed loan period and a fixed per-day fine rate."
        ),
        "key_concepts": "relationship/cardinality modeling (Book vs BookCopy), lifecycle/state transitions, business rules",
    },
    {
        "title": "Rate Limiter",
        "difficulty": "Medium",
        "summary": "Design a configurable rate limiter that can be applied per client to an API.",
        "requirements": (
            "- Limit the number of requests a client can make within a configurable time window.\n"
            "- Support at least one rate-limiting algorithm (e.g. token bucket or sliding window).\n"
            "- The limiting algorithm should be swappable without changing how the rest of the system calls the limiter."
        ),
        "constraints": (
            "- Must work per-client (not global).\n"
            "- Assume in-memory state is acceptable for MVP, but the storage mechanism should be abstracted from the limiting policy."
        ),
        "key_concepts": "strategy/interface design, abstraction over storage vs. policy",
    },
    {
        "title": "Movie Ticket Booking System",
        "difficulty": "Medium-Hard",
        "summary": "Design a system for browsing shows, selecting seats, and booking/paying for tickets.",
        "requirements": (
            "- Browse shows for a movie (theatre, screen, time slot).\n"
            "- Select one or more seats for a show and hold them temporarily.\n"
            "- Confirm a booking via payment, or release the hold on timeout/cancellation."
        ),
        "constraints": (
            "- Two users must not be able to book the same seat for the same show.\n"
            "- A held-but-unpaid seat should eventually become available again.\n"
            "- Reason about the seat-locking approach even if not fully implemented."
        ),
        "key_concepts": "concurrency-sensitive design, booking lifecycle state machine, multi-entity relationships",
    },
]
