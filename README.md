# 📖 Chat Chronicle

Tired of your precious memories fading away in endless chat logs?  `chat-chronicle` is here to help! This tool
automatically transforms your chat history into concise and insightful diary entries, powered by the magic of Large
Language Models (LLMs). Whether it's Instagram DMs or other chat platforms (future feature!), `chat-chronicle` helps you
reflect on your conversations and relive your digital life.

## ✨ Key Features

### 💬 **Chat Parsing:**

- **Configurable Input:** Reads Instagram and WhatsApp chat exports.
- **Chat Session Management:** Smartly identifies and separates chat sessions based on inactivity periods.
- **Ignore Chat Functionality:** Filter out chats based on date ranges.

### ✍️ **Daily Summaries:**

- **Chat-to-Diary Conversion:** Uses an LLM to generate a simple diary entry summarizing the messages from a day.
- **LLM Powered:** Customizable AI model settings

### 📑 **Flexible Output:**

- **Multiple file formats**:Supports different export formats (TXT, NDJSON, or JSON)
- **Multi and single file mode**:Options to combine all summaries into a single file.

## ✅ Prerequisites

* Python 3.11
* An LLM inference service endpoint (e.g., running locally or a cloud-based service).

## 🚀 Quick Start

1. ⬇️ **Clone the repository**:
   ```bash
   git clone https://github.com/YOUR_USERNAME/chat-chronicle.git
   cd chat-chronicle
   ```

2. 📲 **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. 🔧 **Configure**:
    - Edit `config.yml` to set your preferences
    - Set AI parameters (temperature, model, etc.)
    - Configure input/output paths
    - Adjust parsing rules for your language/needs
    - Enable/disable features like chat session detection

4. 🏃‍➡️ **Run**

   📚 **Batch Mode**:
    - Place your chat export files in the `input` directory
    - Configure the application in `config.yml`
    - Run the application:
      ```bash
      python main.py batch
      ```
    - The generated diary entries will be saved in the `output` directory

   🌐 API Mode
    - Start the API server to integrate with other apps:
      ```bash
      python main.py API
      ```
    - Access the Swagger docs at `http://localhost:8000/swagger-ui`

## 🤝 Contributing

Contributions are welcome!  Please feel free to submit pull requests with bug fixes, new features, or improvements to
the documentation.

## 📝 License

Licensed under the [MIT](https://github.com/Manuel-Materazzo/chat-chronicle/blob/master/LICENSE