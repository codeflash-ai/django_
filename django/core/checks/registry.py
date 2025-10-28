from collections.abc import Iterable
from itertools import chain

from django.utils.inspect import func_accepts_kwargs


class Tags:
    """
    Built-in tags for internal checks.
    """

    admin = "admin"
    async_support = "async_support"
    caches = "caches"
    commands = "commands"
    compatibility = "compatibility"
    database = "database"
    files = "files"
    models = "models"
    security = "security"
    signals = "signals"
    sites = "sites"
    staticfiles = "staticfiles"
    templates = "templates"
    translation = "translation"
    urls = "urls"


class CheckRegistry:
    def __init__(self):
        self.registered_checks = set()
        self.deployment_checks = set()

    def register(self, check=None, *tags, **kwargs):
        """
        Can be used as a function or a decorator. Register given function
        `f` labeled with given `tags`. The function should receive **kwargs
        and return list of Errors and Warnings.

        Example::

            registry = CheckRegistry()
            @registry.register('mytag', 'anothertag')
            def my_check(app_configs, **kwargs):
                # ... perform checks and collect `errors` ...
                return errors
            # or
            registry.register(my_check, 'mytag', 'anothertag')
        """

        def inner(check):
            if not func_accepts_kwargs(check):
                raise TypeError(
                    "Check functions must accept keyword arguments (**kwargs)."
                )
            check.tags = tags
            checks = (
                self.deployment_checks
                if kwargs.get("deploy")
                else self.registered_checks
            )
            checks.add(check)
            return check

        if callable(check):
            return inner(check)
        else:
            if check:
                tags += (check,)
            return inner

    def run_checks(
        self,
        app_configs=None,
        tags=None,
        include_deployment_checks=False,
        databases=None,
    ):
        """
        Run all registered checks and return list of Errors and Warnings.
        """
        errors = []
        checks = self.get_checks(include_deployment_checks)

        # Optimize tag filtering by using set logic only once and using generator expression.
        if tags is not None:
            tags = set(tags)
            # Use generator expression for memory efficiency
            checks = (
                check
                for check in checks
                if check.tags and not set(check.tags).isdisjoint(tags)
            )

        # Loop optimization: instead of repeatedly checking isinstance in every iteration,
        # we minimize list extension cost by using a local errors list, and avoid extending for empty results.
        append_error = errors.extend
        iterable_type = Iterable

        for check in checks:
            new_errors = check(app_configs=app_configs, databases=databases)
            if not isinstance(new_errors, iterable_type):
                raise TypeError(
                    "The function %r did not return a list. All functions "
                    "registered with the checks registry must return a list." % check,
                )
            # Only extend when non-empty to reduce overhead
            if new_errors:
                append_error(new_errors)
        return errors

    def tag_exists(self, tag, include_deployment_checks=False):
        return tag in self.tags_available(include_deployment_checks)

    def tags_available(self, deployment_checks=False):
        return set(
            chain.from_iterable(
                check.tags for check in self.get_checks(deployment_checks)
            )
        )

    def get_checks(self, include_deployment_checks=False):
        # Use set union to avoid intermediate list extension
        if include_deployment_checks:
            return list(self.registered_checks | self.deployment_checks)
        else:
            return list(self.registered_checks)


registry = CheckRegistry()
register = registry.register
run_checks = registry.run_checks
tag_exists = registry.tag_exists
