from unittest import TestCase

from xrlint.util.naming import to_kebab_case
from xrlint.util.naming import to_snake_case


class NamingTest(TestCase):
    def test_to_kebab_case(self):
        self.assertEqual("", to_kebab_case(""))
        self.assertEqual("rule", to_kebab_case("rule"))
        self.assertEqual("rule", to_kebab_case("Rule"))
        self.assertEqual("my-rule", to_kebab_case("MyRule"))
        self.assertEqual("my-rule-a", to_kebab_case("MyRuleA"))
        self.assertEqual("my-rule-3", to_kebab_case("MyRule3"))
        self.assertEqual("my-rule-3", to_kebab_case("MyRule_3"))
        self.assertEqual("my-rule-3", to_kebab_case("My_Rule_3"))
        self.assertEqual("my-rule-3", to_kebab_case("my-rule-3"))
        self.assertEqual("my-rule-3", to_kebab_case("My-Rule-3"))
        self.assertEqual("my-rule-3", to_kebab_case("My-Rule 3"))
        self.assertEqual("abc-rule-123", to_kebab_case("ABCRule123"))
        self.assertEqual("abc-rule-xyz", to_kebab_case("ABCRuleXYZ"))

    def test_to_snake_case(self):
        self.assertEqual("", to_snake_case(""))
        self.assertEqual("rule", to_snake_case("rule"))
        self.assertEqual("rule", to_snake_case("Rule"))
        self.assertEqual("my_rule", to_snake_case("MyRule"))
        self.assertEqual("my_rule_a", to_snake_case("MyRuleA"))
        self.assertEqual("my_rule_3", to_snake_case("MyRule3"))
        self.assertEqual("my_rule_3", to_snake_case("MyRule_3"))
        self.assertEqual("my_rule_3", to_snake_case("My_Rule_3"))
        self.assertEqual("my_rule_3", to_snake_case("my-rule-3"))
        self.assertEqual("my_rule_3", to_snake_case("My-Rule-3"))
        self.assertEqual("my_rule_3", to_snake_case("My-Rule 3"))
        self.assertEqual("abc_rule_123", to_snake_case("ABCRule123"))
        self.assertEqual("abc_rule_xyz", to_snake_case("ABCRuleXYZ"))
