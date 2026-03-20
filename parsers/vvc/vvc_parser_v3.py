"""
VVC/H.266 specification parser - Version 3.
Extracts COMPLETE syntax structures including control flow logic.
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
    """Parser for VVC/H.266 specification documents (full syntax extraction)."""

    def __init__(self, config: Dict):
        super().__init__(config)

    def extract_syntax_structures(self) -> Dict[str, SyntaxStructure]:
        """
        Extract all syntax structures with COMPLETE syntax table.

        Includes:
        - All parameters
        - Control flow (if, for, while)
        - Braces and nesting
        - Function calls
        """
        syntax_structures = {}

        print("Extracting COMPLETE syntax structures with control flow...")

        # Find all Heading 4 paragraphs with "syntax" in the name
        # Also look back for Heading 3 to get section number
        current_section = ""

        for i, para in enumerate(self.doc.paragraphs):
            # Track section numbers from ANY heading
            if para.style and para.style.name.startswith('Heading'):
                # Try to extract section number (e.g., "7.3.1.1", "7.3.2.15")
                section_match = re.match(r'^(7\.3(?:\.\d+)+)', para.text.strip())
                if section_match:
                    current_section = section_match.group(1)

            if para.style and 'Heading 4' in para.style.name:
                text = para.text.strip()
                if 'syntax' in text.lower():
                    # Try to extract section from this heading
                    section_match = re.match(r'^(7\.3(?:\.\d+)+)', text)
                    if section_match:
                        section_number = section_match.group(1)
                    else:
                        section_number = current_section if current_section else "7.3"

                    print(f"  Found: [{section_number}] {text}")

                    # Extract syntax structure name from heading
                    struct_name = self._heading_to_struct_name(text)

                    # Extract FULL syntax table
                    structure = self._extract_full_syntax_table(i, text, struct_name, section_number)

                    if structure and len(structure.parameters) > 0:
                        syntax_structures[struct_name] = structure
                        print(f"    ✓ Extracted {len(structure.parameters)} syntax lines")
                    else:
                        print(f"    ✗ No syntax found")

        return syntax_structures

    def _heading_to_struct_name(self, heading: str) -> str:
        """Convert heading text to structure name."""
        name = heading.lower()
        name = name.replace(' syntax', '')
        name = name.replace(' ', '_')
        name = re.sub(r'[^a-z0-9_]', '', name)
        return name

    def _extract_full_syntax_table(self, heading_idx: int, heading_text: str, struct_name: str, section_number: str = "") -> SyntaxStructure:
        """Extract COMPLETE syntax structure from table including control flow."""
        from docx.table import Table
        from docx.text.paragraph import Paragraph

        syntax_lines = []  # Will store ALL lines from the syntax table

        # Find the table after this heading
        found_heading = False
        for i, element in enumerate(self.doc.element.body):
            if element.tag.endswith('p'):
                para = Paragraph(element, self.doc)
                if para.text.strip() == heading_text:
                    found_heading = True
                    continue

            if found_heading and element.tag.endswith('tbl'):
                table = Table(element, self.doc)
                print(f"    Found table with {len(table.rows)} rows")

                # Parse ALL table rows
                for row_idx, row in enumerate(table.rows):
                    if row_idx == 0:  # Skip header row
                        continue

                    cells = [cell.text.strip() for cell in row.cells]
                    if len(cells) < 2:
                        continue

                    syntax_text = cells[0]
                    descriptor = cells[1] if len(cells) > 1 else ""

                    # Skip empty rows
                    if not syntax_text:
                        continue

                    # Determine the line type
                    line_type = self._classify_syntax_line(syntax_text, descriptor)

                    # Create syntax parameter object for this line
                    syntax_lines.append(SyntaxParameter(
                        name=syntax_text,  # Full text including if/for/etc
                        type=descriptor,   # Descriptor (or empty for control flow)
                        condition=line_type  # Store line type in condition field
                    ))

                break

            # Stop if we hit another heading
            if found_heading and element.tag.endswith('p'):
                para = Paragraph(element, self.doc)
                if para.style and 'Heading' in para.style.name:
                    break

        if not syntax_lines:
            return None

        return SyntaxStructure(
            id=struct_name,
            section=section_number,
            name=struct_name,
            descriptor=heading_text,
            parameters=syntax_lines  # Store ALL syntax lines
        )

    def _classify_syntax_line(self, text: str, descriptor: str) -> str:
        """Classify what type of syntax line this is."""
        text_lower = text.lower()

        if text.strip() == '{':
            return 'brace_open'
        elif text.strip() == '}':
            return 'brace_close'
        elif text_lower.startswith('if(') or text_lower.startswith('if ('):
            return 'if_statement'
        elif text_lower.startswith('else if(') or text_lower.startswith('else if ('):
            return 'else_if_statement'
        elif text_lower.strip() == 'else':
            return 'else_statement'
        elif text_lower.startswith('for(') or text_lower.startswith('for ('):
            return 'for_loop'
        elif text_lower.startswith('while(') or text_lower.startswith('while ('):
            return 'while_loop'
        elif text_lower.startswith('do'):
            return 'do_while'
        elif '(' in text and ')' in text and not descriptor:
            # Function call (has parentheses but no descriptor)
            return 'function_call'
        elif descriptor:
            # Regular parameter
            return 'parameter'
        else:
            # Unknown/other
            return 'other'

    def extract_semantics(self) -> Dict[str, SemanticInfo]:
        """Extract semantic information from paragraphs."""
        semantics = {}

        print("Extracting semantics...")

        current_parameter = None
        current_definition = []

        for para in self.doc.paragraphs:
            text = para.text.strip()

            if not text:
                continue

            # Check if this is a parameter definition
            param_match = re.match(r'^([a-z_][a-z0-9_]+)\s+(specifies|indicates|identifies|contains|provides|equal to)', text, re.IGNORECASE)

            if param_match:
                # Save previous parameter
                if current_parameter and current_definition:
                    semantics[current_parameter] = self._create_semantic_info(
                        current_parameter,
                        "",
                        ' '.join(current_definition)
                    )

                # Start new parameter
                current_parameter = param_match.group(1)
                current_definition = [text]
            elif current_parameter:
                # Continue current definition or stop at heading
                if para.style and 'Heading' in para.style.name:
                    if current_definition:
                        semantics[current_parameter] = self._create_semantic_info(
                            current_parameter,
                            "",
                            ' '.join(current_definition)
                        )
                    current_parameter = None
                    current_definition = []
                else:
                    current_definition.append(text)

        # Save last parameter
        if current_parameter and current_definition:
            semantics[current_parameter] = self._create_semantic_info(
                current_parameter,
                "",
                ' '.join(current_definition)
            )

        return semantics

    def _create_semantic_info(self, parameter: str, section: str, definition: str) -> SemanticInfo:
        """Create SemanticInfo object from parsed information."""
        constraints = self.extract_constraints(definition)
        related = self.find_related_parameters(definition)

        return SemanticInfo(
            parameter=parameter,
            section=section,
            definition=definition,
            constraints=constraints,
            related_parameters=related
        )
