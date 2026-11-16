from app.gateway.tool_registry import ToolRegistry


def main():
    registry = ToolRegistry()

    print("\nAll tools:")
    tools = registry.list_tools()

    for tool in tools:
        print(tool)

    print("\nSpecific tool:")
    tool = registry.get_tool("add")
    print(tool)


if __name__ == "__main__":
    main()