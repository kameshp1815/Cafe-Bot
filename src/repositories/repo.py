

# src/repositories/repo.py

import random
import string
from sqlalchemy.orm                     import Session
from repositories.Database              import get_db
from repositories.schema.schema         import MenuItem, Order, OrderItem, ErrorLog
from utils.exceptions.custom_exceptions import BrewBaseException
from utils.exceptions.error_codes       import ErrorCodes


# =============================================================================
# CoffeeRepository — all ORM queries for Bean & Brew
# =============================================================================

class CoffeeRepository:

    def __init__(self, session: Session):
        self.session = session

    # -------------------------------------------------------------------------
    # get_menu — fetch all available menu items
    # -------------------------------------------------------------------------
    def get_menu(self) -> list[MenuItem]:
        try:
            return (
                self.session.query(MenuItem)
                .filter(MenuItem.is_available == True)
                .order_by(MenuItem.name)
                .all()
            )
        except Exception as e:
            raise BrewBaseException(
                status_code = 500,
                error_code  = ErrorCodes.BB_MENU_001,
                message     = f"Failed to fetch menu: {str(e)}"
            )

    # -------------------------------------------------------------------------
    # get_menu_item_by_name — fetch single item by name from menu table
    # -------------------------------------------------------------------------
    def get_menu_item_by_name(self, item_name: str) -> MenuItem | None:
        try:
            return (
                self.session.query(MenuItem)
                .filter(MenuItem.name.ilike(f"%{item_name}%"))
                .first()
            )
        except Exception as e:
            raise BrewBaseException(
                status_code = 500,
                error_code  = ErrorCodes.BB_MENU_001,
                message     = f"Failed to fetch menu item: {str(e)}"
            )

    # -------------------------------------------------------------------------
    # get_order_status_by_code — live fetch from orders table every request
    # -------------------------------------------------------------------------
    def get_order_status_by_code(self, order_code: str) -> Order:
        try:
            self.session.expire_all()

            order = (
                self.session.query(Order)
                .filter(Order.order_code == order_code.strip().upper())
                .first()
            )

            if not order:
                with get_db() as error_session:
                    ErrorLogRepository(error_session).log_error(
                        file_name     = "repo.py",
                        function_name = "check_order_status codeeeee",
                        error_message = f"Order {order_code} not found. Please check your order code.",
                    )
                raise BrewBaseException(
                    status_code = 404,
                    error_code  = ErrorCodes.BB_ORDER_001,
                    message     = f"Order {order_code} not found. Please check your order code."
                )

            return order

        except BrewBaseException as e:
            raise e
        except Exception as e:
            with get_db() as error_session:
                ErrorLogRepository(error_session).log_error(
                    file_name     = "repo.py",
                    function_name = "check_order_status codeeeee",
                    error_message = str(e),
                )
            raise BrewBaseException(
                status_code = 500,
                error_code  = ErrorCodes.BB_ORDER_001,
                message     = f"Failed to fetch order: {str(e)}"
            )

    # -------------------------------------------------------------------------
    # get_inventory — fetch stock for a specific item from menu table
    # -------------------------------------------------------------------------
    def get_inventory(self, item_id: str) -> int:
        try:
            item = (
                self.session.query(MenuItem)
                .filter(MenuItem.menu_item_id == item_id)
                .first()
            )

            if not item:
                raise BrewBaseException(
                    status_code = 404,
                    error_code  = ErrorCodes.BB_INV_001,
                    message     = f"Menu item not found"
                )

            if not item.is_available or item.stock <= 0:
                raise BrewBaseException(
                    status_code = 400,
                    error_code  = ErrorCodes.BB_INV_001,
                    message     = f"{item.name} is currently out of stock"
                )

            return item.stock

        except BrewBaseException as e:
            raise e
        except Exception as e:
            raise BrewBaseException(
                status_code = 500,
                error_code  = ErrorCodes.BB_INV_001,
                message     = f"Failed to fetch inventory: {str(e)}"
            )

    # -------------------------------------------------------------------------
    # add_order — insert order + order_items + reduce stock in menu table
    # -------------------------------------------------------------------------
    def add_order(self, customer_name: str, items: list) -> Order:
        try:
            order_code  = "ORD" + "".join(random.choices(string.digits, k=4))
            total_price = sum(float(i["price"]) * int(i["quantity"]) for i in items)

            # Step 1 — insert order
            new_order = Order(
                name         = customer_name,
                order_code   = order_code,
                status       = "pending",
                total_price  = total_price,
                is_available = True,
                created_by   = "SYSTEM",
                updated_by   = "SYSTEM"
            )
            self.session.add(new_order)
            self.session.flush()

            print(f"[DEBUG] Order flushed — order_id: {new_order.order_id}, order_code: {new_order.order_code}")

            # Step 2 — insert order items + reduce stock
            for i in items:

                order_item = OrderItem(
                    order_id   = new_order.order_id,
                    item_id    = i["item_id"],
                    quantity   = i["quantity"],
                    price      = i["price"],
                    created_by = "SYSTEM",
                    updated_by = "SYSTEM"
                )
                self.session.add(order_item)

                menu_item = (
                    self.session.query(MenuItem)
                    .filter(MenuItem.menu_item_id == i["item_id"])
                    .first()
                )

                if menu_item:
                    new_stock = menu_item.stock - i["quantity"]

                    if new_stock < 0:
                        raise BrewBaseException(
                            status_code = 400,
                            error_code  = ErrorCodes.BB_INV_001,
                            message     = f"Not enough stock for {menu_item.name}. Available: {menu_item.stock}"
                        )

                    menu_item.stock      = new_stock
                    menu_item.updated_by = "SYSTEM"

                    if new_stock == 0:
                        menu_item.is_available = False
                        print(f"[DEBUG] {menu_item.name} stock is now 0 — marked as unavailable")

                    print(f"[DEBUG] Stock reduced — {menu_item.name}: {menu_item.stock + i['quantity']} → {new_stock}")

            self.session.commit()
            print(f"[DEBUG] Order committed successfully — {new_order.order_code}")

            return new_order

        except BrewBaseException as e:
            self.session.rollback()
            raise e
        except Exception as e:
            self.session.rollback()
            print(f"[DEBUG] add_order failed — {str(e)}")
            raise BrewBaseException(
                status_code = 500,
                error_code  = ErrorCodes.BB_ORDER_001,
                message     = f"Failed to place order: {str(e)}"
            )


# =============================================================================
# ErrorLogRepository — logs unexpected errors to error_logs table
# =============================================================================

class ErrorLogRepository:

    def __init__(self, session: Session):
        self.session = session

    # -------------------------------------------------------------------------
    # log_error — inserts error log record using injected session
    # -------------------------------------------------------------------------
    def log_error(
        self,
        file_name     : str,
        function_name : str,
        error_message : str,
    ) -> None:
        try:
            new_log = ErrorLog(
                file_name     = file_name,
                function_name = function_name,
                error_message = error_message,
                is_active     = True,
                created_by    = "SYSTEM",
                updated_by    = "SYSTEM",
            )
            self.session.add(new_log)
            self.session.flush()
            self.session.commit()

            print(f"[ErrorLog] Error log added successfully | id: {new_log.error_id}")

        except Exception as e:
            print(f"[ErrorLog] Failed to insert error log into DB: {str(e)}")


