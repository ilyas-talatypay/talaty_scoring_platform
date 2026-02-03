def dataset_prefix(dataset_id: str, version: str) -> str:
    return f"datasets/{dataset_id}/{version}/"


def feature_set_prefix(feature_set_id: str, version: str) -> str:
    return f"featuresets/{feature_set_id}/{version}/"


def run_prefix(run_id: str) -> str:
    return f"runs/{run_id}/"


def report_prefix(run_id: str) -> str:
    return f"reports/{run_id}/"

