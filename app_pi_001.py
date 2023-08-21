
import streamlit as st
import openai
import uuid


# サービス名を表示する
st.sidebar.title("[Dev] AI Assistant")

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
                indented_response = f"<pre style='margin-left: 20px;'>{complete_response}</pre>" # インデントで回答
                bot_response_placeholder.markdown(indented_response, unsafe_allow_html=True)

        # After all chunks are received, add the complete response to the chat history
        if complete_response:
            bot_message = {"role": "assistant", "content": complete_response}
            messages.append(bot_message)

        # Reset the messages after the chat
        messages = [{"role": "system", "content": "You are the best AI assistant in the world."}]

    # サイドバーで機能を選択
    selected_option = st.sidebar.selectbox(
        "機能を選択してください",
        ["選択してください", "Q&A", "Translation", "Proofreading", "Excel Formula Analysis", "VBA Analysis", "Data Analysis"],
        index=0, # デフォルト値として「選択してください」を設定
        key="selectbox_key"  # 固定のキーを指定する
    )

    # モデルを選択
    model = st.sidebar.selectbox(
        "モデルを選択してください",
        ["gpt-3.5-turbo-16k", "gpt-4"],
        key="model_selectbox_key"  # 固定のキーを指定する
    )

    # タイトル「オプション」を追加
    st.sidebar.header("オプション")

    # Temperatureスライダーとその補足情報
    with st.sidebar.beta_expander("Temperature  🛈"):
        st.write("Temperature（温度）:モデルの出力の「確信度」または「多様性」を制御します。値が高いとモデルの出力は多様性が増し、予測はよりランダムになります。逆に、値が低いとモデルの出力はより確信度が高くなり、最も確率的に高い結果を選びやすくなります。【推奨値:0.10】")
        temperature = st.slider("", 0.0, 2.0, 0.1, 0.01)

    # Top_Pスライダーとその補足情報
    with st.sidebar.beta_expander("Top_P  🛈"):
        st.write("Top_P: 温度と同様に、これはランダム性を制御しますが、別の方法を使用します。Top_P を下げると、より可能性が高い回答に絞り込まれます。Top_P を上げると、確率が高い回答と低い回答の両方から選択されるようになります。【推奨値:0.50】")
        top_p = st.slider("", 0.0, 1.0, 0.5, 0.01)

    # 留意点の表示
    st.sidebar.markdown('<span style="color:red">***個人情報や機密情報は入力しないでください**</span>', unsafe_allow_html=True)

    # 機能に応じたUIの表示
    if selected_option == "選択してください":
        pass  # 何も表示しない
    elif selected_option == "Q&A":
        # Build the user interface
        st.title("Q&A")

        # Create a placeholder for the user's input
        user_input = st.text_area("自由に質問を入力してください。", value=st.session_state.get("user_input_Q&A", ""))

        # トークン数（文字数）をカウント
        token_count = len(user_input.split())

        # トークン数を表示
        st.markdown(f'<span style="color:grey; font-size:12px;">トークン: {token_count}</span>', unsafe_allow_html=True)

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

        # 右側の入力フォーム
        user_input = st.text_area("翻訳したい文章を入力し、実行ボタンを押してください。", height=200, key="user_input_translation")

        # 追加：補足情報の入力フィールド
        additional_info = st.text_area("補足情報を入力してください。", "", key="additional_info")

        # トークン数（文字数）をカウント
        token_count = len(user_input.split()) + len(additional_info.split())

        # トークン数を表示
        st.markdown(f'<span style="color:grey; font-size:12px;">トークン: {token_count}</span>', unsafe_allow_html=True)

        # Create a placeholder for the bot's responses
        bot_response_placeholder = st.empty()

        if st.button("実行", key="send_button_translation"):
            if user_input.strip() == "":
                st.warning("データを入力してください。")
            else:
                initial_prompt = (
                    "あなたは優秀な翻訳家です。あなたの役割は、英文を日本語に翻訳し、日本語のウェブサイト上で日本人の投資家向けに翻訳された間違いのない情報を提供することです。\n"
                    "可能な限り原文に忠実に、漏れや間違いなく、自然な日本語に翻訳してください。\n"
                    "＃指示\n"
                    f"{user_input}を翻訳してください。\n"
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
                communicate(initial_prompt, bot_response_placeholder, model, temperature, top_p)

    elif selected_option == "Proofreading":
        st.title("Proofreading")

        # 右側の入力フォーム
        user_input = st.text_area("校閲/校正したい文章を入力し、実行ボタンを押してください。", height=200, key="user_input_proof")

        # 追加：補足情報の入力フィールド
        additional_info = st.text_area("補足情報を入力してください。", "", key="additional_info")

        # トークン数（文字数）をカウント
        token_count = len(user_input.split()) + len(additional_info.split())

        # トークン数を表示
        st.markdown(f'<span style="color:grey; font-size:12px;">トークン: {token_count}</span>', unsafe_allow_html=True)

        # Create a placeholder for the bot's responses
        bot_response_placeholder = st.empty()

        if st.button("実行", key="send_button_proofreading"):
            if user_input.strip() == "":
                st.warning("データを入力してください。")
            else:
                initial_prompt = (
                    """あなたは校閲・校正の優秀なスペシャリストです。
                    あなたの役割は、日本の投資家向けに公表される情報を校閲・校正し、間違いなく高品質な文章を作成することです。
                    これから入力する文章に対して、下記の操作1を行い、出力してください。
                    操作1:[
                    修正1:誤字脱字、タイプミスがあった場合は全て指摘してください。指摘した個所は
                    ・「〇〇」→「〇〇」
                    と箇条書きで抽出してください。
                    修正2:言葉の表記にばらつきがあった場合は全て指摘してしてください。
                    修正3:数字の表記は、１桁は全角、２桁以上は半角とします。表記にばらつきがあった場合は全て指摘してしてください。
                    修正4:慣用句やことわざの表現に誤りがあると考えられる場合は全て指摘してください。
                    修正5:文脈に合わない単語が使われている場合は誤りを全て指摘してください。
                    修正6:主語と述語の組み合わせが間違っている場合は全て指摘してください。
                    修正7:文末の表現は全て「です、ます」口調に統一してください。
                    修正8:句読点の打ち方に不自然な点がある場合は全て指摘してください。
                    ]

                    操作1を行う際には下記の条件を遵守して操作を行ってください。
                    条件:[
                    ・文章の順番に変更を加えない
                    ・架空の表現や慣用句、ことわざを使用しない。
                    ・文章を省略しない。
                    ]

                    操作2:[
                    操作1を行った後に指摘事項を全て修正した正しい文章を出力してください。]
                    """
                    f"{user_input}を校閲・校正してください。\n"
                    f"＃補足情報: {additional_info}"
                )
                st.session_state["user_input"] = initial_prompt
                communicate(initial_prompt, bot_response_placeholder, model, temperature, top_p)


    elif selected_option == "Excel Formula Analysis":
        st.title("Excel Formula Analysis")

        # 右側の入力フォーム
        user_input = st.text_area("解析したいExcelの式を入力し、実行ボタンを押してください。", height=200, key="user_input_excel")

        # 追加：補足情報の入力フィールド
        additional_info = st.text_area("補足情報を入力してください。", "", key="additional_info")

        # トークン数（文字数）をカウント
        token_count = len(user_input.split()) + len(additional_info.split())

        # トークン数を表示
        st.markdown(f'<span style="color:grey; font-size:12px;">トークン: {token_count}</span>', unsafe_allow_html=True)

        # Create a placeholder for the bot's responses
        bot_response_placeholder = st.empty()

        if st.button("実行", key="send_button_formula"):
            if user_input.strip() == "":
                st.warning("データを入力してください。")
            else:
                initial_prompt = (
                    "あなたは金融・投資・経済情報の分析を行うスペシャリストで、Microsoft Excelのエキスパートです。\n"
                    "あなたの役割は、情報分析のために作成された過去の複雑なExcel関数を分析し、わかりやすく説明することです。\n"
                    "これから入力するExcel関数に対して、下記の操作1を行い、出力してください。\n"
                    "操作1:[\n"
                    "複雑なネスト構造になっているExcel関数を改行し、わかりやすく表示してください。\n"
                    "]\n"
                    "操作2:[\n"
                    "操作1を行った後にこのExcel関数がどのような処理を行おうとしているものか解説し、よりシンプルで分かりやすい関数に書き換えが可能であれば、その提案をしてください。]\n"
                    "＃Excel関数:\n"
                    f"{user_input}\n"
                    "＃補足情報:\n"
                    f"{additional_info}\n"
                )
                st.session_state["user_input"] = initial_prompt
                communicate(initial_prompt, bot_response_placeholder, model, temperature, top_p)


    elif selected_option == "VBA Analysis":
        st.title("VBA Analysis")

        # 右側の入力フォーム
        user_input = st.text_area("解析したいVBAのコードを入力し、実行ボタンを押してください。", height=200, key="user_input_vba")

        # 追加：補足情報の入力フィールド
        additional_info = st.text_area("補足情報を入力してください。", "", key="additional_info")

        # トークン数（文字数）をカウント
        token_count = len(user_input.split()) + len(additional_info.split())

        # トークン数を表示
        st.markdown(f'<span style="color:grey; font-size:12px;">トークン: {token_count}</span>', unsafe_allow_html=True)

        # Create a placeholder for the bot's responses
        bot_response_placeholder = st.empty()

        if st.button("実行", key="send_button_vba"):
            if user_input.strip() == "":
                st.warning("データを入力してください。")
            else:
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
                st.session_state["user_input"] = initial_prompt
                communicate(initial_prompt, bot_response_placeholder, model, temperature, top_p)

    elif selected_option == "Data Analysis":
        st.title("Data Analysis")

        # 右側の入力フォーム
        user_input = st.text_area("解析したいログデータを入力し、実行ボタンを押してください。", height=200, key="user_input_data")

        # 追加：補足情報の入力フィールド
        additional_info = st.text_area("補足情報を入力してください。", "", key="additional_info")

        # トークン数（文字数）をカウント
        token_count = len(user_input.split()) + len(additional_info.split())

        # トークン数を表示
        st.markdown(f'<span style="color:grey; font-size:12px;">トークン: {token_count}</span>', unsafe_allow_html=True)

        # Create a placeholder for the bot's responses
        bot_response_placeholder = st.empty()

        if st.button("実行", key="send_button_data"):
            if user_input.strip() == "":
                st.warning("データを入力してください。")
            else:
                initial_prompt = (
                    "あなたはデータ分析のスペシャリストです。\n"
                    "以下のインプット情報に記載されたログ情報を分析して、セキュリティリスク（不正兆候や異常値等）があるデータを抽出して、理由とともに教えてください。]\n"
                    "＃インプット:\n"
                    f"{user_input}\n"
                    "＃補足情報:\n"
                    f"{additional_info}\n"
                )
                st.session_state["user_input"] = initial_prompt
                communicate(initial_prompt, bot_response_placeholder, model, temperature, top_p)


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

