import unittest

from env_assert import EnvAssertError, assert_env


class AssertEnvTests(unittest.TestCase):
    def test_valid_schema(self) -> None:
        env = assert_env(
            {
                "PORT": {"type": "int", "min": 1, "max": 65535},
                "DEBUG": {"type": "bool", "default": False},
                "MODE": {"type": "enum", "values": ["dev", "prod"]},
                "API_URL": {"type": "url"},
            },
            {"PORT": "3000", "MODE": "dev", "API_URL": "https://example.com"},
        )
        self.assertEqual(env["PORT"], 3000)
        self.assertEqual(env["DEBUG"], False)
        self.assertEqual(env["MODE"], "dev")

    def test_aggregates_errors(self) -> None:
        with self.assertRaises(EnvAssertError) as ctx:
            assert_env(
                {
                    "A": {"type": "string"},
                    "B": {"type": "int"},
                },
                {"B": "nope"},
            )
        self.assertEqual(ctx.exception.missing, ["A"])
        self.assertEqual(ctx.exception.invalid[0][0], "B")


if __name__ == "__main__":
    unittest.main()
