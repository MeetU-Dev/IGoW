import time
from image_hash import mine_block


def benchmark(data: str = "BENCH", difficulty: int = 2, width: int = 10, height: int = 10, workers_list=None):
    if workers_list is None:
        workers_list = [1, 2, 4]

    results = []
    for w in workers_list:
        start = time.time()
        res = mine_block(data, difficulty, width, height, max_workers=w)
        end = time.time()
        duration = round(end - start, 4)
        results.append((w, res["attempts"], res["elapsed"], duration))
        print(f"workers={w} attempts={res['attempts']} elapsed={res['elapsed']} wall={duration}s")
    return results


if __name__ == '__main__':
    benchmark()
