# The subjective criteria the AI evaluator scores. Submission structural
# completeness is deliberately NOT here — it's a deterministic check
# (see models.submission.Submission.missing_sections) that gates whether
# the AI is called at all.

RUBRIC_CRITERIA = [
    {
        "name": "Requirement understanding",
        "description": "Did the learner correctly interpret the problem's functional and non-functional requirements?",
        "good_evidence": "Explicitly references constraints/edge cases from the problem statement.",
        "weak_evidence": "Generic design with no reference to the stated constraints.",
    },
    {
        "name": "Class responsibilities",
        "description": "Is each class's responsibility singular and clearly stated?",
        "good_evidence": "Each class has one clearly described job.",
        "weak_evidence": "Vague classes (e.g. 'Manager', 'Handler') with no described responsibility.",
    },
    {
        "name": "Coupling & cohesion",
        "description": "Are dependencies between classes minimal and justified?",
        "good_evidence": "Explicit statement of what depends on what, with reasoning.",
        "weak_evidence": "Everything implicitly depends on everything, unaddressed.",
    },
    {
        "name": "Encapsulation",
        "description": "Is state hidden behind behaviour rather than freely exposed?",
        "good_evidence": "Internal state is described as owned/protected by its class.",
        "weak_evidence": "Fields described as freely mutable from outside the class.",
    },
    {
        "name": "Interface / abstraction usage",
        "description": "Are varying concerns abstracted behind an interface where appropriate?",
        "good_evidence": "Identifies a varying concern (e.g. pricing, scheduling) and abstracts it.",
        "weak_evidence": "Hardcodes a varying concern with no interface, even conceptually.",
    },
    {
        "name": "Extensibility",
        "description": "Can the design absorb a plausible future change without a rewrite?",
        "good_evidence": "Explicitly reasons about what would/wouldn't need to change.",
        "weak_evidence": "No mention of change resilience at all.",
    },
    {
        "name": "Explanation quality",
        "description": "Does the submission argue for its choices, not just list classes?",
        "good_evidence": "Trade-offs and 'why' are articulated.",
        "weak_evidence": "Bare class list with no justification.",
    },
]
