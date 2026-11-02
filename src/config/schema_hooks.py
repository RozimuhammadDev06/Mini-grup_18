def _get_operation(result, path, method):
    return result.get("paths", {}).get(path, {}).get(method)


def _add_link(response, name, operation, description, parameters=None):
    if not response or not operation:
        return

    links = response.setdefault("links", {})
    if name in links:
        return

    link = {
        "operationId": operation["operationId"],
        "description": description,
    }
    if parameters:
        link["parameters"] = parameters
    links[name] = link


def _response_has_id(response, schemas):
    def schema_has_id(schema, seen):
        if not isinstance(schema, dict):
            return False

        if "id" in schema.get("properties", {}):
            return True

        reference = schema.get("$ref")
        if reference:
            name = reference.rsplit("/", 1)[-1]
            if name not in seen:
                seen.add(name)
                if schema_has_id(schemas.get(name, {}), seen):
                    return True

        return any(
            schema_has_id(part, seen)
            for part in schema.get("allOf", [])
        )

    schema = (
        response.get("content", {})
        .get("application/json", {})
        .get("schema", {})
    )
    return schema_has_id(schema, set())


def add_relevant_response_links(result, generator, request, public):
    paths = result.get("paths", {})
    login_path = "/api/auth/login/"
    password_reset_path = "/api/auth/password/reset/request/"
    password_confirm_path = "/api/auth/password/reset/confirm/"
    profile_path = "/api/auth/profile/"
    payment_login_path = "/api/payments/login"
    payment_init_path = "/api/payments/pay/init/"

    auth_login = _get_operation(result, login_path, "post")
    password_reset = _get_operation(result, password_reset_path, "post")
    password_confirm = _get_operation(result, password_confirm_path, "post")
    profile_get = _get_operation(result, profile_path, "get")
    payment_init = _get_operation(result, payment_init_path, "post")

    # Authentication errors should lead to the relevant sign-in flow.
    for path, path_item in paths.items():
        for method, operation in path_item.items():
            if method not in {"get", "post", "put", "patch", "delete"}:
                continue

            unauthorized = operation.get("responses", {}).get("401")
            if path == login_path and method == "post":
                _add_link(
                    unauthorized,
                    "requestPasswordReset",
                    password_reset,
                    "Request a password reset if you cannot sign in.",
                )
            elif path.startswith("/api/payments/"):
                payment_login = _get_operation(
                    result,
                    payment_login_path,
                    "post",
                )
                _add_link(
                    unauthorized,
                    "paymentProviderLogin",
                    payment_login,
                    "Sign in to the payment provider, then retry with its "
                    "returned authorization token.",
                )
            else:
                _add_link(
                    unauthorized,
                    "signIn",
                    auth_login,
                    "Sign in and authorize the request before retrying.",
                )

    # Password and session errors have direct recovery operations.
    for path, method, name, target, description in (
        (
            "/api/auth/password/reset/confirm/",
            "post",
            "requestNewResetToken",
            password_reset,
            "Request a new password reset token if this one is invalid or expired.",
        ),
        (
            "/api/auth/password/change/",
            "post",
            "requestPasswordReset",
            password_reset,
            "Request a password reset if you do not know your current password.",
        ),
        (
            "/api/auth/logout/",
            "post",
            "signInAgain",
            auth_login,
            "Sign in again to obtain a valid refresh token.",
        ),
    ):
        operation = _get_operation(result, path, method)
        if operation:
            for response in operation.get("responses", {}).values():
                if response.get("description", "").lower() in {
                    "invalid or expired reset token.",
                    "current password is incorrect.",
                    "invalid or expired refresh token.",
                }:
                    _add_link(
                        response,
                        name,
                        target,
                        description,
                    )

    _add_link(
        _get_operation(result, password_reset_path, "post")
        .get("responses", {})
        .get("200"),
        "confirmPasswordReset",
        password_confirm,
        "Submit the reset token received by email and choose a new password.",
    )
    _add_link(
        _get_operation(result, password_confirm_path, "post")
        .get("responses", {})
        .get("200"),
        "signIn",
        auth_login,
        "Sign in with the new password.",
    )
    _add_link(
        _get_operation(result, login_path, "post")
        .get("responses", {})
        .get("200"),
        "getCurrentProfile",
        profile_get,
        "Authorize with the returned access token, then retrieve the profile.",
    )
    _add_link(
        _get_operation(result, profile_path, "patch")
        .get("responses", {})
        .get("200"),
        "getUpdatedProfile",
        profile_get,
        "Retrieve the updated profile.",
    )
    _add_link(
        _get_operation(result, "/api/auth/token/refresh/", "post")
        .get("responses", {})
        .get("200"),
        "getCurrentProfile",
        profile_get,
        "Authorize with the refreshed access token, then retrieve the profile.",
    )
    _add_link(
        _get_operation(result, profile_path, "get")
        .get("responses", {})
        .get("200"),
        "manageAddresses",
        _get_operation(result, "/api/auth/addresses/", "get"),
        "View and manage the addresses associated with this account.",
    )
    _add_link(
        _get_operation(result, "/api/auth/password/change/", "post")
        .get("responses", {})
        .get("200"),
        "getCurrentProfile",
        profile_get,
        "Retrieve the profile after changing the password.",
    )
    _add_link(
        _get_operation(result, "/api/auth/register/", "post")
        .get("responses", {})
        .get("201"),
        "signIn",
        auth_login,
        "Sign in after registering.",
    )
    _add_link(
        _get_operation(result, "/api/auth/logout/", "post")
        .get("responses", {})
        .get("205"),
        "signInAgain",
        auth_login,
        "Sign in again when you are ready to start a new session.",
    )

    # CRUD responses link to an existing read operation for the same resource.
    for path, path_item in paths.items():
        for method, operation in path_item.items():
            if method not in {"get", "post", "put", "patch", "delete"}:
                continue

            if method == "post":
                response = operation.get("responses", {}).get("201")
                if not response:
                    continue

                detail_path = f"{path.rstrip('/')}/{{id}}/"
                retrieve = _get_operation(result, detail_path, "get")
                if retrieve and _response_has_id(
                    response,
                    result.get("components", {}).get("schemas", {}),
                ):
                    _add_link(
                        response,
                        "retrieveCreatedResource",
                        retrieve,
                        "Retrieve the resource created by this request.",
                        {"id": "$response.body#/id"},
                    )
                continue

            if "{id}" not in path:
                continue

            collection_path = path.split("{id}", 1)[0]
            collection = _get_operation(result, collection_path, "get")
            retrieve = _get_operation(result, path, "get")

            if method in {"put", "patch"}:
                response = operation.get("responses", {}).get("200")
                _add_link(
                    response,
                    "retrieveUpdatedResource",
                    retrieve,
                    "Retrieve the resource after updating it.",
                    {"id": "$request.path.id"},
                )
            elif method == "delete":
                response = operation.get("responses", {}).get("204")
                _add_link(
                    response,
                    "listResources",
                    collection,
                    "Return to the resource collection.",
                )
            elif method == "get":
                response = operation.get("responses", {}).get("200")
                _add_link(
                    response,
                    "listResources",
                    collection,
                    "Browse the resource collection.",
                )

            not_found = operation.get("responses", {}).get("404")
            _add_link(
                not_found,
                "listResources",
                collection,
                "Browse the collection to find an existing resource.",
            )

    # FintechHub's card-token flow requests verification before payment.
    payment_paths = {
        path.rstrip("/"): item
        for path, item in paths.items()
        if path.startswith("/api/payments/")
    }
    card_request = payment_paths.get("/api/payments/card/request")
    card_verify = payment_paths.get("/api/payments/card/verify")
    card_payment = payment_paths.get("/api/payments/card/payment")
    payment_register = _get_operation(
        result,
        "/api/payments/register/",
        "post",
    )
    for login_route in (payment_login_path, "/api/payments/login/"):
        payment_login = _get_operation(result, login_route, "post")
        if payment_login:
            _add_link(
                payment_login.get("responses", {}).get("400"),
                "registerPaymentProviderAccount",
                payment_register,
                "If you do not already have a payment-provider account, "
                "register one before signing in.",
            )
            _add_link(
                payment_login.get("responses", {}).get("200"),
                "startPayment",
                payment_init,
                "Start a payment using the payment-provider token.",
            )
    _add_link(
        payment_register.get("responses", {}).get("201")
        if payment_register
        else None,
        "paymentProviderLogin",
        _get_operation(result, payment_login_path, "post"),
        "Sign in to the payment provider after registering.",
    )

    for path, path_item in paths.items():
        if not path.endswith("/") or path.startswith("/api/payments/"):
            continue
        list_operation = path_item.get("get")
        create_operation = path_item.get("post")
        if list_operation and create_operation:
            _add_link(
                list_operation.get("responses", {}).get("200"),
                "createResource",
                create_operation,
                "Create a new resource in this collection.",
            )

    for version_prefix in ("/api/", "/api/v1/"):
        _add_link(
            _get_operation(
                result,
                f"{version_prefix}news/rubrics/",
                "get",
            )
            .get("responses", {})
            .get("200"),
            "browseNews",
            _get_operation(
                result,
                f"{version_prefix}news/",
                "get",
            ),
            "Browse news articles by rubric.",
        )
        _add_link(
            _get_operation(
                result,
                f"{version_prefix}products/filters/",
                "get",
            )
            .get("responses", {})
            .get("200"),
            "browseProducts",
            _get_operation(
                result,
                f"{version_prefix}products/",
                "get",
            ),
            "Browse products using the available filters.",
        )

    if card_request and card_verify:
        _add_link(
            card_request.get("post", {}).get("responses", {}).get("200"),
            "verifyCardToken",
            card_verify.get("post"),
            "Submit the verification code sent for the card-token request.",
        )
    if card_verify and card_payment:
        _add_link(
            card_verify.get("post", {}).get("responses", {}).get("200"),
            "makeCardPayment",
            card_payment.get("post"),
            "Submit the payment after the card token is verified.",
        )

    return result
