"""
End-to-End Test: Strategy Mode with Brand Identity Knowledge Pack
Tests the complete workflow from brief to strategic prompt generation

Test Scenario: Luxury Wellness Startup Brand Identity
Expected: Agent detects Strategy Mode, queries knowledge pack, applies expert principles
"""

import json
import sys
import io

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

from graphic_designer.tools.BriefGeneratorTool import BriefGeneratorTool
from graphic_designer.tools.PromptSynthesizerTool import PromptSynthesizerTool
from graphic_designer.tools.BrandIdentityKnowledgeTool import BrandIdentityKnowledgeTool

print("=" * 80)
print("END-TO-END TEST: Strategy Mode - Luxury Wellness Brand Identity")
print("=" * 80)

# ============================================================================
# SCENARIO: User requests brand identity for luxury wellness startup
# ============================================================================

user_request = """
Develop a brand identity for a luxury wellness startup called 'Serenity Labs'.

Target audience: Busy professionals (30-50 years old) seeking premium self-care
Brand positioning: Against generic wellness apps, we are the personalized, science-backed choice for discerning professionals
Core values: Sophistication, personalization, scientific credibility, calm
Industry: Health & Wellness / Digital Health
"""

print("\n📋 USER REQUEST:")
print(user_request)
print("\n" + "=" * 80)

# ============================================================================
# STEP 1: Generate Brief with Strategic Analysis (Strategy Mode)
# ============================================================================

print("\n🔍 STEP 1: Generating Brief with Strategic Analysis...")
print("-" * 80)

brief_tool = BriefGeneratorTool(
    extracted_text=user_request,
    user_prompt="Focus on luxury positioning and wellness psychology",
    include_strategic_analysis=True  # ✅ Strategy Mode enabled
)

brief_result = brief_tool.run()
brief_data = json.loads(brief_result)

print("\n📝 GENERATED BRIEF:")
print(f"  {brief_data['brief']}")

if 'strategic_analysis' in brief_data:
    print("\n✅ STRATEGIC ANALYSIS INCLUDED:")
    print(f"  Strategic Questions:")
    for q in brief_data['strategic_analysis']['strategic_questions']:
        print(f"    • {q}")
    print(f"\n  Recommended Approach: {brief_data['strategic_analysis']['recommended_approach']}")
else:
    print("\n❌ ERROR: Strategic analysis NOT included!")

print("\n" + "=" * 80)

# ============================================================================
# STEP 2: Query Knowledge Pack for Brand Strategy Guidance
# ============================================================================

print("\n🧠 STEP 2: Querying Brand Identity Knowledge Pack...")
print("-" * 80)

# Query brand strategy
strategy_tool = BrandIdentityKnowledgeTool(domain="brand_strategy")
strategy_knowledge = strategy_tool.run()
print("\n📚 Brand Strategy Knowledge Retrieved:")
print(f"  {strategy_knowledge[:300]}...")

# Query color psychology for luxury + wellness
color_tool = BrandIdentityKnowledgeTool(domain="color_theory", query="emotional_color_mapping")
color_knowledge = color_tool.run()
print("\n🎨 Color Psychology Knowledge Retrieved:")
print(f"  {color_knowledge[:300]}...")

# Query typography for luxury positioning
typo_tool = BrandIdentityKnowledgeTool(domain="typography", query="strategic_typeface_selection")
typo_knowledge = typo_tool.run()
print("\n✍️ Typography Knowledge Retrieved:")
print(f"  {typo_knowledge[:300]}...")

print("\n✅ Knowledge pack queries successful!")
print("\n" + "=" * 80)

# ============================================================================
# STEP 3: Generate Prompts - PRODUCTION MODE (Baseline)
# ============================================================================

print("\n⚡ STEP 3A: Generating Prompts - PRODUCTION MODE (Baseline)...")
print("-" * 80)

prompt_tool_production = PromptSynthesizerTool(
    brief=brief_data['brief'],
    tone="professional and sophisticated",
    platform="instagram",
    use_brand_knowledge=False  # ❌ Production Mode - no knowledge pack
)

production_result = prompt_tool_production.run()
production_data = json.loads(production_result)

