def track_event(event_name: str, payload: dict):
    """
    Basic analytics hook (to be expanded or swapped for real tracking).
    """
    try:
        from django.conf import settings
        if getattr(settings, "PARLAY_ANALYTICS_ENABLED", True):
            # TODO: BETTER ANALYTICS HERE!!!
            # print(f"[Analytics] {event_name}: {payload}")
            # Replace with actual analytics call:
            # send_to_sentry(event_name, payload)
            # send_to_kinesis(...)
            # save_to_model(...)
            pass

    except Exception as e:
        print(f"[Analytics] Error tracking event {event_name}: {e}")