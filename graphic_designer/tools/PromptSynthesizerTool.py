from agency_swarm.tools import BaseTool
from pydantic import Field
import json
import os
from typing import Optional

class PromptSynthesizerTool(BaseTool):
    """
    Generates 3 style variant prompts (conservative, bold, minimal) from the creative brief.
    Produces Kie.ai-optimized prompts for each variant.
    
    Now supports explicit "Athar Signature" style which overrides variants with a specific strict aesthetic.
    """
    brief: str = Field(
        ..., description="Creative brief text generated from BriefGeneratorTool"
    )
    tone: str = Field(
        default="professional", description="Overall tone (e.g., 'professional', 'playful', 'urgent')"
    )
    platform: str = Field(
        default="instagram", description="Target platform: 'instagram', 'facebook', 'linkedin', etc."
    )
    use_brand_knowledge: bool = Field(
        default=False,
        description="If True, query BrandIdentityKnowledgeTool for expert principles to enhance prompts (Strategy Mode)"
    )
    brand_personality: Optional[str] = Field(
        None,
        description="Brand personality type (e.g., 'luxury', 'tech', 'wellness', 'creative') for strategic prompt enhancement"
    )
    use_athar_signature: bool = Field(
        default=False,
        description="If True, enforces the strict Athar Visual Constitution (Sacred Void, Abyssal Teal, Kintsugi Gold, etc.)."
    )
    
    def run(self):
        """
        Creates variant prompts optimized for Kie.ai image generation.
        Returns JSON with variants or a single 'athar_signature' variant if requested.
        """
        
        # ATHAR SIGNATURE LOGIC
        if self.use_athar_signature:
             return self._generate_athar_signature()
        
        # ... (Existing logic below) ...
        # Step 0: Get brand knowledge if requested (Strategy Mode)
        knowledge_context = {}
        if self.use_brand_knowledge:
            knowledge_context = self._get_brand_knowledge()
        
        # Step 1: Extract key themes from brief
        brief_lower = self.brief.lower()
        
        # Identify visual elements based on brief keywords
        has_people = any(word in brief_lower for word in ['people', 'person', 'entrepreneur', 'professional', 'customer'])
        has_product = any(word in brief_lower for word in ['product', 'app', 'tool', 'software', 'device'])
        has_abstract = any(word in brief_lower for word in ['concept', 'idea', 'innovation', 'growth', 'success'])
        
        # Step 2: Build base prompt elements
        platform_specs = {
            'instagram': 'optimized for Instagram feed, square format, centered composition',
            'facebook': 'optimized for Facebook posts, engaging thumbnail, clear focal point',
            'linkedin': 'professional LinkedIn post, business-appropriate, sophisticated',
            'twitter': 'Twitter/X post graphic, attention-grabbing, quick to understand',
            'pinterest': 'Pinterest pin, vertical format, visually striking'
        }
        platform_spec = platform_specs.get(self.platform.lower(), 'social media post, engaging composition')
        
        # Step 3: Create variant prompts
        prompts = {}
        
        # Conservative variant
        conservative_elements = [
            "Professional social media graphic",
            f"{platform_spec}",
            "Clean modern design",
            self._get_color_guidance('conservative', knowledge_context),
            "High quality commercial photography style" if has_people else "Polished vector illustration",
            "Minimal text overlay, plenty of white space",
            "Corporate aesthetic, trustworthy feel"
        ]
        if knowledge_context.get('typography'):
            conservative_elements.append(knowledge_context['typography'])
        prompts['conservative'] = ", ".join(conservative_elements) + f". Tone: {self.tone}, refined and approachable."
        
        # Bold variant
        bold_elements = [
            "Eye-catching social media graphic designed to stop scrolling",
            f"{platform_spec}",
            self._get_color_guidance('bold', knowledge_context),
            "Bold typography with modern sans-serif fonts",
            "Dynamic composition with diagonal lines and energy",
            "High contrast, cinematic look",
            "Trending style, Instagram-worthy aesthetic"
        ]
        if knowledge_context.get('typography'):
            bold_elements.append(knowledge_context['typography'])
        prompts['bold'] = ", ".join(bold_elements) + f". Tone: {self.tone}, energetic and compelling."
        
        # Minimal variant
        minimal_elements = [
            "Minimalist social media graphic with maximum impact",
            f"{platform_spec}",
            self._get_color_guidance('minimal', knowledge_context),
            "Generous negative space, breathing room",
            "Simple geometric shapes or single focal element",
            "Ultra-clean, Scandinavian design influence",
            "Modern and timeless aesthetic"
        ]
        if knowledge_context.get('typography'):
            minimal_elements.append(knowledge_context['typography'])
        prompts['minimal'] = ", ".join(minimal_elements) + f". Tone: {self.tone}, calm and sophisticated."
        
        # Step 4: Return all variants
        results = {
            'conservative': {
                'prompt': prompts['conservative'],
                'style_description': 'Professional, brand-safe, corporate-friendly',
                'recommended_for': 'LinkedIn, business audiences, conservative brands'
            },
            'bold': {
                'prompt': prompts['bold'],
                'style_description': 'Vibrant, attention-grabbing, trendy',
                'recommended_for': 'Instagram, young audiences, dynamic brands'
            },
            'minimal': {
                'prompt': prompts['minimal'],
                'style_description': 'Clean, modern, essential',
                'recommended_for': 'All platforms, tech brands, sophisticated audiences'
            },
            'metadata': {
                'original_brief': self.brief,
                'tone': self.tone,
                'platform': self.platform,
                'brand_knowledge_applied': self.use_brand_knowledge,
                'brand_personality': self.brand_personality if self.use_brand_knowledge else None
            }
        }
        
        return json.dumps(results, indent=2)
    
    def _generate_athar_signature(self):
        """Generate stricter Athar Signature prompt."""
        
        # Extract visual elements requested in valid brief
        brief_lower = self.brief.lower()
        symbol = "healing element"
        if "lavender" in brief_lower: symbol = "single lavender stem"
        elif "book" in brief_lower: symbol = "closed book with soft worn edges"
        elif "crystal" in brief_lower or "gemstone" in brief_lower: symbol = "single crystal (transparent gemstone)"
        elif "stone" in brief_lower: symbol = "smooth stone"
        
        prompt = (
            f"A T H A R S I G N A T U R E style: {symbol} centered in sacred void. "
            "60% soft negative space. "
            "Colors: Abyssal Teal ambient shadows, Kintsugi Gold highlights, Limestone Beige texture, Memory Lavender accents. "
            "Lighting: Soft celestial beam entering from a window slit, casting a quiet long shadow. "
            "Hyper-texture: Macro details, organic pores, soft leather/grain. "
            "Atmosphere: 'a breath in a silent room', contemplative serenity. "
            "Composition: Minimal, poetic, rule of thirds. "
            "No digital noise, no text, cinematic soft lensing."
        )
        
        results = {
            'athar_signature': {
                'prompt': prompt,
                'style_description': 'Athar Visual Constitution: Sacred Void, Abyssal Teal, Kintsugi Gold.',
                'image_input': [] # Placeholder for future visual anchors
            }
        }
        return json.dumps(results, indent=2)

    def _get_brand_knowledge(self) -> dict:
        """Query BrandIdentityKnowledgeTool for relevant principles."""
        try:
            from .BrandIdentityKnowledgeTool import BrandIdentityKnowledgeTool
            
            knowledge = {}
            
            # Query color theory for emotional mapping
            color_tool = BrandIdentityKnowledgeTool(domain="color_theory", query="emotional_color_mapping")
            color_result = color_tool.run()
            knowledge['color_mapping'] = color_result
            
            # Query typography if brand personality is specified
            if self.brand_personality:
                typo_tool = BrandIdentityKnowledgeTool(domain="typography", query="strategic_typeface_selection")
                typo_result = typo_tool.run()
                knowledge['typography'] = self._extract_typography_guidance(typo_result)
            
            return knowledge
        except Exception as e:
            # If knowledge pack fails, continue with standard prompts
            return {}
    
    def _extract_typography_guidance(self, typo_result: str) -> str:
        """Extract typography guidance based on brand personality."""
        if not self.brand_personality:
            return ""
        
        personality_lower = self.brand_personality.lower()
        
        # Map personality to typography style
        if 'luxury' in personality_lower or 'premium' in personality_lower:
            return "Elegant serif typography (transitional or didone style)"
        elif 'tech' in personality_lower or 'modern' in personality_lower:
            return "Clean geometric sans-serif or grotesk typography"
        elif 'wellness' in personality_lower or 'health' in personality_lower:
            return "Warm rounded sans-serif typography"
        elif 'creative' in personality_lower or 'bold' in personality_lower:
            return "Bold display typography with high contrast"
        else:
            return "Professional neo-grotesk typography"
    
    def _get_color_guidance(self, variant: str, knowledge_context: dict) -> str:
        """Get color guidance based on variant and brand knowledge."""
        if not knowledge_context or 'color_mapping' not in knowledge_context:
            # Fallback to standard color descriptions
            if variant == 'conservative':
                return "Subtle color palette with brand-safe tones"
            elif variant == 'bold':
                return "Vibrant saturated colors, dramatic lighting"
            else:  # minimal
                return "Flat design, limited color palette (2-3 colors max)"
        
        # Use brand personality to get strategic color guidance
        if self.brand_personality:
            personality_lower = self.brand_personality.lower()
            
            if 'luxury' in personality_lower or 'premium' in personality_lower:
                colors = "Black, gold, deep emerald, or burgundy tones (luxury palette)"
            elif 'tech' in personality_lower or 'innovation' in personality_lower:
                colors = "Electric blue, neon purple, or holographic gradients (innovation palette)"
            elif 'wellness' in personality_lower or 'health' in personality_lower:
                colors = "Sage green, mint, lavender, or soft pink (wellness palette)"
            elif 'creative' in personality_lower or 'bold' in personality_lower:
                colors = "Purple, magenta, vibrant pink, or coral (creativity palette)"
            elif 'trust' in personality_lower or 'corporate' in personality_lower:
                colors = "Blue, navy, or teal (trust palette)"
            else:
                colors = "Harmonious color palette aligned with brand personality"
            
            # Adjust for variant
            if variant == 'conservative':
                return f"Refined {colors}, subtle and professional"
            elif variant == 'bold':
                return f"Vibrant {colors}, saturated and energetic"
            else:  # minimal
                return f"Limited {colors}, 2-3 colors maximum, flat design"
        
        # Default fallback
        return self._get_color_guidance(variant, {})
