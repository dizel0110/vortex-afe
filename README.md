# VORTEX: APPARENT FLOW ENGINE (V-AFE)

An engineering and ML-inspired approach to systematizing kiteboarding mechanics.

## Core Equation
$$ \vec{W_{app}} = \vec{W_{true}} + \vec{W_{board}} $$

## Architecture
- `data/v-afe_core.json`: The source of truth for physical concepts and maneuvers.
- `data/v-afe_core.md`: Human-readable markdown version of the knowledge base.
- `logs/sessions/`: YAML tracking of individual sessions.
- `.config/system_prompt.txt`: The system prompt for the cognitive engine.
- `scripts/`: Utilities for interacting with the knowledge base.

## Usage
Add new sessions using the template in `logs/template.yaml`. Provide the logs to the V-AFE agent (Antigravity) to extract validated insights and update the core data structure via RAG mechanics.
