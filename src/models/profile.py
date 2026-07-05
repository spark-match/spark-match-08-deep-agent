"""Student vocational profile schema.

This schema is used by langmem to extract structured profile data
from natural conversations. The agent chats with the student and
langmem progressively fills in the fields as information emerges.
"""

from pydantic import BaseModel, Field


class StudentProfile(BaseModel):
    """Structured vocational profile of a student.

    This model is progressively filled by langmem as the agent
    converses with the student. Fields start as None and are
    populated as the student reveals information naturally.
    """

    # --- Identity ---
    name: str | None = Field(default=None, description="Student's name")
    age: int | None = Field(default=None, description="Student's age")
    education_level: str | None = Field(
        default=None,
        description="Current education level: secundaria, preparatoria, universidad, posgrado",
    )
    current_studies: str | None = Field(
        default=None,
        description="What the student is currently studying, if anything",
    )

    # --- RIASEC Scores (1-10 each) ---
    realistic: int | None = Field(
        default=None,
        description="RIASEC Realistic score (1-10): hands-on, physical, mechanical work",
    )
    investigative: int | None = Field(
        default=None,
        description="RIASEC Investigative score (1-10): analytical, scientific, research",
    )
    artistic: int | None = Field(
        default=None,
        description="RIASEC Artistic score (1-10): creative, expressive, design",
    )
    social: int | None = Field(
        default=None,
        description="RIASEC Social score (1-10): helping, teaching, counseling",
    )
    enterprising: int | None = Field(
        default=None,
        description="RIASEC Enterprising score (1-10): leading, persuading, managing",
    )
    conventional: int | None = Field(
        default=None,
        description="RIASEC Conventional score (1-10): organizing, data, detail-oriented",
    )

    # --- Derived ---
    riasec_code: str | None = Field(
        default=None,
        description="3-letter RIASEC code derived from top 3 scores (e.g., 'IAS', 'RIC')",
    )

    # --- Interests & Context ---
    interests: list[str] = Field(
        default_factory=list,
        description="List of topics, activities, or subjects the student enjoys",
    )
    strengths: list[str] = Field(
        default_factory=list,
        description="Self-reported or inferred strengths and skills",
    )
    preferred_fields: list[str] = Field(
        default_factory=list,
        description="Professional fields the student is drawn to",
    )
    dislikes: list[str] = Field(
        default_factory=list,
        description="Activities, subjects, or work environments the student wants to avoid",
    )

    # --- Career Direction ---
    target_career: str | None = Field(
        default=None,
        description="Career the student has chosen or is leaning towards",
    )
    career_goals: str | None = Field(
        default=None,
        description="What the student hopes to achieve professionally",
    )

    @property
    def has_riasec_profile(self) -> bool:
        """Check if enough RIASEC data exists to compute a profile."""
        scores = [
            self.realistic,
            self.investigative,
            self.artistic,
            self.social,
            self.enterprising,
            self.conventional,
        ]
        return all(s is not None for s in scores)

    @property
    def profile_completeness(self) -> float:
        """Calculate how complete the profile is (0.0 to 1.0)."""
        fields = [
            self.name,
            self.age,
            self.education_level,
            self.realistic,
            self.investigative,
            self.artistic,
            self.social,
            self.enterprising,
            self.conventional,
        ]
        filled = sum(1 for f in fields if f is not None)
        filled += min(len(self.interests), 3)  # Up to 3 interests count
        total = len(fields) + 3
        return round(filled / total, 2)
