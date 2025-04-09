import time
from monitor_resources import start_stress_test

test_scenarios = [
    # Format: (duration, threads, ramp_time, database, query_type)

    # --- PostgreSQL scenarios ---
    (1800, 100, 60, 'pg', 'insert'),
    (1800, 100, 60, 'pg', 'update'),
    (1800, 100, 60, 'pg', 'read'),
    (1800, 100, 60, 'pg', 'mixed'),

    (1800, 200, 120, 'pg', 'insert'),
    (1800, 200, 120, 'pg', 'update'),
    (1800, 200, 120, 'pg', 'read'),
    (1800, 200, 120, 'pg', 'mixed'),

    (1800, 400, 240, 'pg', 'insert'),
    (1800, 400, 240, 'pg', 'update'),
    (1800, 400, 240, 'pg', 'read'),
    (1800, 400, 240, 'pg', 'mixed'),

    # --- MongoDB scenarios ---
    (1800, 100, 60, 'mongo', 'insert'),
    (1800, 100, 60, 'mongo', 'update'),
    (1800, 100, 60, 'mongo', 'read'),
    (1800, 100, 60, 'mongo', 'mixed'),

    (1800, 200, 120, 'mongo', 'insert'),
    (1800, 200, 120, 'mongo', 'update'),
    (1800, 200, 120, 'mongo', 'read'),
    (1800, 200, 120, 'mongo', 'mixed'),

    (1800, 400, 240, 'mongo', 'insert'),
    (1800, 400, 240, 'mongo', 'update'),
    (1800, 400, 240, 'mongo', 'read'),
    (1800, 400, 240, 'mongo', 'mixed'),
]

# test_scenarios = [
#     (1800, 400, 240, 'pg', 'insert'),
#     (1800, 400, 240, 'pg', 'read'),
#     (1800, 400, 240, 'mongo', 'insert'),
#     (1800, 400, 240, 'mongo', 'read'),
# ]

def run_all_tests():
    for i, scenario in enumerate(test_scenarios):
        duration, threads, ramp_time, db, query_type = scenario

        print(f"\n--- Running Test {i+1}/{len(test_scenarios)} ---")
        print(f"→ Duration: {duration}s | Threads: {threads} | Ramp-up: {ramp_time}s | DB: {db} | Type: {query_type}")

        start_stress_test(duration, threads, ramp_time, db, query_type)

        if i < len(test_scenarios) - 1:
            print(f"✅ Finished Test {i+1}, waiting 5 minutes before next...\n")
            time.sleep(300)  # 5-minute cooldown before next test

    print("🎉 All tests completed!")

if __name__ == "__main__":
    run_all_tests()
