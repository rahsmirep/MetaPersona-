from concurrent.futures import ThreadPoolExecutor

print("[TEST] About to create ThreadPoolExecutor")
with ThreadPoolExecutor(max_workers=4) as executor:
    print("[TEST] ThreadPoolExecutor created successfully")
    future = executor.submit(lambda: 42)
    result = future.result()
    print(f"[TEST] Got result from thread: {result}")
print("[TEST] ThreadPoolExecutor closed")
