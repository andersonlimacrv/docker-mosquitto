error_openssl_map = {
    "unable to get local issuer certificate": {
        "tag": "[UNABLE TO GET LOCAL ISSUER CERTIFICATE]",
        "description": "The client certificate could not be validated because the issuing CA was not found. Make sure the client was signed by the same CA or that the full certificate chain is provided."
    },
    "unable to get issuer certificate": {
        "tag": "[UNABLE TO GET ISSUER CERTIFICATE]",
        "description": "The issuing CA certificate could not be located or is missing from the CA file."
    },
    "self signed certificate in certificate chain": {
        "tag": "[SELF SIGNED CERTIFICATE IN CERTIFICATE CHAIN]",
        "description": "A self-signed certificate was found in the chain and is not trusted."
    },
    "certificate has expired": {
        "tag": "[CERTIFICATE HAS EXPIRED]",
        "description": "The certificate is no longer valid because its expiration date has passed."
    },
    "verification failed": {
        "tag": "[VERIFICATION FAILED]",
        "description": "Certificate verification failed. The CA file might be incorrect or the chain incomplete."
    },
}


def interpret_openssl_error(output: str) -> tuple[str, str] | None:
    """
    Return a tuple of (TAG, description) for known OpenSSL errors.
    Returns None if no match is found.
    """
    for key, value in error_openssl_map.items():
        if key in output:
            return value["tag"], value["description"]
    return None