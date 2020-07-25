import resource

_resource_nums = set()
for name in dir(resource):
    if name.startswith("RLIMIT_"):
        _resource_nums.add(getattr(resource, name))


def check_rlimit_resource(res: int) -> None:
    if res not in _resource_nums:
        raise ValueError("invalid resource specified")
