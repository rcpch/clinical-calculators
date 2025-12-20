# AI-Powered Calculator Assistant

## Overview

The Clinical Calculators project includes an AI-powered assistant that helps users create new medical calculators through an interactive conversation. This assistant makes calculator creation accessible to clinicians without requiring them to learn TOML syntax or Python programming.

## How It Works

### Conversation Flow

1. **User describes their calculator** - "I need a calculator for pediatric dosing"
2. **Assistant asks clarifying questions** - About age ranges, input parameters, validation rules
3. **Assistant generates TOML specification** - Based on the conversation
4. **User reviews and refines** - Can ask for changes or accept the specification
5. **Code generation** - The specification is automatically converted to Python code with tests

### The AI Assistant Tab

In the calculator generator interface, users can:

- Switch between **Manual Form** (traditional form-based input) and **AI Assistant** tabs
- Have a natural language conversation with the LLM
- Ask questions about calculator requirements
- Get real-time feedback and guidance
- Extract a complete TOML specification when ready
- Generate Python code and comprehensive tests from the specification

## Technology

- **Model**: Qwen 3 30B
- **Hosting**: Customer-hosted Ollama API (Azure API Management)
- **API Endpoint**: `/chat/calculator`
- **Rate Limiting**: 10 requests per minute per IP
- **Response Time**: ~10-30 seconds depending on server load

## Transparency & Open Governance

### Published System Prompt

We believe in **open and transparent AI governance**. The system prompt used to guide the LLM is published in this documentation: [LLM System Prompt](llm-system-prompt.md)

This commitment to transparency means:

✅ **Auditability** - Anyone can review exactly what instructions the model follows  
✅ **Trust** - No hidden prompts or undisclosed constraints  
✅ **Accountability** - We're responsible for the behavior we've programmed  
✅ **Community Input** - Users and clinicians can suggest improvements to the prompt  
✅ **Safety** - Security measures are documented and can be independently verified

### System Prompt Features

The published prompt includes:

- **Clear scope** - LLM only helps with calculator creation
- **Safety guardrails** - Explicitly prevents misuse (no clinical advice, no code execution)
- **Role definition** - Exactly what the assistant will do
- **Example output** - Shows the TOML format the assistant should generate
- **Security constraints** - Documents input limits, conversation limits, and validation rules

You can read the complete prompt [here](llm-system-prompt.md).

## Security & Safety

The AI assistant has multiple layers of protection:

### Input Protection

- Messages limited to 1000 characters
- Conversations capped at 30 turns (15 exchanges)
- Rate limited to 10 requests/minute per IP

### Scope Constraint

- Keyword filtering detects off-topic queries
- System prompt enforces calculator-only focus
- LLM refuses to answer non-calculator questions

### Output Validation

- Responses checked for calculator-related content
- TOML specifications validated against schema
- Generated Python code passes linting and testing

### Clinical Safety

- Explicitly prevents clinical advice or medical decisions
- Users are responsible for validating calculator logic
- Generated code must be reviewed by clinicians before use

## Limitations

The AI assistant has important limitations users should understand:

1. **Not a substitute for expert review** - Generated calculators must be validated by domain experts
2. **May require refinement** - The assistant might need clarification or corrections
3. **Depends on user input quality** - Vague requirements produce vague specifications
4. **No medical knowledge** - Cannot provide clinical guidance (by design)
5. **Language model limitations** - May occasionally generate imperfect TOML that needs minor fixes

## Using the AI Assistant

### Best Practices

✅ **Be specific** - Describe exactly what your calculator should do  
✅ **Provide context** - Mention clinical guidelines or references  
✅ **Ask questions** - If unclear, the assistant will help clarify  
✅ **Review output** - Always check the generated specification before using  
✅ **Iterate** - It's okay to ask for changes or refinements  

### Example Conversation

**User**: "I need a paediatric antibiotic dosing calculator"

**Assistant**: I'd be happy to help! To create an accurate dosing calculator, I need some clarification:

1. Which antibiotics should this cover? (e.g., Amoxicillin, Cephalexin, etc.)
2. What's the age range? (e.g., neonates, infants, all paediatric)
3. Should dosing be weight-based, age-based, or both?
4. Are there any renal function adjustments needed?
5. What's your clinical reference? (e.g., BNF for Children, local guidelines)

**User**: "Age-based for children 1-18 years. Just Amoxicillin to start. Weight-based dosing. BNF for Children reference."

**Assistant**: Great! One more set of questions:

1. What's the dose range? (e.g., 15-30 mg/kg per dose)
2. How many times daily? (e.g., 3 times daily)
3. Should output show mg/kg AND absolute mg dose?
4. Any maximum daily dose limits?
5. Should it include warnings for allergies or interactions?

**User**: "15-30 mg/kg, three times daily. Show both calculations. Max 3g daily. Skip warnings for now."

**Assistant**: Perfect! Here's your TOML specification:

```toml
[calculator]
name = "paediatric_amoxicillin_dosing"
title = "Paediatric Amoxicillin Dosing Calculator"
description = "Calculate age-based amoxicillin dosing for children 1-18 years"
reference = "BNF for Children 2024"

[inputs]
age_years = { type = "number", unit = "years", min = 1, max = 18, required = true }
weight_kg = { type = "number", unit = "kg", min = 3, max = 100, required = true }

[outputs]
dose_per_kg = { type = "number", unit = "mg/kg" }
dose_mg = { type = "number", unit = "mg" }
frequency = { type = "string" }
max_daily = { type = "string" }

[logic]
dose_per_kg = 22.5
dose_mg = weight_kg * dose_per_kg
frequency = "Three times daily"
max_daily = f"Maximum daily dose: 3000 mg (age {age_years} years"
```

User: "Looks good! Can you generate the Python code and tests?"

The assistant extracts the TOML and the system automatically generates:

✅ Python calculator file
✅ Comprehensive test suite
✅ Both validated and ready for review

## Getting Started

1. Go to the Calculator Generator
2. Click the "AI Assistant" tab
3. Describe your calculator needs
4. Review and refine the specification
5. Generate code and tests
6. Submit for review and integration

## Support

For issues or questions about the AI assistant:

- Check the LLM System Prompt documentation
- Review the Calculator Generator guide
- See Contributing Guidelines for submission workflow