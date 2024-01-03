from dbdpy.apple_watch import AppleWatch

def read_file(filepath: str) -> AppleWatch:
    return AppleWatch.read_file(filepath)