from unittest import TestCase


class AllTest(TestCase):
    def test_api_is_complete(self):
        import xrlint.all as xrl

        # noinspection PyProtectedMember
        from xrlint.all import __all__

        # noinspection PyUnresolvedReferences
        keys = set(
            k
            for k, v in xrl.__dict__.items()
            if isinstance(k, str) and not k.startswith("_")
        )
        self.assertEqual(set(__all__), keys)
