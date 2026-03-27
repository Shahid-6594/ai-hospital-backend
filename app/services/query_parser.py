def parse_query(query: str):

    query = query.lower().strip()

    result = {
        "service": None,
        "sort_by_price": False,
        "sort_by_rating": False,
        "nearby": False
    }

    # Service keywords mapping
    service_map = {
        "x ray": ["x ray", "x-ray", "xray"],
        "blood test": ["blood test", "blood", "test"],
        "mri": ["mri", "mri scan"],
        "ct scan": ["ct", "ct scan", "ct-scan"],
        "ultrasound": ["ultrasound", "sonography"],
    }

    # Detect service
    for service_name, keywords in service_map.items():
        for word in keywords:
            if word in query:
                result["service"] = service_name
                break
        if result["service"]:
            break

    # Price keywords
    cheap_keywords = ["cheap", "low cost", "affordable", "budget"]
    for word in cheap_keywords:
        if word in query:
            result["sort_by_price"] = True

    # Rating keywords
    rating_keywords = ["best", "top", "good", "rating"]
    for word in rating_keywords:
        if word in query:
            result["sort_by_rating"] = True

    # Nearby keywords
    nearby_keywords = ["near me", "nearby", "close"]
    for word in nearby_keywords:
        if word in query:
            result["nearby"] = True

    print("PARSED:", result)

    return result