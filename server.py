from mcp.server.lowlevel import Server
import mcp.types as types
import httpx
import os
import json
import glob

# Initialize the server
app = Server("dev-tools-server")

@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    """Handle tool calls from the client."""
    if name == "search_code":
        return await search_code(arguments.get("query", ""), arguments.get("directory", "."))
    elif name == "analyze_dependencies":
        return await analyze_dependencies(arguments.get("directory", "."))
    elif name == "fetch_documentation":
        return await fetch_documentation(arguments.get("package", ""))
    else:
        return [types.TextContent(
            type="text",
            text=f"Error: Unknown tool: {name}"
        )]

async def search_code(query: str, directory: str) -> list[types.TextContent]:
    """Search code files for a specific query."""
    # Security improvement: Sanitize directory path
    base_directory = os.path.abspath(os.getcwd())
    directory = os.path.normpath(os.path.join(base_directory, directory))
    
    # Prevent directory traversal attacks
    if not directory.startswith(base_directory):
        return [types.TextContent(
            type="text",
            text="Access denied: Invalid directory"
        )]
    
    results = []
    for ext in ['.py', '.js', '.ts', '.jsx', '.tsx', '.html', '.css']:
        for filepath in glob.glob(f"{directory}/**/*{ext}", recursive=True):
            try:
                with open(filepath, 'r', encoding='utf-8') as file:
                    content = file.read()
                    if query.lower() in content.lower():
                        match_context = get_context(content, query)
                        results.append(f"File: {filepath}\n{match_context}\n---\n")
            except Exception as e:
                # Log the error but continue searching
                print(f"Error reading {filepath}: {str(e)}")
                continue
    
    if results:
        return [types.TextContent(
            type="text",
            text="Search Results:\n\n" + "\n".join(results)
        )]
    else:
        return [types.TextContent(
            type="text",
            text=f"No results found for '{query}' in directory '{directory}'."
        )]

def get_context(content: str, query: str, context_lines: int = 3) -> str:
    """Get context around a match."""
    lines = content.split('\n')
    matches = []
    
    for i, line in enumerate(lines):
        if query.lower() in line.lower():
            start = max(0, i - context_lines)
            end = min(len(lines), i + context_lines + 1)
            context = "\n".join(lines[start:end])
            matches.append(f"Lines {start+1}-{end}:\n{context}")
    
    return "\n\n".join(matches)

async def analyze_dependencies(directory: str) -> list[types.TextContent]:
    """Analyze project dependencies."""
    # Security improvement: Sanitize directory path
    base_directory = os.path.abspath(os.getcwd())
    directory = os.path.normpath(os.path.join(base_directory, directory))
    
    # Prevent directory traversal attacks
    if not directory.startswith(base_directory):
        return [types.TextContent(
            type="text",
            text="Access denied: Invalid directory"
        )]
    
    dependency_files = {
        'python': ['requirements.txt', 'setup.py', 'pyproject.toml'],
        'node': ['package.json'],
        'dotnet': ['*.csproj', '*.fsproj', '*.vbproj'],
    }
    
    results = []
    
    for lang, files in dependency_files.items():
        for file_pattern in files:
            try:
                for filepath in glob.glob(f"{directory}/**/{file_pattern}", recursive=True):
                    try:
                        with open(filepath, 'r', encoding='utf-8') as file:
                            content = file.read()
                            results.append(f"Found {lang} dependencies in {filepath}:\n{content}\n---\n")
                    except Exception as e:
                        print(f"Error reading {filepath}: {str(e)}")
                        continue
            except Exception as e:
                print(f"Error in glob pattern {file_pattern}: {str(e)}")
                continue
    
    if results:
        return [types.TextContent(
            type="text",
            text="Dependency Analysis:\n\n" + "\n".join(results)
        )]
    else:
        return [types.TextContent(
            type="text",
            text=f"No dependency files found in directory '{directory}'."
        )]

async def fetch_documentation(package: str) -> list[types.TextContent]:
    """Fetch documentation for a package."""
    # Sanitize package name to prevent injection
    package = package.strip()
    if not package or not all(c.isalnum() or c in "-_." for c in package):
        return [types.TextContent(
            type="text",
            text="Invalid package name. Package names should only contain alphanumeric characters, hyphens, underscores, or periods."
        )]
    
    try:
        # For Python packages
        url = f"https://pypi.org/pypi/{package}/json"
        async with httpx.AsyncClient() as client:
            response = await client.get(url, timeout=10.0)
            if response.status_code == 200:
                data = response.json()
                summary = data.get("info", {}).get("summary", "No summary available")
                description = data.get("info", {}).get("description", "No description available")
                
                return [types.TextContent(
                    type="text",
                    text=f"Documentation for {package}:\n\nSummary: {summary}\n\nDescription:\n{description[:1000]}...(truncated)"
                )]
    except Exception as e:
        print(f"Error fetching PyPI data: {str(e)}")
    
    # Try npm packages if PyPI fails
    try:
        url = f"https://registry.npmjs.org/{package}"
        async with httpx.AsyncClient() as client:
            response = await client.get(url, timeout=10.0)
            if response.status_code == 200:
                data = response.json()
                description = data.get("description", "No description available")
                
                return [types.TextContent(
                    type="text",
                    text=f"Documentation for {package}:\n\nDescription: {description}"
                )]
    except Exception as e:
        print(f"Error fetching NPM data: {str(e)}")
    
    return [types.TextContent(
        type="text",
        text=f"Could not fetch documentation for package '{package}'."
    )]

