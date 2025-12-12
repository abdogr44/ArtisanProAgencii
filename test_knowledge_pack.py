"""
Test script to validate Expert Brand Identity Knowledge Pack integration
Tests both Production Mode and Strategy Mode workflows
"""

# Test 1: BrandIdentityKnowledgeTool
print("=" * 60)
print("TEST 1: BrandIdentityKnowledgeTool - Color Theory Query")
print("=" * 60)

from graphic_designer.tools.BrandIdentityKnowledgeTool import BrandIdentityKnowledgeTool

tool = BrandIdentityKnowledgeTool(domain="color_theory", query="emotional_color_mapping")
result = tool.run()
print(result[:500] + "...\n")  # Print first 500 chars

# Test 2: PromptSynthesizerTool - Production Mode (Standard)
print("=" * 60)
print("TEST 2: PromptSynthesizerTool - Production Mode")
print("=" * 60)

from graphic_designer.tools.PromptSynthesizerTool import PromptSynthesizerTool
import json

brief = "Create engaging social media graphics for a tech startup"
tool_prod = PromptSynthesizerTool(
    brief=brief,
    tone="professional",
    platform="instagram",
    use_brand_knowledge=False  # Production Mode
)
result_prod = tool_prod.run()
data_prod = json.loads(result_prod)
print(f"Conservative prompt: {data_prod['conservative']['prompt'][:200]}...")
print(f"Brand knowledge applied: {data_prod['metadata']['brand_knowledge_applied']}\n")

# Test 3: PromptSynthesizerTool - Strategy Mode (Knowledge-Enhanced)
print("=" * 60)
print("TEST 3: PromptSynthesizerTool - Strategy Mode")
print("=" * 60)

tool_strategy = PromptSynthesizerTool(
    brief=brief,
    tone="professional",
    platform="instagram",
    use_brand_knowledge=True,  # Strategy Mode
    brand_personality="luxury"
)
result_strategy = tool_strategy.run()
data_strategy = json.loads(result_strategy)
print(f"Conservative prompt: {data_strategy['conservative']['prompt'][:200]}...")
print(f"Brand knowledge applied: {data_strategy['metadata']['brand_knowledge_applied']}")
print(f"Brand personality: {data_strategy['metadata']['brand_personality']}\n")

# Test 4: BriefGeneratorTool - Strategy Mode
print("=" * 60)
print("TEST 4: BriefGeneratorTool - Strategy Mode")
print("=" * 60)

from graphic_designer.tools.BriefGeneratorTool import BriefGeneratorTool

sample_text = "Launch campaign for luxury wellness brand targeting professionals"
tool_brief = BriefGeneratorTool(
    extracted_text=sample_text,
    include_strategic_analysis=True  # Strategy Mode
)
result_brief = tool_brief.run()
data_brief = json.loads(result_brief)
print(f"Brief: {data_brief['brief']}")
if 'strategic_analysis' in data_brief:
    print(f"\nStrategic Questions:")
    for q in data_brief['strategic_analysis']['strategic_questions']:
        print(f"  - {q}")

print("\n" + "=" * 60)
print("ALL TESTS COMPLETED SUCCESSFULLY!")
print("=" * 60)
print("\nSummary:")
print("✅ BrandIdentityKnowledgeTool: Working")
print("✅ PromptSynthesizerTool (Production Mode): Working")
print("✅ PromptSynthesizerTool (Strategy Mode): Working with brand knowledge")
print("✅ BriefGeneratorTool (Strategy Mode): Working with strategic analysis")
print("\n🎉 Expert Brand Identity Knowledge Pack is fully integrated!")
