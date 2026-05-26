# src/tools/tools.py

from langchain_core.tools               import tool
from repositories.repo                  import CoffeeRepository, ErrorLogRepository
from repositories.Database              import get_db
from utils.exceptions.custom_exceptions import BrewBaseException
from utils.exceptions.error_codes       import ErrorCodes


# =============================================================================
# TOOL 1 — check_menu
# =============================================================================

@tool
def check_menu() -> str:
    """
    Fetch all available menu items from Bean and Brew coffee shop.
    Use when the customer asks what drinks are available,
    what is on the menu, show me the menu, or what coffees do you have.
    Also use when customer wants to order but has not specified which drink.
    """
    try:
        with get_db() as session:
            repo  = CoffeeRepository(session)
            items = repo.get_menu()

            if not items:
                return "Sorry, no menu items are available right now."

            result = "Here is our menu today \n\n"
            for item in items:
                result += f"• {item.name} — ₹{item.price:.2f}\n  {item.description}\n\n"
            return result

    except BrewBaseException as e:
        raise e

    except Exception as e:
        with get_db() as error_session:
            ErrorLogRepository(error_session).log_error(
                file_name     = "tools.py",
                function_name = "check_menu",
                error_message = str(e),
            )
        raise BrewBaseException(
            status_code = 500,
            error_code  = ErrorCodes.BB_MENU_001,
            message     = f"Failed to fetch menu: {str(e)}"
        )


# =============================================================================
# TOOL 2 — check_inventory
# =============================================================================

@tool
def check_inventory(item_name: str) -> str:
    """
    Check if a specific menu item is available and in stock.
    Always query the menu_items table live to get current stock.
    Use when customer asks if a specific drink is available,
    do you have X, or is X in stock.
    If stock is 0 or is_available is False — tell customer it is out of stock.
    """
    try:
        with get_db() as session:
            repo = CoffeeRepository(session)
            item = repo.get_menu_item_by_name(item_name)

            print('tool 1')

            if not item:
                return (
                    f"Sorry, {item_name} is not on our menu. "
                    f"Would you like to see what we have? "
                )

            if item.stock == 0 or not item.is_available:
                return (
                    f"Sorry, {item.name} is currently out of stock. "
                    f"Would you like to try something else from our menu? "
                )

            return (
                f" {item.name} is available!\n"
                f"Price : ₹{item.price:.2f}\n"
                f"Stock : {item.stock} remaining\n"
                f"Want me to add it to your order? "
            )

    except BrewBaseException as e:
        raise e

    except Exception as e:
        with get_db() as error_session:
            ErrorLogRepository(error_session).log_error(
                file_name     = "tools.py",
                function_name = "check_inventory",
                error_message = str(e),
            )
        raise BrewBaseException(
            status_code = 500,
            error_code  = ErrorCodes.BB_INV_001,
            message     = f"Failed to check inventory: {str(e)}"
        )


# =============================================================================
# TOOL 3 — check_order_status
# =============================================================================

@tool
def check_order_status(order_code: str) -> str:
    """
    Check the current status of a customer order by querying the orders table.
    Always fetch live from DB for every request — never assume status.
    The order code is provided by customer in chat like ORD1234.
    Use when customer asks if their order is ready or wants order status.
    """
    try:
        with get_db() as session:
            repo  = CoffeeRepository(session)
            order = repo.get_order_status_by_code(order_code)

            status_messages = {
                "pending"   : (
                    f" Order #{order.order_code} is received and pending.\n"
                    f"We will start preparing it shortly!"
                ),
                "preparing" : (
                    f" Order #{order.order_code} is currently being prepared.\n"
                    f"Almost ready — hang tight!"
                ),
                "ready"     : (
                    f" Great news! Order #{order.order_code} is ready for pickup!\n"
                    f"Please head to the counter. "
                ),
                "picked_up" : (
                    f" Order #{order.order_code} has already been picked up.\n"
                    f"Enjoy your coffee! "
                ),
            }

            return status_messages.get(
                order.status,
                f"Order #{order.order_code} current status: {order.status}"
            )

    except BrewBaseException as e:
        raise e

    except Exception as e:
        with get_db() as error_session:
            ErrorLogRepository(error_session).log_error(
                file_name     = "tools.py",
                function_name = "check_order_status",
                error_message = str(e),
            )
        raise BrewBaseException(
            status_code = 500,
            error_code  = ErrorCodes.BB_ORDER_001,
            message     = f"Failed to fetch order status: {str(e)}"
        )


# =============================================================================
# TOOL 4 — add_order
# =============================================================================

@tool
def add_order(item_name: str, quantity: int) -> str:
    """
    Place a new order for the customer at Bean and Brew coffee shop.
    Use ONLY when you have confirmed:
    1. item_name — the exact drink name they want
    2. quantity  — how many they want
    Always pass customer_name as "Guest".
    """
    try:
        with get_db() as session:
            repo = CoffeeRepository(session)

            item = repo.get_menu_item_by_name(item_name)
            print('tool 2')

            if not item:
                return f"Sorry, {item_name} is not found on our menu. Please check the menu and try again."

            if item.stock == 0 or not item.is_available:
                return f"Sorry, {item.name} is currently out of stock. Please choose another drink. "

            if quantity <= 0:
                return "Quantity must be greater than zero. How many would you like?"

            items = [{
                "item_id"  : item.menu_item_id,
                "item_name": item.name,
                "quantity" : quantity,
                "price"    : float(item.price)
            }]

            order = repo.add_order(
                customer_name = "Guest",
                items         = items
            )

            total = float(item.price) * quantity

            return (
                f" Order confirmed!\n\n"
                f"Order Code  : {order.order_code}\n"
                f"Item        : {item.name} x{quantity}\n"
                f"Total Price : ₹{total:.2f}\n"
                f"Status      : Pending\n\n"
                f"We will call your order when it is ready! "
            )

    except BrewBaseException as e:
        raise e

    except Exception as e:
        with get_db() as error_session:
            ErrorLogRepository(error_session).log_error(
                file_name     = "tools.py",
                function_name = "add_order",
                error_message = str(e),
            )
        raise BrewBaseException(
            status_code = 500,
            error_code  = ErrorCodes.BB_ORDER_001,
            message     = f"Failed to place order: {str(e)}"
        )



