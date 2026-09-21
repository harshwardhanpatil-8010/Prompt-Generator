from typing import Dict, List, Optional
from ..context.evaluator import ContextScores
from ..context.graph import DependencyGraphData
from ..context.representation import (
    APISpec,
    AssumptionItem,
    ComponentSpec,
    ContextSource,
    ContextStatus,
    DatabaseEntity,
    DecisionItem,
    DesignSpec,
    IntentData,
    PageSpec,
    Requirement,
    RequirementCategory,
    RequirementPriority,
    StructuredContext,
    TaskSpec,
    TechnicalSpec,
    UnknownItem,
    WebpageContext,
)
from .base import BaseLLMProvider


class MockLLMProvider(BaseLLMProvider):
    """
    Deterministic, domain-aware mock LLM provider.
    Inspects user requirements to generate realistic, structured context representations
    without needing an external API or running neural model.
    """

    def _detect_domain(self, text: str) -> str:
        text_lower = text.lower()
        if any(k in text_lower for k in ["gym", "fitness", "workout", "trainer", "crossfit"]):
            return "Fitness & Health"
        elif any(k in text_lower for k in ["sneaker", "shoe", "footwear"]):
            return "Sneaker & Footwear Retail"
        elif any(k in text_lower for k in ["shop", "store", "ecommerce", "cart", "product"]):
            return "E-Commerce & Retail"
        elif any(k in text_lower for k in ["restaurant", "cafe", "food", "menu", "dining"]):
            return "Food & Hospitality"
        elif any(k in text_lower for k in ["portfolio", "resume", "designer", "developer"]):
            return "Personal Portfolio"
        elif any(k in text_lower for k in ["saas", "dashboard", "analytics", "b2b"]):
            return "SaaS & Software"
        return "Business & Services"

    def extract_intent(
        self, prompt: str, context: Optional[WebpageContext] = None
    ) -> IntentData:
        domain = self._detect_domain(prompt)
        text_lower = prompt.lower()

        known_info = [f"User requirement: {prompt}"]
        unknowns = [
            "Exact business brand guidelines and logo",
            "Production payment gateway credentials",
            "Customer support phone and business address",
        ]

        if "sneaker" in text_lower or "shoe" in text_lower or "footwear" in text_lower:
            project_type = "Modern Sneaker Store E-Commerce Platform"
            primary_goal = "Showcase exclusive sneaker drops, provide interactive 3D/carousel product galleries, allow size selection, and enable smooth checkout."
            target_users = ["Sneaker enthusiasts", "Streetwear collectors", "General footwear shoppers"]
            core_func = [
                "Exclusive Drop Countdown & Featured Sneaker Hero",
                "Faceted Product Grid with Brand/Size/Price Filters",
                "Product Detail Modal with Dynamic Size Selector & Stock Counter",
                "Interactive Slide-Over Shopping Cart with Order Summary",
                "Verified Customer Reviews & Rating Badges",
            ]
            content_reqs = ["High-res product photography", "Release date calendar", "Size conversion charts", "Authenticity guarantee badges"]
            design_reqs = ["Bold streetwear aesthetic with high-contrast typography", "Minimalist dark/light mode with neon accent highlights"]
            tech_reqs = ["Semantic HTML5", "Modern CSS / Tailwind Grid", "Vanilla JS cart state management"]
            constraints = ["Mobile viewport responsiveness", "Fast image render performance", "WCAG AA accessibility"]
            known_info.extend(["Sneaker e-commerce store requested", "Modern visual style requested"])
            unknowns.extend(["Inventory SKU list", "Shipping courier integrations"])
        elif "gym" in text_lower or "fitness" in text_lower:
            project_type = "Modern Fitness & Gym Platform"
            primary_goal = "Showcase facility offerings, trainer expertise, class schedules, and convert visitors into active members."
            target_users = ["Prospective gym members", "Current athletes", "Fitness enthusiasts", "Class attendees"]
            core_func = [
                "Membership Tier Comparison & Direct Enrollment",
                "Trainer Profiles with Specializations & Booking Modal",
                "Weekly Class Schedule & Interactive Filter",
                "Verified Member Testimonials & Social Proof",
                "Free Trial Pass & Tour Booking Form",
            ]
            content_reqs = ["Membership pricing cards", "Trainer bios and certifications", "Class schedule timetable", "Member reviews"]
            design_reqs = ["Energetic, athletic dark theme with vibrant accents", "Dynamic typography", "Mobile-optimized cards"]
            tech_reqs = ["Semantic HTML5", "Modern CSS / Tailwind", "Interactive vanilla JS filters", "RESTful API stubs"]
            constraints = ["Mobile responsiveness", "Sub-second initial load", "WCAG AA compliance"]
            known_info.extend(["Gym website requested", "Trainers, classes, membership, testimonials"])
            unknowns.extend(["Exact monthly membership fees", "Gym operating hours and address"])
        else:
            project_type = f"{domain} Web Application"
            primary_goal = f"Deliver an engaging, high-conversion web presence for {domain} with modern interactive components."
            target_users = ["General public", "Potential clients", "Service subscribers"]
            core_func = ["Hero Banner with CTA", "Core Service Highlights", "Interactive Showcase", "Contact / Inquiry Form"]
            content_reqs = ["Service descriptions", "Company overview", "Testimonials", "Contact information"]
            design_reqs = ["Clean modern layout with balanced whitespace", "Accessible typography and high contrast"]
            tech_reqs = ["Semantic HTML5 markup", "Responsive CSS flexbox/grid", "Vanilla JavaScript interactivity"]
            constraints = ["Mobile responsiveness", "Fast loading times"]
            unknowns.extend(["Detailed content copy", "Brand identity assets"])

        if context and context.enabled and context.page_title:
            known_info.append(f"Webpage reference: {context.page_title} ({context.page_url or 'N/A'})")
            if context.selected_text:
                known_info.append(f"Selected reference text: {context.selected_text[:120]}...")

        return IntentData(
            project_type=project_type,
            business_domain=domain,
            primary_goal=primary_goal,
            target_users=target_users,
            core_functionality=core_func,
            content_requirements=content_reqs,
            design_requirements=design_reqs,
            technical_requirements=tech_reqs,
            constraints=constraints,
            known_information=known_info,
            unknown_information=unknowns,
        )

    def expand_requirements(
        self, intent: IntentData, prompt: str, context: Optional[WebpageContext] = None
    ) -> List[Requirement]:
        reqs: List[Requirement] = []
        text_lower = prompt.lower()

        # REQ-001: Core Hero & Brand Presentation
        reqs.append(
            Requirement(
                id="REQ-001",
                title="Hero Banner & Primary Value Proposition",
                description="Prominent hero section delivering clear brand messaging, motivational imagery, and immediate call-to-action buttons for getting started.",
                category=RequirementCategory.FUNCTIONAL.value,
                priority=RequirementPriority.HIGH.value,
                source=ContextSource.USER.value,
                confidence=1.0,
                dependencies=[],
                related_pages=["PAGE-001"],
                related_components=["COMP-001", "COMP-002"],
            )
        )

        # REQ-002: Catalog / Products / Membership
        is_sneaker = "sneaker" in text_lower or "shoe" in text_lower or "ecommerce" in text_lower or "store" in text_lower
        if is_sneaker:
            reqs.append(
                Requirement(
                    id="REQ-002",
                    title="Sneaker Catalog Grid & Dynamic Faceted Filters",
                    description="Interactive product catalog with category, brand, size, price-range filters, and real-time product card rendering with discount badges.",
                    category=RequirementCategory.FUNCTIONAL.value,
                    priority=RequirementPriority.HIGH.value,
                    source=ContextSource.USER.value,
                    confidence=1.0,
                    dependencies=["REQ-001"],
                    related_pages=["PAGE-001", "PAGE-002"],
                    related_components=["COMP-003", "COMP-004"],
                    related_apis=["API-001"],
                    related_entities=["DB-001"],
                )
            )
            reqs.append(
                Requirement(
                    id="REQ-003",
                    title="Product Detail View & Interactive Size Selector",
                    description="Detailed modal/drawer with multi-angle image gallery, dynamic shoe size picker (US 7-13), stock status alert, and Add to Cart trigger.",
                    category=RequirementCategory.FUNCTIONAL.value,
                    priority=RequirementPriority.HIGH.value,
                    source=ContextSource.MODEL_INFERRED.value,
                    confidence=0.95,
                    dependencies=["REQ-002"],
                    related_pages=["PAGE-002"],
                    related_components=["COMP-005"],
                    related_apis=["API-002"],
                    related_entities=["DB-001"],
                )
            )
            reqs.append(
                Requirement(
                    id="REQ-004",
                    title="Slide-Over Cart & Checkout Drawer",
                    description="Persistent slide-out cart drawer showing selected sneakers, quantity modifiers, item removal, subtotal calculation, and instant checkout button.",
                    category=RequirementCategory.FUNCTIONAL.value,
                    priority=RequirementPriority.HIGH.value,
                    source=ContextSource.MODEL_INFERRED.value,
                    confidence=0.90,
                    dependencies=["REQ-003"],
                    related_pages=["PAGE-001", "PAGE-002"],
                    related_components=["COMP-006", "COMP-007"],
                    related_apis=["API-003"],
                    related_entities=["DB-002"],
                )
            )
        else:
            reqs.append(
                Requirement(
                    id="REQ-002",
                    title="Tiered Membership Plans & Pricing Comparison",
                    description="Interactive comparison cards showcasing membership tiers (Basic, Pro, Elite), feature checklists, monthly/annual toggles, and direct signup buttons.",
                    category=RequirementCategory.FUNCTIONAL.value,
                    priority=RequirementPriority.HIGH.value,
                    source=ContextSource.USER.value if "membership" in text_lower else ContextSource.MODEL_INFERRED.value,
                    confidence=1.0 if "membership" in text_lower else 0.85,
                    dependencies=["REQ-001"],
                    related_pages=["PAGE-001", "PAGE-002"],
                    related_components=["COMP-003", "COMP-004"],
                    related_apis=["API-001"],
                    related_entities=["DB-001"],
                )
            )
            reqs.append(
                Requirement(
                    id="REQ-003",
                    title="Certified Trainer Profiles & Specialties",
                    description="Showcase professional trainer bio cards with photography, certifications, training philosophy, and consultation booking triggers.",
                    category=RequirementCategory.FUNCTIONAL.value,
                    priority=RequirementPriority.HIGH.value,
                    source=ContextSource.USER.value if "trainer" in text_lower else ContextSource.MODEL_INFERRED.value,
                    confidence=1.0 if "trainer" in text_lower else 0.85,
                    dependencies=["REQ-001"],
                    related_pages=["PAGE-001", "PAGE-003"],
                    related_components=["COMP-005"],
                    related_apis=["API-002"],
                    related_entities=["DB-002"],
                )
            )
            reqs.append(
                Requirement(
                    id="REQ-004",
                    title="Weekly Class Schedule & Interactive Filter",
                    description="Interactive timetable grid enabling users to filter classes by day, intensity level, and instructor with reservation buttons.",
                    category=RequirementCategory.FUNCTIONAL.value,
                    priority=RequirementPriority.HIGH.value,
                    source=ContextSource.USER.value if "class" in text_lower else ContextSource.MODEL_INFERRED.value,
                    confidence=1.0 if "class" in text_lower else 0.85,
                    dependencies=["REQ-003"],
                    related_pages=["PAGE-001", "PAGE-004"],
                    related_components=["COMP-006", "COMP-007"],
                    related_apis=["API-003"],
                    related_entities=["DB-003"],
                )
            )

        # REQ-005: Member Testimonials / Reviews
        reqs.append(
            Requirement(
                id="REQ-005",
                title="Customer Reviews & Social Proof Showcase",
                description="Verified client testimonials, star ratings, and review carousel displaying authentic feedback to build credibility and trust.",
                category=RequirementCategory.FUNCTIONAL.value,
                priority=RequirementPriority.MEDIUM.value,
                source=ContextSource.USER.value if "testimonial" in text_lower or "review" in text_lower else ContextSource.MODEL_INFERRED.value,
                confidence=1.0 if "testimonial" in text_lower else 0.80,
                dependencies=["REQ-001"],
                related_pages=["PAGE-001"],
                related_components=["COMP-008"],
            )
        )

        # REQ-006: Lead Capture / Contact Form
        reqs.append(
            Requirement(
                id="REQ-006",
                title="Inquiry & Contact Form with Client Validation",
                description="Validated inquiry/support form allowing users to submit messages or requests with immediate field error checking.",
                category=RequirementCategory.FUNCTIONAL.value,
                priority=RequirementPriority.HIGH.value,
                source=ContextSource.MODEL_INFERRED.value,
                confidence=0.90,
                dependencies=["REQ-001"],
                related_pages=["PAGE-001"],
                related_components=["COMP-009"],
                related_apis=["API-004"],
            )
        )

        # REQ-007: Mobile Navigation & Sticky Header
        reqs.append(
            Requirement(
                id="REQ-007",
                title="Sticky Navigation with Mobile Hamburger Menu",
                description="Responsive sticky header containing logo, smooth-scrolling section anchor links, and an accessible mobile slide-out drawer menu.",
                category=RequirementCategory.DESIGN.value,
                priority=RequirementPriority.MEDIUM.value,
                source=ContextSource.MODEL_INFERRED.value,
                confidence=0.95,
                dependencies=[],
                related_pages=["PAGE-001"],
                related_components=["COMP-010"],
            )
        )

        # REQ-008: Accessibility & WCAG Compliance
        reqs.append(
            Requirement(
                id="REQ-008",
                title="WCAG 2.1 AA Accessibility & Keyboard Navigation",
                description="Full keyboard focus management, visible outline rings, ARIA labels on dynamic toggles, and color contrast ratios exceeding 4.5:1.",
                category=RequirementCategory.ACCESSIBILITY.value,
                priority=RequirementPriority.HIGH.value,
                source=ContextSource.MODEL_INFERRED.value,
                confidence=0.95,
                dependencies=[],
                related_pages=["PAGE-001"],
                related_components=["COMP-001", "COMP-003", "COMP-009", "COMP-010"],
            )
        )

        # REQ-009: Input Validation & Security
        reqs.append(
            Requirement(
                id="REQ-009",
                title="Client-side Input Sanitization & Form Protection",
                description="Strict XSS sanitization, email format validation, and debounce protection against rapid form submissions.",
                category=RequirementCategory.SECURITY.value,
                priority=RequirementPriority.HIGH.value,
                source=ContextSource.MODEL_INFERRED.value,
                confidence=0.90,
                dependencies=["REQ-006"],
                related_pages=["PAGE-001"],
                related_components=["COMP-009"],
                related_apis=["API-004"],
            )
        )

        # REQ-010: Redundant Boilerplate (Used for demonstrating optimizer pruning)
        reqs.append(
            Requirement(
                id="REQ-010",
                title="General Aesthetic Filler & Verbose Description",
                description="General descriptive marketing boilerplate stating that the website should look good, feel nice to use, contain standard footer links, and follow generic web guidelines.",
                category=RequirementCategory.NON_FUNCTIONAL.value,
                priority=RequirementPriority.LOW.value,
                source=ContextSource.ASSUMPTION.value,
                confidence=0.50,
                dependencies=[],
                related_pages=["PAGE-001"],
                related_components=[],
            )
        )

        return reqs

    def generate_specification(
        self,
        intent: IntentData,
        requirements: List[Requirement],
        prompt: str,
        context: Optional[WebpageContext] = None,
    ) -> StructuredContext:
        pages = [
            PageSpec(
                id="PAGE-001",
                name="Home / Landing Page",
                path="/",
                purpose="Primary high-conversion landing page presenting all core services, featured items, and action triggers.",
                sections=["Hero", "Highlights", "Featured Collection / Pricing", "Showcase", "Testimonials", "Contact / Footer"],
                components=["COMP-001", "COMP-002", "COMP-003", "COMP-005", "COMP-006", "COMP-008", "COMP-009", "COMP-010"],
                requirements=["REQ-001", "REQ-002", "REQ-003", "REQ-004", "REQ-005", "REQ-006", "REQ-007", "REQ-008", "REQ-009"],
                source=ContextSource.MODEL_INFERRED.value,
            ),
            PageSpec(
                id="PAGE-002",
                name="Catalog / Details View",
                path="/catalog",
                purpose="Detailed catalog breakdown with category filters and interactive modal.",
                sections=["Header", "Faceted Filter Bar", "Product/Tier Grid", "Detail Drawer"],
                components=["COMP-003", "COMP-004", "COMP-005"],
                requirements=["REQ-002", "REQ-003", "REQ-008"],
                source=ContextSource.MODEL_INFERRED.value,
            ),
        ]

        components = [
            ComponentSpec(
                id="COMP-001",
                name="HeroSection",
                type="layout",
                description="Visual header featuring bold display title, supporting subtitle, background overlay, and primary/secondary CTA buttons.",
                props=["title", "subtitle", "ctaText", "secondaryCtaText"],
                state_items=[],
                requirements=["REQ-001"],
                source=ContextSource.MODEL_INFERRED.value,
            ),
            ComponentSpec(
                id="COMP-002",
                name="StatsCounter",
                type="display",
                description="Animated counter badges displaying key metrics.",
                props=["statsList"],
                state_items=["hasAnimated"],
                requirements=["REQ-001"],
                source=ContextSource.MODEL_INFERRED.value,
            ),
            ComponentSpec(
                id="COMP-003",
                name="CatalogGrid",
                type="container",
                description="Responsive container rendering item cards with category filter chips.",
                props=["items", "activeCategory"],
                state_items=["selectedFilter"],
                requirements=["REQ-002"],
                source=ContextSource.MODEL_INFERRED.value,
            ),
            ComponentSpec(
                id="COMP-004",
                name="ProductCard",
                type="card",
                description="Individual card highlighting badge, title, pricing, and action button.",
                props=["id", "title", "price", "image", "badge"],
                state_items=["isHovered"],
                requirements=["REQ-002"],
                source=ContextSource.MODEL_INFERRED.value,
            ),
            ComponentSpec(
                id="COMP-005",
                name="DetailModal",
                type="modal",
                description="Interactive modal displaying item specifications, image gallery, and action triggers.",
                props=["item", "isOpen", "onClose"],
                state_items=["selectedOption"],
                requirements=["REQ-003"],
                source=ContextSource.MODEL_INFERRED.value,
            ),
            ComponentSpec(
                id="COMP-006",
                name="ScheduleOrCartDrawer",
                type="drawer",
                description="Slide-out drawer managing scheduled items or selected cart orders.",
                props=["items", "isOpen", "onClose"],
                state_items=["totalCount"],
                requirements=["REQ-004"],
                source=ContextSource.MODEL_INFERRED.value,
            ),
            ComponentSpec(
                id="COMP-008",
                name="TestimonialSlider",
                type="slider",
                description="Accessible swipeable carousel rendering customer reviews, star ratings, and author names.",
                props=["reviews"],
                state_items=["currentIndex"],
                requirements=["REQ-005"],
                source=ContextSource.MODEL_INFERRED.value,
            ),
            ComponentSpec(
                id="COMP-009",
                name="InquiryForm",
                type="form",
                description="Validated contact form with inputs for name, email, and message.",
                props=["onSubmit"],
                state_items=["formData", "errors", "isSubmitting"],
                requirements=["REQ-006", "REQ-009"],
                source=ContextSource.MODEL_INFERRED.value,
            ),
            ComponentSpec(
                id="COMP-010",
                name="StickyNavBar",
                type="navigation",
                description="Sticky header with brand logo, desktop link list, and mobile hamburger drawer.",
                props=["navItems", "brandName"],
                state_items=["isMobileOpen", "activeSection"],
                requirements=["REQ-007", "REQ-008"],
                source=ContextSource.MODEL_INFERRED.value,
            ),
        ]

        apis = [
            APISpec(
                id="API-001",
                endpoint="/api/items",
                method="GET",
                description="Fetch available catalog items or membership tiers.",
                response_body='{"items": [{"id": "item1", "name": "Item A", "price": 99}]}',
                requirements=["REQ-002"],
                source=ContextSource.MODEL_INFERRED.value,
            ),
            APISpec(
                id="API-002",
                endpoint="/api/items/{id}",
                method="GET",
                description="Fetch item detail specifications and availability.",
                response_body='{"id": "item1", "description": "Full details"}',
                requirements=["REQ-003"],
                source=ContextSource.MODEL_INFERRED.value,
            ),
            APISpec(
                id="API-003",
                endpoint="/api/checkout",
                method="POST",
                description="Submit cart or schedule reservation.",
                request_body='{"items": [{"id": "item1", "qty": 1}]}',
                response_body='{"success": true, "orderId": "ORD-123"}',
                requirements=["REQ-004"],
                source=ContextSource.MODEL_INFERRED.value,
            ),
            APISpec(
                id="API-004",
                endpoint="/api/contact",
                method="POST",
                description="Submit inquiry or trial booking message.",
                request_body='{"name": "string", "email": "string", "message": "string"}',
                response_body='{"success": true}',
                requirements=["REQ-006", "REQ-009"],
                source=ContextSource.MODEL_INFERRED.value,
            ),
        ]

        database_entities = [
            DatabaseEntity(
                id="DB-001",
                name="ProductOrService",
                fields=[
                    {"name": "id", "type": "VARCHAR(36)", "constraint": "PRIMARY KEY"},
                    {"name": "name", "type": "VARCHAR(150)", "constraint": "NOT NULL"},
                    {"name": "price", "type": "DECIMAL(10,2)", "constraint": "NOT NULL"},
                    {"name": "category", "type": "VARCHAR(50)", "constraint": "NOT NULL"},
                ],
                relations=[],
                requirements=["REQ-002", "REQ-003"],
                source=ContextSource.MODEL_INFERRED.value,
            ),
            DatabaseEntity(
                id="DB-002",
                name="OrderOrReservation",
                fields=[
                    {"name": "id", "type": "VARCHAR(36)", "constraint": "PRIMARY KEY"},
                    {"name": "customer_email", "type": "VARCHAR(255)", "constraint": "NOT NULL"},
                    {"name": "total_amount", "type": "DECIMAL(10,2)", "constraint": "NOT NULL"},
                    {"name": "status", "type": "VARCHAR(50)", "constraint": "DEFAULT 'PENDING'"},
                ],
                relations=["ProductOrService"],
                requirements=["REQ-004"],
                source=ContextSource.MODEL_INFERRED.value,
            ),
        ]

        tasks = [
            TaskSpec(
                id="TASK-001",
                title="Initialize Semantic HTML5 & CSS Architecture",
                description="Set up layout structure with CSS custom properties, fluid typography, and dark/light token palette.",
                category="foundation",
                priority=RequirementPriority.HIGH.value,
                requirements=["REQ-001", "REQ-007", "REQ-008"],
                source=ContextSource.MODEL_INFERRED.value,
            ),
            TaskSpec(
                id="TASK-002",
                title="Implement Sticky Navigation & Mobile Menu Drawer",
                description="Build sticky navbar with scroll spy and focus-trapping mobile drawer.",
                category="frontend",
                priority=RequirementPriority.HIGH.value,
                requirements=["REQ-007", "REQ-008"],
                source=ContextSource.MODEL_INFERRED.value,
            ),
            TaskSpec(
                id="TASK-003",
                title="Build Dynamic Catalog Grid & Filters",
                description="Implement responsive catalog with interactive category pills and real-time DOM updates.",
                category="frontend",
                priority=RequirementPriority.HIGH.value,
                requirements=["REQ-002"],
                source=ContextSource.MODEL_INFERRED.value,
            ),
            TaskSpec(
                id="TASK-004",
                title="Implement Interactive Modal / Drawer",
                description="Build accessible modal with ESC keyboard listener and backdrop blur.",
                category="frontend",
                priority=RequirementPriority.HIGH.value,
                requirements=["REQ-003", "REQ-008"],
                source=ContextSource.MODEL_INFERRED.value,
            ),
            TaskSpec(
                id="TASK-005",
                title="Implement Contact Form & Validation",
                description="Create validated form with email regex checks and feedback states.",
                category="frontend",
                priority=RequirementPriority.HIGH.value,
                requirements=["REQ-006", "REQ-009"],
                source=ContextSource.MODEL_INFERRED.value,
            ),
        ]

        design = DesignSpec(
            visual_style="Modern, clean, aesthetic dark theme with vibrant energetic accents",
            layout="High-density responsive grid (12-column desktop, 1-column mobile)",
            color_direction="Deep Slate (#0F172A), Electric Accent (#3B82F6 / #10B981), Pure White (#FFFFFF)",
            typography="Headings: Space Grotesk / Inter Bold (700/800); Body: Inter (400/500)",
            spacing="8pt base grid: 8px, 16px, 24px, 32px, 48px, 64px",
            components="Elevated cards with subtle borders, filter chips, gradient accent buttons",
            responsive_behavior="Mobile-first (<640px stacked, >640px grid)",
            navigation="Sticky top navigation with backdrop-filter blur and mobile slide-over",
            interaction_patterns="Smooth scroll, active filter transitions, button scale on hover",
            cta_strategy="High-contrast primary buttons with clear action verbs",
            source=ContextSource.ASSUMPTION.value,
        )

        technical = TechnicalSpec(
            frontend="Semantic HTML5, Vanilla JavaScript (ES6+), Modern CSS3 (CSS Variables, Flexbox, Grid)",
            backend="FastAPI REST service (Simulated / Inferred)",
            api_style="RESTful JSON endpoints",
            database="Relational schema",
            authentication="Session / JWT token where applicable",
            authorization="Role-based access",
            security="Sanitized HTML outputs, form regex validation, HTTPS enforcement",
            performance="Lazy loaded images, zero heavy frontend frameworks, sub-1s First Contentful Paint",
            accessibility="WCAG 2.1 AA compliant, visible focus rings, ARIA expanded/controls attributes",
            seo="Semantic tags, OpenGraph meta tags, JSON-LD schema",
            deployment="Single-page static export with modular component structure",
            recommendations=[
                "Use vanilla ES6 modules to minimize bundle weight and maximize loading performance",
                "Ensure form submissions provide immediate visual feedback without reloading the page",
            ],
            source=ContextSource.MODEL_INFERRED.value,
        )

        constraints = [
            "Must be fully functional in modern evergreen web browsers (Chrome, Firefox, Safari, Edge)",
            "Mobile viewports (375px+) must display complete functionality without horizontal scrolling",
            "Zero commercial API key dependencies for core UI rendering",
        ]

        assumptions = [
            AssumptionItem(
                id="ASSUMP-001",
                text="Brand identity uses modern dark mode theme with neon/electric accents",
                rationale="Inferred modern design direction",
                source=ContextSource.ASSUMPTION.value,
            ),
            AssumptionItem(
                id="ASSUMP-002",
                text="Catalog items and pricing represent realistic starter inventory",
                rationale="Required for visual layout completion",
                source=ContextSource.ASSUMPTION.value,
            ),
        ]

        unknowns = [
            UnknownItem(
                id="UNK-001",
                text="Actual business legal name, physical address, and telephone number",
                impact="Placeholder text will be used until user provides actual business profile",
                source=ContextSource.UNKNOWN.value,
            ),
            UnknownItem(
                id="UNK-002",
                text="Production payment merchant credentials",
                impact="Simulated checkout / reservation stub used",
                source=ContextSource.UNKNOWN.value,
            ),
        ]

        decisions = [
            DecisionItem(
                id="DEC-001",
                decision="Use Vanilla JS for client-side state management instead of heavy frontend frameworks",
                rationale="Ensures instant load time and zero build step dependencies",
            )
        ]

        return StructuredContext(
            intent=intent,
            requirements=requirements,
            pages=pages,
            components=components,
            apis=apis,
            database_entities=database_entities,
            design=design,
            technical=technical,
            tasks=tasks,
            constraints=constraints,
            assumptions=assumptions,
            unknowns=unknowns,
            decisions=decisions,
        )

    def evaluate_context(
        self, ctx: StructuredContext, graph: DependencyGraphData
    ) -> Dict[str, ContextScores]:
        scores: Dict[str, ContextScores] = {}
        critical_nodes = set(graph.critical_path_node_ids)
        isolated_nodes = set(graph.isolated_node_ids)

        for req in ctx.requirements:
            is_critical = req.priority == RequirementPriority.HIGH.value or req.id in critical_nodes
            is_user = req.source == ContextSource.USER.value
            is_low = req.priority == RequirementPriority.LOW.value or req.category == RequirementCategory.NON_FUNCTIONAL.value

            if is_low and req.id in isolated_nodes:
                relevance = 0.30
                importance = 0.25
                redundancy = 0.85
                dep_score = 0.10
                conf = req.confidence
                prune = "PRUNE"
                reason = "Low-priority, isolated non-functional boilerplate with no active graph dependencies."
            elif is_critical:
                relevance = 0.98 if is_user else 0.92
                importance = 0.95
                redundancy = 0.05
                dep_score = 0.90
                conf = req.confidence
                prune = "KEEP"
                reason = "Critical functional requirement on core dependency path."
            else:
                relevance = 0.85
                importance = 0.75
                redundancy = 0.20
                dep_score = 0.65
                conf = req.confidence
                prune = "KEEP"
                reason = "Important supporting requirement providing functional value."

            scores[req.id] = ContextScores(
                id=req.id,
                relevance=relevance,
                importance=importance,
                redundancy=redundancy,
                dependency_score=dep_score,
                confidence=conf,
                prune_decision=prune,
                prune_reason=reason,
            )

        return scores
