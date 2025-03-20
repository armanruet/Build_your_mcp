# Building Your Own MCP Server

This repository contains code and examples for building a Model Context Protocol (MCP) server that works with various AI-powered code editors like Claude, Cursor, Windsurf, and Zed.

**Note:** This represents a snapshot of the Model Context Protocol (MCP) implementation as of March 2025. Since the MCP ecosystem is rapidly evolving, readers should check the official documentation for each client for the most current information and implementation details.

## Getting Started

### Prerequisites

- Python 3.10+ or Node.js 16+
- Basic understanding of JSON-RPC
- An MCP-compatible client (Claude Desktop, Cursor, Windsurf, Zed, etc.)

### Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/armanruet/Build_your_mcp.git
   cd Build_your_mcp
   ```

2. Create a virtual environment and install dependencies:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

## Running the MCP Server

You can run the server in two modes:

1. **STDIO mode** (useful for desktop clients like Claude Desktop):
   ```bash
   python server.py
   ```

2. **SSE mode** (useful for web-based clients):
   ```bash
   python server.py sse 8000
   ```

## Important Implementation Notes

### Client Support Status
As of March 2025, Claude Desktop and Cursor offer robust MCP support, while Windsurf and Zed implementations may vary in features and stability. Always check each client's latest documentation for current compatibility.

### Code Implementation
The code examples provided are for demonstration purposes and may need additional error handling and optimization for production environments. Consider this a starting point rather than a production-ready solution.

### Security Improvements
To enhance security, implement path sanitization to prevent directory traversal attacks as shown in the `server.py` file.

### Client-Specific Instructions
For Windsurf, locate the MCP configuration in Settings → AI → External Tools. For Zed, refer to their documentation for the latest MCP integration steps as the implementation details may have changed since publication.

### Testing Recommendation
Before deploying your MCP server, thoroughly test it with each client you intend to support. Client behaviors may differ slightly, especially regarding tool discovery and parameter passing.

## Connecting to Clients

### Claude Desktop

1. Edit your Claude Desktop configuration file:
   - On macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - On Windows: `%APPDATA%\Claude\claude_desktop_config.json`

2. Add your server configuration as shown in `claude_config_example.json`

3. Restart Claude Desktop and look for the tools icon to appear.

### Cursor IDE

1. Run your server in SSE mode:
   ```bash
   python server.py sse 8000
   ```

2. In Cursor, go to Settings → Features → MCP Servers
3. Add a new server with:
   - Name: `dev-tools`
   - Type: `sse`
   - URL: `http://localhost:8000/sse`

## Resources

- [Model Context Protocol Documentation](https://modelcontextprotocol.io/)
- [Anthropic MCP GitHub Repository](https://github.com/modelcontextprotocol)
- [Claude Desktop Configuration Guide](https://docs.anthropic.com/claude/docs/claude-desktop-mcp-setup)
- [Cursor IDE Documentation](https://cursor.sh/docs/mcp-integration)
