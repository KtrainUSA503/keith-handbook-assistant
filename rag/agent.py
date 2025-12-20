# FILE: rag/agent.py
"""
Agentic RAG orchestration for KEITH Manufacturing Handbook.
PLAN → SEARCH → EVALUATE → ANSWER → SELF-CRITIQUE
"""

import json
import re
from typing import Optional, Callable, List, Dict
from openai import OpenAI

from .embeddings import get_single_embedding
from .pinecone_store import init_pinecone, query_similar
from .prompts import (
    PLANNER_SYSTEM_PROMPT,
    EVALUATOR_SYSTEM_PROMPT,
    ANSWER_SYSTEM_PROMPT,
    CRITIQUE_SYSTEM_PROMPT,
    format_chunks_for_prompt,
    format_chunks_for_evaluation
)

# Use GPT-4o for best results
OPENAI_CHAT_MODEL = "gpt-4o"
TOP_K_RESULTS = 5
MAX_AGENT_ITERATIONS = 2


def parse_json_response(response: str) -> Optional[Dict]:
    """Safely parse JSON from LLM response."""
    try:
        response = response.strip()
        if response.startswith("```json"):
            response = response[7:]
        if response.startswith("```"):
            response = response[3:]
        if response.endswith("```"):
            response = response[:-3]
        return json.loads(response.strip())
    except json.JSONDecodeError:
        match = re.search(r'\{.*\}', response, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except json.JSONDecodeError:
                pass
        return None


class AgenticRAG:
    """Agentic RAG system for KEITH Manufacturing Handbook Q&A."""
    
    def __init__(
        self,
        openai_api_key: str,
        pinecone_api_key: str,
        index_name: str,
        namespace: str,
        top_k: int = TOP_K_RESULTS,
        chat_model: str = OPENAI_CHAT_MODEL,
        status_callback: Optional[Callable[[str], None]] = None
    ):
        self.openai_api_key = openai_api_key
        self.pinecone_api_key = pinecone_api_key
        self.index_name = index_name
        self.namespace = namespace
        self.top_k = top_k
        self.chat_model = chat_model
        self.status_callback = status_callback
        
        self.openai_client = OpenAI(api_key=openai_api_key)
        init_pinecone(pinecone_api_key)
        
        self.reasoning_steps = []
    
    def _update_status(self, message: str):
        if self.status_callback:
            self.status_callback(message)
    
    def _add_reasoning(self, step: str, detail: str):
        self.reasoning_steps.append({
            "type": step.lower().replace(" ", "-"),
            "step": step,
            "description": detail
        })
    
    def _call_openai_chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.3,
        max_tokens: int = 2000
    ) -> str:
        response = self.openai_client.chat.completions.create(
            model=self.chat_model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        )
        return response.choices[0].message.content
    
    def _plan_search(self, question: str) -> Dict:
        self._add_reasoning("Planning", "Analyzing question to create search strategy...")
        
        messages = [
            {"role": "system", "content": "You are a planning agent. Respond only with valid JSON."},
            {"role": "user", "content": PLANNER_SYSTEM_PROMPT.format(question=question)}
        ]
        
        response = self._call_openai_chat(messages, temperature=0.2, max_tokens=500)
        plan = parse_json_response(response)
        
        if not plan:
            plan = {
                "question_type": "simple",
                "sub_questions": [question],
                "search_terms": question.split()[:5],
                "requires_calculation": False,
                "reasoning": "Using direct search"
            }
        
        self._add_reasoning("Plan Created", plan.get("reasoning", "Direct search"))
        return plan
    
    def _search(self, query: str) -> List[Dict]:
        self._add_reasoning("Searching", f"Query: '{query[:50]}...'")
        
        embedding = get_single_embedding(query, self.openai_api_key)
        results = query_similar(
            self.index_name,
            embedding,
            self.namespace,
            top_k=self.top_k,
            include_metadata=True
        )
        
        self._add_reasoning("Results", f"Found {len(results)} relevant sections")
        return results
    
    def _evaluate_results(self, question: str, results: List[Dict]) -> Dict:
        self._add_reasoning("Evaluating", "Checking if results are sufficient...")
        
        results_text = format_chunks_for_evaluation(results)
        
        messages = [
            {"role": "system", "content": "You evaluate search results. Respond only with valid JSON."},
            {"role": "user", "content": EVALUATOR_SYSTEM_PROMPT.format(
                question=question,
                results=results_text
            )}
        ]
        
        response = self._call_openai_chat(messages, temperature=0.2, max_tokens=300)
        evaluation = parse_json_response(response)
        
        if not evaluation:
            evaluation = {"sufficient": True, "confidence": 0.7, "missing_info": None}
        
        confidence = evaluation.get('confidence', 0)
        self._add_reasoning(
            "Evaluation", 
            f"Sufficient: {evaluation.get('sufficient')}, Confidence: {confidence:.0%}"
        )
        
        return evaluation
    
    def _generate_answer(self, question: str, context: List[Dict], reasoning: str) -> str:
        self._add_reasoning("Generating", "Creating comprehensive answer...")
        
        context_text = format_chunks_for_prompt(context)
        
        messages = [
            {"role": "system", "content": "You are an expert HR assistant for KEITH Manufacturing."},
            {"role": "user", "content": ANSWER_SYSTEM_PROMPT.format(
                reasoning=reasoning,
                context=context_text,
                question=question
            )}
        ]
        
        answer = self._call_openai_chat(messages, temperature=0.4, max_tokens=2000)
        return answer
    
    def _self_critique(self, question: str, context: List[Dict], answer: str) -> Dict:
        self._add_reasoning("Self-Critique", "Reviewing answer for accuracy...")
        
        context_text = "\n\n".join([
            f"[Page {c.get('page_number', '?')}] {c.get('text', '')[:300]}..." 
            for c in context[:3]
        ])
        
        messages = [
            {"role": "system", "content": "You review answers for accuracy. Respond only with valid JSON."},
            {"role": "user", "content": CRITIQUE_SYSTEM_PROMPT.format(
                question=question,
                context=context_text,
                answer=answer
            )}
        ]
        
        response = self._call_openai_chat(messages, temperature=0.2, max_tokens=400)
        critique = parse_json_response(response)
        
        if not critique:
            critique = {"final_verdict": "approve", "is_accurate": True, "is_complete": True}
        
        self._add_reasoning("Critique Result", critique.get("final_verdict", "approve"))
        return critique
    
    def answer(self, question: str) -> dict:
        """Main entry point: Answer a question using the agentic loop."""
        self.reasoning_steps = []
        all_results = []
        seen_ids = set()
        
        try:
            # Step 1: Plan
            self._update_status("🧠 Planning search strategy...")
            plan = self._plan_search(question)
            
            if plan.get("question_type") == "clarification_needed":
                return {
                    "answer": "I need more details to answer your question. Could you please be more specific about what you'd like to know from the handbook?",
                    "sources": [],
                    "reasoning_steps": self.reasoning_steps
                }
            
            # Step 2: Search
            search_queries = plan.get("sub_questions", [question])
            if not search_queries:
                search_queries = [question]
            
            for i, query in enumerate(search_queries[:3]):
                self._update_status(f"🔍 Searching ({i+1}/{len(search_queries[:3])})...")
                results = self._search(query)
                
                for r in results:
                    chunk_id = r.get("chunk_id", r.get("id", ""))
                    if chunk_id not in seen_ids:
                        seen_ids.add(chunk_id)
                        all_results.append(r)
            
            all_results.sort(key=lambda x: x.get('score', 0), reverse=True)
            top_results = all_results[:8]
            
            if not top_results:
                self._add_reasoning("Complete", "No relevant content found")
                return {
                    "answer": "I couldn't find relevant information in the KEITH Employee Handbook to answer your question. Please try rephrasing or contact HR at 541-475-3802 for assistance.",
                    "sources": [],
                    "reasoning_steps": self.reasoning_steps
                }
            
            # Step 3: Evaluate
            self._update_status("📊 Evaluating results...")
            evaluation = self._evaluate_results(question, top_results)
            
            # Step 4: Re-search if needed
            iteration = 0
            while (not evaluation.get("sufficient", True) and 
                   evaluation.get("suggested_search") and 
                   iteration < MAX_AGENT_ITERATIONS):
                
                iteration += 1
                self._update_status(f"🔄 Refining search (attempt {iteration})...")
                
                new_results = self._search(evaluation.get("suggested_search"))
                
                for r in new_results:
                    chunk_id = r.get("chunk_id", r.get("id", ""))
                    if chunk_id not in seen_ids:
                        seen_ids.add(chunk_id)
                        top_results.append(r)
                
                top_results.sort(key=lambda x: x.get('score', 0), reverse=True)
                top_results = top_results[:8]
                
                evaluation = self._evaluate_results(question, top_results)
            
            # Step 5: Generate answer
            self._update_status("✍️ Generating answer...")
            reasoning_summary = "\n".join([
                f"- {s['step']}: {s['description']}" 
                for s in self.reasoning_steps
            ])
            answer = self._generate_answer(question, top_results, reasoning_summary)
            
            # Step 6: Self-critique
            self._update_status("🔎 Reviewing answer...")
            critique = self._self_critique(question, top_results, answer)
            
            # Step 7: Revise if needed
            if critique.get("final_verdict") == "revise" and critique.get("improvements"):
                self._update_status("📝 Improving answer...")
                self._add_reasoning("Revision", critique.get("improvements", "Minor improvements"))
                
                enhanced_reasoning = reasoning_summary + f"\n- Improvement needed: {critique.get('improvements')}"
                answer = self._generate_answer(question, top_results, enhanced_reasoning)
            
            self._add_reasoning("Complete", "Answer ready")
            self._update_status("")
            
            sources = [
                {
                    "page_number": r.get("page_number", 0),
                    "section_title": r.get("section_title", "Unknown"),
                    "score": r.get("score", 0),
                    "chunk_id": r.get("chunk_id", r.get("id", ""))
                }
                for r in top_results[:5]
            ]
            
            return {
                "answer": answer,
                "sources": sources,
                "reasoning_steps": self.reasoning_steps
            }
            
        except Exception as e:
            self._add_reasoning("Error", str(e))
            self._update_status("")
            return {
                "answer": f"I encountered an error while processing your question: {str(e)}. Please try again or contact HR at 541-475-3802.",
                "sources": [],
                "reasoning_steps": self.reasoning_steps
            }
