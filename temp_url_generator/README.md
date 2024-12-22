# Temp URL Generator

This project contains a Python script to generate temporary URLs. The script is located in the `temp_url_generator.py` file.

## Features

- Generate temporary URLs with expiration times.

## Requirements

- Python 3.10.11
- `hashlib` library (usually included in the Python standard library)

## Usage

1. Clone the repository:
    ```sh
    git clone https://github.com/thedatamonk/system-design-masterclass.git
    cd system-design-masterclass/temp_url_generator
    ```

2. Run the script:
    ```sh
    python temp_url_generator.py
    ```

3. Follow the prompts to generate a temporary URL.

## Example

```python
from temp_url_generator import generate_temp_url

url = generate_temp_url("https://example.com/resource", expiration_time=3600)
print(url)
```

## License

This project is licensed under the MIT License. See the [LICENSE](../LICENSE) file for details.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any changes.

## Contact

For any questions or suggestions, please email me @ [rohilpal9763@gmail.com](mailto:rohilpal9763@gmail.com).