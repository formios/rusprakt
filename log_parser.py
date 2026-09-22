import collections

def parse_logs(input_file, output_file):
    counts = collections.Counter()
    with open(input_file, 'r', encoding='utf-8') as f_in, open(output_file, 'w', encoding='utf-8') as f_out:
        for line in f_in:
            if "ERROR" in line:
                f_out.write(line)
                parts = line.split("ERROR")
                err_msg = parts[1].strip() if len(parts) > 1 else "Unknown"
                counts[err_msg] += 1
    return counts

if __name__ == "__main__":
    error_counts = parse_logs("server.log", "errors.log")
    for msg, count in error_counts.items():
        print(f"{msg}: {count}")