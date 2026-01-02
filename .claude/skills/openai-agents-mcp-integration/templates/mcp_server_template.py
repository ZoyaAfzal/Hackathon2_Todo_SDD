"""
MCP Server Template - Expose Tools via MCP Protocol

Copy this template to create your own MCP server with custom tools.

Usage:
    1. Copy this file to your project's mcp_server directory
    2. Implement your custom tools using @app.call_tool() decorator
    3. Update tool signatures and logic
    4. Run with: python -m mcp_server
"""

import asyncio
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp import types

# Import your services/database here
# from db import get_session
# from services.my_service import MyService


# Create MCP server
# UPDATE: Server name
app = Server("my-mcp-server")


# EXAMPLE TOOL 1: Simple data retrieval
@app.call_tool()
async def get_items(
    user_id: str,
    filter: str = "all"
) -> list[types.TextContent]:
    """
    Get items for user with optional filter.

    Args:
        user_id: User's unique identifier
        filter: Filter option (all, active, archived)

    Returns:
        Formatted list of items
    """
    # TODO: Implement your logic here
    try:
        # Example: Get data from database
        # session = next(get_session())
        # items = await MyService.get_items(session, user_id, filter)

        # Placeholder response
        items = [
            {"id": 1, "name": "Item 1"},
            {"id": 2, "name": "Item 2"},
        ]

        if not items:
            return [types.TextContent(
                type="text",
                text="No items found."
            )]

        # Format response
        item_list = "\n".join([
            f"{i+1}. {item['name']}"
            for i, item in enumerate(items)
        ])

        return [types.TextContent(
            type="text",
            text=f"Your items:\n{item_list}"
        )]

    except Exception as e:
        return [types.TextContent(
            type="text",
            text=f"Error retrieving items: {str(e)}"
        )]


# EXAMPLE TOOL 2: Create/modify data
@app.call_tool()
async def create_item(
    user_id: str,
    name: str,
    description: str | None = None
) -> list[types.TextContent]:
    """
    Create a new item for user.

    Args:
        user_id: User's unique identifier
        name: Item name (required)
        description: Optional item description

    Returns:
        Success message with item details
    """
    # TODO: Implement your logic here
    try:
        # Example: Save to database
        # session = next(get_session())
        # item = await MyService.create_item(
        #     session=session,
        #     user_id=user_id,
        #     name=name,
        #     description=description
        # )

        # Placeholder response
        return [types.TextContent(
            type="text",
            text=f"Item created: '{name}'"
        )]

    except Exception as e:
        return [types.TextContent(
            type="text",
            text=f"Error creating item: {str(e)}"
        )]


# EXAMPLE TOOL 3: Delete data
@app.call_tool()
async def delete_item(
    user_id: str,
    item_id: int
) -> list[types.TextContent]:
    """
    Delete an item permanently.

    Args:
        user_id: User's unique identifier
        item_id: ID of item to delete

    Returns:
        Success or error message
    """
    # TODO: Implement your logic here
    try:
        # Example: Delete from database
        # session = next(get_session())
        # await MyService.delete_item(
        #     session=session,
        #     user_id=user_id,
        #     item_id=item_id
        # )

        return [types.TextContent(
            type="text",
            text="Item deleted successfully."
        )]

    except Exception as e:
        return [types.TextContent(
            type="text",
            text=f"Error deleting item: {str(e)}"
        )]


# EXAMPLE TOOL 4: Update data
@app.call_tool()
async def update_item(
    user_id: str,
    item_id: int,
    name: str | None = None,
    description: str | None = None
) -> list[types.TextContent]:
    """
    Update item details.

    Args:
        user_id: User's unique identifier
        item_id: ID of item to update
        name: New name (optional)
        description: New description (optional)

    Returns:
        Success or error message
    """
    # TODO: Implement your logic here
    try:
        # Example: Update in database
        # session = next(get_session())
        # item = await MyService.update_item(
        #     session=session,
        #     user_id=user_id,
        #     item_id=item_id,
        #     name=name,
        #     description=description
        # )

        return [types.TextContent(
            type="text",
            text="Item updated successfully."
        )]

    except Exception as e:
        return [types.TextContent(
            type="text",
            text=f"Error updating item: {str(e)}"
        )]


# Run MCP server
async def main():
    """Start MCP server with stdio transport."""
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())
