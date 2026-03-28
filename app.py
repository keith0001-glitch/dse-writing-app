import streamlit as st
import google.generativeai as genai
from PIL import Image

# --- 網頁設定 ---
st.set_page_config(page_title="DSE 中文作文 AI 批改助手", page_icon="📝")
st.title("📝 DSE 中文作文 AI 批改助手")
st.markdown("上傳你的手寫作文照片，AI 閱卷員為你提供 DSE 標準評分與改寫任務！")

# --- 系統設定：自動讀取隱藏的 API Key ---
try:
    # 讓程式自動從 Streamlit 的保險箱讀取金鑰
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
except KeyError:
    st.error("系統尚未設定 API Key，請聯絡開發者！")
    st.stop() # 找不到金鑰就暫停執行

# --- 主畫面：用戶輸入區 ---
col1, col2 = st.columns(2)
with col1:
    grade = st.selectbox("學生年級", ["中一", "中二", "中三", "中四", "中五", "中六"])
    genre = st.selectbox("文體", ["記敘抒情", "議論文", "說明文", "描寫文", "實用文"])
with col2:
    topic = st.text_input("作文題目", placeholder="例如：我的夢想 / 談知足")
    custom_rubric = st.text_input("自訂評分要求 (選填)", placeholder="例如：必須使用三個成語")

# --- 圖片上傳區 ---
uploaded_file = st.file_uploader("📸 拍照或上傳作文圖片 (支援 JPG, PNG)", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    # 顯示上傳的圖片
    image = Image.open(uploaded_file)
    st.image(image, caption="已上傳的作文", use_container_width=True)

# --- 批改按鈕與 AI 處理邏輯 ---
if st.button("🚀 開始批改", type="primary"):
    if not api_key:
        st.error("請先在左側輸入 Gemini API Key！")
    elif not topic:
        st.warning("請輸入作文題目！")
    else:
        with st.spinner("AI 閱卷員正在認真批改中，請稍候..."):
            try:
                # 設定 Gemini 模型 (使用 Flash 模型速度快且支援視覺，或可改用 pro)
                model = genai.GenerativeModel('gemini-1.5-flash-latest')
                
                # 組合 Prompt
                prompt = f"""
                你現在是一位資深的香港中學文憑試（DSE）中文科卷二寫作能力閱卷員。
                學生年級：{grade}
                文章文體：{genre}
                寫作題目：{topic}
                附加要求：{custom_rubric if custom_rubric else "無"}
                
                請辨識圖片中的手寫文字（繁簡皆可），並按以下格式以 Markdown 輸出：
                
                1. 【原文辨識】：列出辨識出的原文。
                2. 【文字與病句修正】：捉出错别字、病句並修正。
                3. 【謄改任務】：指出文章中 1-2 處最需要改善的位置。不要直接給出完美答案，而是設計一個簡單的「改寫任務」，引導學生自行思考如何修改（例如提示修辭、立意提升等）。
                4. 【整體評分】：根據 DSE 標準預估等級。
                5. 【總結評語】：分為內容、表達、結構三方面給予具體評價。
                6. 【參考範文】：根據上述條件，提供一篇高質量範文。
                """
                
                # 呼叫 API (傳入 Prompt 和 圖片)
                response = model.generate_content([prompt, image])
                
                # 顯示結果
                st.success("批改完成！")
                st.markdown(response.text)
                
            except Exception as e:
                st.error(f"發生錯誤：{e}")