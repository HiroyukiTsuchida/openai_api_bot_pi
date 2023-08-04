
import streamlit as st
import openai
import uuid
from PIL import Image
import requests

# DeepLのAPIキーを取得
#DEEPL_API_KEY = st.secrets["DeepLAPI"]["deepl_api_key"]

# DeepLのAPIを呼び出す関数
#def translate_to_english(text):
#    url = "https://api-free.deepl.com/v2/translate"
#    headers = {"Content-Type": "application/x-www-form-urlencoded"}
#    data = {
#        "auth_key": DEEPL_API_KEY,
#        "text": text,
#        "target_lang": "EN",
#    }
#    response = requests.post(url, headers=headers, data=data)
#    return response.json()["translations"][0]["text"]

# サービス名を表示する
st.sidebar.title("[Pi] AI Assistant")

# Create a unique key for the widget
unique_key = str(uuid.uuid4())

# Streamlit Community Cloudの「Secrets」からOpenAI API keyを取得
openai.api_key = st.secrets.OpenAIAPI.openai_api_key

# st.session_stateを使いメッセージのやりとりを保存
if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {"role":"system","content":"You are the best of Internal Audit AI assistant in the world."}
    ]

if "user_input" not in st.session_state:
    st.session_state["user_input"] = ""

# チャットボットとやりとりする関数
def communicate(user_input, bot_response_placeholder, model):
    messages = [{"role":"system","content":""}]
    user_message = {"role": "user", "content": user_input}
    messages.append(user_message)

    # Temporary variable to store chunks
    complete_response = ""

    # Get the response from ChatCompletion in streaming mode
    for chunk in openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=0,
        stream=True
    ):
        content = chunk["choices"][0].get("delta", {}).get("content")
        if content is not None:
            # Accumulate content and update the bot's response in real time
            complete_response += content
            bot_response_placeholder.markdown(complete_response, unsafe_allow_html=True)

    # After all chunks are received, add the complete response to the chat history
    if complete_response:
        bot_message = {"role": "assistant", "content": complete_response}
        messages.append(bot_message)

    # Reset the messages after the chat
    messages = [{"role":"system","content":"You are the best of Internal Audit AI assistant in the world."}]

# サイドバーで機能を選択
selected_option = st.sidebar.selectbox(
    "機能を選択してください",
    ["Q&A", "Translation", "Proofreading", "Formula Analysis", "VBA", "Data Analysis"],
    key="selectbox_key"  # 固定のキーを指定する
)

# モデルを選択
model = st.sidebar.selectbox(
    "モデルを選択してください",
    ["gpt-3.5-turbo-16k", "gpt-4"],
    key="model_selectbox_key"  # 固定のキーを指定する
)

# 機能に応じたUIの表示
if selected_option == "Q&A":
    # Build the user interface
    st.title("AI Assistant")

    # Create a placeholder for the user's input
    user_input = st.text_area("自由に質問を入力してください。", value=st.session_state.get("user_input_Q&A", ""))

    # Create a placeholder for the bot's responses
    bot_response_placeholder = st.empty()

    # Execute the communicate function when the user presses the 'Submit' button
    if st.button("実行", key="send_button_Q&A"):
        st.session_state["user_input_Q&A"] = user_input
        communicate(st.session_state["user_input_Q&A"], bot_response_placeholder, model)

        # Clear the user input
        st.session_state["user_input_Q&A"] = ""

elif selected_option == "Translation":
    st.title("Translation")

    # チェックボックス
    #checkboxes = ["監査概要","監査項目・着眼点","想定されるリスク", "期待されるコントロール", "規準（クライテリア）", "インタビュー項目","ToD（デザインの有効性評価）","ToE（運用状況の有効性評価）", "監査証拠（資料名・データ名）", "対象部門","想定される発見事項"]
    #selected_items = []
    #for checkbox in checkboxes:
    #    if st.sidebar.checkbox(checkbox, key=f"checkbox_{checkbox}"):
    #        selected_items.append(checkbox)

    # 右側の入力フォーム
    theme = st.text_area("翻訳したい文章を入力し、実行ボタンを押してください。", height=200, key="theme_input")

    # 追加：補足情報の入力フィールド
    additional_info = st.text_area("補足情報を入力してください。", "", key="additional_info")

    # Create a placeholder for the bot's responses
    bot_response_placeholder = st.empty()

    if st.button("実行", key="send_button_auditors_view"):
        initial_prompt = (
            "あなたは優秀な翻訳家です。あなたの役割は、英文を日本語に翻訳し、日本語のウェブサイト上で日本人の投資家向けに翻訳された間違いのない情報を提供することです。\n"
            f"{theme}を翻訳してください。\n"
            "以下は補足情報です。\n"
            f"補足情報: {additional_info}"
            "以下は注意点です。\n"
            f"可能な限り原文に忠実に、漏れや間違いなく、自然な日本語に翻訳してください。\n"
        )
        st.session_state["user_input"] = initial_prompt
        communicate(initial_prompt, bot_response_placeholder, model)

elif selected_option == "Proofreading":
    st.title("[WIP] Proofreading")


elif selected_option == "Formula Analysis":
    st.title("[WIP] Formula Analysis")


elif selected_option == "VBA":
    st.title("[WIP] VBA")


elif selected_option == "Data Analysis":
    st.title("[WIP] Data Analysis")

