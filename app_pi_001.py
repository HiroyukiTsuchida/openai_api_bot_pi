
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
            "可能な限り原文に忠実に、漏れや間違いなく、自然な日本語に翻訳してください。\n"
            "＃指示\n"
            f"{theme}を翻訳してください。\n"
            f"＃補足情報: {additional_info}"
            "＃注意してほしい点：所有格を無理に全部訳さない\n"
            "＃例①\n"
            "【英文】At some point, our kids will be out in the world and their self-esteem will be pivotal to their success. \n"
            "【悪い日本語訳の例】いつか私たちの子供たちが世界に飛び立った時、彼らの自尊心は成功の大きな要となるでしょう。 \n"
            "【良い日本語訳の例】いつか子供たちが世界に旅立ったとき、自尊心は成功の大きな要となるでしょう。\n"
            "＃例②\n"
            "【英文】The Company aims to nearly double its number of restaurants. \n"
            "【悪い日本語訳の例】その会社は自社のレストランの店舗数をほぼ倍にすることを目指している。 \n"
            "【良い日本語訳の例】その会社はレストランの店舗数をほぼ倍にすることを目指している。 \n"
            "＃注意してほしい点：複数形は状況によっては無理に訳さない\n" 
            "＃例①\n"
            "【英文】The task of facilitating language learning for our children may seem complicated.\n"
            "【悪い日本語訳の例】子供たちに外国語を学ばせることは難しいように思うかもしれません。\n"
            "【良い日本語訳の例】子供に外国語を学ばせることは難しいように思うかもしれません。\n"
            "＃例②\n"
            "【原文】For parents, preparing a list of questions before an appointment is a good start as teachers are busy.\n" 
            "【悪い日本語訳の例】教師たちは忙しいので親はあらかじめ質問したいことを書き出して面談に臨むといいでしょう。\n" 
            "【良い日本語訳の例】教師は忙しいので親はあらかじめ質問したいことを書き出して面談に臨むといいでしょう。 \n"
            "＃注意してほしい点：「any」は「もし～なら」に分解したほうがいい場合もある\n"
            "＃例①\n"
            "【英文】Any accident should be reported to the supervisor immediately.\n"
            "【悪い日本語訳の例】どんな事故も上司に報告されなければならない。\n"
            "【良い日本語訳の例】事故があった場合は必ず上司に報告しなければならない。\n"
            "＃例②\n"
            "【原文】Any member who is in doubt should submit a copy of the medical certificate from their doctor. \n"
            "【悪い日本語訳の例】疑いのあるいずれのメンバーも、医師の診断書を提出しなければならない。\n"
            "【良い日本語訳の例】自然な訳文：メンバーは、疑いがある場合は必ず医師の診断書を提出しなければならない。 \n"
            "＃注意してほしい点：名詞を動詞に、動詞を名詞に変換したほうが良い場合もある\n"
            "＃例①：名詞句を動詞句に変換する場合\n"
            "【英文】Exposure to organophosphates can cause headache and diarrhea.\n"
            "【悪い日本語訳の例】有機リン酸への暴露は頭痛と下痢を引き起こすことがある。\n"
            "【良い日本語訳の例】有機リン酸に晒されると頭痛と下痢が生じることがある。\n"
            "＃例②：動詞を名詞に変換する場合の英和翻訳例\n"
            "【英文】The strong sales of Japanese comic books is attributable to the expansion of the international e-commerce market.\n"
            "【悪い日本語訳の例】日本のマンガの好調な売り上げは海外のＥコマース市場の拡大に起因する。\n"
            "【良い日本語訳の例】日本のマンガの売上が好調な理由として海外のＥコマース市場の拡大が挙げられる。 \n"
            "＃注意してほしい点：受動態を能動態に、能動態を受動態に変換したほうが良い場合もある\n"
            "＃例①：受動態を能動態に変換する場合\n"
            "#①‐a\n"
            "【英文】They wer examined by their respective family doctors.\n"
            "【悪い日本語訳の例】彼らはそれぞれかかりつけ医により診察された。\n"
            "【良い日本語訳の例】彼らはそれぞれかかりつけ医の診察を受けた。\n"
            "#①-b\n"
            "【原文】Any problem has to be resolved by employees.\n"
            "【悪い日本語訳の例】いかなる問題も従業員によって解決されなければならない。\n"
            "【良い日本語訳の例】いかなる問題も従業員が解決しなければならない。\n"
            "＃例②能動態を受動態に変換する場合\n"
            "【英文】How technology enables business model innovation.\n"
            "【悪い日本語訳の例】テクノロジーがいかにビジネスモデルのイノベーションを可能にしているか。\n"
            "【良い日本語訳の例】テクノロジーによりいかにビジネスモデルのイノベーションがもたらされるか。 \n"
            "＃注意してほしい点：使役動詞はかみ砕いて訳した方がいい場合が多い\n"
            "＃例①\n"
            "【英文】This combination of experience and innovation has made the company so successful. \n"
            "【悪い日本語訳の例】この経験とイノベーションの組み合わせがその企業を成功させた。 \n"
            "【良い日本語訳の例】この経験とイノベーションこそがその企業を成功に導いた要因だ。\n"
            "＃例②\n"
            "【原文】Professor Smith has made me want to become a teacher.\n" 
            "【悪い日本語訳の例】スミス教授は私を先生になりたくさせた。\n"
            "【良い日本語訳の例】スミス教授に出会って私は先生になりたいと思った。\n"
            "＃注意してほしい点：「～ための」の「to」や「for」を訳し下げる\n"
            "＃例①\n"
            "【英文】Lisa had turned her head to observe the birds climbing into the blue sky. \n"
            "【悪い日本語訳の例】リサは鳥たちが青い空へと飛び立っていくのを見るために振り返った。\n"
            "【良い日本語訳の例】リサが振り返ると鳥たちが青い空へと飛び立っていくのが見えた。\n"
            "＃例②\n"
            "【英文】The application shall be submitted to the president for review. \n"
            "【悪い日本語訳の例】申込書は確認のために社長に提出されなければならない。\n" 
            "【良い日本語訳の例】申込書を提出し社長の確認を受けなければならない。\n"
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

