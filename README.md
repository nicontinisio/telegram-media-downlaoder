
# Telegram Media Downloader

## Description
The `app.py` program is an advanced Python script designed for interacting with the [Telegram API](https://core.telegram.org/), specifically aimed at retrieving and downloading content from Telegram channels or groups.

### Specific Functions
- **Configuration Loading**: Loads essential parameters for connecting to the Telegram API from `config.json`.
- **Link Validation**: Verifies that the provided link conforms to the formats accepted by Telegram using a series of regular expression patterns. This ensures that the input is a valid Telegram link or identifier before attempting any API calls.
- **Link Cleaning**: Extracts the necessary identifier for API operations from various link formats, removing unnecessary parts such as protocol prefixes and path components that are irrelevant to the API operations.
- **Message Retrieval**: Retrieves and stores messages from a channel or group.
- **Media Download**: Downloads media associated with selected messages.
- **Session Management and User Input**: Manages user input and the Telegram client session.

#### Detailed Functionality
- **Link Validation Patterns**: The script uses regular expressions to match the input link against expected Telegram URL formats, including direct channel links, invitation links, and numeric identifiers.
- **Clean Link Function**: Simplifies the provided link to extract the core information needed for Telegram API requests, ensuring compatibility and correctness in API usage.
- **Error Handling**: Includes robust error handling throughout the script to manage exceptions such as invalid links, access errors, and API limits.
- **Flood Wait Handling**: Implements strategies to respect Telegram's flood wait limits by pausing execution as required, preventing the script from being blocked or banned by Telegram's rate limiting.

### Practical Usage Example
After correctly configuring the `config.json` file and installing dependencies via `pip install -r requirements.txt`, the script can be started with `python app.py`.

#### Usage Steps:
1. **Link Input**: Enter the desired Telegram channel or group link.
2. **Message Processing**: View and select messages from which to download media.
3. **Message Selection for Download**: Choose between message numbers, ranges, or all messages.
4. **Download**: Media are downloaded to the specified folder.

## Installation
Ensure Python is installed and then execute:
```
pip install -r requirements.txt
```

## Starting the Script
```
python app.py
```

## User Input
After starting, follow the on-screen instructions to enter the link and select messages to download.

## Contributing
Feel free to fork this repository and contribute by submitting pull requests with enhancements or bug fixes.

## License
Distributed under the GPL License. See `LICENSE` for more information.
