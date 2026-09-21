from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class ContextSource(str, Enum):
    USER = "USER"
    MODEL_INFERRED = "MODEL_INFERRED"
    WEBPAGE = "WEBPAGE"
    ASSUMPTION = "ASSUMPTION"
    UNKNOWN = "UNKNOWN"


class ContextStatus(str, Enum):
    ACTIVE = "ACTIVE"
    REVIEW = "REVIEW"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    ARCHIVED = "ARCHIVED"


class RequirementPriority(str, Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class RequirementCategory(str, Enum):
    FUNCTIONAL = "FUNCTIONAL"
    NON_FUNCTIONAL = "NON_FUNCTIONAL"
    DESIGN = "DESIGN"
    TECHNICAL = "TECHNICAL"
    SECURITY = "SECURITY"
    ACCESSIBILITY = "ACCESSIBILITY"
    PERFORMANCE = "PERFORMANCE"
    SEO = "SEO"


class WebpageContext(BaseModel):
    page_title: Optional[str] = None
    page_url: Optional[str] = None
    selected_text: Optional[str] = None
    enabled: bool = False


class IntentData(BaseModel):
    project_type: str = ""
    business_domain: str = ""
    primary_goal: str = ""
    target_users: List[str] = Field(default_factory=list)
    core_functionality: List[str] = Field(default_factory=list)
    content_requirements: List[str] = Field(default_factory=list)
    design_requirements: List[str] = Field(default_factory=list)
    technical_requirements: List[str] = Field(default_factory=list)
    constraints: List[str] = Field(default_factory=list)
    known_information: List[str] = Field(default_factory=list)
    unknown_information: List[str] = Field(default_factory=list)


class Requirement(BaseModel):
    id: str  # REQ-001, etc.
    title: str
    description: str
    category: str = RequirementCategory.FUNCTIONAL.value
    priority: str = RequirementPriority.MEDIUM.value
    source: str = ContextSource.USER.value
    confidence: float = 1.0
    status: str = ContextStatus.ACTIVE.value
    dependencies: List[str] = Field(default_factory=list)
    related_pages: List[str] = Field(default_factory=list)
    related_components: List[str] = Field(default_factory=list)
    related_apis: List[str] = Field(default_factory=list)
    related_entities: List[str] = Field(default_factory=list)


class PageSpec(BaseModel):
    id: str  # PAGE-001
    name: str
    path: str
    purpose: str
    sections: List[str] = Field(default_factory=list)
    components: List[str] = Field(default_factory=list)
    requirements: List[str] = Field(default_factory=list)
    source: str = ContextSource.MODEL_INFERRED.value
    status: str = ContextStatus.ACTIVE.value


class ComponentSpec(BaseModel):
    id: str  # COMP-001
    name: str
    type: str
    description: str
    props: List[str] = Field(default_factory=list)
    state_items: List[str] = Field(default_factory=list)
    requirements: List[str] = Field(default_factory=list)
    source: str = ContextSource.MODEL_INFERRED.value
    status: str = ContextStatus.ACTIVE.value


class APISpec(BaseModel):
    id: str  # API-001
    endpoint: str
    method: str
    description: str
    request_body: str = ""
    response_body: str = ""
    requirements: List[str] = Field(default_factory=list)
    source: str = ContextSource.MODEL_INFERRED.value
    status: str = ContextStatus.ACTIVE.value


class DatabaseEntity(BaseModel):
    id: str  # DB-001
    name: str
    fields: List[Dict[str, str]] = Field(default_factory=list)
    relations: List[str] = Field(default_factory=list)
    requirements: List[str] = Field(default_factory=list)
    source: str = ContextSource.MODEL_INFERRED.value
    status: str = ContextStatus.ACTIVE.value


class DesignSpec(BaseModel):
    visual_style: str = "Modern, clean, aesthetic"
    layout: str = "Responsive multi-section layout"
    color_direction: str = "Neutral dark/light base with high-contrast accent"
    typography: str = "Sans-serif header and body typography"
    spacing: str = "8pt grid system"
    components: str = "Cards, buttons, modals, forms"
    responsive_behavior: str = "Mobile-first, desktop adaptive"
    navigation: str = "Sticky top navigation bar with mobile toggle"
    interaction_patterns: str = "Smooth scroll, hover transitions, active states"
    cta_strategy: str = "Primary action buttons prominent above the fold"
    source: str = ContextSource.ASSUMPTION.value
    status: str = ContextStatus.ACTIVE.value


class TechnicalSpec(BaseModel):
    frontend: str = "HTML5, modern CSS / Tailwind, Vanilla JS"
    backend: str = "FastAPI / Node (recommended/inferred)"
    api_style: str = "RESTful JSON endpoints"
    database: str = "Relational / Document schema"
    authentication: str = "Session / JWT based"
    authorization: str = "Role-based access where applicable"
    security: str = "Input sanitization, CORS protection, HTTPS"
    performance: str = "Optimized asset loading, responsive images"
    accessibility: str = "WCAG 2.1 AA compliance, keyboard navigation, ARIA attributes"
    seo: str = "Semantic tags, meta tags, OpenGraph support"
    deployment: str = "Static / server container"
    recommendations: List[str] = Field(default_factory=list)
    source: str = ContextSource.MODEL_INFERRED.value
    status: str = ContextStatus.ACTIVE.value


class TaskSpec(BaseModel):
    id: str  # TASK-001
    title: str
    description: str
    category: str = "implementation"
    priority: str = RequirementPriority.MEDIUM.value
    requirements: List[str] = Field(default_factory=list)
    source: str = ContextSource.MODEL_INFERRED.value
    status: str = ContextStatus.ACTIVE.value


class AssumptionItem(BaseModel):
    id: str  # ASSUMP-001
    text: str
    rationale: str = ""
    source: str = ContextSource.ASSUMPTION.value
    status: str = ContextStatus.ACTIVE.value


class UnknownItem(BaseModel):
    id: str  # UNK-001
    text: str
    impact: str = ""
    source: str = ContextSource.UNKNOWN.value
    status: str = ContextStatus.ACTIVE.value


class DecisionItem(BaseModel):
    id: str  # DEC-001
    decision: str
    rationale: str = ""
    status: str = ContextStatus.APPROVED.value


class StructuredContext(BaseModel):
    intent: IntentData = Field(default_factory=IntentData)
    requirements: List[Requirement] = Field(default_factory=list)
    pages: List[PageSpec] = Field(default_factory=list)
    components: List[ComponentSpec] = Field(default_factory=list)
    apis: List[APISpec] = Field(default_factory=list)
    database_entities: List[DatabaseEntity] = Field(default_factory=list)
    design: DesignSpec = Field(default_factory=DesignSpec)
    technical: TechnicalSpec = Field(default_factory=TechnicalSpec)
    tasks: List[TaskSpec] = Field(default_factory=list)
    constraints: List[str] = Field(default_factory=list)
    assumptions: List[AssumptionItem] = Field(default_factory=list)
    unknowns: List[UnknownItem] = Field(default_factory=list)
    decisions: List[DecisionItem] = Field(default_factory=list)
