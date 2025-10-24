from functools import wraps

from asgiref.sync import iscoroutinefunction


def _make_csp_decorator(config_attr_name, config_attr_value):
    """General CSP override decorator factory."""

    if not isinstance(config_attr_value, dict):
        raise TypeError("CSP config should be a mapping.")

    # Bind config_attr_name/config_attr_value once for each closure to avoid repeated lookups
    def decorator(view_func):
        # Use local variables for closure instead of attribute lookups inside wrapper
        setattr_ = setattr
        attr_name = config_attr_name
        attr_value = config_attr_value

        if iscoroutinefunction(view_func):

            @wraps(view_func)
            async def _wrapped_async_view(request, *args, **kwargs):
                response = await view_func(request, *args, **kwargs)
                setattr_(response, attr_name, attr_value)
                return response

            return _wrapped_async_view
        else:

            @wraps(view_func)
            def _wrapped_sync_view(request, *args, **kwargs):
                response = view_func(request, *args, **kwargs)
                setattr_(response, attr_name, attr_value)
                return response

            return _wrapped_sync_view

    return decorator


def csp_override(config):
    """Override the Content-Security-Policy header for a view."""
    return _make_csp_decorator("_csp_config", config)


def csp_report_only_override(config):
    """Override the Content-Security-Policy-Report-Only header for a view."""
    return _make_csp_decorator("_csp_ro_config", config)
