import json
import argparse

def main():
    parser = argparse.ArgumentParser(description='Format JSON files for easier viewing')
    parser.add_argument('-i', '--input', required=True, help='Input JSON file')
    parser.add_argument('-o', '--output', required=True, help='Output formatted JSON file')
    
    args = parser.parse_args()
    
    # Read the file
    with open(args.input, 'r') as f:
        data = json.load(f)
    
    # Write it back formatted
    with open(args.output, 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"Successfully formatted {args.input} -> {args.output}")

if __name__ == '__main__':
    main()
