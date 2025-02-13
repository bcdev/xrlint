#  Copyright © 2025 Brockmann Consult GmbH.
#  This software is distributed under the terms and conditions of the
#  MIT license (https://mit-license.org/).

from xrlint.node import AttrNode, AttrsNode, DatasetNode, DataTreeNode, VariableNode
from xrlint.rule import RuleConfig, RuleExit, RuleOp

from ..constants import DATASET_ROOT_NAME, DATATREE_ROOT_NAME
from .rulectx import RuleContextImpl


def apply_rule(
    ctx: RuleContextImpl,
    rule_id: str,
    rule_config: RuleConfig,
):
    """Apply rule given by `rule_id` to dataset given in
    `context` using rule configuration `rule_config`.
    """
    try:
        rule = ctx.config.get_rule(rule_id)
    except ValueError as e:
        ctx.report(f"{e}", fatal=True)
        return

    if rule_config.severity == 0:
        # rule is off
        return

    with ctx.use_state(severity=rule_config.severity):
        # TODO: validate rule_config.args/kwargs against rule.meta.schema
        # noinspection PyArgumentList
        rule_op: RuleOp = rule.op_class(*rule_config.args, **rule_config.kwargs)
        try:
            if ctx.datatree is not None:
                name = (
                    DATATREE_ROOT_NAME
                    if ctx.file_index is None
                    else f"{DATATREE_ROOT_NAME}[{ctx.file_index}]"
                )
                _visit_datatree_node(
                    rule_op,
                    ctx,
                    DataTreeNode(
                        parent=None, path=name, name=name, datatree=ctx.datatree
                    ),
                )
            else:
                name = (
                    DATASET_ROOT_NAME
                    if ctx.file_index is None
                    else f"{DATASET_ROOT_NAME}[{ctx.file_index}]"
                )
                _visit_dataset_node(
                    rule_op,
                    ctx,
                    DatasetNode(parent=None, path=name, name=name, dataset=ctx.dataset),
                )
        except RuleExit:
            # This is ok, the rule requested it.
            pass


def _visit_datatree_node(rule_op: RuleOp, context: RuleContextImpl, node: DataTreeNode):
    with context.use_state(node=node):
        rule_op.validate_datatree(context, node)
        if node.datatree.is_leaf:
            _visit_dataset_node(
                rule_op,
                context,
                DatasetNode(
                    parent=node,
                    path=f"{node.path}/{node.datatree.name}",
                    name=node.datatree.name,
                    dataset=node.datatree.dataset,
                ),
            )
        else:
            for name, datatree in node.datatree.children.items():
                _visit_datatree_node(
                    rule_op,
                    context,
                    DataTreeNode(
                        parent=node,
                        path=f"{node.path}/{name}",
                        name=name,
                        datatree=datatree,
                    ),
                )


def _visit_dataset_node(rule_op: RuleOp, context: RuleContextImpl, node: DatasetNode):
    with context.use_state(dataset=node.dataset, node=node):
        rule_op.validate_dataset(context, node)
        _visit_attrs_node(
            rule_op,
            context,
            AttrsNode(
                parent=node,
                path=f"{node.path}.attrs",
                attrs=node.dataset.attrs,
            ),
        )
        for name, variable in node.dataset.coords.items():
            _visit_variable_node(
                rule_op,
                context,
                VariableNode(
                    parent=node,
                    path=f"{node.path}.coords[{name!r}]",
                    name=name,
                    array=variable,
                ),
            )
        for name, variable in node.dataset.data_vars.items():
            _visit_variable_node(
                rule_op,
                context,
                VariableNode(
                    parent=node,
                    path=f"{node.path}.data_vars[{name!r}]",
                    name=name,
                    array=variable,
                ),
            )


def _visit_variable_node(rule_op: RuleOp, context: RuleContextImpl, node: VariableNode):
    with context.use_state(node=node):
        rule_op.validate_variable(context, node)
        _visit_attrs_node(
            rule_op,
            context,
            AttrsNode(
                parent=node,
                path=f"{node.path}.attrs",
                attrs=node.array.attrs,
            ),
        )


def _visit_attrs_node(rule_op: RuleOp, context: RuleContextImpl, node: AttrsNode):
    with context.use_state(node=node):
        rule_op.validate_attrs(context, node)
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
        rule_op.validate_attr(context, node)
