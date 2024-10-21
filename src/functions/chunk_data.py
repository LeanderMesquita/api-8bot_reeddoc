def chunk_data(data, size):
    return [data[i:i + size] for i in range(0, len(data), size)]