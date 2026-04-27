     # 🤖 BRO CLI

     ```
     ██████╗ ██████╗  ██████╗ 
     ██╔══██╗██╔══██╗██╔═══██╗
     ██████╔╝██████╔╝██║   ██║
     ██╔══██╗██╔══██╝██║   ██║
     ██████╔╝██║  ██║╚██████╔╝
     ╚═════╝ ╚═╝  ╚═╝ ╚═════╝ 
     ```

     **AI-Powered CLI Bot with DuckDuckGo Web Search**  
     Uses OpenRouter API · ChromaDB · Rich Terminal UI

     ---

     ## 📦 Installation

     ```bash
     pip install -r requirements.txt
     ```

     ## ⚙️ Setup `.env`

     ```env
     OPENROUTER_API_KEY=your_openrouter_api_key_here
     OPENROUTER_MODEL=openai/gpt-4o-mini
     SMTP_HOST=smtp.gmail.com
     SMTP_PORT=587
     SMTP_USER=your_email@gmail.com
     SMTP_PASS=your_app_password_here
     ```

     > For Gmail: use an **App Password** (Google Account → Security → App Passwords)

     ## 🚀 Run

     ```bash
     python app.py
     ```

     ---

     ## 💬 Commands

     | Command      | Action                              |
     |-------------|--------------------------------------|
     | `+<text>`   | Autocomplete files in current dir    |
     | `/`         | Open OS file explorer to attach file |
     | `/logout`   | Logout current session               |
     | `/h`        | Show chat history                    |
     | `/clean`    | Clear all chat history               |
     | `Shift+Tab` | Cycle color theme (Blue→Cyan→Green→Red→Orange) |

     ---

     ## 📁 File Structure

     ```
     app.py        # Main loop, splash, auth flow, chat loop
     database.py   # ChromaDB: users (hashed passwords) + chat history
     auth.py       # Registration, login, email OTP verification
     search.py     # DuckDuckGo search → context string
     chat.py       # OpenRouter API call with search context
     .env          # API keys and SMTP config
     requirements.txt
     ```

     ---

     ## 🔐 Security

     - Passwords stored as **SHA-256 hashes** in ChromaDB (local, persistent)
     - Email verified via **6-digit OTP** before account activation
     - `.bro_db/` folder is created locally (add to `.gitignore`)

     ---

     ## 🎨 Themes

     Press **Shift+Tab** to cycle:  
     `Blue → Cyan → Green → Red → Orange`

     ---

     ## 📎 File Attachment

     - Type `+` and autocomplete suggests files in the current directory
     - Type `/` alone to open a GUI file picker
     - Attached file content is sent to the AI with your next question