from .handler import handle

# Test your handler here

# To disable testing, you can set the build_arg `TEST_ENABLED=false` on the CLI or in your stack.yml
# https://docs.openfaas.com/reference/yaml/#function-build-args-build-args

def test_handle():
    # Simulate the event and context
    class MockEvent:
        def __init__(self, body):
            self.body = body

    # Test with a valid username
    event = MockEvent("testuser")
    result = handle(event, None)
    assert result["statusCode"] == 200
    assert "body" in result
    assert isinstance(result["body"], str)  # Ensure the body is a string (base64 encoded QR code)

    # Test with an empty username
    event = MockEvent("")
    result = handle(event, None)
    assert result["statusCode"] == 400
    assert result["body"] == "Missing username"
