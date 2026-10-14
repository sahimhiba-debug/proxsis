"""Normalised schema: company, project, signal, need estimate, candidate
(fictional), call outcome, agency, consultant.

Every ingested row carries provenance fields (source, url, retrieved_at,
license, fictif). Dates are calendar dates; ``available_at`` is the date the
information became public and is the only date usable for point-in-time
features.
"""

from __future__ import annotations

from datetime import date, datetime
from typing import Any, Literal

import pandas as pd
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from proxsis.entities import normalize_uid
from proxsis.taxonomy import CANTON_LANGUAGES, SECTOR_TRADES, SIGNAL_FAMILIES, TRADES

Language = Literal["fr", "de", "it", "rm"]
OutcomeCode = Literal["rendez_vous", "a_rappeler", "pas_de_besoin", "mauvais_contact", "deja_servi", "commande"]
Role = Literal["consultant", "chef_agence", "groupe"]


class _Base(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class _WithProvenance(_Base):
    source: str = Field(min_length=1)
    url: str = Field(min_length=1)
    retrieved_at: datetime
    license: str = Field(min_length=1)
    fictif: bool = False


def _check_canton(v: str) -> str:
    if v not in CANTON_LANGUAGES:
        raise ValueError(f"canton inconnu: {v}")
    return v


def _check_trades(v: list[str]) -> list[str]:
    unknown = [t for t in v if t not in TRADES]
    if unknown:
        raise ValueError(f"métiers inconnus: {unknown}")
    return v


class Company(_WithProvenance):
    company_id: str
    uid: str | None = None
    name: str = Field(min_length=1)
    canton: str
    commune: str | None = None
    npa: str | None = None
    lat: float | None = None
    lon: float | None = None
    language: Language
    sector: str
    employees_est: int | None = Field(default=None, ge=0)

    @field_validator("uid")
    @classmethod
    def _uid(cls, v: str | None) -> str | None:
        if v is None:
            return None
        n = normalize_uid(v)
        if n is None:
            raise ValueError(f"IDE invalide: {v}")
        return n

    _canton = field_validator("canton")(classmethod(lambda cls, v: _check_canton(v)))

    @field_validator("sector")
    @classmethod
    def _sector(cls, v: str) -> str:
        if v not in SECTOR_TRADES:
            raise ValueError(f"secteur inconnu: {v}")
        return v


class Project(_WithProvenance):
    project_id: str
    company_id: str | None
    kind: Literal["marche_public", "permis_construire", "extension_site"]
    canton: str
    commune: str | None = None
    value_chf: float | None = Field(default=None, ge=0)
    announced_at: date
    expected_start: date | None = None
    expected_end: date | None = None
    trades: list[str] = Field(default_factory=list)

    _canton = field_validator("canton")(classmethod(lambda cls, v: _check_canton(v)))
    _trades = field_validator("trades")(classmethod(lambda cls, v: _check_trades(v)))


class Signal(_WithProvenance):
    signal_id: str
    company_id: str | None
    family: str
    subtype: str
    event_date: date
    available_at: date
    canton: str
    commune: str | None = None
    lat: float | None = None
    lon: float | None = None
    value_chf: float | None = Field(default=None, ge=0)
    trades: list[str] = Field(default_factory=list)
    title: str = ""
    summary: str = ""
    project_id: str | None = None

    _canton = field_validator("canton")(classmethod(lambda cls, v: _check_canton(v)))
    _trades = field_validator("trades")(classmethod(lambda cls, v: _check_trades(v)))

    @model_validator(mode="after")
    def _dates_and_family(self) -> Signal:
        if self.family not in SIGNAL_FAMILIES:
            raise ValueError(f"famille inconnue: {self.family}")
        if self.subtype not in SIGNAL_FAMILIES[self.family]:
            raise ValueError(f"sous-type inconnu pour {self.family}: {self.subtype}")
        if self.available_at < self.event_date:
            raise ValueError("available_at ne peut pas précéder event_date")
        return self


class NeedEstimate(_Base):
    company_id: str
    week_start: date
    trade: str
    n_low: float = Field(ge=0)
    n_mid: float = Field(ge=0)
    n_high: float = Field(ge=0)
    confidence: float = Field(ge=0, le=1)
    method: str
    assumptions: list[str]

    @model_validator(mode="after")
    def _check(self) -> NeedEstimate:
        if self.week_start.weekday() != 0:
            raise ValueError("week_start doit être un lundi")
        if not (self.n_low <= self.n_mid <= self.n_high):
            raise ValueError("il faut n_low <= n_mid <= n_high")
        _check_trades([self.trade])
        return self


class Candidate(_Base):
    """Candidate — ALWAYS fictional in this repository."""

    candidate_id: str
    trades: list[str]
    skills: list[str] = Field(default_factory=list)
    certifications: list[str] = Field(default_factory=list)
    canton: str
    lat: float
    lon: float
    languages: list[Language] = Field(default_factory=lambda: list[Language](["fr"]))
    available_from: date | None = None
    driving_licence: bool = False
    max_travel_km: float = 40.0
    fictif: bool

    _canton = field_validator("canton")(classmethod(lambda cls, v: _check_canton(v)))
    _trades = field_validator("trades")(classmethod(lambda cls, v: _check_trades(v)))

    @field_validator("fictif")
    @classmethod
    def _must_be_fictional(cls, v: bool) -> bool:
        if not v:
            raise ValueError("les candidats de ce dépôt doivent être FICTIFS")
        return v


class CallOutcome(_Base):
    outcome_id: str
    company_id: str
    consultant_id: str
    alert_week: date
    outcome: OutcomeCode
    comment: str = ""
    created_at: datetime | None = None


class Agency(_Base):
    agency_id: str
    name: str
    brand: str
    canton: str
    lat: float
    lon: float
    language: Language
    cantons_covered: list[str]
    fictif: bool = True


class Consultant(_Base):
    consultant_id: str
    agency_id: str
    display_name: str
    role: Role
    fictif: bool = True


def validate_frame(df: pd.DataFrame, model: type[BaseModel], max_rows: int | None = None) -> list[str]:
    """Contract check of a DataFrame against a schema model.

    Returns a list of human-readable errors (empty list = valid).
    """
    errors: list[str] = []
    required = [n for n, f in model.model_fields.items() if f.is_required()]
    missing = [c for c in required if c not in df.columns]
    if missing:
        errors.append(f"colonnes manquantes: {missing}")
        return errors
    rows = df if max_rows is None else df.head(max_rows)
    known = set(model.model_fields)
    for i, rec in enumerate(rows.to_dict(orient="records")):
        payload: dict[str, Any] = {k: v for k, v in rec.items() if k in known and not _is_nan(v)}
        try:
            model.model_validate(payload)
        except Exception as e:
            errors.append(f"ligne {i}: {e}")
    return errors


def _is_nan(v: Any) -> bool:
    try:
        return bool(pd.isna(v)) if not isinstance(v, list | tuple | dict) else False
    except (TypeError, ValueError):
        return False
