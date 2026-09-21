from typing import Any, Dict, List
from .representation import Requirement, StructuredContext


class PromptBuilder:
    """Builds a high-density, minimum-sufficient generation prompt for external AI website generators."""

    def build_prompt(
        self,
        ctx: StructuredContext,
        optimized_context: Dict[str, Any],
        preserved_requirements: List[Requirement],
    ) -> str:
        lines: List[str] = []

        # 1. Header & Project Overview
        lines.append("=== AI WEBSITE GENERATION SPECIFICATION ===")
        lines.append(f"PROJECT: {ctx.intent.project_type or 'Modern Web Application'}")
        lines.append(f"DOMAIN: {ctx.intent.business_domain}")
        lines.append(f"OBJECTIVE: {ctx.intent.primary_goal}")
        lines.append("")

        # 2. Target Users
        if ctx.intent.target_users:
            lines.append("TARGET AUDIENCE:")
            for user in ctx.intent.target_users:
                lines.append(f"- {user}")
            lines.append("")

        # 3. Core Functional Requirements
        lines.append("CORE REQUIREMENTS:")
        for req in preserved_requirements:
            lines.append(
                f"- [{req.id}] ({req.priority}) {req.title}: {req.description}"
            )
        lines.append("")

        # 4. Site Structure & Pages
        if optimized_context.get("pages"):
            lines.append("SITE STRUCTURE & PAGES:")
            for page in optimized_context["pages"]:
                sections_str = ", ".join(page.get("sections", []))
                lines.append(
                    f"- {page.get('name')} ({page.get('path')}): Sections: [{sections_str}]"
                )
            lines.append("")

        # 5. Component Specifications
        if optimized_context.get("components"):
            lines.append("KEY UI COMPONENTS:")
            for comp in optimized_context["components"]:
                props_str = ", ".join(comp.get("props", []))
                lines.append(
                    f"- {comp.get('name')} ({comp.get('type')}): Props: [{props_str}]"
                )
            lines.append("")

        # 6. API & Data Contracts
        if optimized_context.get("apis"):
            lines.append("API SPECIFICATIONS:")
            for api in optimized_context["apis"]:
                lines.append(f"- {api.get('endpoint')}: {api.get('desc')}")
            lines.append("")

        if optimized_context.get("data_schema"):
            lines.append("DATA ENTITIES:")
            for ent in optimized_context["data_schema"]:
                fields_str = ", ".join(ent.get("fields", []))
                lines.append(f"- {ent.get('entity')}: [{fields_str}]")
            lines.append("")

        # 7. Design System
        design = optimized_context.get("design", {})
        lines.append("DESIGN SYSTEM:")
        lines.append(f"- Style: {design.get('style')}")
        lines.append(f"- Color Direction: {design.get('theme')}")
        lines.append(f"- Typography: {design.get('typography')}")
        lines.append(f"- Layout: {design.get('layout')}")
        lines.append(f"- Responsive: {design.get('responsive')}")
        lines.append(f"- Navigation: {design.get('nav')}")
        lines.append("")

        # 8. Technical & Quality Constraints
        tech = optimized_context.get("tech", {})
        lines.append("TECHNICAL & QUALITY CONSTRAINTS:")
        lines.append(f"- Stack: {tech.get('stack')}")
        lines.append(f"- Accessibility: {tech.get('accessibility')}")
        lines.append(f"- Security: {tech.get('security')}")
        for constraint in optimized_context.get("constraints", []):
            lines.append(f"- Constraint: {constraint}")
        lines.append("")

        # 9. Deliverable Output Requirements
        lines.append("OUTPUT REQUIREMENTS:")
        lines.append(
            "- Produce complete, valid, semantic HTML5, modern CSS3, and vanilla JavaScript."
        )
        lines.append(
            "- Implement all navigation anchors, interactive filters, modals, and form validations."
        )
        lines.append(
            "- Maintain clean modular code structure with inline documentation."
        )

        return "\n".join(lines)
