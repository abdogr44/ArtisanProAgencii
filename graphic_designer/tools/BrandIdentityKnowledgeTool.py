import json
import os
from typing import Optional, Dict, Any
from agency_swarm.tools import BaseTool
from pydantic import Field


class BrandIdentityKnowledgeTool(BaseTool):
    """
    Provides expert-level brand identity knowledge from the certified knowledge pack.
    
    Use this tool to access strategic frameworks, principles, rules, and examples
    for brand strategy, color psychology, and typography systems.
    
    This tool is essential for Strategy Mode operations where brand knowledge
    should inform design decisions.
    """
    
    domain: str = Field(
        ...,
        description="Knowledge domain to query. Options: 'brand_strategy', 'color_theory', 'typography', 'evaluation_criteria', 'case_studies'"
    )
    
    query: Optional[str] = Field(
        None,
        description="Specific query within the domain (optional). Examples: 'strategic_pillars', 'palette_architecture', 'pairing_rules', 'emotional_color_mapping'"
    )
    
    def run(self) -> str:
        """
        Query the brand identity knowledge pack and return relevant expert knowledge.
        """
        try:
            # Load knowledge pack
            knowledge_path = os.path.join(
                os.path.dirname(__file__),
                "..",
                "knowledge",
                "brand_knowledge_pack.json"
            )
            
            with open(knowledge_path, 'r', encoding='utf-8') as f:
                knowledge_pack = json.load(f)
            
            # Handle case studies separately
            if self.domain == "case_studies":
                return self._get_case_studies()
            
            # Validate domain
            if self.domain not in knowledge_pack.get('domains', {}):
                available_domains = list(knowledge_pack.get('domains', {}).keys())
                available_domains.append('case_studies')
                return f"Error: Domain '{self.domain}' not found. Available domains: {', '.join(available_domains)}"
            
            domain_data = knowledge_pack['domains'][self.domain]
            
            # If no specific query, return domain overview
            if not self.query:
                return self._format_domain_overview(domain_data)
            
            # Search for specific query in domain
            result = self._search_domain(domain_data, self.query)
            
            if result:
                return self._format_result(result, self.query)
            else:
                return f"No specific information found for query '{self.query}' in domain '{self.domain}'. Returning domain overview:\n\n{self._format_domain_overview(domain_data)}"
        
        except FileNotFoundError:
            return "Error: Brand knowledge pack not found. Please ensure knowledge/brand_knowledge_pack.json exists."
        except json.JSONDecodeError:
            return "Error: Brand knowledge pack JSON is malformed."
        except Exception as e:
            return f"Error accessing knowledge pack: {str(e)}"
    
    def _get_case_studies(self) -> str:
        """Load and format case studies."""
        try:
            case_studies_path = os.path.join(
                os.path.dirname(__file__),
                "..",
                "knowledge",
                "examples",
                "case_studies.json"
            )
            
            with open(case_studies_path, 'r', encoding='utf-8') as f:
                case_data = json.load(f)
            
            output = "# Brand Identity Case Studies\n\n"
            
            for study in case_data.get('case_studies', []):
                output += f"## {study['brand']} ({study['industry']})\n\n"
                output += f"**Challenge**: {study['challenge']}\n\n"
                output += f"**Strategy**:\n"
                output += f"- Core Truth: {study['strategy']['core_truth']}\n"
                output += f"- Positioning: {study['strategy']['positioning']}\n"
                output += f"- Story Kernel: {study['strategy']['story_kernel']}\n\n"
                output += f"**Color Palette**: {study['color_palette']['primary_name']} (primary), "
                output += f"{', '.join(study['color_palette']['secondary_names'])} (secondary), "
                output += f"{study['color_palette']['accent_name']} (accent)\n\n"
                output += f"**Typography**: {study['typography']['primary']} + {study['typography']['secondary']}\n\n"
                output += f"**Rationale**: {study['color_palette']['rationale']}\n\n"
                output += "---\n\n"
            
            # Add anti-patterns
            if 'anti_patterns' in case_data:
                output += "## Common Anti-Patterns to Avoid\n\n"
                for pattern in case_data['anti_patterns']:
                    output += f"**{pattern['scenario']}**: {pattern['mistake']}\n"
                    output += f"- Why it fails: {pattern['why_it_fails']}\n"
                    output += f"- Lesson: {pattern['lesson']}\n\n"
            
            return output
            
        except Exception as e:
            return f"Error loading case studies: {str(e)}"
    
    def _format_domain_overview(self, domain_data: Dict[str, Any]) -> str:
        """Format domain overview for agent consumption."""
        overview = f"# {domain_data.get('title', 'Domain Overview')}\n\n"
        overview += f"{domain_data.get('description', '')}\n\n"
        
        if 'principles' in domain_data:
            overview += "## Key Principles:\n"
            for key in domain_data['principles'].keys():
                overview += f"- {key.replace('_', ' ').title()}\n"
            overview += "\n"
        
        if 'rules' in domain_data:
            overview += "## Rules:\n"
            for rule in domain_data['rules']:
                overview += f"- {rule}\n"
            overview += "\n"
        
        if 'strategic_questions' in domain_data:
            overview += "## Strategic Questions to Ask:\n"
            for question in domain_data['strategic_questions']:
                overview += f"- {question}\n"
            overview += "\n"
        
        if 'behavioral_standards' in domain_data:
            overview += "## Behavioral Standards:\n"
            for standard in domain_data['behavioral_standards']:
                overview += f"- {standard}\n"
            overview += "\n"
        
        return overview
    
    def _search_domain(self, domain_data: Dict[str, Any], query: str) -> Optional[Dict[str, Any]]:
        """Search for specific query within domain data."""
        query_lower = query.lower().replace(' ', '_')
        
        # Search in principles
        if 'principles' in domain_data:
            for key, value in domain_data['principles'].items():
                if query_lower in key.lower():
                    return {key: value}
        
        # Search in rules
        if 'rules' in domain_data and query_lower in 'rules':
            return {'rules': domain_data['rules']}
        
        return None
    
    def _format_result(self, result: Dict[str, Any], query: str) -> str:
        """Format search result for agent consumption."""
        output = f"# {query.replace('_', ' ').title()}\n\n"
        
        for key, value in result.items():
            if key != query.replace(' ', '_').lower():
                output += f"## {key.replace('_', ' ').title()}\n\n"
            output += self._format_value(value)
        
        return output
    
    def _format_value(self, value: Any, indent: int = 0) -> str:
        """Recursively format value for readable output."""
        indent_str = "  " * indent
        
        if isinstance(value, dict):
            output = ""
            for k, v in value.items():
                if isinstance(v, (dict, list)):
                    output += f"{indent_str}**{k.replace('_', ' ').title()}**:\n"
                    output += self._format_value(v, indent + 1)
                else:
                    output += f"{indent_str}**{k.replace('_', ' ').title()}**: {v}\n"
            return output
        elif isinstance(value, list):
            output = ""
            for item in value:
                if isinstance(item, dict):
                    output += f"{indent_str}- "
                    for k, v in item.items():
                        output += f"{k.replace('_', ' ').title()}: {v}, "
                    output = output.rstrip(', ') + "\n"
                else:
                    output += f"{indent_str}- {item}\n"
            return output
        else:
            return f"{indent_str}{value}\n\n"


