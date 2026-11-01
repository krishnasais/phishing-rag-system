import ipaddress
from urllib.parse import urlparse


def inspect_url(raw_url):

    url = (raw_url or "").strip()

    if not url:
        return {
            "input": "",
            "hostname": "",
            "scheme": "",
            "findings": ["No URL entered."],
            "warning_count": 0,
            "risk_score": 0,
            "risk_label": "Not assessed",
            "is_valid_format": False
        }

    # Add HTTP scheme if missing
    candidate = (
        url if "://" in url
        else "http://" + url
    )

    # Parse URL
    try:
        parsed = urlparse(candidate)
        host = (parsed.hostname or "").lower()

        # Validate malformed ports/authority
        _ = parsed.port

    except ValueError:
        return {
            "input": url,
            "hostname": "",
            "scheme": "",
            "findings": [
                "This text is not a valid URL format."
            ],
            "warning_count": 0,
            "risk_score": 0,
            "risk_label": "Not assessed",
            "is_valid_format": False
        }

    if not host:
        return {
            "input": url,
            "hostname": "",
            "scheme": parsed.scheme.lower(),
            "findings": [
                "Could not identify a hostname."
            ],
            "warning_count": 0,
            "risk_score": 0,
            "risk_label": "Not assessed",
            "is_valid_format": False
        }

    findings = []

    # 1. Check @ symbol
    if "@" in candidate:
        findings.append(
            "Contains an @ symbol; inspect carefully."
        )

    # 2. Check URL length
    if len(url) > 100:
        findings.append(
            "Unusually long URL (over 100 characters)."
        )

    # 3. Check IPv4 hostname
    try:
        ipaddress.IPv4Address(host)

        findings.append(
            "Uses an IP address instead of a familiar domain."
        )

    except ipaddress.AddressValueError:
        pass

    # 4. Check hostname segments
    labels = [
        part for part in host.split(".") if part
    ]

    if len(labels) >= 5:
        findings.append(
            "Contains many hostname segments/subdomains."
        )

    # 5. Check Punycode
    if any(label.startswith("xn--") for label in labels):
        findings.append(
            "Contains a punycode-style hostname."
        )

    # 6. Check HTTP scheme
    if parsed.scheme.lower() == "http":
        findings.append(
            "Uses HTTP. HTTPS alone does not prove trust."
        )

    # Heuristic risk score
    weights = {
        "Contains an @ symbol; inspect carefully.": 20,
        "Unusually long URL (over 100 characters).": 10,
        "Uses an IP address instead of a familiar domain.": 20,
        "Contains many hostname segments/subdomains.": 15,
        "Contains a punycode-style hostname.": 20,
        "Uses HTTP. HTTPS alone does not prove trust.": 15
    }

    score = min(
        100,
        sum(weights[item] for item in findings)
    )

    if score == 0:
        risk_label = "No listed indicators"
    elif score < 30:
        risk_label = "Low indicator score"
    elif score < 60:
        risk_label = "Moderate indicator score"
    else:
        risk_label = "Elevated indicator score"

    if not findings:
        findings.append(
            "No listed warning signs found. "
            "This does NOT prove safety."
        )

    warning_count = len([
        item for item in findings
        if not item.startswith("No listed warning signs")
    ])

    return {
        "input": url,
        "hostname": host,
        "scheme": parsed.scheme.lower(),
        "findings": findings,
        "warning_count": warning_count,
        "risk_score": score,
        "risk_label": risk_label,
        "is_valid_format": True
    }