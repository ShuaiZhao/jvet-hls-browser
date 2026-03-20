"""
VVC/H.266 specification parser - Version 2.
Extracts syntax structures based on Heading styles (not section numbers).
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
    """Parser for VVC/H.266 specification documents (using heading styles)."""

    def __init__(self, config: Dict):
        super().__init__(config)

    def extract_syntax_structures(self) -> Dict[str, SyntaxStructure]:
        """
        Extract all syntax structures based on Heading 4 style.

        VVC spec uses Heading 4 for syntax structure names like:
        - "Video parameter set RBSP syntax"
        - "Sequence parameter set RBSP syntax"
        - etc.
        """
        syntax_structures = {}

        print("Searching for syntax structures using Heading 4 style...")

        # Find all Heading 4 paragraphs with "syntax" in the name
        for i, para in enumerate(self.doc.paragraphs):
            if para.style and 'Heading 4' in para.style.name:
                text = para.text.strip()
                if 'syntax' in text.lower():  # Remove RBSP requirement
                    print(f"  Found: {text}")

                    # Extract syntax structure name from heading
                    # "Video parameter set RBSP syntax" -> "video_parameter_set_rbsp"
                    struct_name = self._heading_to_struct_name(text)

                    # Look for syntax table/code after this heading
                    structure = self._extract_syntax_after_heading(i, text, struct_name)

                    if structure and len(structure.parameters) > 0:
                        syntax_structures[struct_name] = structure
                        print(f"    ✓ Extracted {len(structure.parameters)} parameters")
                    else:
                        print(f"    ✗ No parameters found")

        return syntax_structures

    def _heading_to_struct_name(self, heading: str) -> str:
        """Convert heading text to structure name."""
        # "Video parameter set RBSP syntax" -> "video_parameter_set_rbsp"
        name = heading.lower()
        name = name.replace(' syntax', '')
        name = name.replace(' ', '_')
        # Remove special characters
        name = re.sub(r'[^a-z0-9_]', '', name)
        return name

    def _extract_syntax_after_heading(self, heading_idx: int, heading_text: str, struct_name: str) -> SyntaxStructure:
        """Extract syntax structure content from tables after heading."""
        from docx.table import Table
        from docx.text.paragraph import Paragraph

        parameters = []

        # Look for tables in document elements after this heading
        found_heading = False
        for i, element in enumerate(self.doc.element.body):
            # Find the heading element
            if element.tag.endswith('p'):
                para = Paragraph(element, self.doc)
                if para.text.strip() == heading_text:
                    found_heading = True
                    continue

            # Once we found the heading, look for the next table
            if found_heading and element.tag.endswith('tbl'):
                table = Table(element, self.doc)
                print(f"    Found table with {len(table.rows)} rows")

                # Parse table rows (skip header row)
                for row_idx, row in enumerate(table.rows):
                    if row_idx == 0:  # Skip header
                        continue

                    cells = [cell.text.strip() for cell in row.cells]

                    if len(cells) < 2:
                        continue

                    param_name = cells[0]
                    param_type = cells[1]

                    # Skip if it's not a valid parameter name
                    if not re.match(r'^[a-z_][a-z0-9_]*$', param_name):
                        continue

                    # Skip if it's not a valid type
                    if not re.match(r'(ue\(v\)|u\(\d+\)|se\(v\)|i\(\d+\)|f\(\d+\)|ae\(v\))', param_type):
                        continue

                    # Check for condition in parameter name or third column
                    condition = None
                    # Conditions might be in the parameter name cell with "if(...)"
                    if 'if' in param_name.lower():
                        cond_match = re.search(r'if\s*\((.*?)\)', param_name)
                        if cond_match:
                            condition = cond_match.group(1)
                            # Extract actual param name
                            param_name = re.sub(r'\s*if.*', '', param_name).strip()

                    parameters.append(SyntaxParameter(
                        name=param_name,
                        type=param_type,
                        condition=condition
                    ))

                # Found and processed the table
                break

            # Stop if we hit another heading
            if found_heading and element.tag.endswith('p'):
                para = Paragraph(element, self.doc)
                if para.style and 'Heading' in para.style.name:
                    break

        if not parameters:
            return None

        return SyntaxStructure(
            id=struct_name,
            section="",
            name=struct_name,
            descriptor=heading_text,
            parameters=parameters
        )

    def extract_semantics(self) -> Dict[str, SemanticInfo]:
        """
        Extract semantic information from paragraphs.

        VVC semantics typically start with parameter_name followed by description.
        """
        semantics = {}

        print("Extracting semantics...")

        current_parameter = None
        current_definition = []

        for para in self.doc.paragraphs:
            text = para.text.strip()

            if not text:
                continue

            # Check if this is a parameter definition
            # Pattern: "parameter_name specifies..." or "parameter_name indicates..."
            param_match = re.match(r'^([a-z_][a-z0-9_]+)\s+(specifies|indicates|identifies|contains|provides|equal to)', text, re.IGNORECASE)

            if param_match:
                # Save previous parameter if exists
                if current_parameter and current_definition:
                    semantics[current_parameter] = self._create_semantic_info(
                        current_parameter,
                        "",  # section
                        ' '.join(current_definition)
                    )

                # Start new parameter
                current_parameter = param_match.group(1)
                current_definition = [text]
            elif current_parameter:
                # Continue current definition
                # Stop if we hit a new parameter or heading
                if para.style and 'Heading' in para.style.name:
                    # Save and reset
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
