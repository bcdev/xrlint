from ..node import AttrNode
from ..node import AttrsNode
from ..node import DataArrayNode
from ..node import DatasetNode
from xrlint.rule import RuleOp
from .rule_ctx_impl import RuleContextImpl


def verify_dataset(verifier: RuleOp, context: RuleContextImpl):
    _verify_dataset_node(
        verifier,
        context,
        DatasetNode(parent=None, path="dataset", dataset=context.dataset),
    )


def _verify_dataset_node(verifier: RuleOp, context: RuleContextImpl, node: DatasetNode):
    with context.use_state(node=node):
        verifier.dataset(context, node)
        _verify_attrs_node(
            verifier,
            context,
            AttrsNode(
                parent=node,
                path=f"{node.path}.attrs",
                attrs=node.dataset.attrs,
            ),
        )
        for name, data_array in node.dataset.coords.items():
            _verify_data_array_node(
                verifier,
                context,
                DataArrayNode(
                    parent=node,
                    path=f"{node.path}.coords[{name!r}]",
                    name=name,
                    data_array=data_array,
                ),
            )
        for name, data_array in node.dataset.data_vars.items():
            _verify_data_array_node(
                verifier,
                context,
                DataArrayNode(
                    parent=node,
                    path=f"{node.path}.data_vars[{name!r}]",
                    name=name,
                    data_array=data_array,
                ),
            )


def _verify_data_array_node(
    verifier: RuleOp, context: RuleContextImpl, node: DataArrayNode
):
    with context.use_state(node=node):
        verifier.data_array(context, node)
        _verify_attrs_node(
            verifier,
            context,
            AttrsNode(
                parent=node,
                path=f"{node.path}.attrs",
                attrs=node.data_array.attrs,
            ),
        )


def _verify_attrs_node(verifier: RuleOp, context: RuleContextImpl, node: AttrsNode):
    with context.use_state(node=node):
        verifier.attrs(context, node)
        for name, value in node.attrs.items():
            _verify_attr_node(
                verifier,
                context,
                AttrNode(
                    parent=node,
                    name=name,
                    value=value,
                    path=f"{node.path}[{name!r}]",
                ),
            )


def _verify_attr_node(verifier: RuleOp, context: RuleContextImpl, node: AttrNode):
    with context.use_state(node=node):
        verifier.attr(context, node)
