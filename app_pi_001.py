
import streamlit as st
import openai
import uuid
from PIL import Image
import numpy as np
import pdfplumber
import pandas as pd
from docx import Document
import base64


# サービス名を表示する
st.sidebar.title("AI Assistant")

# 初回ログイン認証
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    user_id = st.text_input("ユーザーIDを入力してください:")
    password = st.text_input("パスワードを入力してください:", type="password")
    if st.button("ログイン"):
        if user_id == "admin" and password == "LLM@2023":
            st.session_state["authenticated"] = True
            st.success("ログイン成功!")
            if st.button("続ける"):
                pass
        else:
            st.error("誤ったユーザーIDまたはパスワードです。")

if st.session_state["authenticated"]:
    # Create a unique key for the widget
    unique_key = str(uuid.uuid4())

    # Streamlit Community Cloudの「Secrets」からOpenAI API keyを取得
    openai.api_key = st.secrets.OpenAIAPI.openai_api_key

    # st.session_stateを使いメッセージのやりとりを保存
    if "messages" not in st.session_state:
        st.session_state["messages"] = [
            {"role": "system", "content": "You are the best AI assistant in the world."}
        ]

    if "user_input" not in st.session_state:
        st.session_state["user_input"] = ""

    def count_tokens(text):
        response = openai.Completion.create(model="text-davinci-002", prompt=text, max_tokens=1)
        token_count = response['usage']['total_tokens']
        return token_count

    def get_binary_file_downloader_html(bin_file, file_label="File"):
        with open(bin_file, "rb") as f:
            data = f.read()
        bin_str = base64.b64encode(data).decode()
        href = f'<a href="data:application/octet-stream;base64,{bin_str}" download="{file_label}.docx">Download {file_label}</a>'
        return href

    # チャットボットとやりとりする関数
    def communicate(user_input, bot_response_placeholder, model, temperature, top_p):
        messages = st.session_state["messages"]
        user_message = {"role": "user", "content": user_input}
        messages.append(user_message)

        # Temporary variable to store chunks
        complete_response = ""

        # Get the response from ChatCompletion in streaming mode
        for chunk in openai.ChatCompletion.create(
            model=model,
            messages=messages,
            temperature=temperature,
            top_p=top_p,
            stream=True
        ):
            content = chunk["choices"][0].get("delta", {}).get("content")
            if content is not None:
                # Accumulate content and update the bot's response in real time
                complete_response += content
                formatted_response = complete_response.replace("\n", "<br>")
                indented_response = "".join([f"<div style='margin-left: 20px; white-space: pre-wrap;'>{line}</div>" for line in complete_response.split('\n')]) # インデントで回答
                bot_response_placeholder.markdown(indented_response, unsafe_allow_html=True)

        # After all chunks are received, add the complete response to the chat history
        if complete_response:
            bot_message = {"role": "assistant", "content": complete_response}
            messages.append(bot_message)

        # Reset the messages after the chat
        messages = [{"role": "system", "content": "You are the best AI assistant in the world."}]

        return complete_response

    # サイドバーで機能を選択
    selected_option = st.sidebar.selectbox(
        "機能を選択してください",
        ["選択してください", "Q&A", "Translation", "Proofreading", "Excel Formula Analysis", "VBA Analysis", "Data Analysis"],
        index=0, # デフォルト値として「選択してください」を設定
        key="selectbox_key"  # 固定のキーを指定する
    )

    # タイトル「オプション」を追加
    st.sidebar.header("オプション")

    # モデルの選択とその補足情報
    with st.sidebar.beta_expander("モデル  🛈"):
        st.write(
        """gpt-4（推奨）は、高品質な回答を出力します。入力・出力の合計で約8,000トークンまで処理可能です。gpt-3.5-turbo-16kは、gpt-4と比較すると回答の質は下がりますが、入力・出力の合計で約16,000トークンまで処理でき、gpt-4に比べ高速で回答の出力が可能です。
        """)
        model = st.selectbox(
        "モデルを選択してください",
        ["gpt-4", "gpt-3.5-turbo-16k"],
        key="model_selectbox_key"  # 固定のキーを指定する
    )

    # Temperatureスライダーとその補足情報
    with st.sidebar.beta_expander("Temperature  🛈"):
        st.write("Temperature（温度）:モデルの出力の「確信度」または「多様性」を制御します。値が高いとモデルの出力は多様性が増し、予測はよりランダムになります。逆に、値が低いとモデルの出力はより確信度が高くなり、最も確率的に高い結果を選びやすくなります。【推奨値:0.10】")
        temperature = st.slider("", 0.0, 2.0, 0.1, 0.01)

    # Top_Pスライダーとその補足情報
    with st.sidebar.beta_expander("Top_P  🛈"):
        st.write("Top_P: 温度と同様に、これはランダム性を制御しますが、別の方法を使用します。Top_P を下げると、より可能性が高い回答に絞り込まれます。Top_P を上げると、確率が高い回答と低い回答の両方から選択されるようになります。【推奨値:0.50】")
        top_p = st.slider("", 0.0, 1.0, 0.5, 0.01)

    # 累積トークン数リセットボタンの設置
    if st.sidebar.button("トークン数リセット"):
        st.session_state["messages"] = [
            {"role": "system", "content": "You are the best AI assistant in the world."}
        ]

    # 「お問い合わせ」ハイパーリンクの設置
    def create_mailto_link():
        to_address = "kazuki.takahashi@front-ia.com,katakahashi@pictet.com"
        cc_address = "hiroyuki.tsuchida@front-ia.com"
        subject = "AI Assistant"
        return f"mailto:{to_address}?subject={subject}&cc={cc_address}"

    mailto_link = create_mailto_link()
    st.sidebar.markdown(f'<a href="{mailto_link}" target="_blank">お問い合わせ</a>', unsafe_allow_html=True)

    # (準備中)ユーザーアンケート
    #st.sidebar.markdown("""
    #[お問い合わせ](https://ai-assistant-inquiries-8sft4gmafubshjqsrzx6m2.streamlit.app/)
    #""")

    # バージョン情報表示（リリースノートへのハイパーリンク）
    st.sidebar.markdown("""
    [v1.3.0](https://ai-assistant-releasenote-mfjkhzwcdpy9p33km6tffg.streamlit.app/)
    """)

    def create_word_doc(text):
        doc = Document()
        doc.add_paragraph(text)
        output_path = "/tmp/translated_text.docx"
        doc.save(output_path)
        return output_path


    # 機能に応じたUIの表示
    if selected_option == "選択してください":
        pass  # 何も表示しない

    elif selected_option == "Q&A":
        # Build the user interface
        st.title("Q&A")

        # 留意点の表示
        st.markdown('<span style="color:red">***個人情報や機密情報は入力しないでください**</span>', unsafe_allow_html=True)

        # ユーザー入力を初期化
        user_input = ""
        uploaded_file = ""

        # ラジオボタンで直接入力とファイルアップロードを選択
        choice = st.radio("入力方法を選択してください", ["直接入力", "ファイルをアップロード"])

        # 直接入力が選択された場合
        if choice == "直接入力":
            user_input = st.text_area("自由に質問を入力してください。", value=st.session_state.get("user_input_Q&A", ""), height=500)
            st.session_state["user_input_Q&A"] = user_input

        # ファイルアップロードが選択された場合
        elif choice == "ファイルをアップロード":
            uploaded_file = st.file_uploader("ファイルをアップロード", type='pdf')

            def extract_text_from_pdf(feed):
                extracted_text = ""
                with pdfplumber.open(feed) as pdf:
                    for page in pdf.pages:
                        extracted_text += page.extract_text()
                return extracted_text

            if uploaded_file is not None:
                extracted_text = extract_text_from_pdf(uploaded_file)
                user_input = st.text_area("PDFから抽出したテキスト:", value=extracted_text, height=500)
                st.session_state["user_input_Q&A"] = user_input

        # ユーザー入力の確認
        if 'user_input' in locals() and user_input:
            tokens = count_tokens(user_input) - 1

        # トークン数を表示
            st.markdown(f'<span style="color:grey; font-size:12px;">入力されたトークン数（上限の目安：2,000）: {tokens}</span>', unsafe_allow_html=True)
        else:
            tokens = 0

        # Create a placeholder for the bot's responses
        bot_response_placeholder = st.empty()

        # Execute the communicate function when the user presses the 'Submit' button
        if st.button("実行", key="send_button_data"):
            if user_input.strip() == "":
                st.warning("データを入力してください。")
            else:
                st.session_state["user_input_Q&A"] = user_input
                communicate(st.session_state["user_input_Q&A"], bot_response_placeholder, model, temperature, top_p)

        # Clear the user input
        st.session_state["user_input_Q&A"] = ""


    elif selected_option == "Translation":
        st.title("Translation")

        # 留意点の表示
        st.markdown('<span style="color:red">***個人情報や機密情報は入力しないでください**</span>', unsafe_allow_html=True)

        # ユーザー入力を初期化
        user_input = ""
        uploaded_file = ""

        # ラジオボタンで直接入力とファイルアップロードを選択
        choice = st.radio("入力方法を選択してください", ["直接入力", "ファイルをアップロード"])

        # 直接入力が選択された場合
        if choice == "直接入力":
            # session_stateの更新
            if "user_input_translation" in st.session_state:
                default_value = st.session_state["user_input_translation"]
            else:
                default_value = ""
            # ウィジェット生成
            user_input = st.text_area("翻訳したい文章を入力してください。", value=default_value, height=500, key="user_input_translation")

        # ファイルアップロードが選択された場合
        elif choice == "ファイルをアップロード":
            uploaded_file = st.file_uploader("ファイルをアップロード", type='pdf')

            def extract_text_from_pdf(feed):
                extracted_text = ""
                with pdfplumber.open(feed) as pdf:
                    for page in pdf.pages:
                        extracted_text += page.extract_text()
                return extracted_text

            if uploaded_file is not None:
                extracted_text = extract_text_from_pdf(uploaded_file)
                # session_stateの更新
                st.session_state["user_input_translation"] = extracted_text
                # ウィジェット生成
                user_input = st.text_area("PDFから抽出したテキスト:", value=extracted_text, key="user_input_translation", height=500)


        # 追加：補足情報の入力フィールド
        additional_info = st.text_area("補足情報を入力してください。", "", key="additional_info")

        # ユーザー入力の確認
        if 'user_input' in locals() and user_input:
            tokens = count_tokens(user_input) - 2

        # トークン数を表示
            st.markdown(f'<span style="color:grey; font-size:12px;">入力されたトークン数（上限の目安：2,000）: {tokens}</span>', unsafe_allow_html=True)
        else:
            tokens = 0

        # Create a placeholder for the bot's responses
        bot_response_placeholder = st.empty()

        initial_prompt = (
                    "あなたは優秀な翻訳家です。あなたの役割は、英文を日本語に翻訳し、日本語のウェブサイト上で日本人の投資家向けに翻訳された間違いのない情報を提供することです。\n"
                    "以下の指示1及び指示2に従って作業を行ってください。出力は下記の「形式」に従いmarkdown形式とし、「#指示」の文言は出力しないでください。\n"
                    "＃指示1\n"
                    f"{user_input}を、下記の「注意してほしい点」を参照しながら、可能な限り原文に忠実に、漏れや間違いなく、自然な日本語に翻訳し、【翻訳結果】として出力してください\n"
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
                    "###\n"
                    "＃指示2\n"
                    "#指示1で翻訳により作成された文章を、半分の分量になるよう要約し、【要約】として出力してください。\n"
                    "###\n"
        )

        if st.button("実行", key="send_button_translation"):
            if user_input.strip() == "":
                st.warning("データを入力してください。")
            else:
                st.session_state["user_input"] = initial_prompt
                generated_text = communicate(initial_prompt, bot_response_placeholder, model, temperature, top_p)

                # 生成されたテキストをUIに表示します。
                #bot_response_placeholder = st.write(generated_text)

                # Word文書を生成
                doc_path = create_word_doc(generated_text)

                def get_binary_file_downloader_html(bin_file, file_label='File'):
                    with open(bin_file, 'rb') as f:
                        data = f.read()
                    bin_str = base64.b64encode(data).decode()
                    href = f'<a href="data:application/octet-stream;base64,{bin_str}" download="{bin_file}">{file_label}</a>'
                    return href

                # Word文書をダウンロードリンクとして提供
                st.markdown(get_binary_file_downloader_html(doc_path, "結果をWord形式でダウンロード"), unsafe_allow_html=True)

        # 「システムプロンプトを表示」ボタンの説明
        st.markdown('<span style="color:grey; font-size:12px;">***下の「システムプロンプトを表示」ボタンを押すと、この機能にあらかじめ組み込まれているプロンプト（命令文）を表示できます。**</span>', unsafe_allow_html=True)

        # 「システムプロンプトを表示」ボタンの設置
        if st.button("システムプロンプトを表示"):
            st.write(initial_prompt)


    elif selected_option == "Proofreading":
        st.title("Proofreading")

        # 留意点の表示
        st.markdown('<span style="color:red">***個人情報や機密情報は入力しないでください**</span>', unsafe_allow_html=True)

        # ユーザー入力を初期化
        user_input = ""
        uploaded_file = ""

        # ラジオボタンで直接入力とファイルアップロードを選択
        choice = st.radio("入力方法を選択してください", ["直接入力", "ファイルをアップロード"])

        # 直接入力が選択された場合
        if choice == "直接入力":
            # session_stateの更新
            if "user_input_proof" in st.session_state:
                default_value = st.session_state["user_input_proof"]
            else:
                default_value = ""
            # ウィジェット生成
            user_input = st.text_area("校閲/校正したい文章を入力してください。", value=default_value, height=500, key="user_input_proof")

        # ファイルアップロードが選択された場合
        elif choice == "ファイルをアップロード":
            uploaded_file = st.file_uploader("ファイルをアップロード", type='pdf')

            def extract_text_from_pdf(feed):
                extracted_text = ""
                with pdfplumber.open(feed) as pdf:
                    for page in pdf.pages:
                        extracted_text += page.extract_text()
                return extracted_text

            if uploaded_file is not None:
                extracted_text = extract_text_from_pdf(uploaded_file)
                # session_stateの更新
                st.session_state["user_input_proof"] = extracted_text
                # ウィジェット生成
                user_input = st.text_area("PDFから抽出したテキスト:", value=extracted_text, key="user_input_proof", height=500)

        # 追加：補足情報の入力フィールド
        additional_info = st.text_area("補足情報を入力してください。", "", key="additional_info")

        # ユーザー入力の確認
        if 'user_input' in locals() and user_input:
            tokens = count_tokens(user_input) - 2

        # トークン数を表示
            st.markdown(f'<span style="color:grey; font-size:12px;">入力されたトークン数（上限の目安：2,000）: {tokens}</span>', unsafe_allow_html=True)
        else:
            tokens = 0

        # Create a placeholder for the bot's responses
        bot_response_placeholder = st.empty()

        initial_prompt = (
            "## あなたは校閲・校正の優秀なスペシャリストです。  \n"
            "あなたの役割は、日本の投資家向けに公表される情報を校閲・校正し、間違いなく高品質な文章を作成することです。  \n"
            "これから入力する文章に対して、下記の処理と出力を記載された順番通り行ってください。  \n"
            "なお、処理1と処理2については、後の出力1・2のための処理を行うのみとし、結果を文章として出力しないでください。  \n"
            "出力は出力1「修正箇所リスト」の出力と出力2「修正後全文」においてのみ行ってください。  \n"
            "また、該当するものがない項目についても、出力はしないでください \n"
            "###  \n"
            "処理1:誤りの検知（出力しない） \n"
            "以下の基準に該当するものをすべて検知してください。 \n"
            "検知された個所は、どんなに大量になっても構いません。 \n"
            "正しいかどうかの判断が微妙な、微細な誤りと思われるものも含め、少しでも違和感があるものは、積極的にできるだけ多く検知し、一つの漏れもなく、すべてリスト化してください。 \n"
            "### \n"
            "基準:  \n"
            "#1:誤字脱字、タイプミスと思われるもの  \n"
            "【例】 \n"
            "・×「こんにちわ」→〇「こんにちは」 \n"
            "・×「よろしくお願いしmす」→〇「よろしくお願いします」 \n"
            "・×「こじんまり」→〇「こぢんまり」 \n"
            "・×「ちじこまる」→〇「ちぢこまる」 \n"
            "・×「いちぢるしい」→〇「いちじるしい」 \n"
            "・×「かたずける」→〇「かたづける」 \n"
            "・×「金ずる」→〇「金づる」 \n"
            "・×「つくずく」→〇「つくづく」 \n"
            "・×「うなづく」→〇「うなずく」 \n"
            "・×「口づさむ」→〇「口ずさむ」 \n"
            "・「時季」「時期」「時機」など、意味が似通っていて、見た目にも判断しづらく誤変換しやすい単語 \n"
            "#2:数字の表記が全角になっているもの（数字の表記は全て半角で統一する。） \n"
            "#3:慣用句やことわざの表現に誤りがあると考えられるもの \n"
            "【例】 \n"
            "・×「的を得る」→〇「的を射る」 \n"
            "・×「とんでもありません」→〇「とんでもないことです」（「とんでもない」は形容詞のため活用しない。） \n"
            "#4:経済関係用語について下記のルールに沿っておらず誤りがあると考えられるもの \n"
            "【ルール】 \n"
            "（1）下記のような経済関係用語は、単体では送り仮名が必要 \n"
            "【例】 \n"
            "・預入れ \n"
            "・売上げ \n"
            "・卸売り \n"
            "・買掛け \n"
            "・利回り \n"
            "（2）（1）にあるような語が複合語となると、送り仮名は不要となる \n"
            "【例】 \n"
            "・×受付け件数→〇受付件数 \n"
            "・×売上げ高→〇売上高 \n"
            "・×卸売り問屋→〇卸売問屋 \n"
            "・×支払い総額→〇支払総額 \n"
            "・×振込み手数料→〇振込み手数料 \n"
            "・×申し込み期間→〇申込期間 \n"
            "・×割り当て数量→〇割当数量 \n"
            "・×割り増し料金→〇割増料金 \n"
            "#5:文脈に合わない単語が使われているもの \n"
            "【例】 \n"
            "・×「PERが拡大している」→〇「PERが上昇している」（PERは「率」であるので拡大・縮小するものではなく上昇・下落するもの） \n"
            "・×「新規受注が大きく上昇する」→〇「新規受注が大幅に増加する」（新規受注は「件数」であるので、上昇・下落するものではなく増加・減少するもの） \n"
            "・×「トレンド指標が強く改善している」→〇「トレンド指標が大幅に改善している」 \n"
            "・×「中立金利は概ね減少傾向であった」→○「低下傾向であった」  \n"
            "#6:主語と述語の組み合わせが間違っているもの、または不明瞭なもの \n"
            "#7:文末の表現が「です、ます」口調になっているもの \n"
            "#8:句読点の打ち方に不自然な点があるもの \n"
            "【例】 \n"
            "・句点や記号以外で改行している \n"
            "・一文に読点が4つ以上ある \n"
            "・50文字以上の文に読点がない \n"
            "・一文が100文字以上ある \n"
            "#9:括弧やカギ括弧、クォーテーションマーク等の始点・終点が欠けているもの \n"
            "#10:話し言葉等の正式な文章にふさわしくない表現になっているもの \n"
            "【例】 \n"
            "・「ちゃんと」や「ちょっと」 \n"
            "・「食べれない」（「食べられない」の「ら」が抜けた「ら抜き言葉」） \n"
            "・「怒ってる」（「怒っている」の「い」が抜けた「い抜き言葉」） \n"
            "・「読まさせる」や「聞かさせる」（「読ませる」「聞かせる」に本来不要な「さ」が入った「さ入れ表現」） \n"
            "#11:重複表現になっているもの \n"
            "【例】 \n"
            "・「一番最初」 \n"
            "・「後で後悔する」 \n"
            "・「必ず必要」 \n"
            "・「被害を被る」 \n"
            "#12:差別語・不快語､その他ポリティカル・コレクトネスに反するもの \n"
            "・「二人三脚」や「気違い」など、できれば使用すべきでない差別語となりうる言葉や、受け取る人にとっては不快な言葉 \n"
            "・「ビジネスマン」や「看護婦」など、偏見を含むか、公平でない言葉と捉えられる可能性のある言葉 \n"
            "#13:助詞の使用が誤っていたり不適切であると考えられるもの \n"
            "【例】 \n"
            "・×「運用を柔軟化を決定した後も」→〇「運用の柔軟化を決定した後も」（格助詞「を」の使用が不適切） \n"
            "・×「自然利率が上昇については」→〇「自然利子率の上昇については」（格助詞「が」の使用が不適切） \n"
            "・×「FOMCが長期の政策金利が」→〇「FOMCによる長期の政策金利が」（格助詞「が」の使用が不適切） \n"
            "・×「このブログ公表される前」→〇「このブログが公表される前」（格助詞「が」の抜け） \n"
            "#14:その他不適切な表現の例 \n"
            "【例】 \n"
            "・×「講演の残りには」→〇「講演の後半には」 \n"
            "・×「労働人口」→〇「労働力人口」 \n"
            "・×「日欧米」→〇「日米欧」 \n"
            "### \n"
            "処理2:誤りの修正（出力しない） \n"
            "操作1で検知したすべての誤りについて、下記の条件を遵守して修正を行ってください。 \n"
            "条件: \n"
            "#1:文章の順番に変更を加えないこと。 \n"
            "#2:架空の表現や慣用句、ことわざを使用しないこと。 \n"
            "#3:文章を省略しないこと。 \n"
            "出力1:修正箇所リスト \n"
            "操作2で修正した指摘したすべての個所について、以下に示す箇条書きの形式で、一つずつ改行して出力してください。なお、該当がない項目については項目を含め出力しないでください。 \n"
            "形式: \n"
            "・「〇〇」→「〇〇」 \n"
            "出力2:下記の例にあるような表記揺れ（同音・同義の語句について異なる文字表記が付されること）があるものは、該当する語句を全て、その下に示す形式で出力してください。その際、表記揺れと考えた理由は出力しないでください。 \n"
            "【例】 \n"
            "（1）送り仮名による表記ゆれ \n"
            "送り仮名の不統一（ばらつき・不揃い）により表記ゆれがある。 \n"
            "・引っ越し/引越し/引越 \n"
            "・受け付け/受付 \n"
            "（2）文字の種類による表記ゆれ \n"
            "同じ意味を持つ言葉であるにもかかわらず、文字の種類（ひらがな・カタカナ・漢字・アラビア数字/漢数字）により表記ゆれがある \n"
            "・りんご/リンゴ/林檎 \n"
            "・いぬ/イヌ/犬/狗 \n"
            "・ばら/バラ/薔薇 \n"
            "（3）漢字による表記ゆれ \n"
            "漢字変換による表記ゆれがある。最初の2つのように、漢字の原義によって意味合いが異なることがある。 \n"
            "・臭い/匂い （両方とも、「におい」） \n"
            "・会う/逢う \n"
            "・寿司/鮨/鮓 \n"
            "人名・地名などの固有名詞においても表記ゆれが生じることがある。 \n"
            "・斎藤/斉藤/齋藤/齊藤 \n"
            "（4）外来語における表記ゆれ \n"
            "「コンピューター」と「コンピュータ」のように、長音符の有無により表記ゆれがある。また、「ディーゼル」が「ジーゼル」と表記されることがあるように、「ディ」や「ティ」や「トゥ」などがほかの文字で置き換えられることもある。 \n"
            "（5）固有名詞や正式名称における表記ゆれ \n"
            "・「Java Script」（「JavaScript」の誤り。スペースが入ってしまっている。） \n"
            "・「Youtube」（「YouTube」の誤り。Tが小文字。） \n"
            "（6）時期によって正式な表記が異なることによる表記ゆれ \n"
            "例えばマーベル・コミックは、時期により『マーヴル・コミック』など表記が異なる。 \n"
            "形式: \n"
            "表記揺れと考えられるもの \n"
            "・「〇〇」「〇〇」「〇〇」 \n"
            "・「△△」「△△」「△△」 \n"
            "出力3:修正後全文 \n"
            "修正を反映させた全文を出力してください。 \n"
            f"**{user_input}**を校閲・校正してください。  \n"
            f"＃補足情報: **{additional_info}**"
            )

        if st.button("実行", key="send_button_proofreading"):
            if user_input.strip() == "":
                st.warning("データを入力してください。")
            else:
                st.session_state["user_input"] = initial_prompt
                communicate(initial_prompt, bot_response_placeholder, model, temperature, top_p)

        # 「システムプロンプトを表示」ボタンの説明
        st.markdown('<span style="color:grey; font-size:12px;">***下の「システムプロンプトを表示」ボタンを押すと、この機能にあらかじめ組み込まれているプロンプト（命令文）を表示できます。**</span>', unsafe_allow_html=True)

        # 「システムプロンプトを表示」ボタンの設置
        if st.button("システムプロンプトを表示"):
            st.write(initial_prompt)

    elif selected_option == "Excel Formula Analysis":
        st.title("Excel Formula Analysis")

        # 留意点の表示
        st.markdown('<span style="color:red">***個人情報や機密情報は入力しないでください**</span>', unsafe_allow_html=True)

        # ユーザー入力を初期化
        user_input = ""
        uploaded_file = ""

        # ラジオボタンで直接入力とファイルアップロードを選択
        choice = st.radio("入力方法を選択してください", ["直接入力", "ファイルをアップロード"])

        # 直接入力が選択された場合
        if choice == "直接入力":
            # session_stateの更新
            if "user_input_formula" in st.session_state:
                default_value = st.session_state["user_input_formula"]
            else:
                default_value = ""
            # ウィジェット生成
            user_input = st.text_area("解析したいExcelの式を入力してください。", value=default_value, height=500, key="user_input_formula")

        # ファイルアップロードが選択された場合
        elif choice == "ファイルをアップロード":
            uploaded_file = st.file_uploader("ファイルをアップロード", type='csv')

            def extract_data_from_csv(feed):
                # CSVをpandas DataFrameとして読み込む
                df = pd.read_csv(feed, encoding='ISO-8859-1')
                # DataFrameを文字列として返す（あるいは、必要なデータを抽出・変換する）
                return df.to_string()

            if uploaded_file is not None:
                extracted_data = extract_data_from_csv(uploaded_file)
                # session_stateの更新
                st.session_state["user_input_formula"] = extracted_data
                # ウィジェット生成
                user_input = st.text_area("CSVから抽出したデータ:", value=extracted_data, key="user_input_formula", height=500)

        # 追加：補足情報の入力フィールド
        additional_info = st.text_area("補足情報を入力してください。", "", key="additional_info")

        # ユーザー入力の確認
        if 'user_input' in locals() and user_input:
            tokens = count_tokens(user_input) - 2

        # トークン数を表示
            st.markdown(f'<span style="color:grey; font-size:12px;">入力されたトークン数（上限の目安：2,000）: {tokens}</span>', unsafe_allow_html=True)
        else:
            tokens = 0

        # Create a placeholder for the bot's responses
        bot_response_placeholder = st.empty()

        initial_prompt = (
                    "あなたは金融・投資・経済情報の分析を行うスペシャリストで、Microsoft Excelのエキスパートです。\n"
                    "あなたの役割は、情報分析のために作成された過去の複雑なExcel関数を分析し、わかりやすく説明することです。\n"
                    "これから入力するExcel関数に対して、下記の操作1を行い、出力してください。\n"
                    "操作1:[\n"
                    "複雑なネスト構造になっているExcel関数を改行し、かつインデント表示をすることで、わかりやすく表示してください。インデントは見やすくなるよう全角\n"
                    "]\n"
                    "操作2:[\n"
                    "操作1を行った後にこのExcel関数がどのような処理を行おうとしているものか解説し、よりシンプルで分かりやすい関数に書き換えが可能であれば、その提案をしてください。]\n"
                    "＃Excel関数:\n"
                    f"{user_input}\n"
                    "＃補足情報:\n"
                    f"{additional_info}\n"
                )

        if st.button("実行", key="send_button_formula"):
            if user_input.strip() == "":
                st.warning("データを入力してください。")
            else:
                st.session_state["user_input"] = initial_prompt
                communicate(initial_prompt, bot_response_placeholder, model, temperature, top_p)

        # 「システムプロンプトを表示」ボタンの説明
        st.markdown('<span style="color:grey; font-size:12px;">***下の「システムプロンプトを表示」ボタンを押すと、この機能にあらかじめ組み込まれているプロンプト（命令文）を表示できます。**</span>', unsafe_allow_html=True)

        # 「システムプロンプトを表示」ボタンの設置
        if st.button("システムプロンプトを表示"):
            st.write(initial_prompt)


    elif selected_option == "VBA Analysis":
        st.title("VBA Analysis")

        # 留意点の表示
        st.markdown('<span style="color:red">***個人情報や機密情報は入力しないでください**</span>', unsafe_allow_html=True)

        # ユーザー入力を初期化
        user_input = ""
        uploaded_file = ""

        # ラジオボタンで直接入力とファイルアップロードを選択
        choice = st.radio("入力方法を選択してください", ["直接入力", "ファイルをアップロード"])

        # 直接入力が選択された場合
        if choice == "直接入力":
            # session_stateの更新
            if "user_input_vba" in st.session_state:
                default_value = st.session_state["user_input_vba"]
            else:
                default_value = ""
            # ウィジェット生成
            user_input = st.text_area("解析したいVBAのコードを入力してください。", value=default_value, height=500, key="user_input_vba")

        # ファイルアップロードが選択された場合
        elif choice == "ファイルをアップロード":
            uploaded_file = st.file_uploader("ファイルをアップロード", type='csv')

            def extract_data_from_csv(feed):
                # CSVをpandas DataFrameとして読み込む
                df = pd.read_csv(feed, encoding='ISO-8859-1')
                # DataFrameを文字列として返す（あるいは、必要なデータを抽出・変換する）
                return df.to_string()

            if uploaded_file is not None:
                extracted_data = extract_data_from_csv(uploaded_file)
                # session_stateの更新
                st.session_state["user_input_vba"] = extracted_data
                # ウィジェット生成
                user_input = st.text_area("CSVから抽出したデータ:", value=extracted_data, key="user_input_vba", height=500)

        # 追加：補足情報の入力フィールド
        additional_info = st.text_area("補足情報を入力してください。", "", key="additional_info")

        # ユーザー入力の確認
        if 'user_input' in locals() and user_input:
            tokens = count_tokens(user_input) - 2

        # トークン数を表示
            st.markdown(f'<span style="color:grey; font-size:12px;">入力されたトークン数（上限の目安：2,000）: {tokens}</span>', unsafe_allow_html=True)
        else:
            tokens = 0

        # Create a placeholder for the bot's responses
        bot_response_placeholder = st.empty()

        initial_prompt = (
                    "あなたは金融・投資・経済情報の分析を行うスペシャリストで、Microsoft Excelのエキスパートです。\n"
                    "あなたの役割は、一つ目は情報分析のために作成された過去の複雑なVBAコードを分析し、わかりやすく説明すること、二つ目は実行したい作業内容をVBAコードに書き起こすです。\n"
                    "これから入力するデータがVBAコードの場合は下記の操作1を、日本語の場合は操作2を行い、出力してください。\n"
                    "操作1:[\n"
                    "このVBAコードがどのような処理を実行しようとするものか、わかりやすく表示してください。\n"
                    "]\n"
                    "操作2:[\n"
                    "入力された作業内容を実行するため、シンプルで分かりやすいVBAコードを書き起こしてください。]\n"
                    "＃インプット:\n"
                    f"{user_input}\n"
                    "＃補足情報:\n"
                    f"{additional_info}\n"
                )


        if st.button("実行", key="send_button_vba"):
            if user_input.strip() == "":
                st.warning("データを入力してください。")
            else:
                st.session_state["user_input"] = initial_prompt
                communicate(initial_prompt, bot_response_placeholder, model, temperature, top_p)

        # 「システムプロンプトを表示」ボタンの説明
        st.markdown('<span style="color:grey; font-size:12px;">***下の「システムプロンプトを表示」ボタンを押すと、この機能にあらかじめ組み込まれているプロンプト（命令文）を表示できます。**</span>', unsafe_allow_html=True)

        # 「システムプロンプトを表示」ボタンの設置
        if st.button("システムプロンプトを表示"):
            st.write(initial_prompt)



    elif selected_option == "Data Analysis":
        st.title("Data Analysis")

        # 留意点の表示
        st.markdown('<span style="color:red">***個人情報や機密情報は入力しないでください**</span>', unsafe_allow_html=True)

        # 右側の入力フォーム
        user_input = st.text_area("解析したいログデータを入力し、実行ボタンを押してください。", height=500, key="user_input_data")

        # 追加：補足情報の入力フィールド
        additional_info = st.text_area("補足情報を入力してください。", "", key="additional_info")

        # トークン数を計算
        tokens = count_tokens(user_input) + count_tokens(additional_info)-4

        # トークン数を表示
        st.markdown(f'<span style="color:grey; font-size:12px;">入力されたトークン数（上限の目安：2,000）: {tokens}</span>', unsafe_allow_html=True)

        # Create a placeholder for the bot's responses
        bot_response_placeholder = st.empty()

        initial_prompt = (
                    "あなたはデータ分析のスペシャリストです。\n"
                    "以下のインプット情報に記載されたログ情報を分析して、セキュリティリスク（不正兆候や異常値等）があるデータを抽出して、理由とともに教えてください。]\n"
                    "＃インプット:\n"
                    f"{user_input}\n"
                    "＃補足情報:\n"
                    f"{additional_info}\n"
                )

        if st.button("実行", key="send_button_data"):
            if user_input.strip() == "":
                st.warning("データを入力してください。")
            else:
                st.session_state["user_input"] = initial_prompt
                communicate(initial_prompt, bot_response_placeholder, model, temperature, top_p)

        # 「システムプロンプトを表示」ボタンの説明
        st.markdown('<span style="color:grey; font-size:12px;">***下の「システムプロンプトを表示」ボタンを押すと、この機能にあらかじめ組み込まれているプロンプト（命令文）を表示できます。**</span>', unsafe_allow_html=True)

        # 「システムプロンプトを表示」ボタンの設置
        if st.button("システムプロンプトを表示"):
            st.write(initial_prompt)



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
