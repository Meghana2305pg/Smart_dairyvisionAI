import unittest

from webapp.services.auth_service import AuthService


class DummySession:
    def __init__(self) -> None:
        self.access_token = "token"

    def model_dump(self) -> dict[str, str]:
        return {"access_token": self.access_token}


class DummyUser:
    def __init__(self, email: str) -> None:
        self.id = "user-123"
        self.email = email


class DummyAuthClient:
    def __init__(self) -> None:
        self.calls: list[dict[str, str]] = []

    def sign_in_with_password(self, payload: dict[str, str]):
        self.calls.append(payload)
        return type(
            "Response",
            (),
            {
                "user": DummyUser(payload["email"]),
                "session": DummySession(),
            },
        )()


class DummySupabaseClient:
    def __init__(self) -> None:
        self.client = type("Client", (), {"auth": DummyAuthClient()})()


class AuthServiceLoginTests(unittest.TestCase):
    def test_login_normalizes_email_before_signing_in(self) -> None:
        client = DummySupabaseClient()
        service = AuthService(client=client)

        result = service.login(" User@Example.COM ", "secret")

        self.assertTrue(result)
        self.assertEqual(client.client.auth.calls[0]["email"], "user@example.com")
        self.assertEqual(client.client.auth.calls[0]["password"], "secret")


if __name__ == "__main__":
    unittest.main()
