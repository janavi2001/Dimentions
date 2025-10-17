class StorageClient:
    def put(self, key: str, data: bytes) -> str:
        return f'mem://{key}'
