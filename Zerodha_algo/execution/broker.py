import time
from utils.logger import get_logger

logger = get_logger("broker")

def place_live_order(kite, symbol, side, qty, retries=3, delay=1):
    """Place a market order with simple retry logic and return the order id or response."""
    for attempt in range(1, retries + 1):
        try:
            resp = kite.place_order(
                variety=kite.VARIETY_REGULAR,
                exchange="NSE",
                tradingsymbol=symbol,
                transaction_type=side,
                quantity=qty,
                product=kite.PRODUCT_MIS,
                order_type=kite.ORDER_TYPE_MARKET
            )
            logger.info("Placed live order %s %s qty=%s resp=%s", side, symbol, qty, resp)
            # try to confirm order status if API supports it
            order_id = resp.get("order_id") if isinstance(resp, dict) else None
            status = None
            try:
                if order_id and hasattr(kite, "order_history"):
                    status = kite.order_history(order_id)
            except Exception:
                status = None

            # attach order confirmation to response for caller
            resp_obj = {"resp": resp, "order_id": order_id, "status": status}
            return resp_obj
        except Exception as e:
            logger.warning("Attempt %d: error placing order %s %s: %s", attempt, side, symbol, e)
            if attempt < retries:
                time.sleep(delay * attempt)
            else:
                logger.error("Failed to place order after %d attempts", retries)
                raise


def confirm_order_status(kite, order_id, timeout=30, poll_interval=2):
    """Attempt to confirm order status by polling available endpoints."""
    import time
    if not order_id:
        return None
    elapsed = 0
    while elapsed < timeout:
        try:
            if hasattr(kite, "order_history"):
                info = kite.order_history(order_id)
                # expect dict or list
                if isinstance(info, dict) and "status" in info:
                    return info.get("status")
                if isinstance(info, list) and info:
                    # look for status keys
                    for it in info:
                        for key in ("status", "order_status"):
                            if key in it:
                                return it.get(key)
            if hasattr(kite, "orders"):
                orders = kite.orders()
                for o in orders.get("data", []) if isinstance(orders, dict) else orders:
                    if str(o.get("order_id")) == str(order_id):
                        for key in ("status", "order_status"):
                            if key in o:
                                return o.get(key)
        except Exception:
            pass
        time.sleep(poll_interval)
        elapsed += poll_interval
    return None