if __name__ == "__main__":
    # Test the tool
    import sys
    import io
    
    # Set UTF-8 encoding for Windows console
    if sys.platform == 'win32':
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    
    print("=== Test 1: Brand Strategy Overview ===")
    tool1 = BrandIdentityKnowledgeTool(domain="brand_strategy")
    result1 = tool1.run()
    print(result1.encode('ascii', 'replace').decode('ascii') if sys.platform == 'win32' else result1)
    
    print("\n=== Test 2: Color Theory - Emotional Mapping ===")
    tool2 = BrandIdentityKnowledgeTool(domain="color_theory", query="emotional_color_mapping")
    result2 = tool2.run()
    print(result2.encode('ascii', 'replace').decode('ascii') if sys.platform == 'win32' else result2)
    
    print("\n=== Test 3: Typography - Pairing Rules ===")
    tool3 = BrandIdentityKnowledgeTool(domain="typography", query="pairing_rules")
    result3 = tool3.run()
    print(result3.encode('ascii', 'replace').decode('ascii') if sys.platform == 'win32' else result3)
    
    print("\n=== Test 4: Case Studies ===")
    tool4 = BrandIdentityKnowledgeTool(domain="case_studies")
    result4 = tool4.run()
    print(result4.encode('ascii', 'replace').decode('ascii') if sys.platform == 'win32' else result4)
