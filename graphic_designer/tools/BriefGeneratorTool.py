from agency_swarm.tools import BaseTool
from pydantic import Field
import json

class BriefGeneratorTool(BaseTool):
    """
    Synthesizes a creative brief from extracted document content.
    Generates a 2-3 sentence brief identifying audience, tone, CTA, and imagery needs.
    """
    extracted_text: str = Field(
        ..., description="Full text extracted from uploaded documents (DOCX/PDF)"
    )
    user_prompt: str = Field(
        default="", description="Optional additional context or instructions from the user"
    )
    include_strategic_analysis: bool = Field(
        default=False,
        description="If True, include expert-level strategic analysis (brand personality, positioning, differentiation) - Strategy Mode"
    )
    
    def run(self):
        """
        Analyzes extracted text and generates a structured creative brief.
        Returns a JSON string with the brief and key insights.
        """
        # Step 1: Analyze text content
        text = self.extracted_text.strip()
        if not text:
            return json.dumps({
                'brief': 'No content provided - create engaging social media graphics',
                'audience': 'general social media users',
                'tone': 'professional and engaging',
                'cta': 'engage with content',
                'imagery_needs': 'modern, clean visuals'
            }, indent=2)
        
        # Step 2: Extract key phrases and sentiment indicators
        text_lower = text.lower()
        
        # Identify audience hints
        audience = 'general audience'
        audience_keywords = {
            'professional': 'professionals and business users',
            'customer': 'customers and prospects',
            'entrepreneur': 'entrepreneurs and startups',
            'marketer': 'marketers and content creators',
            'student': 'students and learners',
            'developer': 'developers and technical users'
        }
        for keyword, aud in audience_keywords.items():
            if keyword in text_lower:
                audience = aud
                break
        
        # Identify tone
        tone = 'professional'
        tone_keywords = {
            'exciting': 'bold and exciting',
            'fun': 'playful and fun',
            'professional': 'professional and polished',
            'urgent': 'urgent and compelling',
            'innovative': 'innovative and cutting-edge',
            'friendly': 'warm and approachable'
        }
        for keyword, t in tone_keywords.items():
            if keyword in text_lower:
                tone = t
                break
        
        # Identify CTA hints
        cta = 'engage with content'
        cta_keywords = {
            'buy': 'purchase or sign up',
            'sign up': 'sign up or register',
            'learn': 'learn more or explore',
            'download': 'download or access',
            'join': 'join or participate',
            'share': 'share or spread the word',
            'register': 'register or attend'
        }
        for keyword, c in cta_keywords.items():
            if keyword in text_lower:
                cta = c
                break
        
        # Identify imagery needs
        imagery = 'modern, professional visuals'
        imagery_keywords = {
            'product': 'product photography and mockups',
            'people': 'people and human connection',
            'technology': 'technology and innovation',
            'nature': 'natural and organic elements',
            'minimal': 'minimal and clean design',
            'colorful': 'vibrant and colorful graphics'
        }
        for keyword, img in imagery_keywords.items():
            if keyword in text_lower:
                imagery = img
                break
        
        # Step 3: Generate brief
        brief_parts = []
        brief_parts.append(f"Create engaging social media graphics targeting {audience}.")
        brief_parts.append(f"Use a {tone} tone to communicate the message effectively.")
        if self.user_prompt:
            brief_parts.append(f"Additional context: {self.user_prompt}")
        brief_parts.append(f"Primary goal is to encourage viewers to {cta}.")
        
        brief = ' '.join(brief_parts)
        
        # Step 4: Build results dictionary
        results = {
            'brief': brief,
            'audience': audience,
            'tone': tone,
            'cta': cta,
            'imagery_needs': imagery,
            'content_length': len(text),
            'has_user_context': bool(self.user_prompt)
        }
        
        # Step 5: Add strategic analysis if requested (Strategy Mode)
        if self.include_strategic_analysis:
            strategic_analysis = self._generate_strategic_analysis()
            results['strategic_analysis'] = strategic_analysis
        
        return json.dumps(results, indent=2)
    
    def _generate_strategic_analysis(self) -> dict:
        """Generate expert-level strategic analysis using BrandIdentityKnowledgeTool."""
        try:
            from .BrandIdentityKnowledgeTool import BrandIdentityKnowledgeTool
            
            # Query brand strategy knowledge
            strategy_tool = BrandIdentityKnowledgeTool(domain="brand_strategy")
            strategy_knowledge = strategy_tool.run()
            
            # Extract strategic questions
            strategic_questions = [
                "What problem is this brand solving?",
                "What emotion should the audience feel?",
                "What differentiates this identity from competitors?"
            ]
            
            analysis = {
                'strategic_questions': strategic_questions,
                'recommended_approach': 'Apply brand strategy principles before visual development',
                'behavioral_standards': [
                    'Always ask strategic questions before designing',
                    'Always justify design decisions with strategic reasoning',
                    'Always follow: Strategy → Concept → Execution'
                ],
                'knowledge_reference': 'BrandIdentityKnowledgeTool queried for strategic frameworks'
            }
            
            return analysis
        except Exception as e:
            return {
                'error': f'Strategic analysis unavailable: {str(e)}',
                'fallback': 'Proceed with standard creative brief'
            }

if __name__ == "__main__":
    # Test case: Generate brief from sample text
    sample_text = """
    Our new productivity app helps busy entrepreneurs manage their time more effectively.
    Join thousands of professionals who have already transformed their workflow.
    Download now and get started with a 14-day free trial.
    """
    
    tool = BriefGeneratorTool(
        extracted_text=sample_text,
        user_prompt="Launch campaign for app release"
    )
    result = tool.run()
    print(result)
