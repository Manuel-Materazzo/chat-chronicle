
<div align="center">
<div>
    <img src="resources/logo.png" width="230" alt="Warp" />
  </div>
<h1>Chat Chronicle</h1>
<a href="https://codecov.io/gh/Manuel-Materazzo/chat-chronicle" > 
 <img src="https://codecov.io/gh/Manuel-Materazzo/chat-chronicle/graph/badge.svg?token=66A5P46Y4N"/> 
</a>
<br>
</div>

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

## 🚀 Getting Started

### 🐳 Docker prebuilt

1. **Pull the Docker Image**:
   ```sh
   docker pull ghcr.io/manuel-materazzo/chat-chronicle:latest
    ```
2. **Run the Container**:
   ```sh
   docker run -d -p 8000:8000 manuel-materazzo/chat-chronicle
    ```

### 🐳🔧 Docker compose self-build

1. **Run docker compose**:
   ```sh
   docker-compose up
   ```

### 📦 Manual installation

1. **Clone Coginets repository**:
   ```sh
   git clone https://github.com/Manuel-Materazzo/chat-chronicle.git
   cd Coginets
   ```
2. **Install the required dependencies**:
   ```sh
   pip install -r requirements.txt
   ```

## 🔧 Setting up

1. 🔧 **Configure**:
    - Edit `config.yml` to set your preferences
    - Set AI parameters (temperature, model, etc.)
    - Configure input/output paths
    - Adjust parsing rules for your language/needs
    - Enable/disable features like chat session detection

2. 🏃‍➡️ **Run**

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

## 📡 API Usage

The API exposes two endpoints under `/summarize`. Both accept a JSON body and return diary entries.

### `POST /summarize/instagram-export`

**Request:**
```json
{
  "messages": [
    {
      "sender_name": "Alice",
      "timestamp_ms": 1700000000000,
      "content": "Hey, how are you?"
    },
    {
      "sender_name": "Bob",
      "timestamp_ms": 1700000060000,
      "content": "I'm good, thanks!"
    }
  ],
  "configs": {}
}
```

### `POST /summarize/whatsapp-export`

**Request:**
```json
{
  "messages": [
    "02/01/2024, 10:00 - Alice: Hey, how are you?",
    "02/01/2024, 10:01 - Bob: I'm good, thanks!"
  ],
  "configs": {}
}
```

### Response (both endpoints)

```json
{
  "entries": [
    {
      "date": "2024-01-02",
      "summary": "Dear Diary, today Alice and Bob had a brief exchange..."
    }
  ]
}
```

The optional `configs` object allows overriding `parsing` and `summarization` settings per request.

### Error Responses

| Status | Meaning |
|--------|---------|
| `200`  | Success |
| `503`  | AI service busy — retry later |

## 🏗️ Architecture

```
main.py → batch_processor / api_server
             ↓                    ↓
         reader_factory     summary_controller
             ↓                    ↓
         parser_factory     ai_processor_factory
             ↓                    ↓
         writer_factory     (linear / map_reduce)
```

- **Readers** load raw chat files (Instagram JSON or WhatsApp TXT).
- **Parsers** split messages into per-day buckets with optional chat-session detection.
- **AI Processors** summarize each day using LangChain + LangGraph (`linear` or `map_reduce` strategy).
- **Writers** output diary entries in TXT, JSON, or NDJSON format.

## 🤝 Contributing

Contributions are welcome!  Please feel free to submit pull requests with bug fixes, new features, or improvements to
the documentation.

## 📝 License

Licensed under the [MIT](https://github.com/Manuel-Materazzo/chat-chronicle/blob/master/LICENSE)