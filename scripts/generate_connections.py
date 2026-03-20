"""
AI-powered connection analysis for syntax parameters.
Uses embeddings and NLP to discover relationships between parameters.
Supports both OpenAI and Claude (Anthropic) APIs.
"""

import re
import os
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    from anthropic import Anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False


@dataclass
class Connection:
    """Represents a connection between two parameters."""
    parameter: str
    type: str  # 'referenced_by', 'derives', 'conditional_dependency', 'similar_pattern'
    context: str
    strength: float  # 0.0 to 1.0


class ConnectionAnalyzer:
    """Analyzes and discovers connections between syntax parameters."""

    def __init__(self, config: Dict, openai_key: Optional[str] = None, anthropic_key: Optional[str] = None):
        """
        Initialize connection analyzer.

        Args:
            config: Configuration dict from codec_config.yaml
            openai_key: OpenAI API key (for embeddings)
            anthropic_key: Anthropic API key (for Claude analysis)
        """
        self.config = config
        self.ai_config = config.get('ai', {})
        self.connection_patterns = config.get('connection_patterns', {})

        # Initialize clients based on available keys
        self.openai_client = None
        self.anthropic_client = None

        if openai_key and OPENAI_AVAILABLE:
            self.openai_client = OpenAI(api_key=openai_key)
            print("✓ OpenAI client initialized (for embeddings)")

        if anthropic_key and ANTHROPIC_AVAILABLE:
            self.anthropic_client = Anthropic(api_key=anthropic_key)
            print("✓ Claude client initialized (for analysis)")

        if not self.openai_client and not self.anthropic_client:
            print("Warning: No API clients initialized. Connection analysis will be limited.")

        self.embeddings_cache = {}

    def analyze(self, syntax_structures: Dict, semantics: Dict) -> Dict[str, Dict]:
        """
        Analyze connections between all parameters.

        Args:
            syntax_structures: Dictionary of syntax structures
            semantics: Dictionary of semantic information

        Returns:
            Dictionary mapping parameter names to their connections
        """
        print("Generating embeddings for all parameters...")
        self._generate_embeddings(semantics)

        print("Analyzing explicit connections...")
        connections = {}

        for param_name in semantics.keys():
            connections[param_name] = {
                'references': [],
                'dependencies': [],
                'related_concepts': []
            }

            # Find explicit references
            references = self._find_explicit_references(
                param_name,
                semantics[param_name],
                semantics
            )
            connections[param_name]['references'] = references

            # Find dependencies from syntax
            dependencies = self._find_dependencies(
                param_name,
                syntax_structures,
                semantics
            )
            connections[param_name]['dependencies'] = dependencies

            # Find similar concepts using embeddings
            related = self._find_related_concepts(
                param_name,
                semantics
            )
            connections[param_name]['related_concepts'] = related

        print(f"Generated connections for {len(connections)} parameters")
        return connections

    def _generate_embeddings(self, semantics: Dict) -> None:
        """
        Generate embeddings for all parameter definitions using OpenAI.

        Args:
            semantics: Dictionary of semantic information
        """
        if not self.openai_client:
            print("Warning: OpenAI client not available. Skipping embeddings generation.")
            return

        model = self.ai_config.get('embedding_model', 'text-embedding-3-small')

        for param_name, info in semantics.items():
            # Create embedding text from definition
            text = f"{param_name}: {info.definition}"

            try:
                response = self.openai_client.embeddings.create(
                    model=model,
                    input=text
                )
                self.embeddings_cache[param_name] = np.array(
                    response.data[0].embedding
                )
            except Exception as e:
                print(f"Warning: Failed to generate embedding for {param_name}: {e}")
                continue

        print(f"Generated {len(self.embeddings_cache)} embeddings")

    def _analyze_with_claude(self, param_name: str, param_info, all_semantics: Dict) -> Dict:
        """
        Use Claude to analyze parameter relationships.

        Args:
            param_name: Name of the parameter
            param_info: SemanticInfo object
            all_semantics: All semantic information

        Returns:
            Dictionary of analyzed connections
        """
        if not self.anthropic_client:
            return {'references': [], 'dependencies': [], 'inferred': []}

        # Build prompt for Claude
        prompt = f"""Analyze the following video codec syntax parameter and identify its relationships with other parameters.

Parameter: {param_name}
Definition: {param_info.definition}

Other parameters in the specification:
{', '.join(list(all_semantics.keys())[:50])}  # Limit to first 50 for context

Please identify:
1. **Direct References**: Parameters that this parameter directly references or is referenced by
2. **Dependencies**: Parameters that this parameter depends on or that depend on it
3. **Related Concepts**: Parameters with similar purposes or naming patterns

For each relationship, provide:
- The parameter name
- The type of relationship (reference/dependency/related)
- A brief context explaining the relationship
- A confidence score (0.0 to 1.0)

Return your analysis in JSON format:
{{
  "references": [{{"parameter": "...", "context": "...", "strength": 0.95}}],
  "dependencies": [{{"parameter": "...", "context": "...", "strength": 0.90}}],
  "related": [{{"parameter": "...", "context": "...", "strength": 0.80}}]
}}"""

        try:
            response = self.anthropic_client.messages.create(
                model="claude-sonnet-4-5-20250929",
                max_tokens=2000,
                temperature=0.3,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )

            # Parse Claude's response
            import json
            response_text = response.content[0].text

            # Extract JSON from response (handle markdown code blocks)
            if '```json' in response_text:
                response_text = response_text.split('```json')[1].split('```')[0].strip()
            elif '```' in response_text:
                response_text = response_text.split('```')[1].split('```')[0].strip()

            analysis = json.loads(response_text)
            return analysis

        except Exception as e:
            print(f"Warning: Claude analysis failed for {param_name}: {e}")
            return {'references': [], 'dependencies': [], 'related': []}

    def _find_explicit_references(
        self,
        param_name: str,
        param_info,
        all_semantics: Dict
    ) -> List[Dict]:
        """
        Find explicit references in semantic text.

        Args:
            param_name: Name of the parameter
            param_info: SemanticInfo object
            all_semantics: All semantic information

        Returns:
            List of reference connections
        """
        references = []
        definition = param_info.definition.lower()

        reference_keywords = self.connection_patterns.get('reference_keywords', [])

        # Search for other parameters mentioned in definition
        for other_param in all_semantics.keys():
            if other_param == param_name:
                continue

            # Check if other parameter is mentioned
            if other_param.lower() in definition:
                # Determine connection type based on keywords
                conn_type = 'referenced_by'
                context = ""

                for keyword in reference_keywords:
                    if keyword in definition:
                        conn_type = 'referenced_by'
                        # Extract context around the reference
                        context = self._extract_context(
                            definition,
                            other_param.lower(),
                            keyword
                        )
                        break

                if not context:
                    context = f"{param_name} references {other_param}"

                # Calculate strength based on directness of reference
                strength = self._calculate_reference_strength(
                    definition,
                    other_param.lower(),
                    reference_keywords
                )

                references.append({
                    'parameter': other_param,
                    'type': conn_type,
                    'context': context,
                    'strength': strength
                })

        return references

    def _find_dependencies(
        self,
        param_name: str,
        syntax_structures: Dict,
        semantics: Dict
    ) -> List[Dict]:
        """
        Find dependencies based on syntax conditions.

        Args:
            param_name: Name of the parameter
            syntax_structures: Dictionary of syntax structures
            semantics: Dictionary of semantic information

        Returns:
            List of dependency connections
        """
        dependencies = []

        # Find where this parameter appears in syntax
        for struct_name, structure in syntax_structures.items():
            for param in structure.parameters:
                if param.name == param_name and param.condition:
                    # Extract parameters from condition
                    dependent_params = self._extract_params_from_condition(
                        param.condition,
                        semantics
                    )

                    for dep_param in dependent_params:
                        dependencies.append({
                            'parameter': dep_param,
                            'type': 'conditional_dependency',
                            'context': f"Present when {param.condition}",
                            'strength': 0.90
                        })

        # Also check semantic text for dependency keywords
        if param_name in semantics:
            definition = semantics[param_name].definition.lower()
            dependency_keywords = self.connection_patterns.get('dependency_keywords', [])

            for keyword in dependency_keywords:
                if keyword in definition:
                    # Extract what it depends on
                    for other_param in semantics.keys():
                        if other_param != param_name and other_param.lower() in definition:
                            context = self._extract_context(
                                definition,
                                other_param.lower(),
                                keyword
                            )
                            dependencies.append({
                                'parameter': other_param,
                                'type': 'derives',
                                'context': context,
                                'strength': 0.85
                            })

        return dependencies

    def _find_related_concepts(
        self,
        param_name: str,
        semantics: Dict
    ) -> List[Dict]:
        """
        Find semantically similar parameters using embeddings.

        Args:
            param_name: Name of the parameter
            semantics: Dictionary of semantic information

        Returns:
            List of related concept connections
        """
        if param_name not in self.embeddings_cache:
            return []

        param_embedding = self.embeddings_cache[param_name].reshape(1, -1)
        related = []

        similarity_threshold = self.ai_config.get('similarity_threshold', 0.75)

        for other_param, other_embedding in self.embeddings_cache.items():
            if other_param == param_name:
                continue

            # Calculate cosine similarity
            similarity = cosine_similarity(
                param_embedding,
                other_embedding.reshape(1, -1)
            )[0][0]

            if similarity >= similarity_threshold:
                # Determine context based on naming patterns
                context = self._infer_relationship_context(
                    param_name,
                    other_param,
                    semantics
                )

                related.append({
                    'parameter': other_param,
                    'type': 'similar_pattern',
                    'context': context,
                    'strength': float(similarity)
                })

        # Sort by strength and return top 5
        related.sort(key=lambda x: x['strength'], reverse=True)
        return related[:5]

    def _extract_params_from_condition(
        self,
        condition: str,
        semantics: Dict
    ) -> List[str]:
        """
        Extract parameter names from a condition string.

        Args:
            condition: Condition string (e.g., "sps_chroma_format_idc == 3")
            semantics: Dictionary of semantic information

        Returns:
            List of parameter names found
        """
        params = []
        condition_lower = condition.lower()

        for param_name in semantics.keys():
            if param_name.lower() in condition_lower:
                params.append(param_name)

        return params

    def _extract_context(
        self,
        text: str,
        target: str,
        keyword: str,
        window: int = 100
    ) -> str:
        """
        Extract context around a target word and keyword.

        Args:
            text: Full text
            target: Target parameter name
            keyword: Keyword to search for
            window: Character window size

        Returns:
            Context string
        """
        # Find position of target and keyword
        target_pos = text.find(target)
        if target_pos == -1:
            return ""

        # Extract surrounding text
        start = max(0, target_pos - window)
        end = min(len(text), target_pos + len(target) + window)

        context = text[start:end].strip()

        # Clean up
        context = ' '.join(context.split())

        return context if context else f"Related to {target}"

    def _calculate_reference_strength(
        self,
        text: str,
        target: str,
        keywords: List[str]
    ) -> float:
        """
        Calculate the strength of a reference.

        Args:
            text: Definition text
            target: Target parameter name
            keywords: List of reference keywords

        Returns:
            Strength score (0.0 to 1.0)
        """
        strength = 0.7  # Base strength

        # Increase if strong keywords present
        strong_keywords = ['shall be equal to', 'is set equal to', 'shall be']
        for kw in strong_keywords:
            if kw in text:
                strength += 0.15
                break

        # Increase if target appears multiple times
        count = text.count(target)
        if count > 1:
            strength += 0.05 * min(count - 1, 2)

        return min(strength, 0.98)

    def _infer_relationship_context(
        self,
        param1: str,
        param2: str,
        semantics: Dict
    ) -> str:
        """
        Infer relationship context between two parameters.

        Args:
            param1: First parameter name
            param2: Second parameter name
            semantics: Dictionary of semantic information

        Returns:
            Context description
        """
        # Check for naming patterns
        if self._has_similar_prefix(param1, param2):
            prefix = self._get_common_prefix(param1, param2)
            return f"Similar naming pattern: both use '{prefix}' prefix"

        if self._has_similar_suffix(param1, param2):
            suffix = self._get_common_suffix(param1, param2)
            return f"Similar naming pattern: both use '{suffix}' suffix"

        # Check semantic similarity
        if param1 in semantics and param2 in semantics:
            def1 = semantics[param1].definition.lower()
            def2 = semantics[param2].definition.lower()

            # Find common significant words
            words1 = set(re.findall(r'\b[a-z]{4,}\b', def1))
            words2 = set(re.findall(r'\b[a-z]{4,}\b', def2))
            common = words1 & words2

            if common:
                common_list = list(common)[:3]
                return f"Related concepts: {', '.join(common_list)}"

        return "Semantically similar parameters"

    def _has_similar_prefix(self, str1: str, str2: str, min_len: int = 3) -> bool:
        """Check if two strings share a common prefix."""
        prefix_len = 0
        for c1, c2 in zip(str1, str2):
            if c1 == c2:
                prefix_len += 1
            else:
                break
        return prefix_len >= min_len

    def _get_common_prefix(self, str1: str, str2: str) -> str:
        """Get common prefix of two strings."""
        prefix = []
        for c1, c2 in zip(str1, str2):
            if c1 == c2:
                prefix.append(c1)
            else:
                break
        return ''.join(prefix)

    def _has_similar_suffix(self, str1: str, str2: str, min_len: int = 5) -> bool:
        """Check if two strings share a common suffix."""
        suffix_len = 0
        for c1, c2 in zip(reversed(str1), reversed(str2)):
            if c1 == c2:
                suffix_len += 1
            else:
                break
        return suffix_len >= min_len

    def _get_common_suffix(self, str1: str, str2: str) -> str:
        """Get common suffix of two strings."""
        suffix = []
        for c1, c2 in zip(reversed(str1), reversed(str2)):
            if c1 == c2:
                suffix.append(c1)
            else:
                break
        return ''.join(reversed(suffix))
