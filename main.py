# import os
# from colorama import init
# from google import genai  # Use the official Gemini SDK

# init(autoreset=True)

# # ========= CONFIGURATION =========
# # Replace with your actual Gemini API Key
# GEMINI_API_KEY = "AIzaSyAVMZZRGXZcBpT16BxOm_Io7iuJDxt2fXM" 

# client = genai.Client(api_key=GEMINI_API_KEY)
# MODEL_ID = "gemini-2.0-flash" 

# # ========= COLOR DEFINITIONS =========
# BOLD = "\033[1m"
# RESET = "\033[0m"
# PURPLE = "\033[38;2;218;112;214m"
# CYAN = "\033[36m"
# BLUE = "\033[34m"

# def show_logo():
#     logo = """
# ██████╗ ██████╗  ██████╗ 
# ██╔══██╗██╔══██╗██╔═══██╗
# ██████╔╝██████╔╝██║   ██║
# ██╔══██╗██╔══██╗██║   ██║
# ██████╔╝██║  ██║╚██████╔╝
# ╚═════╝ ╚═╝  ╚═╝ ╚═════╝ 
# """
#     print(CYAN + logo + RESET)

# def show_intro():
#     print(PURPLE + "Hello " + RESET + CYAN + "Bro" + 
#           RESET + PURPLE + " how can I help you just tell me 😁" + RESET)

# # ========= AI FUNCTION =========
# def Bro(user_input):
#     try:
#         # In Gemini SDK, we use generate_content
#         response = client.models.generate_content(
#             model=MODEL_ID,
#             contents=user_input,
#             config={'system_instruction': 'You are a smart and friendly AI assistant.'}
#         )

#         # The response text is accessed directly via .text
#         ai_reply = response.text
#         print(BLUE + BOLD + "\nBro AI: " + RESET + ai_reply)

#     except Exception as e:
#         print(PURPLE + "\nError: " + RESET + str(e))

# # ========= MAIN =========
# if __name__ == "__main__":
#     show_logo()
#     show_intro()

#     while True:
#         try:
#             user_input = input(CYAN + "\nYou: " + RESET)

#             if user_input.lower() in ["exit", "quit"]:
#                 print(PURPLE + "Bye Bro 👋")
#                 break

#             if not user_input.strip():
#                 continue

#             Bro(user_input)
#         except KeyboardInterrupt:
#             print(PURPLE + "\nBye Bro 👋")
#             break