import streamlit as st
import google.generativeai as genai
from PIL import Image
import json
import re

# --- 1. 页面基础配置 ---
st.set_page_config(page_title="互联网人减脂补救站", layout="wide")

# --- 2. 侧边栏：配置与个人信息 ---
with st.sidebar:
    st.title("⚙️ 教练配置中心")
    api_key = st.text_input("输入你的 Gemini API Key", type="password")
    
    st.divider()
    st.header("📊 个人底座数据")
    height = st.number_input("身高 (cm)", value=175)
    weight = st.number_input("当前体重 (kg)", value=80.0)
    target_mode = st.selectbox("OKR 目标设定", ["躺平版 (0.3kg/周)", "奋斗版 (0.5kg/周)", "极客版 (0.8kg/周)"])
    
    if st.button("更新我的状态"):
        st.success("状态已同步！AI 随时待命。")

# --- 3. 核心逻辑：AI 指令集 (System Instruction) ---
SYSTEM_INSTRUCTION = f"""
你是一位专门为“高压互联网人”设计的“低摩擦减肥教练”。
当前用户信息：身高 {height}cm, 体重 {weight}kg, 目标 {target_mode}。

# 核心准则：
1. 建议必须极易获得（便利店、外卖、食堂）。
2. 运动必须碎片化（工位、小区、不换衣、不流汗）。
3. 语气：像个懂行的互联网同事，多用黑话（ROI、对齐、坏账、补救、下沉）。

# 任务逻辑：
- 识别图片中的食物。
- 给出红黄绿灯评价。
- 提供具体的【补救方案】：下一餐吃什么 + 现在做什么微运动。

# 输出规范：
始终返回 JSON 格式：
{{
  "state": "meal_analysis",
  "analysis": "对食物的毒舌点评",
  "action_point": "具体的补救SOP",
  "coach_comment": "鼓励用户的俏皮话"
}}
"""

# --- 4. 主界面设计 ---
st.title("🏃‍♂️ 互联网人“低摩擦”减脂补救站")
st.caption("基于 Google Gemini 1.5 Pro | 专为高压运营/开发/产品定制")

tab1, tab2 = st.tabs(["📸 饮食补救识别", "📈 我的减脂周报"])

with tab1:
    uploaded_file = st.file_uploader("拍下你的午餐/晚餐/零食...", type=["jpg", "jpeg", "png"])
    
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption="待对齐的卡路里大盘", width=400)
        
        if st.button("开始分析并给出补救方案"):
            if not api_key:
                st.error("请在左侧填入你的 API Key！")
            else:
                try:
                    # 初始化 Gemini
                    genai.configure(api_key=api_key)
                    model = genai.GenerativeModel(
                        model_name="gemini-1.5-pro",
                        system_instruction=SYSTEM_INSTRUCTION
                    )
                    
                    with st.spinner("AI 正在扫描‘坏账’，请稍后..."):
                        response = model.generate_content([image, "请分析这顿饭并给出补救方案。"])
                        
                        # 解析 JSON
                        res_text = response.text
                        # 简单的正则提取 JSON 块
                        json_match = re.search(r'\{.*\}', res_text, re.DOTALL)
                        if json_match:
                            data = json.loads(json_match.group())
                            
                            st.subheader("🧐 AI 教练点评")
                            st.info(data.get("analysis", "分析失败"))
                            
                            st.subheader("💡 补救 Action Point")
                            st.success(data.get("action_point", "补救建议缺失"))
                            
                            st.warning(data.get("coach_comment", "加油！"))
                        else:
                            st.write(res_text) # 如果不是JSON则直接输出
                            
                except Exception as e:
                    st.error(f"发生错误: {str(e)}")

with tab2:
    st.write("周报功能正在快速迭代中... 敬请期待下一个版本。")
    st.metric(label="当前 BMI", value=round(weight / ((height/100)**2), 1))
