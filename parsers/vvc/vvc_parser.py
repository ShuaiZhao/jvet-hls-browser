"""
VVC/H.266 specification parser.
Extracts syntax structures and semantics from Section 7.3 and 7.4.
"""

import re
from typing import Dict, List
from ..base_parser import (
    BaseSpecParser,
    SyntaxStructure,
    SyntaxParameter,
    SemanticInfo
)


class VVCParser(BaseSpecParser):
    """Parser for VVC/H.266 specification documents."""

    def __init__(self, config: Dict):
        super().__init__(config)
        self.current_section = None

    def extract_syntax_structures(self) -> Dict[str, SyntaxStructure]:
        """
        Extract all syntax structures from Section 7.3 subsections.

        VVC Section 7.3 contains syntax in both tables and code blocks across
        multiple subsections (7.3.2, 7.3.4, 7.3.5, ... 7.3.11).
        This method handles both formats.
        """
        syntax_structures = {}

        # Get subsections to search from config
        subsections = self.config.get('syntax_subsections', ['7.3.2'])

        print(f"Searching syntax in subsections: {', '.join(subsections)}")

        # Process each subsection
        for subsection in subsections:
            print(f"  Processing {subsection}...")
            section_paragraphs = self.find_section(subsection)
            print(f"    Found {len(section_paragraphs)} paragraphs")

            structures = self._extract_from_section(section_paragraphs, subsection)
            syntax_structures.update(structures)
            print(f"    Extracted {len(structures)} structures")

        return syntax_structures

    def _extract_from_section(self, section_paragraphs: List, subsection: str) -> Dict[str, SyntaxStructure]:
        """Extract syntax structures from a specific subsection."""
        syntax_structures = {}

        # Track current subsection for context
        current_subsection = subsection
        current_text_block = []
        in_code_block = False

        for para in section_paragraphs:
            text = para.text.strip()

            # Update current subsection header if we find a more specific one
            if re.match(r'^7\.3\.\d+\.\d+\s+', text):
                current_subsection = text
                continue

            # Skip if it's just a section header
            if text == subsection or text.startswith(subsection + ' '):
                continue

            # Detect code blocks (usually in monospace or specific style)
            # VVC spec uses specific paragraph styles for syntax
            if self._is_syntax_block(para):
                in_code_block = True
                current_text_block.append(text)
            elif in_code_block:
                if text and not text.startswith('7.'):
                    current_text_block.append(text)
                else:
                    # End of code block - process it
                    if current_text_block:
                        structure = self._parse_syntax_block(
                            '\n'.join(current_text_block),
                            current_subsection
                        )
                        if structure:
                            syntax_structures[structure.name] = structure
                    current_text_block = []
                    in_code_block = False

        # Process any remaining code block
        if current_text_block:
            structure = self._parse_syntax_block(
                '\n'.join(current_text_block),
                current_subsection
            )
            if structure:
                syntax_structures[structure.name] = structure

            # Also extract from tables in this subsection
            tables_structures = self._extract_from_tables(subsection)
            syntax_structures.update(tables_structures)

        return syntax_structures

    def _is_syntax_block(self, para) -> bool:
        """
        Determine if a paragraph is part of a syntax code block.

        Args:
            para: Paragraph object

        Returns:
            True if it's a syntax block
        """
        text = para.text.strip()

        # Check for syntax structure pattern
        if re.search(r'\w+\s*\(\s*\)\s*\{', text):
            return True

        # Check for parameter patterns
        if re.search(r'\w+\s+(ue\(v\)|u\(\d+\)|se\(v\)|i\(\d+\)|f\(\d+\))', text):
            return True

        # Check paragraph style (if monospace/code style)
        if para.style and 'code' in para.style.name.lower():
            return True

        return False

    def _parse_syntax_block(self, text: str, section_header: str) -> SyntaxStructure:
        """
        Parse a syntax structure from text block.

        Args:
            text: Code block text
            section_header: Section header for context

        Returns:
            SyntaxStructure object or None
        """
        structure = self.extract_syntax_from_text(text)

        if structure:
            # Extract section number from header
            section_match = re.search(r'(7\.3\.\d+(?:\.\d+)?)', section_header)
            if section_match:
                structure.section = section_match.group(1)

            # Extract descriptor from header
            descriptor_match = re.search(r'7\.3\.\d+(?:\.\d+)?\s+(.+)', section_header)
            if descriptor_match:
                structure.descriptor = descriptor_match.group(1).strip()

            # Set semantics reference (7.3.x.x -> 7.4.x.x)
            semantics_section = structure.section.replace('7.3', '7.4')
            for param in structure.parameters:
                param.semantics_ref = semantics_section

        return structure

    def _extract_from_tables(self, subsection: str) -> Dict[str, SyntaxStructure]:
        """
        Extract syntax structures from tables in a specific subsection.

        Some VVC syntax is presented in table format.
        """
        structures = {}
        tables = self.find_tables_in_section(subsection)

        for table, context in tables:
            structure = self._parse_syntax_table(table, context)
            if structure:
                structures[structure.name] = structure

        return structures

    def _parse_syntax_table(self, table, context: str) -> SyntaxStructure:
        """
        Parse syntax structure from a table.

        Args:
            table: Table object
            context: Section header context

        Returns:
            SyntaxStructure object or None
        """
        # Extract structure name from context
        name_match = re.search(r'(\w+)\s*\(\s*\)', context)
        if not name_match:
            return None

        structure_name = name_match.group(1)
        parameters = []

        # Parse table rows (skip header)
        for i, row in enumerate(table.rows):
            if i == 0:  # Skip header row
                continue

            cells = [cell.text.strip() for cell in row.cells]

            if len(cells) >= 2:
                param_name = cells[0]
                param_type = cells[1]

                # Extract condition if present
                condition = cells[2] if len(cells) > 2 and cells[2] else None

                # Only add if it looks like a valid parameter
                if param_name and param_type and not param_name.startswith('7.'):
                    parameters.append(SyntaxParameter(
                        name=param_name,
                        type=param_type,
                        condition=condition
                    ))

        if not parameters:
            return None

        # Extract section number
        section_match = re.search(r'(7\.3\.\d+(?:\.\d+)?)', context)
        section = section_match.group(1) if section_match else ""

        # Extract descriptor
        descriptor_match = re.search(r'7\.3\.\d+(?:\.\d+)?\s+(.+)', context)
        descriptor = descriptor_match.group(1).strip() if descriptor_match else ""

        # Set semantics reference
        semantics_section = section.replace('7.3', '7.4')
        for param in parameters:
            param.semantics_ref = semantics_section

        return SyntaxStructure(
            id=structure_name,
            section=section,
            name=structure_name,
            descriptor=descriptor,
            parameters=parameters
        )

    def extract_semantics(self) -> Dict[str, SemanticInfo]:
        """
        Extract semantic information from Section 7.4.

        VVC Section 7.4 contains semantic definitions for all syntax elements.
        """
        semantics = {}

        # Get all paragraphs in Section 7.4
        section_paragraphs = self.find_section(self.config['semantics_section'])

        current_subsection = ""
        current_parameter = None
        current_definition = []

        for para in section_paragraphs:
            text = para.text.strip()

            if not text:
                continue

            # Update current subsection
            if re.match(r'^7\.4\.\d+(\.\d+)?\s+', text):
                # Save previous parameter if exists
                if current_parameter and current_definition:
                    semantics[current_parameter] = self._create_semantic_info(
                        current_parameter,
                        current_subsection,
                        ' '.join(current_definition)
                    )

                current_subsection = text
                current_parameter = None
                current_definition = []
                continue

            # Check if this is a parameter definition
            # Pattern: "parameter_name specifies..." or "parameter_name indicates..."
            param_match = re.match(r'^([a-z_][a-z0-9_]+)\s+(specifies|indicates|identifies|contains|provides)', text, re.IGNORECASE)

            if param_match:
                # Save previous parameter if exists
                if current_parameter and current_definition:
                    semantics[current_parameter] = self._create_semantic_info(
                        current_parameter,
                        current_subsection,
                        ' '.join(current_definition)
                    )

                # Start new parameter
                current_parameter = param_match.group(1)
                current_definition = [text]
            elif current_parameter:
                # Continue current definition
                current_definition.append(text)

        # Save last parameter
        if current_parameter and current_definition:
            semantics[current_parameter] = self._create_semantic_info(
                current_parameter,
                current_subsection,
                ' '.join(current_definition)
            )

        return semantics

    def _create_semantic_info(self, parameter: str, section_header: str, definition: str) -> SemanticInfo:
        """
        Create SemanticInfo object from parsed information.

        Args:
            parameter: Parameter name
            section_header: Section header
            definition: Semantic definition text

        Returns:
            SemanticInfo object
        """
        # Extract section number
        section_match = re.search(r'(7\.4\.\d+(?:\.\d+)?)', section_header)
        section = section_match.group(1) if section_match else ""

        # Extract constraints
        constraints = self.extract_constraints(definition)

        # Find related parameters
        related = self.find_related_parameters(definition)

        return SemanticInfo(
            parameter=parameter,
            section=section,
            definition=definition,
            constraints=constraints,
            related_parameters=related
        )
