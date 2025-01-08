from xrlint.node import AttrNode
from xrlint.node import AttrsNode
from xrlint.node import DataArrayNode
from xrlint.node import DatasetNode
from xrlint.rule import RuleConfig
from xrlint.rule import RuleExit
from xrlint.rule import RuleOp
from .rulectx import RuleContextImpl


def apply_rule(
    context: RuleContextImpl,
    rule_id: str,
    rule_config: RuleConfig,
):
    """Apply rule given by `rule_id` to dataset given in
    `context` using rule configuration `rule_config`.
    """
    try:
        rule = context.config.get_rule(rule_id)
    except ValueError as e:
        context.report(f"{e}", fatal=True)
        return

    if rule_config.severity == 0:
        # rule is off
        return

    with context.use_state(severity=rule_config.severity):
        # TODO: validate rule_config.args/kwargs against rule.meta.schema
        # noinspection PyArgumentList
        rule_op: RuleOp = rule.op_class(*rule_config.args, **rule_config.kwargs)
        try:
            _visit_dataset_node(
                rule_op,
                context,
                DatasetNode(parent=None, path="dataset", dataset=context.dataset),
            )
        except RuleExit:
            # This is ok, the rule requested it.
            pass


def _visit_dataset_node(rule_op: RuleOp, context: RuleContextImpl, node: DatasetNode):
    with context.use_state(node=node):
        rule_op.dataset(context, node)
        _visit_attrs_node(
            rule_op,
            context,
            AttrsNode(
                parent=node,
                path=f"{node.path}.attrs",
                attrs=node.dataset.attrs,
            ),
        )
        for name, data_array in node.dataset.coords.items():
            _visit_data_array_node(
                rule_op,
                context,
                DataArrayNode(
                    parent=node,
                    path=f"{node.path}.coords[{name!r}]",
                    name=name,
                    data_array=data_array,
                ),
            )
        for name, data_array in node.dataset.data_vars.items():
            _visit_data_array_node(
                rule_op,
                context,
                DataArrayNode(
                    parent=node,
                    path=f"{node.path}.data_vars[{name!r}]",
                    name=name,
                    data_array=data_array,
                ),
            )


def _visit_data_array_node(
    rule_op: RuleOp, context: RuleContextImpl, node: DataArrayNode
):
    with context.use_state(node=node):
        rule_op.data_array(context, node)
        _visit_attrs_node(
            rule_op,
            context,
            AttrsNode(
                parent=node,
                path=f"{node.path}.attrs",
                attrs=node.data_array.attrs,
            ),
        )


def _visit_attrs_node(rule_op: RuleOp, context: RuleContextImpl, node: AttrsNode):
    with context.use_state(node=node):
        rule_op.attrs(context, node)
        for name, value in node.attrs.items():
            _visit_attr_node(
                rule_op,
                context,
                AttrNode(
                    parent=node,
                    name=name,
                    value=value,
                    path=f"{node.path}[{name!r}]",
                ),
            )


def _visit_attr_node(rule_op: RuleOp, context: RuleContextImpl, node: AttrNode):
    with context.use_state(node=node):
        rule_op.attr(context, node)