@app.list_tools()
async def list_tools() -> list[types.Tool]:
    """List available tools."""
    return [
        types.Tool(
            name="search_code",
            description="Search code files for specific queries",
            inputSchema={
                "type": "object",
                "required": ["query"],
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query to find in code files",
                    },
                    "directory": {
                        "type": "string",
                        "description": "The directory to search in (default: current directory)",
                    }
                },
            },
        ),
        types.Tool(
            name="analyze_dependencies",
            description="Analyze project dependencies",
            inputSchema={
                "type": "object",
                "properties": {
                    "directory": {
                        "type": "string",
                        "description": "The directory to analyze (default: current directory)",
                    }
                },
            },
        ),
        types.Tool(
            name="fetch_documentation",
            description="Fetch documentation for a package",
            inputSchema={
                "type": "object",
                "required": ["package"],
                "properties": {
                    "package": {
                        "type": "string",
                        "description": "The package name to fetch documentation for",
                    }
                },
            },
        ),
    ]

@app.list_resources()
async def list_resources() -> list[types.Resource]:
    """List available resources."""
    resources = []
    
    # Add README file if it exists
    readme_paths = ['README.md', 'README.txt', 'Readme.md']
    for path in readme_paths:
        if os.path.exists(path):
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
                resources.append(types.Resource(
                    name=f"readme",
                    description=f"Project README file",
                    content=[types.TextContent(type="text", text=content)]
                ))
                break
            except Exception as e:
                print(f"Error reading README file: {str(e)}")
    
    return resources

@app.list_prompts()
async def list_prompts() -> list[types.Prompt]:
    """List available prompts."""
    return [
        types.Prompt(
            name="code_review",
            description="Perform a code review on a specific file",
            inputSchema={
                "type": "object",
                "required": ["filepath"],
                "properties": {
                    "filepath": {
                        "type": "string",
                        "description": "Path to the file to review",
                    },
                    "focus": {
                        "type": "string",
                        "description": "Specific aspect to focus on (e.g., 'security', 'performance')",
                    }
                },
            },
            template="""
            Please review the following code from {{filepath}}:
            
            ```
            {{#file filepath}}
            ```
            
            {{#if focus}}
            Focus your review on {{focus}} aspects.
            {{else}}
            Provide a general code review focusing on:
            - Code quality
            - Potential bugs
            - Performance issues
            - Security concerns
            {{/if}}
            
            Provide specific suggestions for improvement with code examples where appropriate.
            """
        ),
    ]

if __name__ == "__main__":
    import sys
    
    # Default to stdio transport
    transport = "stdio"
    port = 8000
    
    # Check for command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == "sse":
            transport = "sse"
            if len(sys.argv) > 2:
                try:
                    port = int(sys.argv[2])
                except ValueError:
                    pass
    
    if transport == "sse":
        try:
            from mcp.server.sse import SseServerTransport
            from starlette.applications import Starlette
            from starlette.routing import Mount, Route
            import uvicorn

            sse = SseServerTransport("/messages/")

            async def handle_sse(request):
                async with sse.connect_sse(
                    request.scope, request.receive, request._send
                ) as streams:
                    await app.run(
                        streams[0], streams[1], app.create_initialization_options()
                    )

            starlette_app = Starlette(
                debug=True,
                routes=[
                    Route("/sse", endpoint=handle_sse),
                    Mount("/messages/", app=sse.handle_post_message),
                ],
            )

            print(f"Starting MCP server on port {port} using SSE transport")
            uvicorn.run(starlette_app, host="0.0.0.0", port=port)
        except ImportError:
            print("Error: SSE transport requires additional dependencies.")
            print("Please install with: pip install 'mcp[sse]' uvicorn starlette")
            sys.exit(1)
    else:
        try:
            from mcp.server.stdio import stdio_server
            import anyio

            async def run_stdio():
                async with stdio_server() as streams:
                    await app.run(
                        streams[0], streams[1], app.create_initialization_options()
                    )

            print("Starting MCP server using stdio transport")
            anyio.run(run_stdio)
        except ImportError:
            print("Error: Missing required dependencies.")
            print("Please install with: pip install mcp anyio")
            sys.exit(1)
