def detect_relevant_sections(query):

    query = query.lower()

    if any(word in query for word in [
        "methodology",
        "method",
        "architecture",
        "training",
        "optimizer",
        "hyperparameter"
    ]):
        return ["methodology"]

    elif any(word in query for word in [
        "experiment",
        "evaluation",
        "benchmark",
        "dataset"
    ]):
        return ["experiments", "results"]

    elif any(word in query for word in [
        "result",
        "performance",
        "accuracy"
    ]):
        return ["results"]

    elif any(word in query for word in [
        "conclusion",
        "future work"
    ]):
        return ["conclusion"]

    else:
        return []