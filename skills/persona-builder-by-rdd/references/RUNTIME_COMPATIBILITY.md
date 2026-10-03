# Runtime compatibility

The core protocol needs text dialogue, web research for initial build, file generation, and a way to package the resulting child skill.

## Capability modes
- Conversational: discovery, research synthesis, persona modeling, and file content can be produced in chat, but no package is created unless file tools exist.
- Files: child directory and references can be created.
- Web-enabled: required for the initial evidence research and optional later updates.
- Executable: structural validation and packaging can be run when a local runtime exists.
- Integrated agents: JSON output can be used in Make, n8n, or other orchestration environments, but no provider is a dependency of the core method.

Do not claim native skill installation or identical behavior across ChatGPT, Claude, or other hosts without testing that host.

If initial web research is unavailable, generation is blocked rather than replaced with model memory.