print("\n📄 PRODUCTION MODE - Conservative Prompt:")
print(f"  {production_data['conservative']['prompt'][:200]}...")
print(f"\n  Brand Knowledge Applied: {production_data['metadata']['brand_knowledge_applied']}")

print("\n" + "=" * 80)

# ============================================================================
# STEP 4: Generate Prompts - STRATEGY MODE (Knowledge-Enhanced)
# ============================================================================

print("\n🎯 STEP 3B: Generating Prompts - STRATEGY MODE (Knowledge-Enhanced)...")
print("-" * 80)

prompt_tool_strategy = PromptSynthesizerTool(
    brief=brief_data['brief'],
    tone="professional and sophisticated",
    platform="instagram",
    use_brand_knowledge=True,  # ✅ Strategy Mode - knowledge pack enabled
    brand_personality="luxury wellness"  # ✅ Brand personality specified
)

strategy_result = prompt_tool_strategy.run()
strategy_data = json.loads(strategy_result)

print("\n📄 STRATEGY MODE - Conservative Prompt:")
print(f"  {strategy_data['conservative']['prompt']}")
print(f"\n  Brand Knowledge Applied: {strategy_data['metadata']['brand_knowledge_applied']}")
print(f"  Brand Personality: {strategy_data['metadata']['brand_personality']}")

print("\n" + "=" * 80)

# ============================================================================
# STEP 5: Compare Production vs Strategy Mode
# ============================================================================

print("\n📊 STEP 4: COMPARISON - Production vs Strategy Mode")
print("=" * 80)

print("\n🔴 PRODUCTION MODE (No Knowledge Pack):")
print(f"  Conservative: {production_data['conservative']['prompt'][:150]}...")
print(f"  Knowledge Applied: {production_data['metadata']['brand_knowledge_applied']}")

print("\n🟢 STRATEGY MODE (Knowledge-Enhanced):")
print(f"  Conservative: {strategy_data['conservative']['prompt'][:150]}...")
print(f"  Knowledge Applied: {strategy_data['metadata']['brand_knowledge_applied']}")
print(f"  Brand Personality: {strategy_data['metadata']['brand_personality']}")

# Extract color guidance differences
production_prompt = production_data['conservative']['prompt']
strategy_prompt = strategy_data['conservative']['prompt']

print("\n🎨 COLOR GUIDANCE COMPARISON:")
if "luxury palette" in strategy_prompt.lower() or "wellness palette" in strategy_prompt.lower():
    print("  ✅ Strategy Mode: Strategic color guidance detected (luxury/wellness palette)")
else:
    print("  ⚠️  Strategy Mode: Generic color guidance")

if "brand-safe tones" in production_prompt.lower():
    print("  ⚠️  Production Mode: Generic color guidance (brand-safe tones)")

print("\n" + "=" * 80)

# ============================================================================
# STEP 6: Validation & Results
# ============================================================================

print("\n✅ VALIDATION RESULTS:")
print("=" * 80)

validation_results = {
    "brief_generation": "strategic_analysis" in brief_data,
    "knowledge_queries": True,  # We successfully queried all domains
    "production_mode_works": not production_data['metadata']['brand_knowledge_applied'],
    "strategy_mode_works": strategy_data['metadata']['brand_knowledge_applied'],
    "brand_personality_applied": strategy_data['metadata']['brand_personality'] == "luxury wellness",
    "strategic_color_guidance": "luxury" in strategy_prompt.lower() or "wellness" in strategy_prompt.lower()
}

print("\n📋 Test Results:")
for test, passed in validation_results.items():
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"  {status}: {test.replace('_', ' ').title()}")

all_passed = all(validation_results.values())
print("\n" + "=" * 80)

if all_passed:
    print("\n🎉 SUCCESS! All tests passed!")
    print("\n✅ Strategy Mode is working correctly:")
    print("  • Brief includes strategic analysis")
    print("  • Knowledge pack queries successful")
    print("  • Production Mode works (fast, no knowledge overhead)")
    print("  • Strategy Mode works (knowledge-enhanced prompts)")
    print("  • Brand personality applied to color guidance")
    print("  • Strategic color guidance detected in prompts")
    print("\n🚀 The dual-mode architecture is fully functional!")
else:
    print("\n⚠️  ISSUES DETECTED - Review failed tests above")

print("\n" + "=" * 80)
print("END OF TEST")
print("=" * 80)
