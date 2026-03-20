# Multi-Agent Architecture Research - LibreChat Capabilities

## Research Summary

Based on web research and LibreChat documentation analysis (validated March 11, 2026), here are the key findings for implementing the multi-agent SQL analysis architecture:

## LibreChat's Multi-Agent Capabilities

### 1. Agent Chain (Mixture-of-Agents) ✅ VALIDATED
- **Status**: Beta feature, enabled via `chain` capability
- **Architecture**: Layered MoA (Mixture-of-Agents) approach based on the "Mixture-of-Agents" paper
- **How it works**: Each agent takes outputs from previous layer agents as auxiliary information
- **Validation Source**: [LibreChat Agents Documentation](https://www.librechat.ai/docs/features/agents)
- **Confirmed Limitations**: 
  - Maximum 10 agents in a chain (confirmed in official docs: "The current maximum of agents that can be chained is 10")
  - Sequential execution (not parallel)
  - Currently in beta
  - Accessed from Advanced Settings panel in Agent Builder

### 2. MCP (Model Context Protocol) Integration ✅ VALIDATED
- **Full MCP support** for connecting external tools and data sources
- **Deferred tools**: Load tools on-demand to save context window (enabled by default as of v1.3.4)
- **Tool Search**: Runtime discovery of available tools via ToolSearch mechanism
- **Granular control**: Enable/disable specific tools per agent
- **Validation Source**: [LibreChat MCP Documentation](https://www.librechat.ai/docs/features/mcp) and [Config v1.3.4 Changelog](https://www.librechat.ai/changelog/config_v1.3.4)
- **Confirmed Features**:
  - Deferred tools show clock icon in UI
  - Tools marked as "deferred" excluded from initial LLM context
  - ToolSearch tool automatically added for runtime discovery
  - Once discovered, tool available for rest of conversation
  - Especially useful for agents with many MCP servers/tools

### 3. Agent Capabilities ✅ VALIDATED
LibreChat agents support the following capabilities (all configurable via librechat.yaml):
- `execute_code`: Code execution in multiple languages (Python, JavaScript, TypeScript, Go, C, C++, Java, PHP, Rust, Fortran)
- `file_search`: RAG with semantic search using vector stores
- `actions`: Dynamic tools from OpenAPI specs
- `tools`: Built-in tools (Google Search, Wolfram, OpenWeather, Calculator, Tavily, Azure AI Search, Traversaal)
- `artifacts`: Generate React components, HTML, Mermaid diagrams (can be configured at agent level)
- `context`: File context extraction (text parsing by default, enhanced by OCR)
- `ocr`: OCR processing for images and scanned documents
- `chain`: Agent chaining (MoA) - Beta feature
- `web_search`: Web search functionality
- `deferred_tools`: Lazy/event-driven loading of MCP tools (enabled by default as of v1.3.4)
- `programmatic_tools`: Programmatic tool calling via code execution sandbox (disabled by default)
- **Validation Source**: [LibreChat Agents Documentation](https://www.librechat.ai/docs/features/agents)

### 4. LangGraph Foundation ⚠️ NOT DIRECTLY CONFIRMED
- **Claim**: LibreChat uses LangGraph under the hood
- **Validation Status**: Could not find direct confirmation in LibreChat documentation
- **Alternative Finding**: LibreChat has its own agent architecture with native support for:
  - Agent chaining (Mixture-of-Agents)
  - State management across conversations
  - Tool orchestration via MCP
  - Complex workflows via agent chains
- **Note**: While LangGraph is a popular framework for agent workflows, LibreChat appears to have built its own agent orchestration system
- **Impact**: This doesn't affect our implementation - LibreChat's native capabilities are sufficient for the multi-agent architecture

## Recommended Architecture for Your Use Case

Based on your diagram and LibreChat's capabilities, here's the best approach:

### Option 1: Single Agent with Custom MCP Server (RECOMMENDED)
**Why**: Simplest, most maintainable, leverages existing infrastructure

**Architecture**:
```
User Query
    ↓
Analysis Agent (OCI GenAI)
    ↓
Custom MCP Server (SQL Analysis Tools)
    ├── extract-schema
    ├── interpret-query
    ├── build-sql
    ├── execute-sql (SQLcl)
    ├── generate-visualization
    └── create-report
```

**Pros**:
- Single agent orchestrates all operations
- OCI GenAI handles routing and decision-making
- All specialized logic in one MCP server
- Easy to debug and maintain
- Works with your existing OCI GenAI setup

**Cons**:
- Less modular than true multi-agent
- Single point of failure

### Option 2: Agent Chain with Specialized Agents
**Why**: True multi-agent architecture, better separation of concerns

**Architecture**:
```
User Query
    ↓
Analysis Agent (orchestrator)
    ↓
Schema Extractor Agent → NLP Interpreter Agent → Query Builder Agent → Execution Agent → Visualization Agent
```

**Pros**:
- True multi-agent workflow
- Each agent specialized for one task
- Better separation of concerns
- Matches your diagram closely

**Cons**:
- More complex to set up
- Sequential only (no parallel execution)
- Beta feature (may have bugs)
- Requires multiple agent configurations

### Option 3: Hybrid Approach (BEST OF BOTH WORLDS)
**Why**: Combines simplicity with modularity

**Architecture**:
```
User Query
    ↓
Analysis Agent (OCI GenAI)
    ↓
SQL Analysis MCP Server
    ├── Schema Tools (extract, analyze)
    ├── Query Tools (interpret, build, validate)
    ├── Execution Tools (run SQL via SQLcl)
    └── Visualization Tools (charts, reports)
```

With optional agent chain for complex workflows:
```
Analysis Agent → Validation Agent → Visualization Agent
```

**Pros**:
- Modular MCP tools
- Optional agent chain for quality control
- Flexible and extensible
- Works with current setup

**Cons**:
- Requires building custom MCP server
- More initial development

## Implementation Recommendation

For your use case, I recommend **Option 3 (Hybrid Approach)**:

1. **Phase 1**: Build custom MCP server with specialized tools
   - Schema extraction tools
   - NLP interpretation tools
   - SQL generation tools
   - Execution tools (integrate SQLcl)
   - Visualization tools

2. **Phase 2**: Create single Analysis Agent
   - Configure with OCI GenAI
   - Add all MCP tools
   - Use deferred tools for large tool sets
   - Test end-to-end workflow

3. **Phase 3** (Optional): Add agent chain
   - Validation Agent (checks SQL quality)
   - Visualization Agent (creates charts/reports)
   - Use MoA for improved output quality

## Technical Considerations

### MCP Server Development
- Use Python or TypeScript
- Follow MCP protocol specification
- Implement stdio transport (like SQLcl)
- Each tool should be atomic and focused

### Agent Configuration
```yaml
# librechat.yaml
mcpServers:
  sql_analysis:
    type: stdio
    command: python
    args:
      - "-m"
      - "sql_analysis_mcp"

agents:
  capabilities:
    - execute_code
    - tools
    - chain  # Enable agent chaining
    - artifacts  # For visualizations
```

### Tool Design Principles
1. **Schema Tools**: Introspect database structure
2. **NLP Tools**: Parse natural language to SQL intent
3. **Query Tools**: Generate and validate SQL
4. **Execution Tools**: Run SQL safely
5. **Visualization Tools**: Create charts from results

## Next Steps

1. Create spec for custom MCP server
2. Design tool interfaces
3. Implement MCP server
4. Configure LibreChat agent
5. Test and iterate

## Validation Summary

### ✅ Confirmed Features
1. **Agent Chain (MoA)**: Maximum 10 agents, sequential execution, beta feature
2. **MCP Integration**: Full support with deferred tools (enabled by default)
3. **Agent Capabilities**: All capabilities confirmed including artifacts, tools, file_search, execute_code
4. **Deferred Tools**: Runtime tool discovery via ToolSearch mechanism
5. **Granular Tool Control**: Can enable/disable specific tools per agent
6. **Artifacts**: Can be configured at agent level for HTML/React/Mermaid generation

### ⚠️ Unconfirmed Claims
1. **LangGraph Foundation**: Could not confirm LibreChat uses LangGraph internally (but has equivalent capabilities)

### 📊 Impact on Implementation
- **All planned features are supported** by LibreChat's native capabilities
- **Agent chain limit of 10** is sufficient for our 6-agent architecture
- **Deferred tools** will help manage context window with 16 MCP tools
- **Artifacts capability** confirmed for visualization display
- **MCP integration** confirmed for custom tool server

## References

- [LibreChat Agents Documentation](https://www.librechat.ai/docs/features/agents) - Validated March 11, 2026
- [LibreChat MCP Documentation](https://www.librechat.ai/docs/features/mcp) - Validated March 11, 2026
- [LibreChat Config v1.3.4 Changelog](https://www.librechat.ai/changelog/config_v1.3.4) - Validated March 11, 2026
- [Agents Endpoint Object Structure](https://www.librechat.ai/docs/configuration/librechat_yaml/object_structure/agents) - Validated March 11, 2026
- [MCP Protocol Specification](https://modelcontextprotocol.io/)
- [Mixture-of-Agents Paper](https://arxiv.org/html/2406.04692v1)
