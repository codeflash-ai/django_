"""
A collection of utility routines and classes used by the spatial
backends.
"""


class SpatialOperator:
    """
    Class encapsulating the behavior specific to a GIS operation (used by
    lookups).
    """

    sql_template = None

    def __init__(self, op=None, func=None):
        self.op = op
        self.func = func

    @property
    def default_template(self):
        if self.func:
            return "%(func)s(%(lhs)s, %(rhs)s)"
        else:
            return "%(lhs)s %(op)s %(rhs)s"

    def as_sql(self, connection, lookup, template_params, sql_params):
        sql_template = self.sql_template
        if sql_template is None:
            sql_template = lookup.sql_template
            if sql_template is None:
                sql_template = self.default_template
        template_params["op"] = self.op
        template_params["func"] = self.func
        return sql_template % template_params, sql_params
