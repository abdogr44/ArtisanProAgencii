from agency_swarm.tools import BaseTool
from pydantic import Field
import os
import random

class BookKnowledgeTool(BaseTool):
    """
    Accesses the library of Athar's books to find quotes, passages, and inspiration.
    Use this tool to ground your writing in the authentic voice of the author.
    """
    
    query: str = Field(
        ...,
        description="Keyword or concept to search for (e.g., 'silence', 'pain', 'light'). If empty, returns a random passage."
    )
    
    def run(self) -> str:
        """
        Searches all text files in the 'knowledge' directory for the query.
        Returns relevant paragraphs or a random passage if no query provided.
        """
        knowledge_dir = os.path.join(os.path.dirname(__file__), "..", "knowledge")
        
        # Check if dir exists
        if not os.path.exists(knowledge_dir):
            return "Error: Knowledge directory not found."
            
        files = [f for f in os.listdir(knowledge_dir) if f.endswith('.txt')]
        if not files:
            return "Error: No book files found in the knowledge library."
            
        results = []
        
        # Simple search logic
        for filename in files:
            file_path = os.path.join(knowledge_dir, filename)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                    # Split into paragraphs (assuming double newline separator)
                    paragraphs = content.split('\n\n')
                    
                    if self.query:
                        # Find relevant paragraphs
                        for p in paragraphs:
                            if self.query.lower() in p.lower():
                                results.append(f"From '{filename}':\n{p.strip()}")
                    else:
                        # Collect all for random selection
                        results.extend([f"From '{filename}':\n{p.strip()}" for p in paragraphs if len(p.strip()) > 50])
                        
            except Exception as e:
                # Ignore read errors for now, or log them
                continue
                
        if not results:
            return f"No passages found for concept '{self.query}'. Try a related emotion or word."
            
        # Limit results to avoid context overflow
        if self.query:
            # Return top 3 matches
            return "\n\n---\n\n".join(results[:3])
        else:
            # Return 1 random passage
            return random.choice(results)

